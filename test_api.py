"""测试股票分析 API"""
import httpx
import json

BASE_URL = "http://127.0.0.1:8000"

def test_query_stock():
    """测试股票查询"""
    print("\n[TEST 1] 查询股票：比亚迪 002594")
    with httpx.Client(timeout=60.0) as client:
        response = client.post(
            f"{BASE_URL}/api/stock/query",
            json={"query": "比亚迪 002594", "select_type": "A 股"}
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Success: {data.get('success')}")
            if 'data' in data:
                print(f"Stock: {data['data'].get('name')} ({data['data'].get('code')})")
                print(f"Price: {data['data'].get('price')}")
                print(f"Change: {data['data'].get('change_pct')}%")
        else:
            print(f"Error: {response.text}")

def test_analyze_stock():
    """测试股票分析"""
    print("\n[TEST 2] 分析股票：比亚迪 002594")
    with httpx.Client(timeout=120.0) as client:
        response = client.post(
            f"{BASE_URL}/api/stock/analyze",
            json={"query": "比亚迪 002594", "select_type": "A 股"}
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Success: {data.get('success')}")
            if 'data' in data:
                quote = data['data'].get('quote', {})
                report = data['data'].get('report', {})
                print(f"Stock: {quote.get('name')} ({quote.get('code')})")
                print(f"Rating: {report.get('rating')}")
                print(f"Score: {report.get('score')}/100")
                print(f"\nReport Preview (first 200 chars):")
                print(report.get('content', '')[:200])
        else:
            print(f"Error: {response.text}")

def test_settings():
    """测试获取设置"""
    print("\n[TEST 3] 获取设置")
    with httpx.Client(timeout=10.0) as client:
        response = client.get(f"{BASE_URL}/api/settings")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Settings: {json.dumps(data, indent=2)}")

if __name__ == "__main__":
    print("=" * 60)
    print(" 股票分析 API 测试")
    print("=" * 60)
    
    test_settings()
    test_query_stock()
    test_analyze_stock()
    
    print("\n" + "=" * 60)
    print(" 测试完成")
    print("=" * 60)
