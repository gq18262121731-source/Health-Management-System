"""提醒管理相关测试"""
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
import pytest


def test_create_reminder(client: TestClient, community_admin_token: str, db: Session):
    """测试创建提醒"""
    # 从测试数据中获取老人ID
    from database.models import Elderly
    elderly = db.query(Elderly).first()
    assert elderly is not None
    
    # 准备测试数据
    reminder_data = {
        "elderly_id": elderly.id,
        "title": "运动提醒",
        "content": "请进行30分钟的散步",
        "reminder_type": "exercise",
        "remind_time": "16:00",
        "start_date": "2024-01-01",
        "frequency": "daily",
        "status": "pending"
    }
    
    # 发送请求
    response = client.post(
        "/api/reminder",
        json=reminder_data,
        headers={"Authorization": f"Bearer {community_admin_token}"}
    )
    
    # 验证响应
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "data" in data
    assert data["data"]["title"] == "运动提醒"
    assert data["data"]["reminder_type"] == "exercise"


def test_get_elderly_reminders(client: TestClient, community_admin_token: str, db: Session):
    """测试获取老人的提醒列表"""
    # 从测试数据中获取老人ID
    from database.models import Elderly
    elderly = db.query(Elderly).first()
    assert elderly is not None
    
    # 发送请求
    response = client.get(
        f"/api/reminder/elderly/{elderly.id}",
        headers={"Authorization": f"Bearer {community_admin_token}"}
    )
    
    # 验证响应
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "data" in data
    assert isinstance(data["data"], list)


def test_get_today_reminders(client: TestClient, community_admin_token: str):
    """测试获取今日提醒"""
    # 发送请求
    response = client.get(
        "/api/reminder/today",
        headers={"Authorization": f"Bearer {community_admin_token}"}
    )
    
    # 验证响应
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "data" in data
    assert isinstance(data["data"], list)


def test_get_reminder_detail(client: TestClient, community_admin_token: str, db: Session):
    """测试获取提醒详情"""
    # 从测试数据中获取提醒ID
    from database.models import Reminder
    reminder = db.query(Reminder).first()
    assert reminder is not None
    
    # 发送请求
    response = client.get(
        f"/api/reminder/{reminder.id}",
        headers={"Authorization": f"Bearer {community_admin_token}"}
    )
    
    # 验证响应
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "data" in data
    assert data["data"]["id"] == reminder.id


def test_update_reminder(client: TestClient, community_admin_token: str, db: Session):
    """测试更新提醒"""
    # 从测试数据中获取提醒ID
    from database.models import Reminder
    reminder = db.query(Reminder).first()
    assert reminder is not None
    
    # 准备更新数据
    update_data = {
        "title": "更新后的吃药提醒",
        "content": "请按时服用降压药和降糖药",
        "remind_time": "08:30"
    }
    
    # 发送请求
    response = client.put(
        f"/api/reminder/{reminder.id}",
        json=update_data,
        headers={"Authorization": f"Bearer {community_admin_token}"}
    )
    
    # 验证响应
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "data" in data
    assert data["data"]["title"] == "更新后的吃药提醒"
    assert data["data"]["content"] == "请按时服用降压药和降糖药"


def test_update_reminder_status(client: TestClient, community_admin_token: str, db: Session):
    """测试更新提醒状态"""
    # 从测试数据中获取提醒ID
    from database.models import Reminder
    reminder = db.query(Reminder).first()
    assert reminder is not None
    
    # 准备状态更新数据
    status_data = {
        "status": "completed"
    }
    
    # 发送请求
    response = client.patch(
        f"/api/reminder/{reminder.id}/status",
        json=status_data,
        headers={"Authorization": f"Bearer {community_admin_token}"}
    )
    
    # 验证响应
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "data" in data
    assert data["data"]["status"] == "completed"


def test_delete_reminder(client: TestClient, community_admin_token: str, db: Session):
    """测试删除提醒"""
    # 先创建一个新的提醒用于删除测试
    from database.models import Elderly
    elderly = db.query(Elderly).first()
    assert elderly is not None
    
    create_data = {
        "elderly_id": elderly.id,
        "title": "临时提醒",
        "content": "这是一个临时提醒",
        "reminder_type": "other",
        "remind_time": "12:00",
        "start_date": "2024-01-01",
        "frequency": "once",
        "status": "pending"
    }
    
    create_response = client.post(
        "/api/reminder",
        json=create_data,
        headers={"Authorization": f"Bearer {community_admin_token}"}
    )
    
    assert create_response.status_code == 200
    new_reminder = create_response.json()["data"]
    
    # 发送删除请求
    delete_response = client.delete(
        f"/api/reminder/{new_reminder['id']}",
        headers={"Authorization": f"Bearer {community_admin_token}"}
    )
    
    # 验证响应
    assert delete_response.status_code == 200
    data = delete_response.json()
    assert data["success"] is True
    assert "message" in data