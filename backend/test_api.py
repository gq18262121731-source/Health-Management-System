"""
API功能测试脚本
测试AI健康助手和知识库功能
"""
import requests
import json
import sys

BASE_URL = "http://localhost:8000"

# 设置输出编码
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')


def test_health_check():
    """测试健康检查接口"""
    print("=" * 60)
    print("[测试1] 健康检查接口")
    print("=" * 60)
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"[错误] {str(e)}")
        return False


def test_ai_health():
    """测试AI服务健康检查"""
    print("\n" + "=" * 60)
    print("[测试2] AI服务健康检查")
    print("=" * 60)
    try:
        response = requests.get(f"{BASE_URL}/api/ai/health")
        print(f"状态码: {response.status_code}")
        data = response.json()
        print(f"响应: {json.dumps(data, ensure_ascii=False, indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"[错误] {str(e)}")
        return False


def test_knowledge_base_stats():
    """测试知识库统计"""
    print("\n" + "=" * 60)
    print("[测试3] 知识库统计信息")
    print("=" * 60)
    try:
        response = requests.get(f"{BASE_URL}/api/knowledge-base/stats")
        print(f"状态码: {response.status_code}")
        data = response.json()
        print(f"响应: {json.dumps(data, ensure_ascii=False, indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"[错误] {str(e)}")
        return False


def test_knowledge_base_search():
    """测试知识库搜索"""
    print("\n" + "=" * 60)
    print("[测试4] 知识库搜索功能")
    print("=" * 60)
    try:
        query = "高血压应该注意什么"
        response = requests.get(f"{BASE_URL}/api/knowledge-base/search", params={
            "query": query,
            "top_k": 3
        })
        print(f"查询: {query}")
        print(f"状态码: {response.status_code}")
        data = response.json()
        print(f"找到 {len(data.get('data', {}).get('results', []))} 条结果")
        for i, result in enumerate(data.get('data', {}).get('results', [])[:3], 1):
            print(f"\n结果 {i}:")
            print(f"  标题: {result.get('title', '未知')}")
            print(f"  相似度: {result.get('similarity_score', 0):.3f}")
            print(f"  内容预览: {result.get('content', '')[:100]}...")
        return response.status_code == 200
    except Exception as e:
        print(f"[错误] {str(e)}")
        return False


def test_ai_consult_with_kb():
    """测试AI咨询（使用知识库）"""
    print("\n" + "=" * 60)
    print("[测试5] AI健康咨询（使用知识库）")
    print("=" * 60)
    try:
        payload = {
            "user_input": "我血压偏高，应该怎么控制？",
            "user_role": "elderly",
            "use_knowledge_base": True
        }
        print(f"问题: {payload['user_input']}")
        print("正在调用AI...")
        response = requests.post(
            f"{BASE_URL}/api/ai/consult",
            json=payload,
            timeout=60
        )
        print(f"状态码: {response.status_code}")
        data = response.json()
        
        if response.status_code == 200:
            response_text = data.get('data', {}).get('response', '')
            print(f"\n[AI回复]:")
            print(response_text[:500])
            if len(response_text) > 500:
                print("...")
            return True
        else:
            print(f"错误: {data}")
            return False
    except requests.exceptions.Timeout:
        print("[错误] 请求超时（可能AI服务响应较慢）")
        return False
    except Exception as e:
        print(f"[错误] {str(e)}")
        return False


def test_ai_consult_without_kb():
    """测试AI咨询（不使用知识库）"""
    print("\n" + "=" * 60)
    print("[测试6] AI健康咨询（不使用知识库）")
    print("=" * 60)
    try:
        payload = {
            "user_input": "我最近睡眠不好，怎么办？",
            "user_role": "elderly",
            "use_knowledge_base": False
        }
        print(f"问题: {payload['user_input']}")
        print("正在调用AI...")
        response = requests.post(
            f"{BASE_URL}/api/ai/consult",
            json=payload,
            timeout=60
        )
        print(f"状态码: {response.status_code}")
        data = response.json()
        
        if response.status_code == 200:
            response_text = data.get('data', {}).get('response', '')
            print(f"\n[AI回复]:")
            print(response_text[:300])
            if len(response_text) > 300:
                print("...")
            return True
        else:
            print(f"错误: {data}")
            return False
    except requests.exceptions.Timeout:
        print("[错误] 请求超时")
        return False
    except Exception as e:
        print(f"[错误] {str(e)}")
        return False


def main():
    """主测试函数"""
    print("\n" + "=" * 60)
    print("AI健康助手功能测试")
    print("=" * 60)
    
    # 检查服务是否运行
    try:
        requests.get(f"{BASE_URL}/health", timeout=2)
    except:
        print("[错误] 后端服务未运行！")
        print("请先启动后端服务：")
        print("  cd backend")
        print("  python main.py")
        return
    
    results = []
    
    # 执行测试
    results.append(("健康检查", test_health_check()))
    results.append(("AI服务健康检查", test_ai_health()))
    results.append(("知识库统计", test_knowledge_base_stats()))
    results.append(("知识库搜索", test_knowledge_base_search()))
    results.append(("AI咨询（使用知识库）", test_ai_consult_with_kb()))
    results.append(("AI咨询（不使用知识库）", test_ai_consult_without_kb()))
    
    # 汇总结果
    print("\n" + "=" * 60)
    print("[测试结果汇总]")
    print("=" * 60)
    for name, result in results:
        status = "[通过]" if result else "[失败]"
        print(f"{status} {name}")
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    print(f"\n总计: {passed}/{total} 通过")


if __name__ == "__main__":
    main()


