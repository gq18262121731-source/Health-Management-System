"""密码工具类"""
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt

from config.settings import settings

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class PasswordUtils:
    """密码工具类"""
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """验证密码"""
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        """获取密码哈希值"""
        return pwd_context.hash(password)
    
    @staticmethod
    def validate_password_strength(password: str) -> tuple[bool, str]:
        """验证密码强度
        
        Args:
            password: 要验证的密码
            
        Returns:
            tuple: (是否通过验证, 错误信息)
        """
        # 检查密码长度
        if len(password) < 8:
            return False, "密码长度必须至少为8位"
        
        # 检查是否包含数字
        if not any(char.isdigit() for char in password):
            return False, "密码必须包含至少一个数字"
        
        # 检查是否包含字母
        if not any(char.isalpha() for char in password):
            return False, "密码必须包含至少一个字母"
        
        # 可以根据需求添加更多验证规则
        # 例如检查是否包含特殊字符
        # if not any(not char.isalnum() for char in password):
        #     return False, "密码必须包含至少一个特殊字符"
        
        return True, ""


class JWTUtils:
    """JWT工具类"""
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
        """创建访问令牌
        
        Args:
            data: 要编码的数据
            expires_delta: 过期时间增量
            
        Returns:
            str: JWT令牌
        """
        to_encode = data.copy()
        
        # 设置过期时间
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        
        return encoded_jwt
    
    @staticmethod
    def create_refresh_token(data: dict, expires_delta: timedelta = None) -> str:
        """创建刷新令牌
        
        Args:
            data: 要编码的数据
            expires_delta: 过期时间增量
            
        Returns:
            str: JWT刷新令牌
        """
        to_encode = data.copy()
        
        # 设置过期时间
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        
        return encoded_jwt
    
    @staticmethod
    def decode_token(token: str) -> dict:
        """解码JWT令牌
        
        Args:
            token: JWT令牌
            
        Returns:
            dict: 解码后的数据
        
        Raises:
            jwt.JWTError: 解码失败时抛出
        """
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    
    @staticmethod
    def validate_token(token: str) -> tuple[bool, dict]:
        """验证JWT令牌
        
        Args:
            token: JWT令牌
            
        Returns:
            tuple: (是否有效, 解码后的数据或错误信息)
        """
        try:
            payload = JWTUtils.decode_token(token)
            return True, payload
        except jwt.ExpiredSignatureError:
            return False, {"error": "令牌已过期"}
        except jwt.JWTError:
            return False, {"error": "无效的令牌"}


class TokenManager:
    """令牌管理器"""
    
    @staticmethod
    def generate_tokens(user_id: str, role: str, username: str) -> dict:
        """生成访问令牌和刷新令牌
        
        Args:
            user_id: 用户ID
            role: 用户角色
            username: 用户名
            
        Returns:
            dict: 包含访问令牌和刷新令牌的字典
        """
        # 创建访问令牌
        access_token_expires = timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = JWTUtils.create_access_token(
            data={"sub": user_id, "role": role, "username": username}, 
            expires_delta=access_token_expires
        )
        
        # 创建刷新令牌
        refresh_token_expires = timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
        refresh_token = JWTUtils.create_refresh_token(
            data={"sub": user_id, "role": role, "username": username},
            expires_delta=refresh_token_expires
        )
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
    
    @staticmethod
    def refresh_access_token(refresh_token: str) -> dict:
        """使用刷新令牌获取新的访问令牌
        
        Args:
            refresh_token: 刷新令牌
            
        Returns:
            dict: 新的访问令牌和可能的新刷新令牌
            
        Raises:
            jwt.JWTError: 刷新令牌无效时抛出
        """
        # 验证刷新令牌
        is_valid, payload = JWTUtils.validate_token(refresh_token)
        if not is_valid:
            raise jwt.JWTError("无效的刷新令牌")
        
        # 获取用户信息
        user_id = payload.get("sub")
        role = payload.get("role")
        username = payload.get("username")
        
        if not user_id:
            raise jwt.JWTError("无效的刷新令牌")
        
        # 创建新的访问令牌
        access_token_expires = timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = JWTUtils.create_access_token(
            data={"sub": user_id, "role": role, "username": username},
            expires_delta=access_token_expires
        )
        
        # 可以选择是否创建新的刷新令牌
        # 这里返回相同的刷新令牌
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }