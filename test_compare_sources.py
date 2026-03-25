import httpx

code = '002594'

# 腾讯财经
tc_code = f'sz{code}'
tc_url = f"http://qt.gtimg.cn/q={tc_code}"

print(f"对比数据源 - {code} (比亚迪):\n")
print("=" * 60)

try:
    # 腾讯
    with httpx.Client(timeout=10.0) as client:
        resp = client.get(tc_url)
        content = resp.content.decode('gbk')
        if '=' in content and '~' in content:
            data_str = content.split('=')[1].strip('"').split('~')
            
            print(f"腾讯财经数据:")
            print(f"  名称：{data_str[1] if len(data_str) > 1 else 'N/A'}")
            print(f"  股价：{data_str[3] if len(data_str) > 3 else 'N/A'}")
            print(f"  涨跌幅：{data_str[2] if len(data_str) > 2 else 'N/A'}%")
            print(f"  PE(TTM): {data_str[39] if len(data_str) > 39 else 'N/A'}")
            print(f"  PB: {data_str[43] if len(data_str) > 43 else 'N/A'}")
            print(f"  换手率：{data_str[38] if len(data_str) > 38 else 'N/A'}%")
            print(f"  总市值：{data_str[21] if len(data_str) > 21 else 'N/A'}亿")
            print()
            
    # 东方财富
    em_code = f"0.{code}"
    em_url = "https://push2.eastmoney.com/api/qt/stock/get"
    em_params = {
        "secid": em_code,
        "fields": "f12,f14,f43,f164,f166,f167,f116",
        "ut": "fa5fd1943c7b386f172d6893dbfba10b",
        "fltt": "2",
        "invt": "2",
    }
    
    with httpx.Client(timeout=10.0) as client:
        resp = client.get(em_url, params=em_params)
        data = resp.json()
        
        if data.get("data"):
            d = data["data"]
            print(f"东方财富数据:")
            print(f"  股价：{d.get('f43', 0)}")
            print(f"  PE: {d.get('f164', 0)}")
            print(f"  PB: {d.get('f167', 0)}")
            print(f"  换手率：{d.get('f166', 0)}%")
            print(f"  总市值：{d.get('f116', 0)/1e8:.2f}亿")
            print()
            
    print("=" * 60)
    print("结论：两个数据源应该一致，如果不一致说明有问题")
    
except Exception as e:
    print(f"Error: {e}")
