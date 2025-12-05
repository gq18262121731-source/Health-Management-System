#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试登录功能的脚本"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_health():
    """测试健康检查"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✓ 后端服务运行正常")
            print(f"  响应: {response.json()}")
            return True
        else:
            print(f"✗ 后端服务响应异常: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ 无法连接到后端服务: {e}")
        print("  请确保后端服务已启动 (python main.py)")
        return False

def test_register():
    """测试注册功能"""
    print("\n=== 测试用户注册 ===")
    url = f"{BASE_URL}/api/auth/register"
    
    test_user = {
        "phone_number": "13800138001",
        "password": "123456",
        "role": "elderly"
    }
    
    try:
        response = requests.post(url, json=test_user, timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ 注册成功: {data.get('message')}")
            return True
        else:
            data = response.json()
            if "已被注册" in str(data.get('detail', {}).get('error_msg', '')):
                print("ℹ 用户已存在，跳过注册")
                return True
            else:
                print(f"✗ 注册失败: {response.status_code}")
                print(f"  响应: {json.dumps(data, ensure_ascii=False, indent=2)}")
                return False
    except Exception as e:
        print(f"✗ 注册请求失败: {e}")
        return False

def test_login_oauth2():
    """测试OAuth2格式登录"""
    print("\n=== 测试OAuth2格式登录 ===")
    url = f"{BASE_URL}/api/auth/login"
    
    # OAuth2格式（form-data）
    data = {
        "username": "13800138001",  # 使用手机号
        "password": "123456",
        "scope": "elderly"  # role参数
    }
    
    try:
        response = requests.post(
            url,
            data=data,  # form-data格式
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=5
        )
        
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✓ 登录成功!")
            print(f"  Token: {result.get('data', {}).get('access_token', '')[:50]}...")
            print(f"  用户信息: {json.dumps(result.get('data', {}).get('user_info', {}), ensure_ascii=False, indent=2)}")
            return result.get('data', {}).get('access_token')
        else:
            error_data = response.json()
            print(f"✗ 登录失败: {response.status_code}")
            print(f"  错误信息: {json.dumps(error_data, ensure_ascii=False, indent=2)}")
            return None
    except Exception as e:
        print(f"✗ 登录请求失败: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_login_json():
    """测试JSON格式登录（如果支持）"""
    print("\n=== 测试JSON格式登录 ===")
    url = f"{BASE_URL}/api/auth/login-json"
    
    data = {
        "phone_number": "13800138001",
        "password": "123456",
        "role": "elderly"
    }
    
    try:
        response = requests.post(
            url,
            json=data,
            headers={"Content-Type": "application/json"},
            timeout=5
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✓ JSON格式登录成功!")
            print(f"  Token: {result.get('data', {}).get('access_token', '')[:50]}...")
            return result.get('data', {}).get('access_token')
        else:
            if response.status_code == 404:
                print("ℹ JSON格式登录接口不存在，使用OAuth2格式")
            else:
                error_data = response.json()
                print(f"✗ JSON格式登录失败: {response.status_code}")
                print(f"  错误信息: {json.dumps(error_data, ensure_ascii=False, indent=2)}")
            return None
    except requests.exceptions.RequestException as e:
        if "404" in str(e):
            print("ℹ JSON格式登录接口不存在，使用OAuth2格式")
        else:
            print(f"✗ JSON格式登录请求失败: {e}")
        return None

def test_protected_endpoint(token):
    """测试受保护的端点"""
    if not token:
        print("\n⚠ 没有token，跳过受保护端点测试")
        return
    
    print("\n=== 测试受保护端点 ===")
    url = f"{BASE_URL}/api/auth/me"
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✓ 获取用户信息成功")
            print(f"  用户信息: {json.dumps(data, ensure_ascii=False, indent=2)}")
        else:
            print(f"✗ 获取用户信息失败: {response.status_code}")
            print(f"  响应: {response.text}")
    except Exception as e:
        print(f"✗ 请求失败: {e}")

if __name__ == "__main__":
    print("=" * 50)
    print("登录功能测试")
    print("=" * 50)
    
    # 1. 测试健康检查
    if not test_health():
        print("\n❌ 后端服务未运行，请先启动后端服务:")
        print("   cd backend")
        print("   python main.py")
        exit(1)
    
    # 2. 测试注册
    test_register()
    
    # 3. 测试OAuth2格式登录
    token = test_login_oauth2()
    
    # 如果OAuth2格式失败，尝试JSON格式
    if not token:
        token = test_login_json()
    
    # 4. 测试受保护端点
    if token:
        test_protected_endpoint(token)
        print("\n✅ 登录测试完成!")
        print("\n📝 测试账号信息:")
        print("   手机号: 13800138001")
        print("   密码: 123456")
        print("   角色: elderly")
    else:
        print("\n❌ 登录测试失败，请检查:")
        print("   1. 后端服务是否正常运行")
        print("   2. 数据库中是否存在测试用户")
        print("   3. 密码是否正确")
        print("\n💡 提示: 可以运行 create_test_users.py 创建测试用户")

