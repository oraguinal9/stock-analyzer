import httpx

# 测试新浪财经 API
codes = ['sh600000', 'sz002594', 'sz300750', 'sh600519']
url = f"http://hq.sinajs.cn/list={','.join(codes)}"

print(f"Testing Sina API: {url}\n")

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer': 'https://finance.sina.com.cn/',
}

try:
    with httpx.Client(timeout=30.0) as client:
        resp = client.get(url, headers=headers)
        resp.raise_for_status()
        content = resp.content.decode('gbk')
        
        print(f"Status: {resp.status_code}")
        print(f"Content length: {len(content)}")
        print(f"\nRaw content:\n{content[:1000]}")
        
        # 解析数据
        lines = content.strip().split('\n')
        print(f"\nParsed {len(lines)} lines:")
        for i, line in enumerate(lines):
            if '=' in line:
                parts = line.split('=')
                code = codes[i]
                data_str = parts[1].strip('"').split(',')
                print(f"\n{code}:")
                print(f"  Name: {data_str[0]}")
                print(f"  Price: {data_str[3]}")
                print(f"  Change%: {data_str[2]}")
                print(f"  Open: {data_str[1]}")
                print(f"  High: {data_str[4]}")
                print(f"  Low: {data_str[5]}")
                print(f"  Volume: {data_str[8]}")
                print(f"  Amount: {data_str[9]}")
                
except Exception as e:
    print(f"Error: {e}")
