"""认证相关路由"""
from datetime import timedelta
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import uuid

from config.settings import settings
from database.database import get_db
from database.models import User, UserStatus, ElderlyProfile, ChildrenProfile, CommunityProfile, Gender
from api.auth import (
    verify_password,
    get_password_hash,
    create_access_token,
    get_current_active_user
)
from schemas.models import (
    UserCreate,
    UserLogin,
    UserLoginResponse,
    UserResponse,
    BaseResponse,
    ElderlyProfileCreate,
    ChildrenProfileCreate,
)

router = APIRouter(tags=["认证"])  # prefix 在 main.py 中统一设置为 /api/v1/auth


@router.post("/register", response_model=BaseResponse)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """用户注册"""
    # 检查手机号是否已存在
    existing_user = db.query(User).filter(
        User.phone_number == user_data.phone_number
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error_code": 4001,
                    "error_msg": "该手机号已被注册",
                    "detail": {"phone_number": user_data.phone_number}}
        )
    
    # 创建用户
    hashed_password = get_password_hash(user_data.password)
    # 使用手机号作为username（如果未提供username）
    username = user_data.phone_number  # 默认使用手机号作为用户名
    
    new_user = User(
        id=uuid.uuid4(),
        username=username,
        phone_number=user_data.phone_number,
        password=hashed_password,
        role=user_data.role,
        status=UserStatus.ACTIVE
    )
    
    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        # 根据角色创建对应的档案
        from datetime import datetime, timezone
        from dateutil.relativedelta import relativedelta
        
        if user_data.role == "elderly":
            # 老人档案 - 使用默认值，后续可补全
            birth_date = datetime(1950, 1, 1, tzinfo=timezone.utc)
            age = relativedelta(datetime.now(tz=timezone.utc), birth_date).years
            
            elderly_profile = ElderlyProfile(
                id=uuid.uuid4(),
                user_id=new_user.id,
                name="待完善",  # 必填字段，后续补全
                gender=Gender.MALE,  # 使用枚举类型
                birth_date=birth_date,  # 必填字段，默认值
                age=age,  # 必填字段，根据出生日期计算
                address="待完善",  # 必填字段，后续补全
                phone_number=new_user.phone_number
            )
            db.add(elderly_profile)
        
        elif user_data.role == "children":
            # 子女档案
            children_profile = ChildrenProfile(
                id=uuid.uuid4(),
                user_id=new_user.id,
                name="待完善",  # 必填字段，后续补全
                phone_number=new_user.phone_number
            )
            db.add(children_profile)
        
        elif user_data.role == "community":
            # 社区用户档案
            community_profile = CommunityProfile(
                id=uuid.uuid4(),
                user_id=new_user.id,
                community_name="待完善",  # 必填字段
                address="待完善",  # 必填字段
                contact_person="待完善",  # 必填字段
                contact_phone=new_user.phone_number  # 必填字段
            )
            db.add(community_profile)
        
        db.commit()
        
        return {
            "success": True,
            "message": "注册成功",
            "data": {
                "user_id": new_user.id,
                "phone_number": new_user.phone_number,
                "role": new_user.role
            }
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error_code": 5001,
                    "error_msg": "注册失败，请稍后重试",
                    "detail": str(e)}
        )


@router.post("/login", response_model=UserLoginResponse)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """用户登录
    
    使用OAuth2PasswordRequestForm，支持通过username或phone_number登录，并获取role参数
    """
    print(f"[DEBUG] 登录请求: username={form_data.username}, password长度={len(form_data.password)}, scope={form_data.scopes}")
    
    # 获取额外的role参数（从form_data中获取）
    role = form_data.scopes[0] if form_data.scopes else None
    
    # 查找用户 - 支持通过username或phone_number登录
    print(f"[DEBUG] 查找用户: username={form_data.username}")
    
    # 先尝试通过手机号查找
    user = db.query(User).filter(User.phone_number == form_data.username).first()
    
    # 如果通过手机号没找到，再尝试通过用户名查找
    if not user:
        print(f"[DEBUG] 通过手机号未找到用户，尝试通过用户名查找")
        user = db.query(User).filter(User.username == form_data.username).first()
    
    if user:
        print(f"[DEBUG] 找到用户: id={user.id}, username={user.username}, phone={user.phone_number}, role={user.role}")
        # 密码验证
        print(f"[DEBUG] 准备验证密码: 明文密码长度={len(form_data.password)}, 哈希密码长度={len(user.password)}")
        password_valid = verify_password(form_data.password, user.password)
        print(f"[DEBUG] 密码验证结果: {password_valid}")
        
        if not password_valid:
            print(f"[DEBUG] 密码验证失败")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"error_code": 4011,
                        "error_msg": "手机号或密码错误",
                        "detail": None},
                headers={"WWW-Authenticate": "Bearer"},
            )
    else:
        print(f"[DEBUG] 未找到用户")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error_code": 4011,
                    "error_msg": "手机号或密码错误",
                    "detail": None},
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 如果提供了role参数，验证用户角色是否匹配
    if role and user.role != role:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error_code": 4012,
                    "error_msg": "用户角色不匹配",
                    "detail": f"期望角色: {role}, 实际角色: {user.role}"},
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 检查用户状态
    if user.status != UserStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"error_code": 4031,
                    "error_msg": "账号已被禁用或锁定",
                    "detail": None}
        )
    
    # 创建访问令牌
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    # 确保 role 是字符串值，而不是枚举对象
    role_value = user.role.value if hasattr(user.role, 'value') else str(user.role)
    access_token = create_access_token(
        data={"sub": str(user.id), "role": role_value},
        expires_delta=access_token_expires
    )
    
    # 获取用户详细信息
    user_info = {
        "user_id": str(user.id),
        "phone_number": user.phone_number,
        "role": role_value,
        "status": user.status.value if hasattr(user.status, 'value') else str(user.status)
    }
    
    # 根据角色获取额外信息
    if user.role == "elderly":
        elderly_profile = db.query(ElderlyProfile).filter(
            ElderlyProfile.user_id == user.id
        ).first()
        if elderly_profile:
            user_info["profile_id"] = str(elderly_profile.id)
            user_info["name"] = elderly_profile.name or ""
    
    elif user.role == "children":
        children_profile = db.query(ChildrenProfile).filter(
            ChildrenProfile.user_id == user.id
        ).first()
        if children_profile:
            user_info["profile_id"] = str(children_profile.id)
            user_info["name"] = children_profile.name or ""
    
    elif user.role == "community":
        community_profile = db.query(CommunityProfile).filter(
            CommunityProfile.user_id == user.id
        ).first()
        if community_profile:
            user_info["profile_id"] = str(community_profile.id)
            user_info["community_name"] = community_profile.community_name or ""
    
    # 返回符合前端期望格式的响应
    return {
        "status": "success",
        "data": {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "user_id": str(user.id),
            "username": user.username or user.phone_number,
            "role": role_value  # 使用字符串值
        },
        "message": "登录成功"
    }


@router.post("/login/json", response_model=UserLoginResponse)
def login_json(user_data: UserLogin, db: Session = Depends(get_db)):
    """用户登录(JSON格式)"""
    print(f"[DEBUG-JSON] 登录请求: phone_number={user_data.phone_number}, password长度={len(user_data.password)}")
    
    # 查找用户
    print(f"[DEBUG-JSON] 通过手机号查找用户: {user_data.phone_number}")
    user = db.query(User).filter(
        User.phone_number == user_data.phone_number
    ).first()
    
    if user:
        print(f"[DEBUG-JSON] 找到用户: id={user.id}, username={user.username}, phone={user.phone_number}, role={user.role}")
        # 密码验证
        print(f"[DEBUG-JSON] 准备验证密码: 明文密码长度={len(user_data.password)}, 哈希密码长度={len(user.password)}")
        password_valid = verify_password(user_data.password, user.password)
        print(f"[DEBUG-JSON] 密码验证结果: {password_valid}")
        
        if not password_valid:
            print(f"[DEBUG-JSON] 密码验证失败")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"error_code": 4011,
                        "error_msg": "手机号或密码错误",
                        "detail": None},
                headers={"WWW-Authenticate": "Bearer"},
            )
    else:
        print(f"[DEBUG-JSON] 未找到用户")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error_code": 4011,
                    "error_msg": "手机号或密码错误",
                    "detail": None},
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 检查用户状态
    if user.status != UserStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"error_code": 4031,
                    "error_msg": "账号已被禁用或锁定",
                    "detail": None}
        )
    
    # 创建访问令牌
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    # 确保 role 是字符串值，而不是枚举对象
    role_value = user.role.value if hasattr(user.role, 'value') else str(user.role)
    access_token = create_access_token(
        data={"sub": str(user.id), "role": role_value},
        expires_delta=access_token_expires
    )
    
    # 获取用户详细信息
    user_info = {
        "user_id": str(user.id),
        "phone_number": user.phone_number,
        "role": role_value,
        "status": user.status.value if hasattr(user.status, 'value') else str(user.status)
    }
    
    # 根据角色获取额外信息
    if user.role == "elderly":
        elderly_profile = db.query(ElderlyProfile).filter(
            ElderlyProfile.user_id == user.id
        ).first()
        if elderly_profile:
            user_info["profile_id"] = str(elderly_profile.id)
            user_info["name"] = elderly_profile.name or ""
    
    elif user.role == "children":
        children_profile = db.query(ChildrenProfile).filter(
            ChildrenProfile.user_id == user.id
        ).first()
        if children_profile:
            user_info["profile_id"] = str(children_profile.id)
            user_info["name"] = children_profile.name or ""
    
    elif user.role == "community":
        community_profile = db.query(CommunityProfile).filter(
            CommunityProfile.user_id == user.id
        ).first()
        if community_profile:
            user_info["profile_id"] = str(community_profile.id)
            user_info["community_name"] = community_profile.community_name or ""
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_info": user_info
    }


@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """获取当前用户信息"""
    return current_user


@router.post("/logout", response_model=BaseResponse)
def logout(current_user: User = Depends(get_current_active_user)):
    """用户登出
    
    注意：由于使用JWT令牌，登出主要在前端实现
    这里可以添加令牌黑名单等逻辑（可选）
    """
    # 这里可以添加令牌黑名单逻辑
    return {
        "success": True,
        "message": "登出成功",
        "data": None
    }