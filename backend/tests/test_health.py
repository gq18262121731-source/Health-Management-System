"""健康记录相关测试"""
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
import pytest


def test_add_health_record(client: TestClient, community_admin_token: str, db: Session):
    """测试添加健康记录"""
    # 从测试数据中获取老人ID
    from database.models import Elderly
    elderly = db.query(Elderly).first()
    assert elderly is not None
    
    # 准备测试数据
    health_data = {
        "elderly_id": elderly.id,
        "blood_pressure_systolic": 125,
        "blood_pressure_diastolic": 82,
        "heart_rate": 75,
        "blood_sugar": 5.8,
        "body_temperature": 36.6,
        "oxygen": 99,
        "weight": 66.0,
        "steps": 6000,
        "record_date": "2024-01-02"
    }
    
    # 发送请求
    response = client.post(
        "/api/health/records",
        json=health_data,
        headers={"Authorization": f"Bearer {community_admin_token}"}
    )
    
    # 验证响应
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "data" in data
    assert data["data"]["elderly_id"] == elderly.id
    assert data["data"]["blood_pressure_systolic"] == 125


def test_get_health_records(client: TestClient, community_admin_token: str, db: Session):
    """测试获取健康记录列表"""
    # 从测试数据中获取老人ID
    from database.models import Elderly
    elderly = db.query(Elderly).first()
    assert elderly is not None
    
    # 发送请求
    response = client.get(
        f"/api/health/records/{elderly.id}?page=1&page_size=10",
        headers={"Authorization": f"Bearer {community_admin_token}"}
    )
    
    # 验证响应
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "data" in data
    assert isinstance(data["data"]["items"], list)


def test_get_latest_health_record(client: TestClient, community_admin_token: str, db: Session):
    """测试获取最新健康记录"""
    # 从测试数据中获取老人ID
    from database.models import Elderly
    elderly = db.query(Elderly).first()
    assert elderly is not None
    
    # 发送请求
    response = client.get(
        f"/api/health/latest/{elderly.id}",
        headers={"Authorization": f"Bearer {community_admin_token}"}
    )
    
    # 验证响应
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "data" in data


def test_get_daily_summary(client: TestClient, community_admin_token: str, db: Session):
    """测试获取每日健康摘要"""
    # 从测试数据中获取老人ID
    from database.models import Elderly
    elderly = db.query(Elderly).first()
    assert elderly is not None
    
    # 发送请求
    response = client.get(
        f"/api/health/daily-summary/{elderly.id}/2024-01-01",
        headers={"Authorization": f"Bearer {community_admin_token}"}
    )
    
    # 验证响应
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "data" in data


def test_get_weekly_trends(client: TestClient, community_admin_token: str, db: Session):
    """测试获取周健康趋势"""
    # 从测试数据中获取老人ID
    from database.models import Elderly
    elderly = db.query(Elderly).first()
    assert elderly is not None
    
    # 发送请求
    response = client.get(
        f"/api/health/weekly-trends/{elderly.id}/2024-W01",
        headers={"Authorization": f"Bearer {community_admin_token}"}
    )
    
    # 验证响应
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "data" in data


def test_get_health_alerts(client: TestClient, community_admin_token: str, db: Session):
    """测试获取健康预警"""
    # 从测试数据中获取老人ID
    from database.models import Elderly
    elderly = db.query(Elderly).first()
    assert elderly is not None
    
    # 添加一个异常的健康记录以触发预警
    abnormal_data = {
        "elderly_id": elderly.id,
        "blood_pressure_systolic": 160,
        "blood_pressure_diastolic": 100,
        "heart_rate": 100,
        "blood_sugar": 10.0,
        "body_temperature": 37.8,
        "oxygen": 92,
        "weight": 65.5,
        "steps": 5000,
        "record_date": "2024-01-03"
    }
    
    client.post(
        "/api/health/records",
        json=abnormal_data,
        headers={"Authorization": f"Bearer {community_admin_token}"}
    )
    
    # 发送请求获取预警
    response = client.get(
        f"/api/health/alerts/{elderly.id}",
        headers={"Authorization": f"Bearer {community_admin_token}"}
    )
    
    # 验证响应
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "data" in data