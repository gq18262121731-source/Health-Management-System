"""路由模块初始化文件 - 整合所有API路由"""
from fastapi import APIRouter

# 导入各个模块的路由
from .user import router as user_router
from .elderly import router as elderly_router
from .health import router as health_router
from .reminder import router as reminder_router
from .community import router as community_router
from .children import router as children_router

# 创建主路由
api_router = APIRouter()

# 包含各个子路由
api_router.include_router(user_router)
api_router.include_router(elderly_router)
api_router.include_router(health_router)
api_router.include_router(reminder_router)
api_router.include_router(community_router)
api_router.include_router(children_router)

__all__ = ["api_router"]