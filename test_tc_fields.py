import httpx

code = '300750'
url = f"http://qt.gtimg.cn/q=sz{code}"

try:
    with httpx.Client(timeout=10.0) as client:
        resp = client.get(url)
        content = resp.content.decode('gbk')
        data_str = content.split('=')[1].strip('"').split('~')
        
        print(f"Checking Tencent fields for {code}:\n")
        key_indices = [3, 39, 47, 21, 45, 38, 40, 41, 43, 44]
        for i in key_indices:
            if i < len(data_str):
                print(f"  [{i:2d}] = {data_str[i]}")
            else:
                print(f"  [{i:2d}] = N/A")
                
except Exception as e:
    print(f"Error: {e}")
