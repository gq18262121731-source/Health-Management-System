"""AI咨询记录相关的Repository类"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import desc
import uuid

from repositories.base import BaseRepository
from database.models import AIQuery


class AIQueryRepository(BaseRepository[AIQuery]):
    """AI咨询记录数据访问类"""
    
    def __init__(self, db: Session):
        super().__init__(db, AIQuery)
    
    def create_query(
        self,
        user_id: uuid.UUID,
        query_text: str,
        response_text: str,
        elderly_id: Optional[uuid.UUID] = None,
        query_type: str = "health_advice"
    ) -> AIQuery:
        """
        创建AI咨询记录
        
        Args:
            user_id: 用户ID
            query_text: 用户查询文本
            response_text: AI回复文本
            elderly_id: 关联的老人ID（可选）
            query_type: 查询类型
        
        Returns:
            AIQuery对象
        """
        try:
            from database.models import QueryType
            
            # 将字符串转换为枚举
            try:
                # 尝试直接匹配枚举值
                query_type_enum = QueryType(query_type)
            except ValueError:
                # 如果匹配失败，尝试转换为大写后匹配枚举名
                try:
                    query_type_enum = QueryType[query_type.upper().replace('-', '_')]
                except (KeyError, AttributeError):
                    # 默认使用健康建议
                    query_type_enum = QueryType.HEALTH_ADVICE
            
            ai_query = AIQuery(
                user_id=user_id,
                elderly_id=elderly_id,
                query_text=query_text,
                query_type=query_type_enum,
                response_text=response_text
            )
            
            self.db.add(ai_query)
            self.db.commit()
            self.db.refresh(ai_query)
            
            return ai_query
            
        except Exception as e:
            self.db.rollback()
            print(f"Error creating AI query: {e}")
            raise
    
    def get_user_query_history(
        self,
        user_id: uuid.UUID,
        limit: int = 20,
        elderly_id: Optional[uuid.UUID] = None
    ) -> List[AIQuery]:
        """
        获取用户的咨询历史
        
        Args:
            user_id: 用户ID
            limit: 返回数量限制
            elderly_id: 过滤的老人ID（可选）
        
        Returns:
            AIQuery列表
        """
        try:
            query = self.db.query(AIQuery).filter(
                AIQuery.user_id == user_id
            )
            
            if elderly_id:
                query = query.filter(AIQuery.elderly_id == elderly_id)
            
            return query.order_by(desc(AIQuery.created_at)).limit(limit).all()
            
        except Exception as e:
            print(f"Error getting user query history: {e}")
            return []
    
    def get_conversation_history_for_ai(
        self,
        user_id: uuid.UUID,
        limit: int = 10,
        elderly_id: Optional[uuid.UUID] = None
    ) -> List[Dict[str, str]]:
        """
        获取对话历史（用于AI上下文）
        
        Returns:
            对话历史列表，格式: [{"role": "user", "content": "..."}, ...]
        """
        try:
            queries = self.get_user_query_history(user_id, limit=limit * 2, elderly_id=elderly_id)
            
            # 将查询记录转换为对话格式
            history = []
            for query in reversed(queries):  # 反转以保持时间顺序
                history.append({
                    "role": "user",
                    "content": query.query_text
                })
                history.append({
                    "role": "assistant",
                    "content": query.response_text
                })
            
            # 只返回最近的对话
            return history[-limit:] if len(history) > limit else history
            
        except Exception as e:
            print(f"Error getting conversation history: {e}")
            return []

