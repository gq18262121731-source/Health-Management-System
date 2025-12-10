"""AI健康助手路由 - 集成用户认证、健康数据和对话历史"""
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
import logging
import uuid

from services.ai_service import ai_service
from repositories.ai_query_repository import AIQueryRepository
from repositories.health_repository import HealthRepository
from repositories.elderly_repository import ElderlyRepository
from database.database import get_db
from api.auth import get_current_active_user
from database.models import User

logger = logging.getLogger(__name__)

router = APIRouter()


class ConsultRequest(BaseModel):
    """AI咨询请求"""
    user_input: str = Field(..., description="用户输入的问题", min_length=1, max_length=2000)
    elderly_id: Optional[str] = Field(None, description="关联的老人ID（可选，用于获取健康数据）")
    use_knowledge_base: bool = Field(True, description="是否使用知识库")
    save_history: bool = Field(True, description="是否保存对话历史")


class ConsultResponse(BaseModel):
    """AI咨询响应"""
    status: str = "success"
    data: Dict[str, Any]
    message: str = "咨询成功"


class ErrorResponse(BaseModel):
    """错误响应"""
    status: str = "error"
    error_code: str
    error_message: str
    detail: Optional[str] = None


def get_health_data_for_user(db: Session, user: User, elderly_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    获取用户的健康数据
    
    Args:
        db: 数据库会话
        user: 当前用户
        elderly_id: 老人ID（可选）
    
    Returns:
        健康数据字典或None
    """
    try:
        health_repo = HealthRepository(db)
        elderly_repo = ElderlyRepository(db)
        
        # 确定要查询的老人ID
        target_elderly_id = None
        
        if elderly_id:
            try:
                target_elderly_id = uuid.UUID(elderly_id)
            except ValueError:
                logger.warning(f"无效的老人ID格式: {elderly_id}")
        
        # 如果是老人用户，使用自己的档案
        if user.role == "elderly":
            elderly_profile = elderly_repo.get_by_user_id(user.id)
            if elderly_profile:
                target_elderly_id = elderly_profile.id
        
        # 如果是子女用户，可以查询关联的老人
        elif user.role == "children" and not target_elderly_id:
            # 获取子女关联的第一个老人
            from database.models import ChildrenProfile, ChildrenElderlyRelation
            children_profile = db.query(ChildrenProfile).filter(
                ChildrenProfile.user_id == user.id
            ).first()
            if children_profile:
                relation = db.query(ChildrenElderlyRelation).filter(
                    ChildrenElderlyRelation.children_id == children_profile.id
                ).first()
                if relation:
                    target_elderly_id = relation.elderly_id
        
        if not target_elderly_id:
            return None
        
        # 获取最新的各项健康数据
        health_data = {}
        
        # 获取最新的健康记录
        from database.models import HealthRecord
        latest_record = db.query(HealthRecord).filter(
            HealthRecord.elderly_id == target_elderly_id
        ).order_by(HealthRecord.created_at.desc()).first()
        
        if latest_record:
            health_data = {
                "blood_pressure": f"{latest_record.systolic_pressure}/{latest_record.diastolic_pressure}" if latest_record.systolic_pressure and latest_record.diastolic_pressure else None,
                "heart_rate": latest_record.heart_rate,
                "blood_sugar": latest_record.blood_sugar,
                "temperature": latest_record.temperature,
                "blood_oxygen": latest_record.blood_oxygen,
                "weight": latest_record.weight,
                "last_update": latest_record.created_at.isoformat() if latest_record.created_at else None
            }
        
        return health_data if any(v is not None for v in health_data.values()) else None
        
    except Exception as e:
        logger.error(f"获取健康数据失败: {str(e)}")
        return None


@router.post("/consult", response_model=ConsultResponse)
async def ai_consult(
    request: ConsultRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    AI健康咨询接口（需要认证）
    
    功能：
    1. 从数据库获取用户实时健康数据
    2. 获取对话历史（用于上下文）
    3. 调用AI服务（支持知识库RAG）
    4. 保存对话记录到数据库
    """
    print(f"[DEBUG AI] 开始处理 AI 咨询请求，用户: {current_user.username}, 角色: {current_user.role}")
    
    try:
        # 参数验证
        if not request.user_input or not request.user_input.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户输入不能为空"
            )
        
        # 1. 获取健康数据
        print(f"[DEBUG AI] 步骤1: 获取健康数据...")
        health_data = get_health_data_for_user(db, current_user, request.elderly_id)
        print(f"[DEBUG AI] 健康数据: {health_data}")
        
        # 2. 获取对话历史
        print(f"[DEBUG AI] 步骤2: 获取对话历史...")
        conversation_history = []
        if request.save_history:
            ai_query_repo = AIQueryRepository(db)
            conversation_history = ai_query_repo.get_conversation_history_for_ai(
                user_id=current_user.id,
                limit=10,
                elderly_id=uuid.UUID(request.elderly_id) if request.elderly_id else None
            )
        print(f"[DEBUG AI] 对话历史数量: {len(conversation_history)}")
        
        # 3. 确定elderly_id（用于知识库检索）
        print(f"[DEBUG AI] 步骤3: 确定 elderly_id...")
        elderly_id_for_kb = None
        # 获取角色值用于比较
        user_role_value = current_user.role.value if hasattr(current_user.role, 'value') else str(current_user.role)
        print(f"[DEBUG AI] 用户角色值: {user_role_value}")
        
        if request.elderly_id:
            elderly_id_for_kb = request.elderly_id
        elif user_role_value == "elderly":
            elderly_repo = ElderlyRepository(db)
            elderly_profile = elderly_repo.get_by_user_id(current_user.id)
            if elderly_profile:
                elderly_id_for_kb = str(elderly_profile.id)
        
        print(f"[DEBUG AI] elderly_id_for_kb: {elderly_id_for_kb}")
        
        # 4. 调用AI服务
        print(f"[DEBUG AI] 步骤4: 调用 AI 服务...")
        try:
            ai_response = await ai_service.consult(
                user_input=request.user_input,
                user_role=current_user.role.value if hasattr(current_user.role, 'value') else str(current_user.role),
                elderly_id=elderly_id_for_kb,
                health_data=health_data,
                conversation_history=conversation_history,
                use_knowledge_base=request.use_knowledge_base
            )
        except Exception as e:
            logger.error(f"AI服务调用失败: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"AI服务暂时不可用: {str(e)}"
            )
        
        # 5. 保存对话历史
        print(f"[DEBUG AI] 步骤5: 保存对话历史...")
        if request.save_history:
            try:
                ai_query_repo = AIQueryRepository(db)
                elderly_id_uuid = None
                if request.elderly_id:
                    try:
                        elderly_id_uuid = uuid.UUID(request.elderly_id)
                    except:
                        pass
                elif user_role_value == "elderly":
                    elderly_repo = ElderlyRepository(db)
                    elderly_profile = elderly_repo.get_by_user_id(current_user.id)
                    if elderly_profile:
                        elderly_id_uuid = elderly_profile.id
                
                ai_query_repo.create_query(
                    user_id=current_user.id,
                    query_text=request.user_input,
                    response_text=ai_response,
                    elderly_id=elderly_id_uuid,
                    query_type="health_advice"
                )
            except Exception as e:
                logger.warning(f"保存对话历史失败: {str(e)}")
                # 不阻断响应，只记录警告
        
        return ConsultResponse(
            status="success",
            data={
                "query": request.user_input,
                "response": ai_response,
                "user_role": current_user.role.value if hasattr(current_user.role, 'value') else str(current_user.role),
                "health_data_used": health_data is not None,
                "knowledge_base_used": request.use_knowledge_base
            },
            message="咨询成功"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"AI咨询接口错误: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI服务处理失败: {str(e)}"
        )


@router.get("/health")
async def ai_health_check():
    """AI服务健康检查"""
    is_available = ai_service.provider is not None and ai_service.api_key is not None
    
    return {
        "status": "success",
        "data": {
            "ai_service_available": is_available,
            "provider": ai_service.provider if is_available else None,
            "mode": "real" if is_available else "mock"
        },
        "message": f"AI服务运行正常 ({ai_service.provider})" if is_available else "AI服务运行在模拟模式"
    }


@router.get("/history")
async def get_consultation_history(
    limit: int = 20,
    elderly_id: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """获取咨询历史记录"""
    try:
        ai_query_repo = AIQueryRepository(db)
        
        elderly_id_uuid = None
        if elderly_id:
            try:
                elderly_id_uuid = uuid.UUID(elderly_id)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="无效的老人ID格式"
                )
        
        queries = ai_query_repo.get_user_query_history(
            user_id=current_user.id,
            limit=limit,
            elderly_id=elderly_id_uuid
        )
        
        return {
            "status": "success",
            "data": {
                "queries": [
                    {
                        "id": str(q.id),
                        "query_text": q.query_text,
                        "response_text": q.response_text,
                        "created_at": q.created_at.isoformat() if q.created_at else None,
                        "elderly_id": str(q.elderly_id) if q.elderly_id else None
                    }
                    for q in queries
                ],
                "count": len(queries)
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取咨询历史失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取咨询历史失败: {str(e)}"
        )


class PublicConsultRequest(BaseModel):
    """公开AI咨询请求（无需认证）"""
    user_input: str = Field(..., description="用户输入的问题", min_length=1, max_length=2000)
    user_role: str = Field(default="elderly", description="用户角色: elderly/children/community")


@router.post("/consult/public")
async def ai_consult_public(request: PublicConsultRequest):
    """
    公开AI健康咨询接口（无需认证）
    
    用于前端快速测试多智能体系统
    """
    print(f"[DEBUG AI Public] 收到公开咨询请求，角色: {request.user_role}")
    
    try:
        if not request.user_input or not request.user_input.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户输入不能为空"
            )
        
        # 调用AI服务
        try:
            ai_result = await ai_service.consult(
                user_input=request.user_input,
                user_role=request.user_role,
                elderly_id=None,
                health_data=None,
                conversation_history=[],
                use_knowledge_base=True,
                use_multi_agent=True
            )
        except Exception as e:
            logger.error(f"AI服务调用失败: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"AI服务暂时不可用: {str(e)}"
            )
        
        # 解析返回结果
        response_text = ai_result.get("response", "") if isinstance(ai_result, dict) else ai_result
        agent_name = ai_result.get("agent", "健康管家") if isinstance(ai_result, dict) else "健康管家"
        
        return {
            "status": "success",
            "data": {
                "query": request.user_input,
                "response": response_text,
                "agent": agent_name,
                "user_role": request.user_role,
                "health_data_used": False,
                "knowledge_base_used": True
            },
            "message": "咨询成功"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"公开AI咨询接口错误: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI服务处理失败: {str(e)}"
        )


class StreamConsultRequest(BaseModel):
    """流式AI咨询请求"""
    user_input: str = Field(..., description="用户输入的问题", min_length=1, max_length=2000)
    user_role: str = Field(default="elderly", description="用户角色: elderly/children/community")
    session_id: str = Field(default=None, description="会话ID（用于对话记忆）")


@router.post("/consult/stream")
async def ai_consult_stream(request: StreamConsultRequest):
    """
    流式AI健康咨询接口（SSE）
    
    支持实时返回AI回复，提升用户体验
    """
    from fastapi.responses import StreamingResponse
    import asyncio
    import uuid
    
    session_id = request.session_id or str(uuid.uuid4())[:8]
    
    async def generate():
        try:
            from services.agents.multi_agent_service import multi_agent_service
            from services.spark_service import spark_service
            
            # 先进行意图识别和工具调用
            result = multi_agent_service.process(
                user_input=request.user_input,
                user_id=session_id,
                user_role=request.user_role,
                session_id=session_id
            )
            
            # 发送智能体信息
            agent_name = result.get("agent", "健康管家")
            yield f"data: {{\"type\": \"agent\", \"agent\": \"{agent_name}\"}}\n\n"
            
            # 发送完整响应（分块模拟流式）
            response = result.get("response", "")
            chunk_size = 10  # 每次发送的字符数
            
            for i in range(0, len(response), chunk_size):
                chunk = response[i:i+chunk_size]
                # 转义特殊字符
                chunk_escaped = chunk.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
                yield f"data: {{\"type\": \"content\", \"content\": \"{chunk_escaped}\"}}\n\n"
                await asyncio.sleep(0.05)  # 模拟流式效果
            
            # 发送完成信号
            yield f"data: {{\"type\": \"done\", \"session_id\": \"{session_id}\"}}\n\n"
            
        except Exception as e:
            logger.error(f"流式咨询错误: {e}")
            yield f"data: {{\"type\": \"error\", \"message\": \"{str(e)}\"}}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@router.get("/agents")
async def get_agents_info():
    """
    获取多智能体系统信息
    
    返回所有注册的智能体及其能力
    """
    try:
        from services.agents.multi_agent_service import multi_agent_service
        
        agents = multi_agent_service.get_agents_info()
        
        return {
            "status": "success",
            "data": {
                "agents": agents,
                "count": len(agents),
                "multi_agent_enabled": True
            },
            "message": "多智能体系统运行正常"
        }
    except ImportError:
        return {
            "status": "success",
            "data": {
                "agents": [],
                "count": 0,
                "multi_agent_enabled": False
            },
            "message": "多智能体系统未启用"
        }
    except Exception as e:
        logger.error(f"获取智能体信息失败: {str(e)}")
        return {
            "status": "error",
            "data": {"agents": [], "count": 0, "multi_agent_enabled": False},
            "message": f"获取智能体信息失败: {str(e)}"
        }
