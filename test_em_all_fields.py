import httpx

code = '002594'
full_code = f"0.{code}"

url = "https://push2.eastmoney.com/api/qt/stock/get"

# 获取所有字段
params = {
    "secid": full_code,
    "fields": "f12,f14,f43,f44,f45,f46,f47,f48,f49,f50,f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61,f62,f63,f64,f65,f66,f67,f68,f69,f70,f71,f72,f73,f74,f75,f76,f77,f78,f79,f80,f81,f82,f83,f84,f85,f86,f87,f88,f89,f90,f91,f92,f93,f94,f95,f96,f97,f98,f99,f100,f101,f102,f103,f104,f105,f106,f107,f108,f109,f110,f111,f112,f113,f114,f115,f116,f117,f118,f119,f120,f121,f122,f123,f124,f125,f126,f127,f128,f129,f130,f131,f132,f133,f134,f135,f136,f137,f138,f139,f140,f141,f142,f143,f144,f145,f146,f147,f148,f149,f150,f151,f152,f153,f154,f155,f156,f157,f158,f159,f160,f161,f162,f163,f164,f165,f166,f167,f168,f169,f170,f171,f172,f173,f174,f175,f176,f177,f178,f179,f180,f181,f182,f183,f184,f185,f186,f187,f188,f189,f190,f191,f192,f193,f194,f195,f196,f197,f198,f199,f200",
    "ut": "fa5fd1943c7b386f172d6893dbfba10b",
    "fltt": "2",
    "invt": "2",
}

headers = {
    'User-Agent': 'Mozilla/5.0',
    'Referer': 'https://quote.eastmoney.com/',
}

print(f"东方财富完整字段 - {code}:\n")

try:
    with httpx.Client(timeout=30.0) as client:
        resp = client.get(url, params=params, headers=headers)
        data = resp.json()
        
        if data.get("data"):
            d = data["data"]
            
            print(f"名称 (f14): {d.get('f14')}")
            print(f"股价 (f43): {d.get('f43')}")
            print()
            print(f"可能 PE 的字段:")
            print(f"  f164: {d.get('f164')}")
            print(f"  f162: {d.get('f162')}")
            print(f"  f163: {d.get('f163')}")
            print()
            print(f"可能 PB 的字段:")
            print(f"  f167: {d.get('f167')}")
            print(f"  f168: {d.get('f168')}")
            print()
            print(f"可能换手率的字段:")
            print(f"  f166: {d.get('f166')}")
            print(f"  f165: {d.get('f165')}")
            print()
            print(f"总市值:")
            print(f"  f116: {d.get('f116', 0)/1e8:.2f}亿")
            print(f"  f117: {d.get('f117', 0)/1e8:.2f}亿")
            print()
            print(f"其他:")
            print(f"  f168: {d.get('f168')} (可能是 ROE)")
            print(f"  f169: {d.get('f169')} (涨跌额)")
            print(f"  f170: {d.get('f170')} (涨跌幅%)")
            
except Exception as e:
    print(f"Error: {e}")
