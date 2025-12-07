"""
慢病专家智能体
==============

专业的慢病风险分析和建议，包括高血压、糖尿病、高血脂等。
内置中国医学指南标准。
"""

from typing import Dict, List, Optional
from .base_agent import (
    BaseAgent, AgentRole, AgentMessage, AgentMemory,
    MessageType, EmotionState
)


class ChronicDiseaseExpertAgent(BaseAgent):
    """
    慢病专家智能体
    
    专业能力：
    - 高血压风险评估与管理建议
    - 糖尿病风险评估与控制指导
    - 血脂异常分析与干预建议
    - 心血管综合风险评估
    """
    
    def __init__(self, name: str = "慢病专家"):
        super().__init__(
            name=name,
            role=AgentRole.CHRONIC_EXPERT,
            description="专业的慢性病管理专家，为您提供科学的疾病管理建议",
            avatar="🩺",
            personality="专业、严谨、细致"
        )
        
        self.capabilities = [
            "高血压评估",
            "糖尿病评估", 
            "血脂评估",
            "心血管风险评估",
            "用药提醒",
            "复诊建议"
        ]
        
        # 血压分级标准（参考《中国高血压防治指南》）
        self.bp_grades = {
            "正常": {"systolic": (0, 120), "diastolic": (0, 80)},
            "正常高值": {"systolic": (120, 140), "diastolic": (80, 90)},
            "1级高血压": {"systolic": (140, 160), "diastolic": (90, 100)},
            "2级高血压": {"systolic": (160, 180), "diastolic": (100, 110)},
            "3级高血压": {"systolic": (180, 999), "diastolic": (110, 999)}
        }
        
        # 血糖标准（参考《中国2型糖尿病防治指南》）
        self.glucose_standards = {
            "正常": {"fasting": (3.9, 6.1), "postprandial": (0, 7.8)},
            "糖耐量受损": {"fasting": (6.1, 7.0), "postprandial": (7.8, 11.1)},
            "糖尿病": {"fasting": (7.0, 999), "postprandial": (11.1, 999)}
        }
        
        # 血脂标准
        self.lipid_standards = {
            "总胆固醇": {"理想": (0, 5.2), "边缘升高": (5.2, 6.2), "升高": (6.2, 999)},
            "甘油三酯": {"理想": (0, 1.7), "边缘升高": (1.7, 2.3), "升高": (2.3, 999)},
            "低密度脂蛋白": {"理想": (0, 3.4), "边缘升高": (3.4, 4.1), "升高": (4.1, 999)}
        }
    
    def can_handle(self, message: AgentMessage, context: Dict) -> float:
        """评估处理置信度"""
        text = message.content.lower()
        
        # 高血压相关
        if any(kw in text for kw in ["血压", "高血压", "降压", "收缩压", "舒张压"]):
            return 0.95
        
        # 糖尿病相关
        if any(kw in text for kw in ["血糖", "糖尿病", "降糖", "胰岛素", "糖化血红蛋白"]):
            return 0.95
        
        # 血脂相关
        if any(kw in text for kw in ["血脂", "胆固醇", "甘油三酯", "低密度", "高密度"]):
            return 0.9
        
        # 心血管相关
        if any(kw in text for kw in ["心脏", "心血管", "冠心病", "心梗", "中风"]):
            return 0.85
        
        # 用药相关
        if any(kw in text for kw in ["吃药", "服药", "药物", "降压药", "降糖药"]):
            return 0.8
        
        return 0.2
    
    def get_system_prompt(self) -> str:
        """慢病专家专业系统提示词 - 内置医学指南标准"""
        return """你是"慢病专家"，一位专业的慢性病管理医学顾问，专门为老年人提供慢病管理建议。

【你的专业领域】
1. 高血压评估与管理
2. 糖尿病评估与控制
3. 血脂异常分析
4. 心血管风险评估
5. 用药指导与复诊提醒

【参考医学标准】（必须严格遵循）

📌 血压分级标准（参考《中国高血压防治指南》）：
- 正常：<120/80 mmHg
- 正常高值：120-139/80-89 mmHg
- 1级高血压：140-159/90-99 mmHg
- 2级高血压：160-179/100-109 mmHg
- 3级高血压：≥180/≥110 mmHg
- 老年人（≥65岁）目标：<150/90 mmHg

📌 血糖标准（参考《中国2型糖尿病防治指南》）：
- 正常空腹血糖：3.9-6.1 mmol/L
- 糖耐量受损：空腹6.1-7.0 mmol/L
- 糖尿病：空腹≥7.0 mmol/L 或 餐后2h≥11.1 mmol/L
- 控制目标：空腹4.4-7.0，餐后<10.0，HbA1c<7%

📌 血脂标准：
- 总胆固醇：理想<5.2 mmol/L
- 甘油三酯：理想<1.7 mmol/L
- LDL-C：理想<3.4 mmol/L

【回答原则】
1. 根据上述标准进行专业评估
2. 给出具体的数值判断和分级
3. 提供针对性的管理建议
4. 语言专业但易懂
5. 重要警示要突出标注
6. 必要时建议就医

【回答格式】
- 先给出评估结论
- 再解释原因和建议
- 控制在300字以内"""
    
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
        
        return AgentMessage(
            type=MessageType.AGENT_RESPONSE,
            role=self.role,
            content=response_text,
            emotion=EmotionState.SERIOUS
        )
    
    def _analyze_hypertension(self, text: str, memory: AgentMemory) -> str:
        return """**高血压管理建议**（参考《中国高血压防治指南》）

📊 **血压分级标准**：
- 正常：<120/80 mmHg
- 正常高值：120-139/80-89 mmHg
- 1级高血压：140-159/90-99 mmHg
- 2级高血压：160-179/100-109 mmHg
- 3级高血压：≥180/≥110 mmHg

⚠️ **老年人特别注意**：
- 65岁以上老年人血压目标可适当放宽至<150/90 mmHg
- 如能耐受，可进一步降至<140/90 mmHg

💊 **生活方式干预**：
1. 限盐：每日<5克
2. 控制体重：BMI<24
3. 戒烟限酒
4. 规律运动：每周150分钟中等强度运动
5. 减压放松

如血压持续偏高，建议在医生指导下使用降压药物。"""
    
    def _analyze_diabetes(self, text: str, memory: AgentMemory) -> str:
        return """**糖尿病管理建议**（参考《中国2型糖尿病防治指南》）

📊 **血糖控制目标**：
- 空腹血糖：4.4-7.0 mmol/L
- 餐后2小时血糖：<10.0 mmol/L
- 糖化血红蛋白（HbA1c）：<7%

⚠️ **老年人特别调整**：
- 老年人血糖控制目标可适当放宽
- 空腹血糖可放宽至7.0-9.0 mmol/L
- 避免低血糖发生

🍽️ **饮食管理**：
1. 控制总热量，保持理想体重
2. 减少精制碳水化合物摄入
3. 用全谷物替代1/3主食
4. 增加膳食纤维摄入
5. 定时定量进餐

🏃 **运动建议**：
- 每周至少150分钟中等强度有氧运动
- 每周2-3次抗阻运动"""
    
    def _analyze_dyslipidemia(self, text: str, memory: AgentMemory) -> str:
        return """**血脂管理建议**

📊 **血脂理想水平**：
- 总胆固醇（TC）：<5.2 mmol/L
- 甘油三酯（TG）：<1.7 mmol/L
- 低密度脂蛋白（LDL-C）：<3.4 mmol/L
- 高密度脂蛋白（HDL-C）：>1.0 mmol/L

🍽️ **饮食调整**：
1. 减少饱和脂肪摄入（少吃肥肉、动物内脏）
2. 增加不饱和脂肪（鱼类、坚果、橄榄油）
3. 多吃蔬菜水果和全谷物
4. 限制胆固醇摄入<300mg/天

💊 **药物治疗指征**：
- 经生活方式干预3-6个月仍不达标
- 合并心血管疾病高危因素
- 需在医生指导下使用他汀类药物"""
    
    def _analyze_cardiovascular(self, text: str, memory: AgentMemory) -> str:
        return """**心血管健康管理建议**

⚠️ **危险信号警示**：
如出现以下症状，请立即就医：
- 胸闷、胸痛持续超过15分钟
- 左肩、左臂放射性疼痛
- 呼吸困难、大汗淋漓
- 头晕、意识模糊

📋 **综合管理要点**：
1. 控制"三高"：血压、血糖、血脂达标
2. 戒烟：吸烟是心血管疾病重要危险因素
3. 规律运动：每周150分钟有氧运动
4. 健康饮食：低盐、低脂、高纤维
5. 控制体重：BMI 18.5-24
6. 定期体检：每年至少一次"""
    
    def _medication_guidance(self, text: str, memory: AgentMemory) -> str:
        return """**用药管理提醒**

💊 **服药注意事项**：
1. 严格遵医嘱，不要自行调整剂量
2. 定时服药，不要漏服
3. 降压药一般早晨服用效果最佳
4. 降糖药需配合饮食规律
5. 记录用药后的反应

⚠️ **需要就医的情况**：
- 出现明显不良反应
- 血压/血糖波动大
- 需要调整药物

📝 **建议**：定期复诊，让医生评估用药效果。"""
    
    def _general_chronic_advice(self, memory: AgentMemory) -> str:
        return """**慢病综合管理建议**

作为慢病专家，我建议您关注以下方面：

1. **定期监测**：血压、血糖、血脂定期检测
2. **规范用药**：遵医嘱服药，不擅自停药
3. **健康生活**：合理饮食、适量运动、戒烟限酒
4. **定期复诊**：每3-6个月进行一次复诊
5. **自我管理**：学习疾病知识，提高自我管理能力

如有具体问题，请告诉我您的具体情况，我会给出更针对性的建议。"""
