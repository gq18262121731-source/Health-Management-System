"""
对话记忆服务
============

支持短期记忆（当前对话）和长期记忆（用户健康档案）
"""
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from collections import defaultdict
import json

logger = logging.getLogger(__name__)


class ConversationMemory:
    """对话记忆管理器"""
    
    def __init__(self, max_history: int = 10, memory_ttl_hours: int = 24):
        """
        初始化记忆管理器
        
        Args:
            max_history: 保留的最大对话轮数
            memory_ttl_hours: 记忆过期时间（小时）
        """
        self.max_history = max_history
        self.memory_ttl = timedelta(hours=memory_ttl_hours)
        
        # 短期记忆：当前对话历史 {session_id: [messages]}
        self.conversations: Dict[str, List[Dict]] = defaultdict(list)
        
        # 长期记忆：用户健康档案 {user_id: {health_profile}}
        self.user_profiles: Dict[str, Dict[str, Any]] = defaultdict(dict)
        
        # 记忆时间戳 {session_id: last_update_time}
        self.timestamps: Dict[str, datetime] = {}
    
    def add_message(
        self, 
        session_id: str, 
        role: str, 
        content: str,
        metadata: Optional[Dict] = None
    ):
        """
        添加一条消息到对话历史
        
        Args:
            session_id: 会话ID
            role: 角色 (user/assistant)
            content: 消息内容
            metadata: 额外元数据（如智能体名称、情绪等）
        """
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        
        self.conversations[session_id].append(message)
        self.timestamps[session_id] = datetime.now()
        
        # 限制历史长度
        if len(self.conversations[session_id]) > self.max_history * 2:
            # 保留最近的消息
            self.conversations[session_id] = self.conversations[session_id][-self.max_history * 2:]
        
        # 从对话中提取健康信息
        if role == "user":
            self._extract_health_info(session_id, content)
    
    def get_history(
        self, 
        session_id: str, 
        limit: Optional[int] = None
    ) -> List[Dict]:
        """
        获取对话历史
        
        Args:
            session_id: 会话ID
            limit: 返回的最大消息数
            
        Returns:
            对话历史列表
        """
        self._cleanup_expired()
        
        history = self.conversations.get(session_id, [])
        if limit:
            history = history[-limit * 2:]  # 每轮包含user和assistant
        return history
    
    def get_context_summary(self, session_id: str) -> str:
        """
        获取对话上下文摘要，用于注入到系统提示词
        
        Args:
            session_id: 会话ID
            
        Returns:
            上下文摘要文本
        """
        history = self.get_history(session_id, limit=5)
        profile = self.get_user_profile(session_id)
        
        summary_parts = []
        
        # 添加用户健康档案
        if profile:
            profile_text = self._format_profile(profile)
            if profile_text:
                summary_parts.append(f"【用户健康档案】\n{profile_text}")
        
        # 添加最近对话摘要
        if history:
            recent_topics = self._extract_topics(history)
            if recent_topics:
                summary_parts.append(f"【最近讨论话题】{', '.join(recent_topics)}")
        
        return "\n\n".join(summary_parts) if summary_parts else ""
    
    def get_chat_history_for_llm(self, session_id: str, limit: int = 5) -> List[Dict[str, str]]:
        """
        获取适合传给LLM的对话历史格式
        
        Args:
            session_id: 会话ID
            limit: 最大轮数
            
        Returns:
            [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]
        """
        history = self.get_history(session_id, limit=limit)
        return [{"role": msg["role"], "content": msg["content"]} for msg in history]
    
    def update_user_profile(
        self, 
        session_id: str, 
        key: str, 
        value: Any,
        source: str = "conversation"
    ):
        """
        更新用户健康档案
        
        Args:
            session_id: 会话ID（也作为用户ID）
            key: 档案字段
            value: 值
            source: 来源（conversation/manual/system）
        """
        if session_id not in self.user_profiles:
            self.user_profiles[session_id] = {}
        
        self.user_profiles[session_id][key] = {
            "value": value,
            "updated_at": datetime.now().isoformat(),
            "source": source
        }
        
        logger.debug(f"更新用户档案 [{session_id}]: {key} = {value}")
    
    def get_user_profile(self, session_id: str) -> Dict[str, Any]:
        """
        获取用户健康档案
        
        Args:
            session_id: 会话ID
            
        Returns:
            用户档案字典
        """
        profile = self.user_profiles.get(session_id, {})
        # 简化格式，只返回值
        return {k: v.get("value") for k, v in profile.items() if v.get("value")}
    
    def clear_session(self, session_id: str):
        """清除会话记忆"""
        if session_id in self.conversations:
            del self.conversations[session_id]
        if session_id in self.timestamps:
            del self.timestamps[session_id]
        logger.info(f"清除会话记忆: {session_id}")
    
    def _extract_health_info(self, session_id: str, content: str):
        """
        从用户消息中提取健康信息
        
        Args:
            session_id: 会话ID
            content: 用户消息
        """
        content_lower = content.lower()
        
        # 血压提取
        import re
        bp_pattern = r'血压[是为]?\s*(\d{2,3})[/／](\d{2,3})'
        bp_match = re.search(bp_pattern, content)
        if bp_match:
            systolic, diastolic = bp_match.groups()
            self.update_user_profile(session_id, "blood_pressure", {
                "systolic": int(systolic),
                "diastolic": int(diastolic)
            })
        
        # 单独的高压/低压
        high_bp = re.search(r'高压[是为]?\s*(\d{2,3})', content)
        low_bp = re.search(r'低压[是为]?\s*(\d{2,3})', content)
        if high_bp or low_bp:
            bp = self.user_profiles.get(session_id, {}).get("blood_pressure", {}).get("value", {})
            if high_bp:
                bp["systolic"] = int(high_bp.group(1))
            if low_bp:
                bp["diastolic"] = int(low_bp.group(1))
            if bp:
                self.update_user_profile(session_id, "blood_pressure", bp)
        
        # 血糖提取
        sugar_pattern = r'血糖[是为]?\s*(\d+\.?\d*)'
        sugar_match = re.search(sugar_pattern, content)
        if sugar_match:
            self.update_user_profile(session_id, "blood_sugar", float(sugar_match.group(1)))
        
        # 疾病史提取
        diseases = []
        disease_keywords = {
            "高血压": ["高血压", "血压高"],
            "糖尿病": ["糖尿病", "血糖高", "糖高"],
            "高血脂": ["高血脂", "血脂高", "胆固醇高"],
            "心脏病": ["心脏病", "冠心病", "心梗"],
            "失眠": ["失眠", "睡不着", "睡眠不好"],
        }
        for disease, keywords in disease_keywords.items():
            if any(kw in content for kw in keywords):
                diseases.append(disease)
        
        if diseases:
            existing = self.user_profiles.get(session_id, {}).get("conditions", {}).get("value", [])
            if isinstance(existing, list):
                diseases = list(set(existing + diseases))
            self.update_user_profile(session_id, "conditions", diseases)
        
        # 年龄提取
        age_pattern = r'(\d{1,3})\s*岁'
        age_match = re.search(age_pattern, content)
        if age_match:
            age = int(age_match.group(1))
            if 1 <= age <= 120:
                self.update_user_profile(session_id, "age", age)
        
        # 体重提取
        weight_pattern = r'体重[是为]?\s*(\d{2,3})\s*(斤|公斤|kg)?'
        weight_match = re.search(weight_pattern, content, re.IGNORECASE)
        if weight_match:
            weight = float(weight_match.group(1))
            unit = weight_match.group(2)
            if unit == "斤":
                weight = weight / 2  # 转换为公斤
            self.update_user_profile(session_id, "weight", weight)
    
    def _format_profile(self, profile: Dict) -> str:
        """格式化用户档案为文本"""
        parts = []
        
        if profile.get("age"):
            parts.append(f"年龄: {profile['age']}岁")
        
        if profile.get("weight"):
            parts.append(f"体重: {profile['weight']}公斤")
        
        if profile.get("blood_pressure"):
            bp = profile["blood_pressure"]
            if isinstance(bp, dict):
                parts.append(f"血压: {bp.get('systolic', '?')}/{bp.get('diastolic', '?')} mmHg")
        
        if profile.get("blood_sugar"):
            parts.append(f"血糖: {profile['blood_sugar']} mmol/L")
        
        if profile.get("conditions"):
            conditions = profile["conditions"]
            if isinstance(conditions, list) and conditions:
                parts.append(f"健康状况: {', '.join(conditions)}")
        
        return "\n".join(parts)
    
    def _extract_topics(self, history: List[Dict]) -> List[str]:
        """从对话历史中提取讨论话题"""
        topics = set()
        topic_keywords = {
            "血压": "血压管理",
            "血糖": "血糖控制",
            "运动": "运动健身",
            "饮食": "饮食营养",
            "睡眠": "睡眠问题",
            "心情": "情绪心理",
            "头晕": "头晕症状",
            "胸闷": "心脏问题",
        }
        
        for msg in history:
            content = msg.get("content", "")
            for keyword, topic in topic_keywords.items():
                if keyword in content:
                    topics.add(topic)
        
        return list(topics)[:5]  # 最多5个话题
    
    def _cleanup_expired(self):
        """清理过期的会话记忆"""
        now = datetime.now()
        expired = [
            sid for sid, ts in self.timestamps.items()
            if now - ts > self.memory_ttl
        ]
        for sid in expired:
            self.clear_session(sid)
        
        if expired:
            logger.info(f"清理了 {len(expired)} 个过期会话")


# 创建全局实例
conversation_memory = ConversationMemory()
