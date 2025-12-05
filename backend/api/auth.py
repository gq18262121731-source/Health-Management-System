"""认证相关功能"""
from datetime import datetime, timedelta
from typing import Optional, Union, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
import uuid

from config.settings import settings
from database.database import get_db
from database.models import User, UserStatus

# 密码加密上下文 - 使用pbkdf2_sha256算法，更稳定且没有长度限制问题
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

# OAuth2密码承载令牌（统一使用 /api/v1/auth/login 路径）
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    print(f"[DEBUG] 验证密码: plain_password长度={len(plain_password)}, hashed_password长度={len(hashed_password)}")
    result = pwd_context.verify(plain_password, hashed_password)
    print(f"[DEBUG] 密码验证结果: {result}")
    return result


def get_password_hash(password: str) -> str:
    """获取密码哈希值"""
    return pwd_context.hash(password)


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """创建访问令牌"""
    print(f"[DEBUG] 创建访问令牌: data={data}, expires_delta={expires_delta}")
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    print(f"[DEBUG] 令牌创建成功，expire={expire}")
    return encoded_jwt


def decode_token(token: str) -> Optional[Dict[str, Any]]:
    """解码令牌"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None


async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """获取当前用户"""
    print(f"[DEBUG] 获取当前用户: token={token[:10]}...")
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = decode_token(token)
    if payload is None:
        raise credentials_exception
    
    user_id: str = payload.get("sub")
    if user_id is None:
        raise credentials_exception
    
    # 验证UUID格式
    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        print(f"[DEBUG] 无效的 UUID 格式: {user_id}")
        raise credentials_exception
    
    # 数据库存储的是带连字符的 UUID 字符串格式
    user_id_str = str(user_uuid)
    print(f"[DEBUG] 查询用户 ID: {user_id_str}")
    
    # 使用 text() 进行原始 SQL 查询获取完整用户数据
    from sqlalchemy import text
    from sqlalchemy.orm import Session
    
    result = db.execute(
        text("""SELECT id, username, phone_number, password, role, status, 
                created_at, updated_at, last_login_at 
                FROM users WHERE id = :user_id LIMIT 1"""),
        {"user_id": user_id_str}
    ).fetchone()
    
    if result is None:
        print(f"[DEBUG] 用户不存在: {user_id_str}")
        raise credentials_exception
    
    print(f"[DEBUG] 找到用户: {result[1]}")  # username
    
    # 手动构建 User 对象，避免 ORM UUID 类型问题
    user = User(
        id=uuid.UUID(result[0]),
        username=result[1],
        phone_number=result[2],
        password=result[3],
        role=result[4],
        status=result[5],
        created_at=result[6],
        updated_at=result[7],
        last_login_at=result[8]
    )
    # 标记为已持久化（避免 SQLAlchemy 尝试插入）
    from sqlalchemy import inspect
    db.add(user)
    db.expire(user)
    
    # 检查用户状态
    if user.status != UserStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户账号已被禁用或锁定"
        )
    
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """获取当前活跃用户"""
    if current_user.status != UserStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="用户账号未激活")
    return current_user


def check_user_role(required_role: str):
    """检查用户角色的依赖项"""
    async def role_checker(current_user: User = Depends(get_current_active_user)) -> User:
        if current_user.role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="权限不足，无法访问该资源"
            )
        return current_user
    return role_checker


async def get_elderly_user(current_user: User = Depends(get_current_active_user)) -> User:
    """获取老人用户"""
    if current_user.role != "elderly":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足，需要老人账号"
        )
    return current_user


async def get_children_user(current_user: User = Depends(get_current_active_user)) -> User:
    """获取子女用户"""
    if current_user.role != "children":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足，需要子女账号"
        )
    return current_user


async def get_community_user(current_user: User = Depends(get_current_active_user)) -> User:
    """获取社区用户"""
    if current_user.role != "community":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足，需要社区账号"
        )
    return current_user


def check_elderly_access(elderly_id: Union[str, uuid.UUID], current_user: User, db: Session) -> bool:
    """检查用户是否有权访问指定老人的信息
    
    规则：
    1. 老人本人可以访问自己的信息
    2. 子女用户需要通过children_elderly_relations表验证关系
    3. 社区用户可以访问所有老人的信息
    """
    from database.models import ElderlyProfile, ChildrenElderlyRelation, ChildrenProfile
    
    # 转换UUID格式
    if isinstance(elderly_id, str):
        try:
            elderly_id = uuid.UUID(elderly_id)
        except ValueError:
            return False
    
    # 社区用户有权限访问所有老人
    if current_user.role == "community":
        return True
    
    # 老人本人可以访问自己的信息
    if current_user.role == "elderly":
        elderly = db.query(ElderlyProfile).filter(
            ElderlyProfile.user_id == current_user.id
        ).first()
        return elderly is not None and elderly.id == elderly_id
    
    # 子女用户需要验证关系
    if current_user.role == "children":
        children_profile = db.query(ChildrenProfile).filter(
            ChildrenProfile.user_id == current_user.id
        ).first()
        
        if not children_profile:
            return False
        
        # 检查关系表
        relation = db.query(ChildrenElderlyRelation).filter(
            ChildrenElderlyRelation.children_id == children_profile.id,
            ChildrenElderlyRelation.elderly_id == elderly_id
        ).first()
        
        return relation is not None
    
    return False