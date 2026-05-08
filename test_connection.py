import httpx
import json
import sys

SERVER_URL = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"

def test_connection():
    """测试MCP服务器连接"""
    print(f"测试连接到: {SERVER_URL}")
    print("=" * 60)

    try:
        # 测试基础连接
        print("1. 测试服务器连接...")
        response = httpx.get(f"{SERVER_URL}/", timeout=5.0)
        print(f"   ✓ 服务器响应: {response.status_code}")
    except Exception as e:
        print(f"   ✗ 连接失败: {e}")
        print("\n请确保服务器正在运行！")
        return False

    try:
        # 测试SSE端点
        print("\n2. 测试SSE端点...")
        with httpx.stream("GET", f"{SERVER_URL}/sse", timeout=5.0) as response:
            print(f"   ✓ SSE端点可访问")
            response.close()
    except Exception as e:
        print(f"   ✗ SSE端点测试失败: {e}")

    try:
        # 测试能力端点
        print("\n3. 测试能力端点...")
        response = httpx.get(f"{SERVER_URL}/capabilities", timeout=5.0)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ 服务器能力:")
            if 'tools' in data:
                print(f"     - 工具数量: {len(data['tools'])}")
                for tool in data['tools'][:5]:
                    print(f"     - {tool}")
                if len(data['tools']) > 5:
                    print(f"     - ... 还有 {len(data['tools']) - 5} 个工具")
    except Exception as e:
        print(f"   ✗ 能力端点测试失败: {e}")

    print("\n" + "=" * 60)
    print("测试完成！")
    print("\n在客户端中配置:")
    print(f"  服务器地址: {SERVER_URL}/sse")

    return True


if __name__ == "__main__":
    test_connection()
