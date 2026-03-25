import httpx

code = '300750'
tc_code = f'sz{code}'
url = f"http://qt.gtimg.cn/q={tc_code}"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Referer': 'https://stockapp.finance.qq.com/',
}

print(f"Testing Tencent API: {url}\n")

try:
    with httpx.Client(timeout=10.0) as client:
        resp = client.get(url, headers=headers)
        if resp.status_code == 200:
            content = resp.content.decode('gbk')
            print(f"Raw content:\n{content}\n")
            
            if '=' in content and '~' in content:
                data_str = content.split('=')[1].strip('"').split('~')
                print(f"Total fields: {len(data_str)}")
                print(f"\nKey fields:")
                print(f"  [3] Name: {data_str[3] if len(data_str) > 3 else 'N/A'}")
                print(f"  [39] PE: {data_str[39] if len(data_str) > 39 else 'N/A'}")
                print(f"  [40] PB: {data_str[40] if len(data_str) > 40 else 'N/A'}")
                print(f"  [21] Total Market Cap (亿): {data_str[21] if len(data_str) > 21 else 'N/A'}")
                print(f"  [41] Float Market Cap (亿): {data_str[41] if len(data_str) > 41 else 'N/A'}")
                print(f"  [38] Turnover: {data_str[38] if len(data_str) > 38 else 'N/A'}")
                print(f"  [49] PE (dynamic): {data_str[49] if len(data_str) > 49 else 'N/A'}")
                print(f"  [50] PE (static): {data_str[50] if len(data_str) > 50 else 'N/A'}")
                
except Exception as e:
    print(f"Error: {e}")
