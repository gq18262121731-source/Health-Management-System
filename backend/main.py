"""智慧健康管理系统后端服务主入口"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from logging.config import dictConfig

# 导入配置
from config.settings import settings
from config.logging import LOGGING_CONFIG

# 导入路由
from api.routes import auth, elderly, children, community, ai, knowledge_base, voice, realtime_voice, streaming_voice, health_data, voice_agent

# 初始化日志
logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    logger.info("正在启动智慧健康管理系统后端服务...")
    logger.info(f"系统版本: {settings.APP_VERSION}")
    
    # 数据库初始化
    try:
        from database.database import engine, Base
        Base.metadata.create_all(bind=engine)
        logger.info("数据库表创建成功")
    except Exception as e:
        logger.error(f"数据库初始化失败: {str(e)}")
        raise
    
    yield
    
    # 关闭时执行
    logger.info("正在关闭智慧健康管理系统后端服务...")


# 创建FastAPI应用实例
app = FastAPI(
    title="智慧健康管理系统 API",
    description="为老人、子女和社区提供健康监测和管理服务的后端API",
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs",  # Swagger UI
    redoc_url="/redoc",  # ReDoc
    openapi_url="/openapi.json"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 临时设置为通配符，确保CORS问题解决
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由 - 在此集中管理版本前缀 /api/v1
app.include_router(auth.router, prefix="/api/v1/auth", tags=["认证"])
app.include_router(elderly.router, prefix="/api/v1/elderly", tags=["老人相关"])
app.include_router(children.router, prefix="/api/v1/children", tags=["子女相关"])
app.include_router(community.router, prefix="/api/v1/communities", tags=["社区相关"])
# AI 和知识库相关路由
app.include_router(ai.router, prefix="/api/v1/ai", tags=["AI健康助手"])
app.include_router(knowledge_base.router, prefix="/api/v1/knowledge-base", tags=["知识库管理"])
# 语音服务路由
app.include_router(voice.router, prefix="/api/v1/voice", tags=["语音服务"])
# 语音智能体路由（语音+多Agent集成）
app.include_router(voice_agent.router, prefix="/api/v1/voice-agent", tags=["语音智能体"])
# 实时语音 WebSocket 路由
app.include_router(realtime_voice.router, prefix="/api/v1/realtime-voice", tags=["实时语音"])
# 流式语音 WebSocket 路由
app.include_router(streaming_voice.router, prefix="/api/v1/streaming", tags=["流式语音"])
# 健康数据路由
app.include_router(health_data.router, prefix="/api/health", tags=["健康数据"])


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "智慧健康管理系统后端服务运行中",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "ok"
    }


@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {
        "status": "healthy",
        "service": "智慧健康管理系统",
        "version": settings.APP_VERSION
    }


# RAG 知识库搜索（简化版 - 返回预设健康知识）
@app.api_route("/api/rag/search", methods=["GET", "POST"])
async def rag_search():
    """RAG 知识库搜索接口"""
    # 返回一些预设的健康知识
    return {
        "success": True,
        "data": {
            "results": [
                {
                    "content": "老年人应保持规律作息，每天保证7-8小时睡眠，有助于身体恢复和免疫力提升。",
                    "score": 0.95
                },
                {
                    "content": "建议每天进行30分钟以上的有氧运动，如散步、太极拳等，有助于心血管健康。",
                    "score": 0.90
                },
                {
                    "content": "饮食应清淡，多吃蔬菜水果，少油少盐，注意补充蛋白质和钙质。",
                    "score": 0.85
                }
            ],
            "context": "老年人健康管理建议：保持规律作息，适量运动，均衡饮食，定期体检。"
        }
    }


if __name__ == "__main__":
    import uvicorn
    
    # 开发环境直接运行
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="debug" if settings.DEBUG else "info"
    )