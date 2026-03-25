import httpx

code = '002594'
tc_code = f'sz{code}'
tc_url = f"http://qt.gtimg.cn/q={tc_code}"

print(f"腾讯字段详细分析 - {code}:\n")

try:
    with httpx.Client(timeout=10.0) as client:
        resp = client.get(tc_url)
        content = resp.content.decode('gbk')
        if '=' in content and '~' in content:
            data_str = content.split('=')[1].strip('"').split('~')
            
            print(f"Total fields: {len(data_str)}")
            print(f"\n关键字段:")
            
            # 打印所有可能相关的字段
            key_indices = [1, 2, 3, 21, 38, 39, 43, 45, 47, 49, 50]
            for i in key_indices:
                if i < len(data_str):
                    print(f"  [{i:2d}] = {data_str[i]}")
                    
            # 根据腾讯文档：
            # f1=名称，f2=涨幅%，f3=股价，f21=总市值 (亿), f38=换手率，f39=PE, f43=PB
            print(f"\n根据腾讯文档:")
            print(f"  名称 [1]: {data_str[1] if len(data_str) > 1 else 'N/A'}")
            print(f"  涨幅% [2]: {data_str[2] if len(data_str) > 2 else 'N/A'}")
            print(f"  股价 [3]: {data_str[3] if len(data_str) > 3 else 'N/A'}")
            print(f"  总市值 (亿) [21]: {data_str[21] if len(data_str) > 21 else 'N/A'}")
            print(f"  换手率% [38]: {data_str[38] if len(data_str) > 38 else 'N/A'}")
            print(f"  PE [39]: {data_str[39] if len(data_str) > 39 else 'N/A'}")
            print(f"  PB [43]: {data_str[43] if len(data_str) > 43 else 'N/A'}")
            
except Exception as e:
    print(f"Error: {e}")
