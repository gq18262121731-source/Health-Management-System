"""数据库配置和连接管理"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
import logging

from config.settings import settings

logger = logging.getLogger(__name__)

# 创建数据库引擎
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # 连接池预检查
    pool_size=10,  # 连接池大小
    max_overflow=20,  # 最大溢出连接数
    pool_recycle=3600,  # 连接回收时间(秒)
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基类
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """获取数据库会话的依赖项"""
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"数据库会话错误: {str(e)}")
        raise
    finally:
        db.close()


def init_db() -> None:
    """初始化数据库，创建所有表"""
    try:
        # 导入所有模型，确保它们被Base.metadata发现
        from database.models import (
            User,
            ElderlyProfile,
            HealthRecord,
            SleepData,
            Alert,
            Reminder,
            HealthAssessment,
            ChildrenElderlyRelation,
            AIQuery,
            Community,
            CommunityReport,
            AlertResolution
        )
        
        # 创建所有表
        Base.metadata.create_all(bind=engine)
        logger.info("数据库表创建成功")
        
        # 检查是否需要初始化默认数据
        db = SessionLocal()
        try:
            # 检查是否存在默认社区用户
            from passlib.context import CryptContext
            
            pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
            
            # 创建默认社区管理员账号
            default_community = db.query(User).filter(
                User.username == "community_admin"
            ).first()
            
            if not default_community:
                community_user = User(
                    username="community_admin",
                    password=pwd_context.hash("password123"),
                    phone_number="13800138000",
                    role="community",
                    status="active"
                )
                db.add(community_user)
                db.commit()
                logger.info("默认社区管理员账号创建成功")
        except Exception as e:
            logger.error(f"初始化默认数据失败: {str(e)}")
            db.rollback()
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"数据库初始化失败: {str(e)}")
        raise


def get_engine():
    """获取数据库引擎"""
    return engine