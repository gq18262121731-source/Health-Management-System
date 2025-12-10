"""应用配置"""
import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator


class Settings(BaseSettings):
    """应用配置类"""
    # 应用基本信息
    APP_NAME: str = "智慧健康管理系统"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = Field(default="development")
    DEBUG: bool = Field(default=False)
    
    # 服务器配置
    HOST: str = Field(default="0.0.0.0")
    PORT: int = Field(default=8000)
    
    # 数据库配置
    DATABASE_URL: str = Field(..., description="数据库连接URL")
    
    # Redis配置
    REDIS_URL: str = Field(default="redis://localhost:6379/0")
    
    # 认证配置
    SECRET_KEY: str = Field(..., description="JWT密钥")
    ALGORITHM: str = Field(default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=60)
    
    # CORS配置
    BACKEND_CORS_ORIGINS: List[str] = Field(default=["*"])
    
    # 文件上传配置
    MAX_UPLOAD_SIZE: int = Field(default=10 * 1024 * 1024)  # 10MB
    ALLOWED_IMAGE_EXTENSIONS: List[str] = Field(
        default=[".jpg", ".jpeg", ".png", ".gif"]
    )
    UPLOAD_DIR: str = Field(default="./uploads")
    
    # AI服务配置
    AI_PROVIDER: str = Field(default="deepseek", description="AI服务提供商: deepseek, zhipu, qwen")
    
    # DeepSeek配置（推荐）
    DEEPSEEK_API_KEY: Optional[str] = Field(default=None, description="DeepSeek API密钥")
    DEEPSEEK_API_BASE: str = Field(default="https://api.deepseek.com/v1", description="DeepSeek API地址")
    
    # 智谱GLM配置
    ZHIPU_API_KEY: Optional[str] = Field(default=None, description="智谱GLM API密钥")
    ZHIPU_API_BASE: str = Field(default="https://open.bigmodel.cn/api/paas/v4", description="智谱GLM API地址")
    
    # 通义千问配置
    QWEN_API_KEY: Optional[str] = Field(default=None, description="通义千问API密钥")
    QWEN_API_BASE: str = Field(default="https://dashscope.aliyuncs.com/compatible-mode/v1", description="通义千问API地址")
    
    # 兼容旧配置（OpenAI）
    OPENAI_API_KEY: Optional[str] = Field(default=None)
    OPENAI_API_BASE: Optional[str] = Field(default="https://api.openai.com/v1")
    
    # 硅基流动配置
    SILICONFLOW_API_KEY: Optional[str] = Field(default=None, description="硅基流动API密钥")
    SILICONFLOW_BASE_URL: str = Field(default="https://api.siliconflow.cn/v1", description="硅基流动API地址")
    
    # 讯飞星火配置
    SPARK_APP_ID: Optional[str] = Field(default=None, description="讯飞星火APPID")
    SPARK_API_KEY: Optional[str] = Field(default=None, description="讯飞星火API Key")
    SPARK_API_SECRET: Optional[str] = Field(default=None, description="讯飞星火API Secret")
    SPARK_API_PASSWORD: Optional[str] = Field(default=None, description="讯飞星火API Password")
    
    # 健康阈值配置
    HEALTH_THRESHOLDS: dict = Field(default={
        "heart_rate": {"min": 60, "max": 100},
        "blood_pressure": {
            "systolic": {"min": 90, "max": 140},
            "diastolic": {"min": 60, "max": 90}
        },
        "blood_sugar": {"min": 3.9, "max": 6.1},
        "temperature": {"min": 36.0, "max": 37.3}
    })
    
    @field_validator('APP_ENV')
    def validate_app_env(cls, v: str) -> str:
        """验证应用环境"""
        allowed_envs = ["development", "testing", "production"]
        if v not in allowed_envs:
            raise ValueError(f"APP_ENV must be one of {allowed_envs}")
        return v
    
    @field_validator('BACKEND_CORS_ORIGINS', mode='before')
    def assemble_cors_origins(cls, v):
        """组装CORS源列表"""
        if isinstance(v, str) and not v.startswith('['):
            return [i.strip() for i in v.split(',')]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    class Config:
        env_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
        env_file_encoding = 'utf-8'
        case_sensitive = True


# 创建全局配置实例
settings = Settings()