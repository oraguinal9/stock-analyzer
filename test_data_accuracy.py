import httpx

# 测试比亚迪 002594
code = '002594'
full_code = f"0.{code}"

url = "https://push2.eastmoney.com/api/qt/stock/get"
params = {
    "secid": full_code,
    "fields": "f12,f14,f43,f164,f166,f167,f168,f165,f116,f117",
    "ut": "fa5fd1943c7b386f172d6893dbfba10b",
    "fltt": "2",
    "invt": "2",
}

headers = {
    'User-Agent': 'Mozilla/5.0',
    'Referer': 'https://quote.eastmoney.com/',
}

print(f"Testing {code} (比亚迪):\n")
print("东方财富原始数据 vs 实际应该显示的值")
print("=" * 60)

try:
    with httpx.Client(timeout=30.0) as client:
        resp = client.get(url, params=params, headers=headers)
        data = resp.json()
        
        if data.get("data"):
            d = data["data"]
            
            pe_raw = d.get('f164', 0)
            turnover_raw = d.get('f166', 0)
            pb_raw = d.get('f167', 0)
            roe_raw = d.get('f168', 0)
            volume_ratio_raw = d.get('f165', 0)
            
            print(f"PE 原始值：{pe_raw}")
            print(f"  - 如果显示 25.35，则不需要处理")
            print(f"  - 如果显示 0.25，则需要 ×100")
            print(f"  - 如果显示 2535，则需要 ÷100")
            print()
            print(f"换手率原始值：{turnover_raw}")
            print(f"  - 如果显示 8.24，则不需要处理")
            print(f"  - 如果显示 0.08，则需要 ×100")
            print(f"  - 如果显示 824，则需要 ÷100")
            print()
            print(f"PB 原始值：{pb_raw}")
            print(f"ROE 原始值：{roe_raw}")
            print(f"量比原始值：{volume_ratio_raw}")
            print()
            
            # 对比新浪财经数据
            sina_code = f'sz{code}'
            sina_url = f"http://hq.sinajs.cn/list={sina_code}"
            
            with httpx.Client(timeout=10.0) as c2:
                resp2 = c2.get(sina_url)
                content = resp2.content.decode('gbk')
                if '=' in content:
                    data_str = content.split('=')[1].strip('"').split(',')
                    sina_pe = data_str[39] if len(data_str) > 39 else 'N/A'
                    sina_turnover = data_str[38] if len(data_str) > 38 else 'N/A'
                    
                    print(f"新浪财经数据（参考）:")
                    print(f"  PE: {sina_pe}")
                    print(f"  换手率：{sina_turnover}%")
                    
except Exception as e:
    print(f"Error: {e}")
