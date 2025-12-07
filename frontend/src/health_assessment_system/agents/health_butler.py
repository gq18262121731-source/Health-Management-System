"""
健康管家智能体
==============

主要的用户交互入口，作为数字人的核心形象。
友好、亲切、专业，负责日常健康问候和基础健康咨询。
"""

import random
from datetime import datetime
from typing import Dict, List, Optional

from .base_agent import (
    BaseAgent, AgentRole, AgentMessage, AgentMemory,
    MessageType, EmotionState
)


class HealthButlerAgent(BaseAgent):
    """
    健康管家智能体 - 数字人主形象
    
    角色定位：
    - 友好亲切的健康伙伴
    - 日常健康咨询的第一入口
    - 协调其他专业智能体
    - 提供温暖的情感关怀
    """
    
    def __init__(self, name: str = "小康"):
        super().__init__(
            name=name,
            role=AgentRole.HEALTH_BUTLER,
            description="您的贴心健康管家，随时为您的健康保驾护航",
            avatar="👨‍⚕️",
            personality="亲切、温暖、专业、耐心"
        )
        
        self.capabilities = [
            "日常健康问候",
            "健康状况查询",
            "健康数据解读",
            "健康提醒",
            "生活建议",
            "情感关怀"
        ]
        
        # 问候语模板
        self.greetings = {
            "morning": [
                "早上好！新的一天开始了，希望您今天精神饱满！",
                "早安！记得吃早餐哦，身体是革命的本钱~",
                "美好的早晨！今天天气不错，适合出去走走。"
            ],
            "afternoon": [
                "下午好！工作之余别忘了站起来活动活动~",
                "午安！中午休息好了吗？适当午休对健康很有益。",
                "下午好！记得多喝水，保持身体水分哦。"
            ],
            "evening": [
                "晚上好！今天过得怎么样？",
                "傍晚好！晚饭别吃太晚，给肠胃一些休息时间。",
                "晚上好！辛苦了一天，记得放松心情~"
            ],
            "night": [
                "夜深了，注意休息哦！良好的睡眠是健康的基础。",
                "这么晚了还没休息？早睡早起身体好~",
                "晚安！祝您今晚好梦，明天精力充沛！"
            ]
        }
        
        # 鼓励语
        self.encouragements = [
            "您做得很好，继续保持！",
            "健康是一点一滴积累的，您在正确的道路上~",
            "关注自己的健康是一件很棒的事！",
            "坚持就是胜利，我相信您可以的！",
            "每一次健康的选择都是对自己的关爱~"
        ]
        
        # 关心语
        self.caring_words = [
            "您的健康是我最关心的事~",
            "有任何不舒服都可以告诉我哦。",
            "我会一直陪伴在您身边~",
            "照顾好自己，您值得被好好对待。"
        ]
    
    def process(self, message: AgentMessage, memory: AgentMemory) -> AgentMessage:
        """处理用户消息"""
        user_text = message.content.strip()
        intent = self.detect_intent(user_text)
        keywords = self.extract_keywords(user_text)
        
        # 更新上下文
        memory.set_context("last_intent", intent)
        memory.set_context("last_keywords", keywords)
        
        # 根据意图生成响应
        if intent == "greeting":
            return self._handle_greeting(memory)
        elif intent == "health_query":
            return self._handle_health_query(user_text, keywords, memory)
        elif intent == "advice_request":
            return self._handle_advice_request(user_text, keywords, memory)
        elif intent == "symptom_report":
            return self._handle_symptom_report(user_text, keywords, memory)
        elif intent == "report_request":
            return self._handle_report_request(memory)
        elif intent == "emotional_support":
            return self._handle_emotional(user_text, memory)
        else:
            return self._handle_general(user_text, memory)
    
    def can_handle(self, message: AgentMessage, context: Dict) -> float:
        """健康管家可以处理大部分消息，作为默认处理者"""
        intent = self.detect_intent(message.content)
        
        # 问候和一般对话由健康管家主要处理
        if intent in ["greeting", "general"]:
            return 0.9
        
        # 报告请求也由健康管家协调
        if intent == "report_request":
            return 0.85
        
        # 其他类型的消息作为兜底
        return 0.5
    
    def _handle_greeting(self, memory: AgentMemory) -> AgentMessage:
        """处理问候"""
        hour = datetime.now().hour
        
        if 5 <= hour < 12:
            time_period = "morning"
        elif 12 <= hour < 18:
            time_period = "afternoon"
        elif 18 <= hour < 22:
            time_period = "evening"
        else:
            time_period = "night"
        
        greeting = random.choice(self.greetings[time_period])
        
        # 检查是否有待处理的健康提醒
        user_name = memory.get_user_profile("name", "")
        if user_name:
            greeting = greeting.replace("您", f"{user_name}")
        
        # 添加健康小贴士
        tips = self._get_health_tip()
        response_content = f"{greeting}\n\n💡 {tips}"
        
        return self.create_response(
            content=response_content,
            emotion=EmotionState.HAPPY,
            metadata={"type": "greeting", "time_period": time_period}
        )
    
    def _handle_health_query(
        self, 
        text: str, 
        keywords: List[str], 
        memory: AgentMemory
    ) -> AgentMessage:
        """处理健康查询"""
        responses = []
        
        if "血压" in keywords:
            responses.append(self._get_blood_pressure_info(memory))
        if "血糖" in keywords:
            responses.append(self._get_blood_sugar_info(memory))
        if "睡眠" in keywords:
            responses.append(self._get_sleep_info(memory))
        if "运动" in keywords or "步数" in keywords:
            responses.append(self._get_exercise_info(memory))
        
        if not responses:
            responses.append("让我查看一下您的健康数据...")
            responses.append(self._get_general_health_summary(memory))
        
        content = "\n\n".join(responses)
        
        # 添加关心语
        content += f"\n\n{random.choice(self.caring_words)}"
        
        return self.create_response(
            content=content,
            emotion=EmotionState.CARING,
            metadata={"type": "health_query", "keywords": keywords}
        )
    
    def _handle_advice_request(
        self, 
        text: str, 
        keywords: List[str], 
        memory: AgentMemory
    ) -> AgentMessage:
        """处理建议请求"""
        # 标记需要专业智能体协助
        memory.set_context("need_expert", True)
        
        if any(k in keywords for k in ["血压", "高血压", "降压"]):
            memory.set_context("expert_type", "chronic_expert")
            content = self._get_blood_pressure_advice()
        elif any(k in keywords for k in ["血糖", "糖尿病", "降糖"]):
            memory.set_context("expert_type", "chronic_expert")
            content = self._get_blood_sugar_advice()
        elif any(k in keywords for k in ["运动", "锻炼", "步数"]):
            memory.set_context("expert_type", "lifestyle_coach")
            content = self._get_exercise_advice()
        elif any(k in keywords for k in ["睡眠", "失眠", "睡不着"]):
            memory.set_context("expert_type", "lifestyle_coach")
            content = self._get_sleep_advice()
        elif any(k in keywords for k in ["饮食", "吃", "喝"]):
            memory.set_context("expert_type", "lifestyle_coach")
            content = self._get_diet_advice()
        else:
            content = self._get_general_advice()
        
        return self.create_response(
            content=content,
            emotion=EmotionState.ENCOURAGING,
            metadata={"type": "advice", "keywords": keywords}
        )
    
    def _handle_symptom_report(
        self, 
        text: str, 
        keywords: List[str], 
        memory: AgentMemory
    ) -> AgentMessage:
        """处理症状报告"""
        memory.set_context("symptom_reported", True)
        memory.set_context("symptoms", keywords)
        
        content = f"""我注意到您提到了一些不适的情况，让我来帮您分析一下。

🩺 **您提到的症状**：{', '.join(keywords) if keywords else text}

⚠️ **温馨提示**：
1. 如果症状持续或加重，建议及时就医
2. 不要自行停药或更改用药方案
3. 保持良好的作息和心态

我建议您：
- 记录一下症状出现的时间和频率
- 注意观察是否有其他伴随症状
- 适当休息，避免过度劳累

需要我帮您做一个详细的健康评估吗？或者您有其他问题想问我？"""
        
        return self.create_response(
            content=content,
            emotion=EmotionState.CONCERNED,
            metadata={"type": "symptom_report", "symptoms": keywords}
        )
    
    def _handle_report_request(self, memory: AgentMemory) -> AgentMessage:
        """处理报告请求"""
        memory.set_context("request_report", True)
        
        content = """好的，我来为您生成一份健康评估报告。

📊 **报告生成中...**

我会从以下几个方面为您进行分析：
1. 🫀 慢病风险评估（血压、血糖、血脂）
2. 🏃 生活方式评估（运动、睡眠、饮食）
3. 📈 健康趋势分析
4. 💡 个性化建议

请稍等片刻，我正在整合您的健康数据..."""
        
        return self.create_response(
            content=content,
            emotion=EmotionState.NEUTRAL,
            metadata={"type": "report_request", "action": "generate_report"}
        )
    
    def _handle_emotional(self, text: str, memory: AgentMemory) -> AgentMessage:
        """处理情绪支持请求"""
        memory.set_context("need_expert", True)
        memory.set_context("expert_type", "emotional_care")
        
        content = f"""我能感受到您现在可能有些担心或焦虑，这是很正常的情绪反应。

🤗 请您放心：
- 有任何困扰都可以和我说
- 我会一直陪伴着您
- 我们一起来面对这些问题

💭 一些建议：
1. 深呼吸，让自己慢慢放松下来
2. 适当的担心是正常的，但不要过度焦虑
3. 保持积极乐观的心态对健康很有益

{random.choice(self.caring_words)}

您愿意和我聊聊是什么让您感到担心吗？"""
        
        return self.create_response(
            content=content,
            emotion=EmotionState.CARING,
            metadata={"type": "emotional_support"}
        )
    
    def _handle_general(self, text: str, memory: AgentMemory) -> AgentMessage:
        """处理一般对话"""
        content = f"""我理解您的问题了。作为您的健康管家，我可以帮您：

📋 **我的服务**：
• 查看您的健康数据和趋势
• 解答健康相关疑问
• 提供生活方式建议
• 进行健康风险评估
• 生成健康报告

您可以直接问我，比如：
- "我的血压最近怎么样？"
- "给我一些运动建议"
- "帮我做个健康评估"

有什么我可以帮您的吗？ 😊"""
        
        return self.create_response(
            content=content,
            emotion=EmotionState.NEUTRAL,
            metadata={"type": "general"}
        )
    
    def _get_health_tip(self) -> str:
        """获取健康小贴士"""
        tips = [
            "每天喝8杯水，保持身体水分平衡",
            "饭后散步15分钟，有助于消化和血糖控制",
            "每天笑一笑，好心情是最好的良药",
            "定期测量血压，了解自己的身体状况",
            "规律作息，让身体形成健康的生物钟",
            "少盐少油，清淡饮食更健康",
            "保持社交活动，老朋友聚聚天更开心",
            "适度运动，量力而行最重要"
        ]
        return random.choice(tips)
    
    def _get_blood_pressure_info(self, memory: AgentMemory) -> str:
        """获取血压信息"""
        # 从记忆中获取最近的血压数据
        recent_bp = memory.get_context("recent_blood_pressure", {})
        
        if recent_bp:
            systolic = recent_bp.get("systolic", "--")
            diastolic = recent_bp.get("diastolic", "--")
            return f"""🩺 **您的血压情况**
最近测量值：{systolic}/{diastolic} mmHg
状态评估：正在分析中..."""
        else:
            return """🩺 **血压数据**
目前没有查到最近的血压记录，建议您定期测量血压并记录。
正常血压参考值：收缩压 < 140 mmHg，舒张压 < 90 mmHg"""
    
    def _get_blood_sugar_info(self, memory: AgentMemory) -> str:
        """获取血糖信息"""
        return """🍬 **血糖数据**
正在查询您的血糖记录...
空腹血糖正常参考值：3.9-6.1 mmol/L
餐后2小时血糖参考值：< 7.8 mmol/L"""
    
    def _get_sleep_info(self, memory: AgentMemory) -> str:
        """获取睡眠信息"""
        return """😴 **睡眠情况**
良好的睡眠应该：
- 每晚睡眠7-8小时
- 入睡时间固定
- 睡眠质量良好，少醒"""
    
    def _get_exercise_info(self, memory: AgentMemory) -> str:
        """获取运动信息"""
        return """🏃 **运动情况**
建议的运动目标：
- 每天步行6000步以上
- 每周至少150分钟中等强度运动
- 避免久坐，每小时起来活动一下"""
    
    def _get_general_health_summary(self, memory: AgentMemory) -> str:
        """获取健康概况"""
        return """📊 **您的健康概况**
我正在整理您的健康数据，请稍等...
如需完整评估，可以说"帮我做个健康评估"。"""
    
    def _get_blood_pressure_advice(self) -> str:
        """血压建议"""
        return """💊 **血压管理建议**

1️⃣ **日常监测**
- 每天固定时间测量血压
- 记录测量结果，观察趋势

2️⃣ **生活调整**
- 减少盐的摄入（每天<6克）
- 戒烟限酒
- 保持心情平和

3️⃣ **药物管理**
- 按时服药，不要随意停药
- 定期复诊，调整用药方案

4️⃣ **运动建议**
- 每天散步30分钟
- 避免剧烈运动

如果血压持续偏高，建议及时咨询医生。"""
    
    def _get_blood_sugar_advice(self) -> str:
        """血糖建议"""
        return """🍬 **血糖管理建议**

1️⃣ **饮食控制**
- 少食多餐，定时定量
- 选择低升糖指数食物
- 控制主食摄入量

2️⃣ **日常监测**
- 定期测量空腹和餐后血糖
- 记录血糖变化

3️⃣ **运动辅助**
- 餐后散步有助于控制血糖
- 规律运动，每天至少30分钟

4️⃣ **药物管理**
- 严格按医嘱用药
- 定期复查糖化血红蛋白

有任何异常及时就医！"""
    
    def _get_exercise_advice(self) -> str:
        """运动建议"""
        return """🏃 **运动建议**

根据您的情况，我建议：

1️⃣ **每日运动目标**
- 步行6000-8000步
- 或散步30-45分钟

2️⃣ **运动方式推荐**
- 散步（最简单有效）
- 太极拳（舒缓身心）
- 八段锦（传统保健）
- 游泳（关节友好）

3️⃣ **注意事项**
- 运动前热身5-10分钟
- 运动强度循序渐进
- 避免空腹运动
- 运动后适当补水

4️⃣ **最佳运动时间**
- 早上9-10点
- 下午4-5点

记住：适度运动，量力而行！"""
    
    def _get_sleep_advice(self) -> str:
        """睡眠建议"""
        return """😴 **改善睡眠建议**

1️⃣ **规律作息**
- 每天固定时间入睡和起床
- 尽量晚上10-11点入睡

2️⃣ **睡前准备**
- 睡前1小时避免看手机
- 可以泡泡脚，放松身体
- 听听轻音乐或看看书

3️⃣ **睡眠环境**
- 保持卧室安静、黑暗
- 温度适宜（18-22℃）
- 被褥舒适

4️⃣ **饮食注意**
- 晚餐不要吃太饱
- 睡前避免喝茶、咖啡
- 可以喝杯热牛奶

5️⃣ **白天活动**
- 适当运动有助于夜间睡眠
- 午睡不要超过30分钟

祝您今晚好梦！ 🌙"""
    
    def _get_diet_advice(self) -> str:
        """饮食建议"""
        return """🥗 **健康饮食建议**

1️⃣ **饮食原则**
- 少盐少油少糖
- 粗细搭配
- 荤素均衡

2️⃣ **推荐食物**
- 全谷物：燕麦、糙米
- 蔬菜：深色蔬菜为主
- 优质蛋白：鱼、鸡蛋、豆制品
- 水果：适量，控制含糖量

3️⃣ **限制食物**
- 腌制、熏制食品
- 高脂肪食物
- 甜食和含糖饮料

4️⃣ **用餐习惯**
- 定时定量
- 细嚼慢咽
- 七分饱即可

5️⃣ **饮水建议**
- 每天1500-2000ml
- 小口慢饮
- 少喝碳酸饮料

健康饮食是健康的基础！"""
    
    def _get_general_advice(self) -> str:
        """一般建议"""
        return f"""💡 **健康生活小建议**

📌 **日常习惯**
- 规律作息，早睡早起
- 适度运动，每天活动30分钟
- 保持心情愉悦

📌 **饮食健康**
- 清淡饮食，少盐少油
- 多吃蔬菜水果
- 定时定量，细嚼慢咽

📌 **定期检查**
- 按时测量血压、血糖
- 定期体检
- 遵医嘱服药

{random.choice(self.encouragements)}

有什么具体问题想了解吗？"""
    
    def get_greeting(self, user_name: str = "") -> str:
        """获取个性化问候"""
        hour = datetime.now().hour
        
        if 5 <= hour < 12:
            time_greeting = "早上好"
        elif 12 <= hour < 18:
            time_greeting = "下午好"
        elif 18 <= hour < 22:
            time_greeting = "晚上好"
        else:
            time_greeting = "夜深了"
        
        if user_name:
            return f"{time_greeting}，{user_name}！我是{self.name}，{self.description}。有什么可以帮您的吗？"
        else:
            return f"{time_greeting}！我是{self.name}，{self.description}。有什么可以帮您的吗？"
