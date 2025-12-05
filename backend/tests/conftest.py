"""测试配置文件"""
import pytest
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
import os

from database.database import Base
from database.models import User, Elderly, HealthRecord, Reminder, Alert, Community, Children, ChildrenElderly
from main import app
from dependencies.get_current_user import get_current_user
from utils.password_utils import PasswordUtils

# 创建测试数据库引擎
TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# 创建测试数据库会话
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db() -> Generator:
    """创建测试数据库会话"""
    # 创建所有表
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        # 添加测试数据
        add_test_data(db)
        yield db
    finally:
        # 关闭会话并删除所有表
        db.close()
        Base.metadata.drop_all(bind=engine)


def add_test_data(db):
    """添加测试数据"""
    # 创建测试管理员用户
    admin_user = User(
        username="admin_test",
        password=PasswordUtils.hash_password("Admin@123"),
        phone="13800138000",
        name="管理员",
        role="admin",
        is_active=True
    )
    db.add(admin_user)
    
    # 创建测试社区管理员
    community_admin = User(
        username="community_admin_test",
        password=PasswordUtils.hash_password("Admin@123"),
        phone="13800138001",
        name="社区管理员",
        role="community_admin",
        is_active=True
    )
    db.add(community_admin)
    
    # 创建测试老人
    elderly = Elderly(
        user_id=2,  # 关联社区管理员
        name="张三",
        gender="male",
        birth_date="1945-01-15",
        id_card="110101194501151234",
        phone="13800138002",
        address="北京市海淀区",
        health_status="良好",
        emergency_contact="李四",
        emergency_phone="13800138003"
    )
    db.add(elderly)
    
    # 创建测试社区
    community = Community(
        name="测试社区",
        address="北京市海淀区测试路1号",
        description="这是一个测试社区"
    )
    db.add(community)
    
    # 创建测试子女用户
    children_user = User(
        username="children_test",
        password=PasswordUtils.hash_password("Children@123"),
        phone="13800138004",
        name="子女用户",
        role="children",
        is_active=True
    )
    db.add(children_user)
    
    # 创建测试子女信息
    children = Children(
        user_id=3,
        relationship="子女"
    )
    db.add(children)
    
    db.commit()
    
    # 建立子女与老人的关系
    children_elderly = ChildrenElderly(
        children_id=children.id,
        elderly_id=elderly.id
    )
    db.add(children_elderly)
    
    # 为老人添加健康记录
    health_record = HealthRecord(
        elderly_id=elderly.id,
        blood_pressure_systolic=120,
        blood_pressure_diastolic=80,
        heart_rate=72,
        blood_sugar=5.6,
        body_temperature=36.5,
        oxygen=98,
        weight=65.5,
        steps=5000,
        record_date="2024-01-01"
    )
    db.add(health_record)
    
    # 添加健康提醒
    reminder = Reminder(
        elderly_id=elderly.id,
        title="吃药提醒",
        content="请按时服用降压药",
        reminder_type="medication",
        remind_time="08:00",
        start_date="2024-01-01",
        frequency="daily",
        status="pending"
    )
    db.add(reminder)
    
    db.commit()


@pytest.fixture(scope="function")
def client(db) -> Generator:
    """创建测试客户端"""
    # 重写依赖项，使用测试数据库
    def override_get_db():
        try:
            yield db
        finally:
            pass
    
    # 重写获取当前用户的依赖项，用于测试
    def override_get_current_user():
        # 返回测试管理员用户
        return db.query(User).filter(User.username == "admin_test").first()
    
    # 应用覆盖
    app.dependency_overrides[get_current_user] = override_get_current_user
    
    # 创建测试客户端
    with TestClient(app) as c:
        yield c
    
    # 恢复原始依赖项
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def admin_token(client: TestClient) -> str:
    """获取管理员令牌"""
    # 登录获取令牌
    response = client.post(
        "/api/user/login",
        json={
            "username": "admin_test",
            "password": "Admin@123"
        }
    )
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture(scope="function")
def community_admin_token(client: TestClient) -> str:
    """获取社区管理员令牌"""
    # 登录获取令牌
    response = client.post(
        "/api/user/login",
        json={
            "username": "community_admin_test",
            "password": "Admin@123"
        }
    )
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture(scope="function")
def children_token(client: TestClient) -> str:
    """获取子女令牌"""
    # 登录获取令牌
    response = client.post(
        "/api/user/login",
        json={
            "username": "children_test",
            "password": "Children@123"
        }
    )
    assert response.status_code == 200
    return response.json()["access_token"]