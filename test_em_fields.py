import httpx
import json

code = '002594'  # 比亚迪
full_code = f"0.{code}"

url = "https://push2.eastmoney.com/api/qt/stock/get"
params = {
    "secid": full_code,
    "fields": "f12,f14,f43,f44,f45,f46,f47,f48,f49,f50,f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61,f62,f63,f64,f65,f66,f67,f68,f69,f70,f71,f72,f73,f74,f75,f76,f77,f78,f79,f80,f81,f82,f83,f84,f85,f86,f87,f88,f89,f90,f91,f92,f93,f94,f95,f96,f97,f98,f99,f100,f101,f102,f103,f104,f105,f106,f107,f108,f109,f110,f111,f112,f113,f114,f115,f116,f117,f118,f119,f120,f121,f122,f123,f124,f125,f126,f127,f128,f129,f130,f131,f132,f133,f134,f135,f136,f137,f138,f139,f140,f141,f142,f143,f144,f145,f146,f147,f148,f149,f150,f151,f152,f153,f154,f155,f156,f157,f158,f159,f160,f161,f162,f163,f164,f165,f166,f167,f168,f169,f170",
    "ut": "fa5fd1943c7b386f172d6893dbfba10b",
    "fltt": "2",
    "invt": "2",
}

headers = {
    'User-Agent': 'Mozilla/5.0',
    'Referer': 'https://quote.eastmoney.com/',
}

print(f"Testing EM API for {code}:\n")

try:
    with httpx.Client(timeout=30.0) as client:
        resp = client.get(url, params=params, headers=headers)
        resp.raise_for_status()
        data = resp.json()
        
        if data.get("data"):
            d = data["data"]
            print(f"Code: {d.get('f12')}")
            print(f"Name: {d.get('f14')}")
            print(f"Price (f43): {d.get('f43')}")
            print(f"Change% (f170): {d.get('f170')}")
            print(f"PE (f164): {d.get('f164')}")
            print(f"PB (f167): {d.get('f167')}")
            print(f"ROE (f168): {d.get('f168')}")
            print(f"Turnover (f166): {d.get('f166')}")
            print(f"Volume Ratio (f165): {d.get('f165')}")
            print(f"Market Cap (f116): {d.get('f116')}")
            print(f"Float Cap (f117): {d.get('f117')}")
            
            # 计算验证
            print(f"\n验证计算:")
            print(f"PE 应该显示：{d.get('f164', 0)} (不需要除 100)")
            print(f"换手率应该显示：{d.get('f166', 0)} (不需要除 100)")
            
except Exception as e:
    print(f"Error: {e}")
