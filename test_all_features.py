"""
股票分析助手 - 完整功能测试脚本
测试所有 Web 功能模块
"""
import httpx
import json

BASE_URL = "http://127.0.0.1:8000"

print("=" * 70)
print("  Stock Analyzer - Full Feature Test")
print("=" * 70)

def test_api(name, url, method="GET", data=None):
    """测试 API 接口"""
    print(f"\n{'='*60}")
    print(f"测试：{name}")
    print(f"URL: {method} {url}")
    
    try:
        with httpx.Client(timeout=60.0) as client:
            if method == "GET":
                resp = client.get(url)
            else:
                resp = client.post(url, json=data)
            
            print(f"状态：{resp.status_code}")
            
            if resp.status_code == 200:
                result = resp.json()
                if isinstance(result, dict):
                    if result.get("success"):
                        data_result = result.get("data", {})
                        if isinstance(data_result, list):
                            print(f"[OK] - Got {len(data_result)} items")
                        elif isinstance(data_result, dict):
                            print(f"[OK]")
                            if "price" in data_result:
                                print(f"   Price: {data_result.get('price')}")
                            if "pe" in data_result:
                                print(f"   PE: {data_result.get('pe')}")
                            if "name" in data_result:
                                print(f"   Name: {data_result.get('name')}")
                    else:
                        print(f"[WARN] success=false")
                        print(f"   {result.get('message', '')}")
                else:
                    print(f"[OK] - HTML page")
            else:
                print(f"[FAIL] {resp.status_code}")
                print(f"   {resp.text[:200]}")
                
    except Exception as e:
        print(f"[ERROR] {e}")

# 1. Home Page API
print("\n" + "="*70)
print("[1. Home - Stock Query & Analysis]")
print("="*70)

test_api(
    "Query BYD (002594)",
    f"{BASE_URL}/api/stock/query",
    method="POST",
    data={"query": "002594"}
)

test_api(
    "Query CATL (300750)",
    f"{BASE_URL}/api/stock/query",
    method="POST",
    data={"query": "300750"}
)

test_api(
    "AI Analysis - BYD",
    f"{BASE_URL}/api/stock/analyze",
    method="POST",
    data={"query": "002594"}
)

# 2. Hot Sectors
print("\n" + "="*70)
print("[2. Hot Sectors]")
print("="*70)

test_api(
    "Hot Sectors List",
    f"{BASE_URL}/api/sectors/hot"
)

# 3. Smart Screener
print("\n" + "="*70)
print("[3. Smart Screener]")
print("="*70)

strategies = [
    ("Value", "value"),
    ("Growth", "growth"),
    ("Hot", "hot"),
    ("Dividend", "dividend"),
    ("Tech", "tech"),
    ("Breakout", "breakout"),
    ("LowRisk", "lowrisk"),
    ("North", "north"),
]

for name, strategy in strategies:
    test_api(
        f"Strategy - {name}",
        f"{BASE_URL}/api/screener",
        method="POST",
        data={"strategy": strategy, "query": ""}
    )

# 4. Historical Reports
print("\n" + "="*70)
print("[4. Historical Reports]")
print("="*70)

test_api(
    "Get Reports List",
    f"{BASE_URL}/api/reports"
)

# 5. Settings
print("\n" + "="*70)
print("[5. Settings]")
print("="*70)

test_api(
    "Get Settings",
    f"{BASE_URL}/api/settings"
)

# 6. Page Access Test
print("\n" + "="*70)
print("[6. Page Access Test]")
print("="*70)

pages = [
    ("Home", "/home"),
    ("Sectors", "/sector"),
    ("Screener", "/screener"),
    ("Favorites", "/favorites"),
    ("Reports", "/reports"),
    ("Settings", "/settings"),
]

for name, path in pages:
    test_api(name, f"{BASE_URL}{path}")

# Summary
print("\n" + "="*70)
print("  TEST COMPLETE")
print("="*70)
