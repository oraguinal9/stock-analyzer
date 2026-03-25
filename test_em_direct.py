import httpx

code = '300750'
full_code = f"0.{code}"  # 0=深市

url = "https://push2.eastmoney.com/api/qt/stock/get"
params = {
    "secid": full_code,
    "fields": "f12,f14,f43,f170,f169,f164,f167,f168,f166,f165,f116,f117",
    "ut": "fa5fd1943c7b386f172d6893dbfba10b",
    "fltt": "2",
    "invt": "2",
}

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Referer': 'https://quote.eastmoney.com/',
}

print(f"Testing EM API: {url}")
print(f"Params: {params}\n")

try:
    with httpx.Client(timeout=30.0) as client:
        resp = client.get(url, params=params, headers=headers)
        resp.raise_for_status()
        data = resp.json()
        
        print(f"Full response: {data}\n")
        
        if data.get("data"):
            d = data["data"]
            print(f"f12 (code): {d.get('f12')}")
            print(f"f14 (name): {d.get('f14')}")
            print(f"f43 (price): {d.get('f43')}")
            print(f"f164 (PE): {d.get('f164')}")
            print(f"f167 (PB): {d.get('f167')}")
            
except Exception as e:
    print(f"Error: {e}")
