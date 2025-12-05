"""用户认证相关测试"""
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
import pytest


def test_user_registration(client: TestClient, db: Session):
    """测试用户注册"""
    # 准备测试数据
    user_data = {
        "username": "testuser",
        "password": "Test@123456",
        "phone": "13800138005",
        "name": "测试用户",
        "role": "children"
    }
    
    # 发送注册请求
    response = client.post("/api/user/register", json=user_data)
    
    # 验证响应
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "data" in data
    assert data["data"]["username"] == "testuser"
    assert data["data"]["phone"] == "13800138005"
    assert data["data"]["name"] == "测试用户"
    assert data["data"]["role"] == "children"


def test_user_login(client: TestClient):
    """测试用户登录"""
    # 发送登录请求
    response = client.post(
        "/api/user/login",
        json={
            "username": "admin_test",
            "password": "Admin@123"
        }
    )
    
    # 验证响应
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "data" in data
    assert "access_token" in data["data"]
    assert "token_type" in data["data"]
    assert data["data"]["token_type"] == "bearer"
    assert "user_info" in data["data"]
    assert data["data"]["user_info"]["username"] == "admin_test"


def test_user_login_invalid_credentials(client: TestClient):
    """测试无效凭据登录"""
    # 发送错误的登录请求
    response = client.post(
        "/api/user/login",
        json={
            "username": "admin_test",
            "password": "wrong_password"
        }
    )
    
    # 验证响应
    assert response.status_code == 401
    data = response.json()
    assert data["success"] is False
    assert "error" in data


def test_get_current_user(client: TestClient, admin_token: str):
    """测试获取当前用户信息"""
    # 发送请求
    response = client.get(
        "/api/user/me",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    # 验证响应
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "data" in data
    assert data["data"]["username"] == "admin_test"
    assert data["data"]["role"] == "admin"


def test_refresh_token(client: TestClient, admin_token: str):
    """测试刷新令牌"""
    # 发送请求
    response = client.post(
        "/api/user/refresh",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    # 验证响应
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "data" in data
    assert "access_token" in data["data"]
    assert "token_type" in data["data"]


def test_change_password(client: TestClient, admin_token: str):
    """测试修改密码"""
    # 准备测试数据
    password_data = {
        "current_password": "Admin@123",
        "new_password": "New@123456"
    }
    
    # 发送请求
    response = client.post(
        "/api/user/change-password",
        json=password_data,
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    # 验证响应
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "message" in data
    
    # 验证新密码可以登录
    login_response = client.post(
        "/api/user/login",
        json={
            "username": "admin_test",
            "password": "New@123456"
        }
    )
    assert login_response.status_code == 200


def test_logout(client: TestClient, admin_token: str):
    """测试登出"""
    # 发送请求
    response = client.post(
        "/api/user/logout",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    # 验证响应
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "message" in data