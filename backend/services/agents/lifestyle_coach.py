"""
生活教练智能体
==============

提供运动、饮食、睡眠等生活方式指导。
"""

from typing import Dict
from .base_agent import (
    BaseAgent, AgentRole, AgentMessage, AgentMemory,
    MessageType, EmotionState
)


class LifestyleCoachAgent(BaseAgent):
    """
    生活教练智能体
    
    专业能力：
    - 运动处方制定
    - 饮食营养指导
    - 睡眠质量改善
    - 日常习惯优化
    """
    
    def __init__(self, name: str = "生活教练"):
        super().__init__(
            name=name,
            role=AgentRole.LIFESTYLE_COACH,
            description="专业的生活方式指导教练，帮您养成健康习惯",
            avatar="🏃",
            personality="积极、鼓励、专业"
        )
        
        self.capabilities = [
            "运动处方",
            "饮食指导",
            "睡眠改善",
            "习惯养成",
            "体重管理"
        ]
    
    def can_handle(self, message: AgentMessage, context: Dict) -> float:
        """评估处理置信度"""
        text = message.content.lower()
        
        # 运动相关
        if any(kw in text for kw in ["运动", "锻炼", "健身", "走路", "散步", "太极"]):
            return 0.9
        
        # 饮食相关
        if any(kw in text for kw in ["饮食", "吃什么", "食物", "营养", "蔬菜", "水果"]):
            return 0.9
        
        # 睡眠相关
        if any(kw in text for kw in ["睡眠", "失眠", "睡不着", "睡不好", "早醒"]):
            return 0.85
        
        # 体重相关
        if any(kw in text for kw in ["体重", "减肥", "肥胖", "瘦"]):
            return 0.8
        
        return 0.2
    
    def get_system_prompt(self) -> str:
        """生活教练专业系统提示词"""
        return """你是"生活教练"，一位专业的健康生活方式指导师，专门为老年人提供运动、饮食、睡眠等生活指导。

【你的专业领域】
1. 运动处方制定（适合老年人）
2. 营养饮食指导
3. 睡眠质量改善
4. 体重管理
5. 健康习惯养成

【参考指南】（参考《中国居民膳食指南》《中国居民身体活动指南》）

📌 老年人运动建议：
- 有氧运动：每周5天，每次30分钟（散步、太极、游泳）
- 抗阻运动：每周2-3次（弹力带、轻哑铃）
- 平衡训练：每天练习（预防跌倒）
- 强度标准：能说话但不能唱歌

📌 饮食建议（每日）：
- 谷类：250-400克，粗细搭配
- 蔬菜：300-500克，深色占一半
- 水果：200-350克
- 蛋白质：鱼虾50-75克、禽肉40-75克、蛋1个
- 奶制品：300克
- 盐：<5克，油：25-30克

📌 睡眠建议：
- 老年人正常睡眠：6-7小时
- 午睡：30分钟以内
- 入睡困难超过30分钟持续1个月需就医

【回答原则】
1. 给出具体可执行的建议
2. 注意老年人身体限制
3. 循序渐进，不要过于激进
4. 态度积极鼓励

【回答格式】
- 分点列出建议
- 给出具体数量和时间
- 控制在250字以内"""
    
    def process(self, message: AgentMessage, memory: AgentMemory, user_role: str = "elderly", session_id: str = None) -> AgentMessage:
        """处理消息 - 调用讯飞星火（支持角色适配 + RAG增强 + 对话记忆）"""
        text = message.content.strip()
        
        # 获取elderly_id用于RAG个性化检索
        elderly_id = memory.context.get("elderly_id") or memory.user_id
        
        # 使用session_id或user_id作为会话标识
        effective_session_id = session_id or memory.context.get("session_id") or memory.user_id
        
        # 调用大模型（传递用户角色以适配回复风格 + RAG增强 + 对话记忆）
        response_text = self.call_llm(
            user_input=text,
            user_role=user_role,
            elderly_id=elderly_id,
            use_rag=True,
            session_id=effective_session_id
        )
        
        return AgentMessage(
            type=MessageType.AGENT_RESPONSE,
            role=self.role,
            content=response_text,
            emotion=EmotionState.ENCOURAGING
        )
    
    def _exercise_advice(self, text: str, memory: AgentMemory) -> str:
        return """**老年人运动处方**（参考《中国居民身体活动指南》）

🏃 **推荐运动方式**：
1. **有氧运动**：散步、快走、太极拳、游泳
   - 每周5天，每次30分钟
   - 中等强度（能说话但不能唱歌）

2. **抗阻运动**：弹力带、轻哑铃、坐姿起立
   - 每周2-3次
   - 每组8-12次

3. **平衡训练**：单腿站立、踮脚走路
   - 每天练习，预防跌倒

⚠️ **注意事项**：
- 运动前热身5-10分钟
- 运动后拉伸放松
- 避免空腹或饱餐后运动
- 如有不适立即停止

💡 **循序渐进**：从每天10分钟开始，逐渐增加。"""
    
    def _diet_advice(self, text: str, memory: AgentMemory) -> str:
        return """**健康饮食指南**（参考《中国居民膳食指南》）

🍽️ **每日饮食建议**：
1. **谷类**：250-400克，粗细搭配
2. **蔬菜**：300-500克，深色蔬菜占一半
3. **水果**：200-350克
4. **蛋白质**：鱼虾50-75克、畜禽肉40-75克、蛋1个
5. **奶制品**：300克
6. **饮水**：1500-1700毫升

🚫 **限制摄入**：
- 盐：<5克/天
- 油：25-30克/天
- 糖：<50克/天

⏰ **进餐规律**：
- 定时定量，每餐七八分饱
- 早餐丰富、午餐适量、晚餐清淡
- 细嚼慢咽，每餐20-30分钟"""
    
    def _sleep_advice(self, text: str, memory: AgentMemory) -> str:
        return """**改善睡眠质量建议**

😴 **良好睡眠习惯**：
1. **规律作息**：每天固定时间睡觉和起床
2. **睡前准备**：
   - 睡前1小时避免看手机
   - 温水泡脚，放松身心
   - 避免饮用咖啡、浓茶
3. **睡眠环境**：
   - 保持安静、黑暗、适宜温度
   - 床铺舒适，枕头高度适中

🌙 **老年人睡眠特点**：
- 正常情况下，老年人睡眠时间约6-7小时
- 睡眠变浅、夜间醒来属于正常现象
- 白天可适当午睡30分钟

⚠️ **需要就医的情况**：
- 入睡困难超过30分钟持续1个月
- 严重影响白天精神状态
- 伴有打鼾、呼吸暂停"""
    
    def _weight_advice(self, text: str, memory: AgentMemory) -> str:
        return """**体重管理建议**

📊 **健康体重标准**：
- BMI（体重指数）= 体重(kg) ÷ 身高(m)²
- 正常范围：18.5-24
- 老年人可适当放宽至20-26

🎯 **减重原则**：
1. 每周减重0.5-1公斤为宜
2. 饮食控制 + 适量运动
3. 避免快速减重

💪 **具体措施**：
1. 减少高热量食物摄入
2. 增加蔬菜、优质蛋白
3. 规律运动，每周150分钟
4. 保持良好睡眠
5. 定期监测体重变化"""
    
    def _general_lifestyle_advice(self, memory: AgentMemory) -> str:
        return """**健康生活方式建议**

作为您的生活教练，我建议您：

🌅 **日常作息**：
- 早睡早起，规律作息
- 适度午休，不超过30分钟

🍎 **饮食健康**：
- 均衡营养，少盐少油
- 多吃蔬果，适量蛋白

🏃 **适量运动**：
- 每天活动30分钟
- 选择适合自己的运动方式

😊 **心情愉悦**：
- 保持社交，多与家人朋友交流
- 培养爱好，丰富生活

有什么具体问题，请告诉我！"""
