import httpx

# 测试东方财富 API
url = "https://push2.eastmoney.com/api/qt/clist/get"
params = {
    "pn": 1,
    "pz": 10,
    "po": "1",
    "np": "1",
    "ut": "bd1d9ddb04089700cf9c27f6f7426281",
    "fltt": "2",
    "invt": "2",
    "fid": "f3",
    "fs": "m:0 t:6,m:0 t:80,m:1 t:2,m:1 t:23",
    "fields": "f12,f14,f2,f3,f4"
}

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Referer': 'https://quote.eastmoney.com/',
}

print(f"Testing EastMoney API: {url}")
print(f"Params: {params}\n")

try:
    with httpx.Client(timeout=30.0) as client:
        resp = client.get(url, params=params, headers=headers)
        print(f"Status: {resp.status_code}")
        print(f"Content: {resp.text[:500]}")
except Exception as e:
    print(f"Error: {e}")
