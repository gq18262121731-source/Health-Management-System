"""
慢病专家智能体
==============

专业的慢病风险分析和建议，包括高血压、糖尿病、高血脂等。
"""

from typing import Dict, List, Optional, Any
from datetime import datetime

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
        
        # 血压分级标准（中国高血压指南）
        self.bp_grades = {
            "正常": {"systolic": (0, 120), "diastolic": (0, 80)},
            "正常高值": {"systolic": (120, 140), "diastolic": (80, 90)},
            "1级高血压": {"systolic": (140, 160), "diastolic": (90, 100)},
            "2级高血压": {"systolic": (160, 180), "diastolic": (100, 110)},
            "3级高血压": {"systolic": (180, 999), "diastolic": (110, 999)}
        }
        
        # 血糖标准
        self.glucose_standards = {
            "正常": {"fasting": (3.9, 6.1), "postprandial": (0, 7.8)},
            "糖耐量受损": {"fasting": (6.1, 7.0), "postprandial": (7.8, 11.1)},
            "糖尿病": {"fasting": (7.0, 999), "postprandial": (11.1, 999)}
        }
    
    def process(self, message: AgentMessage, memory: AgentMemory) -> AgentMessage:
        """处理消息"""
        user_text = message.content.strip()
        keywords = self.extract_keywords(user_text)
        intent = self.detect_intent(user_text)
        
        # 分析用户关注的疾病类型
        if any(k in keywords for k in ["血压", "高血压", "降压"]):
            return self._analyze_hypertension(user_text, memory)
        elif any(k in keywords for k in ["血糖", "糖尿病", "降糖"]):
            return self._analyze_diabetes(user_text, memory)
        elif any(k in keywords for k in ["血脂", "胆固醇", "甘油三酯"]):
            return self._analyze_dyslipidemia(user_text, memory)
        elif any(k in keywords for k in ["心脏", "心血管", "冠心病"]):
            return self._analyze_cardiovascular(user_text, memory)
        elif "吃药" in keywords or "服药" in keywords or "药" in keywords:
            return self._medication_guidance(user_text, memory)
        else:
            return self._general_chronic_advice(memory)
    
    def can_handle(self, message: AgentMessage, context: Dict) -> float:
        """判断处理能力"""
        keywords = self.extract_keywords(message.content)
        
        chronic_keywords = ["血压", "高血压", "血糖", "糖尿病", "血脂", 
                          "胆固醇", "心脏", "心血管", "冠心病", "吃药", 
                          "服药", "降压", "降糖", "降脂"]
        
        matched = sum(1 for k in keywords if k in chronic_keywords)
        
        if matched >= 2:
            return 0.95
        elif matched == 1:
            return 0.8
        else:
            return 0.2
    
    def _analyze_hypertension(self, text: str, memory: AgentMemory) -> AgentMessage:
        """分析高血压情况"""
        # 获取血压数据
        bp_data = memory.get_context("blood_pressure_data", {})
        recent_bp = memory.get_context("recent_blood_pressure", {})
        
        analysis = """🩺 **高血压专业分析**

📊 **血压评估**
"""
        
        if recent_bp:
            systolic = recent_bp.get("systolic", 0)
            diastolic = recent_bp.get("diastolic", 0)
            grade = self._get_bp_grade(systolic, diastolic)
            
            analysis += f"""
最近测量值：{systolic}/{diastolic} mmHg
血压分级：{grade}
"""
        else:
            analysis += "\n暂无近期血压数据，建议您定期测量并记录。\n"
        
        analysis += """
📋 **高血压管理要点**

**1️⃣ 监测管理**
- 每天早晚各测量1次血压
- 测量前静坐5分钟
- 记录测量时间和数值

**2️⃣ 生活方式干预**
- 限盐：每天<6克（约1啤酒瓶盖）
- 限酒：男性<25克酒精/天，女性<15克
- 戒烟：烟草是血管的大敌
- 控制体重：BMI维持在24以下

**3️⃣ 饮食建议**
- DASH饮食模式
- 多吃新鲜蔬菜水果
- 选择低脂奶制品
- 减少红肉摄入

**4️⃣ 运动处方**
- 每周150分钟中等强度运动
- 推荐：快走、游泳、骑车
- 避免举重等力量型运动

**5️⃣ 药物治疗**
- 遵医嘱按时服药
- 不要自行停药或换药
- 定期复诊调整方案

⚠️ **警示信号**
出现以下情况请立即就医：
- 血压突然升高>180/120 mmHg
- 剧烈头痛、视物模糊
- 胸闷、心悸
- 肢体麻木无力
"""
        
        return self.create_response(
            content=analysis,
            emotion=EmotionState.SERIOUS,
            metadata={"type": "hypertension_analysis"}
        )
    
    def _analyze_diabetes(self, text: str, memory: AgentMemory) -> AgentMessage:
        """分析糖尿病情况"""
        glucose_data = memory.get_context("glucose_data", {})
        
        analysis = """🍬 **糖尿病专业分析**

📊 **血糖评估**

正常参考范围：
- 空腹血糖：3.9-6.1 mmol/L
- 餐后2小时：<7.8 mmol/L
- 糖化血红蛋白(HbA1c)：<6.5%

📋 **糖尿病管理要点**

**1️⃣ 血糖监测**
- 空腹血糖：每天早餐前
- 餐后血糖：餐后2小时
- 建议使用血糖监测日记

**2️⃣ 饮食控制（五驾马车之一）**
- 定时定量，少食多餐
- 主食控制：每餐1-2两
- 选择低GI食物：
  * 推荐：燕麦、糙米、荞麦
  * 限制：白米饭、面条、馒头
- 蔬菜充足，水果适量

**3️⃣ 运动治疗**
- 餐后1小时开始运动
- 每次30-45分钟
- 每周至少5次
- 推荐：快走、太极拳、游泳

**4️⃣ 药物管理**
- 口服药：按时按量
- 胰岛素：注意注射部位轮换
- 携带糖果预防低血糖

**5️⃣ 并发症预防**
- 每年检查眼底
- 定期检查肾功能
- 注意足部护理

⚠️ **低血糖警示**
出现以下症状请立即补充糖分：
- 心慌、手抖、出冷汗
- 头晕、乏力
- 严重时意识模糊

🔔 **糖尿病患者随身三宝**
1. 血糖仪
2. 糖果/饼干
3. 糖尿病患者卡
"""
        
        return self.create_response(
            content=analysis,
            emotion=EmotionState.SERIOUS,
            metadata={"type": "diabetes_analysis"}
        )
    
    def _analyze_dyslipidemia(self, text: str, memory: AgentMemory) -> AgentMessage:
        """分析血脂异常"""
        analysis = """🫀 **血脂专业分析**

📊 **血脂检测项目及标准**

| 项目 | 理想水平 | 边缘升高 | 升高 |
|------|---------|---------|------|
| 总胆固醇(TC) | <5.2 | 5.2-6.2 | >6.2 |
| 低密度脂蛋白(LDL-C) | <3.4 | 3.4-4.1 | >4.1 |
| 高密度脂蛋白(HDL-C) | >1.0 | — | <1.0(异常) |
| 甘油三酯(TG) | <1.7 | 1.7-2.3 | >2.3 |

（单位：mmol/L）

📋 **血脂管理要点**

**1️⃣ 饮食调整**
- 减少饱和脂肪摄入
  * 限制：猪油、黄油、肥肉
  * 推荐：橄榄油、菜籽油
- 增加膳食纤维
  * 燕麦、豆类、蔬菜
- 每周吃鱼2-3次
- 限制蛋黄（每周<4个）

**2️⃣ 生活方式**
- 戒烟限酒
- 保持理想体重
- 规律运动（有氧运动为主）

**3️⃣ 他汀类药物**
- 是降脂治疗的基石
- 建议晚上服用
- 定期监测肝功能

⚠️ **注意事项**
- 血脂检查需空腹12小时
- 高血脂往往没有症状，定期检查很重要
- 血脂异常是心血管疾病的主要危险因素
"""
        
        return self.create_response(
            content=analysis,
            emotion=EmotionState.SERIOUS,
            metadata={"type": "dyslipidemia_analysis"}
        )
    
    def _analyze_cardiovascular(self, text: str, memory: AgentMemory) -> AgentMessage:
        """分析心血管风险"""
        analysis = """❤️ **心血管风险综合评估**

📊 **主要危险因素**

1. **可控因素**
   - 高血压 ⚠️
   - 高血糖 ⚠️
   - 高血脂 ⚠️
   - 吸烟 ⚠️
   - 肥胖 ⚠️
   - 缺乏运动 ⚠️

2. **不可控因素**
   - 年龄（男>45岁，女>55岁）
   - 家族史
   - 性别

📋 **心血管健康管理**

**1️⃣ 核心指标控制**
- 血压：<140/90 mmHg（有糖尿病<130/80）
- 血糖：空腹<7.0，餐后<10.0
- 血脂：LDL-C<2.6（高危人群<1.8）

**2️⃣ 生活方式**
- 地中海饮食模式
- 每天30分钟有氧运动
- 保持乐观心态
- 充足睡眠（7-8小时）

**3️⃣ 定期检查**
- 每年体检
- 心电图检查
- 颈动脉超声（50岁以上）
- 冠脉CT（有症状者）

⚠️ **心梗预警信号**
以下症状需立即拨打120：
- 持续胸痛（>15分钟）
- 胸闷、压迫感
- 疼痛放射至左臂、下颌
- 伴大汗、恶心
- 休息不能缓解

🆘 **急救要点**
1. 立即停止活动，就地休息
2. 舌下含服硝酸甘油
3. 嚼服阿司匹林300mg
4. 拨打120
"""
        
        return self.create_response(
            content=analysis,
            emotion=EmotionState.SERIOUS,
            metadata={"type": "cardiovascular_analysis"}
        )
    
    def _medication_guidance(self, text: str, memory: AgentMemory) -> AgentMessage:
        """用药指导"""
        guidance = """💊 **慢病用药指导**

📋 **用药基本原则**

**1️⃣ 按时服药**
- 设置用药提醒
- 固定服药时间
- 不要漏服

**2️⃣ 按量服药**
- 严格遵医嘱
- 不自行增减剂量
- 使用药盒分装

**3️⃣ 规律复诊**
- 定期复查指标
- 及时调整方案
- 汇报副作用

📌 **常见慢病药物服用提示**

**降压药**
- 长效药物每天1次，早晨服用
- 不要突然停药
- 监测血压调整剂量

**降糖药**
- 磺脲类：餐前30分钟
- 二甲双胍：随餐或餐后
- α-糖苷酶抑制剂：第一口饭嚼服
- 胰岛素：注意保存和注射方法

**降脂药**
- 他汀类：通常晚上服用
- 定期监测肝功能
- 注意肌肉酸痛症状

**阿司匹林**
- 肠溶片：空腹服用
- 注意出血倾向
- 胃病患者慎用

⚠️ **用药安全提醒**
- 不要自行购买处方药
- 不要轻信偏方秘方
- 药物相互作用需咨询药师
- 出现不适及时就医

您有具体的用药问题想咨询吗？"""
        
        return self.create_response(
            content=guidance,
            emotion=EmotionState.CARING,
            metadata={"type": "medication_guidance"}
        )
    
    def _general_chronic_advice(self, memory: AgentMemory) -> AgentMessage:
        """一般慢病建议"""
        advice = """🏥 **慢性病综合管理建议**

作为慢病专家，我建议您重点关注以下几个方面：

**📊 定期监测**
- 每天测量血压（早晚各1次）
- 定期监测血糖（按医嘱）
- 每3-6个月检查血脂

**💊 规范用药**
- 按医嘱按时服药
- 不要自行停药或换药
- 定期复诊调整方案

**🥗 健康饮食**
- 低盐低脂低糖
- 多吃蔬菜粗粮
- 控制总热量

**🏃 适度运动**
- 每周150分钟中等强度运动
- 推荐：快走、游泳、太极
- 量力而行，循序渐进

**😊 心态调节**
- 保持乐观心态
- 避免情绪激动
- 学会压力管理

有什么具体问题想深入了解吗？我可以为您详细分析。"""
        
        return self.create_response(
            content=advice,
            emotion=EmotionState.ENCOURAGING,
            metadata={"type": "general_chronic_advice"}
        )
    
    def _get_bp_grade(self, systolic: int, diastolic: int) -> str:
        """获取血压分级"""
        if systolic >= 180 or diastolic >= 110:
            return "3级高血压（重度）"
        elif systolic >= 160 or diastolic >= 100:
            return "2级高血压（中度）"
        elif systolic >= 140 or diastolic >= 90:
            return "1级高血压（轻度）"
        elif systolic >= 120 or diastolic >= 80:
            return "正常高值"
        else:
            return "正常血压"
    
    def assess_risk_level(
        self,
        bp_data: Dict = None,
        glucose_data: Dict = None,
        lipid_data: Dict = None
    ) -> Dict[str, Any]:
        """
        综合风险评估
        
        Returns:
            风险评估结果
        """
        risk_factors = []
        risk_level = "低风险"
        risk_score = 0
        
        # 评估血压
        if bp_data:
            systolic = bp_data.get("systolic", 0)
            diastolic = bp_data.get("diastolic", 0)
            if systolic >= 140 or diastolic >= 90:
                risk_factors.append("高血压")
                risk_score += 2
        
        # 评估血糖
        if glucose_data:
            fasting = glucose_data.get("fasting", 0)
            if fasting >= 7.0:
                risk_factors.append("糖尿病")
                risk_score += 2
            elif fasting >= 6.1:
                risk_factors.append("糖耐量受损")
                risk_score += 1
        
        # 评估血脂
        if lipid_data:
            ldl = lipid_data.get("ldl", 0)
            if ldl >= 4.1:
                risk_factors.append("血脂异常")
                risk_score += 2
            elif ldl >= 3.4:
                risk_factors.append("血脂边缘升高")
                risk_score += 1
        
        # 确定风险等级
        if risk_score >= 5:
            risk_level = "高风险"
        elif risk_score >= 3:
            risk_level = "中高风险"
        elif risk_score >= 1:
            risk_level = "中风险"
        
        return {
            "risk_level": risk_level,
            "risk_score": risk_score,
            "risk_factors": risk_factors,
            "recommendations": self._get_risk_recommendations(risk_factors)
        }
    
    def _get_risk_recommendations(self, risk_factors: List[str]) -> List[str]:
        """根据风险因素生成建议"""
        recommendations = []
        
        if "高血压" in risk_factors:
            recommendations.append("建议加强血压监测，规范用药")
        if "糖尿病" in risk_factors:
            recommendations.append("严格控制饮食，按时服用降糖药")
        if "血脂异常" in risk_factors:
            recommendations.append("低脂饮食，考虑他汀类药物治疗")
        
        if not recommendations:
            recommendations.append("保持健康生活方式，定期体检")
        
        return recommendations
