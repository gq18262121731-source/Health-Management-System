"""
测试后端API功能脚本
"""
import sys
import requests
import json
from pathlib import Path

# 设置输出编码
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BASE_URL = "http://localhost:8000"


def test_health_check():
    """测试健康检查"""
    print("\n" + "=" * 60)
    print("[测试] 服务健康检查")
    print("=" * 60)
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        print("[错误] 无法连接到服务器，请确保后端服务已启动")
        return False
    except Exception as e:
        print(f"[错误] {str(e)}")
        return False


def test_ai_health_check():
    """测试AI服务健康检查"""
    print("\n" + "=" * 60)
    print("[测试] AI服务健康检查")
    print("=" * 60)
    try:
        response = requests.get(f"{BASE_URL}/api/ai/health", timeout=5)
        print(f"状态码: {response.status_code}")
        data = response.json()
        print(f"响应: {json.dumps(data, ensure_ascii=False, indent=2)}")
        return data.get("data", {}).get("ai_service_available", False)
    except Exception as e:
        print(f"[错误] {str(e)}")
        return False


def test_knowledge_base_stats():
    """测试知识库统计"""
    print("\n" + "=" * 60)
    print("[测试] 知识库统计信息")
    print("=" * 60)
    try:
        response = requests.get(f"{BASE_URL}/api/knowledge-base/stats", timeout=5)
        print(f"状态码: {response.status_code}")
        data = response.json()
        print(f"响应: {json.dumps(data, ensure_ascii=False, indent=2)}")
        return True
    except Exception as e:
        print(f"[错误] {str(e)}")
        return False


def test_knowledge_base_search():
    """测试知识库搜索"""
    print("\n" + "=" * 60)
    print("[测试] 知识库搜索功能")
    print("=" * 60)
    try:
        query = "高血压应该注意什么"
        response = requests.get(
            f"{BASE_URL}/api/knowledge-base/search",
            params={"query": query, "top_k": 3},
            timeout=10
        )
        print(f"查询: {query}")
        print(f"状态码: {response.status_code}")
        data = response.json()
        
        if data.get("status") == "success":
            results = data.get("data", {}).get("results", [])
            print(f"找到 {len(results)} 条结果:")
            for i, result in enumerate(results, 1):
                print(f"\n  结果 {i}:")
                print(f"    标题: {result.get('title', '未知')}")
                print(f"    相似度: {result.get('similarity_score', 0):.3f}")
                print(f"    内容预览: {result.get('content', '')[:100]}...")
            return True
        else:
            print(f"搜索失败: {data}")
            return False
    except Exception as e:
        print(f"[错误] {str(e)}")
        return False


def test_ai_consult_with_kb():
    """测试AI咨询（带知识库）"""
    print("\n" + "=" * 60)
    print("[测试] AI健康咨询（使用知识库）")
    print("=" * 60)
    try:
        payload = {
            "user_input": "我血压偏高，应该怎么控制？",
            "user_role": "elderly",
            "use_knowledge_base": True
        }
        print(f"问题: {payload['user_input']}")
        response = requests.post(
            f"{BASE_URL}/api/ai/consult",
            json=payload,
            timeout=30
        )
        print(f"状态码: {response.status_code}")
        data = response.json()
        
        if data.get("status") == "success":
            ai_response = data.get("data", {}).get("response", "")
            print(f"\nAI回复:")
            print("-" * 60)
            print(ai_response)
            print("-" * 60)
            return True
        else:
            print(f"咨询失败: {data}")
            return False
    except Exception as e:
        print(f"[错误] {str(e)}")
        return False


def test_ai_consult_without_kb():
    """测试AI咨询（不使用知识库）"""
    print("\n" + "=" * 60)
    print("[测试] AI健康咨询（不使用知识库）")
    print("=" * 60)
    try:
        payload = {
            "user_input": "我最近睡眠不好，怎么办？",
            "user_role": "elderly",
            "use_knowledge_base": False
        }
        print(f"问题: {payload['user_input']}")
        response = requests.post(
            f"{BASE_URL}/api/ai/consult",
            json=payload,
            timeout=30
        )
        print(f"状态码: {response.status_code}")
        data = response.json()
        
        if data.get("status") == "success":
            ai_response = data.get("data", {}).get("response", "")
            print(f"\nAI回复:")
            print("-" * 60)
            print(ai_response[:500] + "..." if len(ai_response) > 500 else ai_response)
            print("-" * 60)
            return True
        else:
            print(f"咨询失败: {data}")
            return False
    except Exception as e:
        print(f"[错误] {str(e)}")
        return False


def main():
    """主测试函数"""
    print("=" * 60)
    print("后端服务API功能测试")
    print("=" * 60)
    print(f"测试目标: {BASE_URL}")
    print("\n提示: 请确保后端服务已启动 (python main.py)")
    
    results = {}
    
    # 1. 健康检查
    results["服务健康"] = test_health_check()
    if not results["服务健康"]:
        print("\n[警告] 服务未启动，请先启动后端服务")
        return
    
    # 2. AI服务检查
    results["AI服务"] = test_ai_health_check()
    
    # 3. 知识库统计
    results["知识库统计"] = test_knowledge_base_stats()
    
    # 4. 知识库搜索
    results["知识库搜索"] = test_knowledge_base_search()
    
    # 5. AI咨询（带知识库）
    results["AI咨询(带知识库)"] = test_ai_consult_with_kb()
    
    # 6. AI咨询（不带知识库）
    results["AI咨询(不带知识库)"] = test_ai_consult_without_kb()
    
    # 总结
    print("\n" + "=" * 60)
    print("[测试总结]")
    print("=" * 60)
    for test_name, passed in results.items():
        status = "✓ 通过" if passed else "✗ 失败"
        print(f"{test_name}: {status}")
    
    passed_count = sum(1 for v in results.values() if v)
    total_count = len(results)
    print(f"\n总计: {passed_count}/{total_count} 项测试通过")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n测试被用户中断")
    except Exception as e:
        print(f"\n[严重错误] {str(e)}")

