"""老人管理相关测试"""
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
import pytest


def test_create_elderly(client: TestClient, community_admin_token: str):
    """测试创建老人信息"""
    # 准备测试数据
    elderly_data = {
        "name": "李四",
        "gender": "female",
        "birth_date": "1948-05-20",
        "id_card": "110101194805202345",
        "phone": "13800138006",
        "address": "北京市朝阳区",
        "health_status": "一般",
        "emergency_contact": "王五",
        "emergency_phone": "13800138007"
    }
    
    # 发送请求
    response = client.post(
        "/api/elderly",
        json=elderly_data,
        headers={"Authorization": f"Bearer {community_admin_token}"}
    )
    
    # 验证响应
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "data" in data
    assert data["data"]["name"] == "李四"
    assert data["data"]["gender"] == "female"


def test_get_elderly_list(client: TestClient, community_admin_token: str):
    """测试获取老人列表"""
    # 发送请求
    response = client.get(
        "/api/elderly",
        headers={"Authorization": f"Bearer {community_admin_token}"}
    )
    
    # 验证响应
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "data" in data
    assert isinstance(data["data"]["items"], list)
    assert data["data"]["total"] >= 1


def test_get_elderly_detail(client: TestClient, community_admin_token: str, db: Session):
    """测试获取老人详情"""
    # 从测试数据中获取老人ID
    from database.models import Elderly
    elderly = db.query(Elderly).first()
    assert elderly is not None
    
    # 发送请求
    response = client.get(
        f"/api/elderly/{elderly.id}",
        headers={"Authorization": f"Bearer {community_admin_token}"}
    )
    
    # 验证响应
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "data" in data
    assert data["data"]["id"] == elderly.id
    assert data["data"]["name"] == elderly.name


def test_update_elderly(client: TestClient, community_admin_token: str, db: Session):
    """测试更新老人信息"""
    # 从测试数据中获取老人ID
    from database.models import Elderly
    elderly = db.query(Elderly).first()
    assert elderly is not None
    
    # 准备更新数据
    update_data = {
        "health_status": "良好",
        "address": "北京市海淀区新地址"
    }
    
    # 发送请求
    response = client.put(
        f"/api/elderly/{elderly.id}",
        json=update_data,
        headers={"Authorization": f"Bearer {community_admin_token}"}
    )
    
    # 验证响应
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "data" in data
    assert data["data"]["health_status"] == "良好"
    assert data["data"]["address"] == "北京市海淀区新地址"


def test_delete_elderly(client: TestClient, community_admin_token: str, db: Session):
    """测试删除老人信息"""
    # 先创建一个新的老人用于删除测试
    elderly_data = {
        "name": "王五",
        "gender": "male",
        "birth_date": "1950-03-10",
        "id_card": "110101195003103456",
        "phone": "13800138008",
        "address": "北京市西城区",
        "health_status": "良好",
        "emergency_contact": "赵六",
        "emergency_phone": "13800138009"
    }
    
    create_response = client.post(
        "/api/elderly",
        json=elderly_data,
        headers={"Authorization": f"Bearer {community_admin_token}"}
    )
    
    assert create_response.status_code == 200
    new_elderly = create_response.json()["data"]
    
    # 发送删除请求
    delete_response = client.delete(
        f"/api/elderly/{new_elderly['id']}",
        headers={"Authorization": f"Bearer {community_admin_token}"}
    )
    
    # 验证响应
    assert delete_response.status_code == 200
    data = delete_response.json()
    assert data["success"] is True
    assert "message" in data