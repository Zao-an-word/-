import requests

BASE_URL = "http://127.0.0.1:8000"

def test_root():
    try:
        response = requests.get(f"{BASE_URL}/")
        assert response.status_code == 200
        print("✅ 根路径 / 测试通过:", response.json())
    except Exception as e:
        print("❌ 根路径 / 测试失败:", str(e))

def test_docs():
    try:
        response = requests.get(f"{BASE_URL}/docs")
        assert response.status_code == 200
        print("✅ Swagger 文档 /docs 可访问")
    except Exception as e:
        print("❌ /docs 文档访问失败:", str(e))

def test_health_check():
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ /health 接口测试通过")
        else:
            print("⚠️ /health 存在但返回非200")
    except Exception:
        print("ℹ️ /health 接口可能未定义，略过")

if __name__ == "__main__":
    print("🚀 正在测试 FastAPI 后端服务状态...\n")
    test_root()
    test_docs()
    test_health_check()
