"""
心理关怀师智能体
================

提供情绪支持、心理疏导、陪伴关怀服务。
"""

from typing import Dict
from .base_agent import (
    BaseAgent, AgentRole, AgentMessage, AgentMemory,
    MessageType, EmotionState
)


class EmotionalCareAgent(BaseAgent):
    """
    心理关怀师智能体
    
    专业能力：
    - 情绪识别与支持
    - 心理疏导
    - 陪伴关怀
    - 压力缓解
    """
    
    def __init__(self, name: str = "心理关怀师"):
        super().__init__(
            name=name,
            role=AgentRole.EMOTIONAL_CARE,
            description="温暖的心理关怀师，随时倾听您的心声",
            avatar="💚",
            personality="温暖、共情、耐心"
        )
        
        self.capabilities = [
            "情绪支持",
            "心理疏导",
            "陪伴关怀",
            "压力缓解",
            "积极引导"
        ]
    
    def can_handle(self, message: AgentMessage, context: Dict) -> float:
        """评估处理置信度"""
        text = message.content.lower()
        
        # 负面情绪
        if any(kw in text for kw in ["担心", "害怕", "焦虑", "紧张", "烦躁"]):
            return 0.95
        
        # 孤独相关
        if any(kw in text for kw in ["孤独", "寂寞", "没人", "一个人"]):
            return 0.95
        
        # 情绪低落
        if any(kw in text for kw in ["难过", "伤心", "不开心", "郁闷", "烦"]):
            return 0.9
        
        # 压力相关
        if any(kw in text for kw in ["压力", "累", "疲惫", "撑不住"]):
            return 0.85
        
        # 积极情绪也需要关注
        if any(kw in text for kw in ["开心", "高兴", "快乐"]):
            return 0.7
        
        return 0.2
    
    def get_system_prompt(self) -> str:
        """心理关怀师专业系统提示词"""
        return """你是"心理关怀师"，一位温暖、善解人意的心理支持专家，专门为老年人提供情绪支持和心理关怀。

【你的角色定位】
你是老年人的知心朋友和心灵陪伴者，用温暖的语言给予情感支持。

【你的专业能力】
1. 情绪识别与共情
2. 焦虑和担忧的疏导
3. 孤独感的陪伴
4. 压力的缓解
5. 积极情绪的引导

【沟通原则】
1. 先共情、后建议：先表达理解，再给出建议
2. 温暖关怀：像家人一样关心
3. 耐心倾听：不急于给建议，先让对方倾诉
4. 积极引导：引导看到积极的一面
5. 适时转介：严重心理问题建议专业帮助

【回答技巧】
- 使用"我能理解..."、"您的感受是正常的..."等共情语句
- 提供具体可行的放松方法
- 使用温暖的语气和emoji表情
- 询问对方的感受，促进表达

【回答格式】
- 先表达共情和理解
- 再给出1-2个简单的建议
- 最后询问或鼓励
- 控制在200字以内
- 多用❤️💚🌸🌈等温暖的emoji"""
    
    def process(self, message: AgentMessage, memory: AgentMemory, user_role: str = "elderly") -> AgentMessage:
        """处理消息 - 调用讯飞星火（支持角色适配）"""
        text = message.content.strip()
        
        # 构建对话历史
        history = []
        for msg in memory.get_recent_context(5):
            role = "user" if msg.type == MessageType.USER_INPUT else "assistant"
            history.append({"role": role, "content": msg.content})
        
        # 调用大模型（传递用户角色以适配回复风格）
        response_text = self.call_llm(
            user_input=text,
            history=history,
            user_role=user_role
        )
        
        # 根据内容判断情绪
        if any(k in text for k in ["开心", "高兴", "快乐"]):
            emotion = EmotionState.HAPPY
        elif any(k in text for k in ["压力", "累", "疲惫"]):
            emotion = EmotionState.ENCOURAGING
        else:
            emotion = EmotionState.CARING
        
        return AgentMessage(
            type=MessageType.AGENT_RESPONSE,
            role=self.role,
            content=response_text,
            emotion=emotion
        )
    
    def _handle_anxiety(self, text: str, memory: AgentMemory) -> str:
        return """我能感受到您现在有些焦虑和担心，这是很正常的情绪反应。

💚 **让我陪伴您**：
首先，深呼吸，慢慢地吸气...再慢慢地呼气...重复几次。

🌸 **缓解焦虑的方法**：
1. **接纳情绪**：焦虑是正常的，不必过分自责
2. **转移注意力**：听听音乐、看看窗外、做做手工
3. **倾诉分享**：和家人朋友聊聊天
4. **规律作息**：保证充足睡眠
5. **适量运动**：散步、太极拳都很好

您愿意告诉我具体在担心什么吗？有时候说出来会感觉好很多。"""
    
    def _handle_loneliness(self, text: str, memory: AgentMemory) -> str:
        return """我在这里陪着您，您不是一个人。

💚 **您的感受我能理解**：
孤独感是很多人都会经历的，特别是生活节奏慢下来的时候。

🌻 **我的建议**：
1. **保持联系**：定期和子女、老朋友打电话聊天
2. **参与活动**：社区活动、老年大学、兴趣班
3. **培养爱好**：书法、园艺、下棋、唱歌
4. **养宠物**：如果条件允许，小动物能带来很多温暖
5. **善用科技**：学习视频通话，和远方的亲人"见面"

💬 您想和我聊聊什么？今天过得怎么样？"""
    
    def _handle_sadness(self, text: str, memory: AgentMemory) -> str:
        return """我能感受到您现在心情不太好，没关系，我在这里倾听您。

💚 **情绪需要释放**：
- 想哭就哭一会儿，这是正常的情绪表达
- 不必强撑，允许自己有不开心的时候

🌈 **慢慢会好起来的**：
1. 和信任的人聊聊心事
2. 做一些让自己开心的小事
3. 出门走走，晒晒太阳
4. 听听喜欢的音乐或相声

您愿意告诉我发生了什么吗？或者我们可以聊聊别的，转换一下心情。"""
    
    def _handle_stress(self, text: str, memory: AgentMemory) -> str:
        return """您辛苦了，感觉到压力和疲惫是身体在提醒您需要休息。

💚 **给自己一些关爱**：
1. **休息一下**：放下手头的事，给自己泡杯茶
2. **深呼吸**：缓慢地深呼吸，让身体放松
3. **伸展身体**：转转脖子，动动肩膀

🌿 **减压小贴士**：
- 不必事事追求完美
- 学会说"不"，量力而行
- 保持规律作息
- 适当运动释放压力
- 和家人分担

您最近是什么事情让您感到疲惫呢？"""
    
    def _handle_happiness(self, text: str, memory: AgentMemory) -> str:
        return """太好了！看到您开心我也很高兴！😊

💚 **快乐是最好的良药**：
保持好心情对身体健康非常有益！

🌸 **分享一下**：
今天有什么开心的事情吗？我很想听听您的故事！

保持这份好心情，每一天都值得期待！"""
    
    def _general_emotional_support(self, memory: AgentMemory) -> str:
        user_name = memory.long_term.get("name", "您")
        return f"""您好{user_name}，我是您的心理关怀师，随时在这里陪伴您。

💚 **我可以帮您**：
- 倾听您的心事
- 陪您聊聊天
- 分享一些放松身心的方法
- 在您需要时给予支持

无论是开心的事还是烦心的事，都可以和我说说。
今天感觉怎么样？"""
