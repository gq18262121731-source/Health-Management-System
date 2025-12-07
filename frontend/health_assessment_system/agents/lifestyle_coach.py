"""
生活方式教练智能体
==================

提供运动、睡眠、饮食等生活方式指导。
"""

import random
from typing import Dict, List, Optional
from datetime import datetime

from .base_agent import (
    BaseAgent, AgentRole, AgentMessage, AgentMemory,
    MessageType, EmotionState
)


class LifestyleCoachAgent(BaseAgent):
    """
    生活方式教练智能体
    
    专业能力：
    - 运动方案制定与指导
    - 睡眠质量改善建议
    - 营养膳食指导
    - 健康习惯培养
    """
    
    def __init__(self, name: str = "生活教练"):
        super().__init__(
            name=name,
            role=AgentRole.LIFESTYLE_COACH,
            description="专业的生活方式指导教练，帮助您养成健康好习惯",
            avatar="🏃",
            personality="热情、激励、专业"
        )
        
        self.capabilities = [
            "运动指导",
            "睡眠改善",
            "饮食建议",
            "体重管理",
            "习惯培养",
            "压力管理"
        ]
        
        # 激励语
        self.motivations = [
            "每一步都算数，坚持就是胜利！",
            "健康是最好的投资，您正在为未来储蓄！",
            "今天的汗水，是明天的健康！",
            "小改变，大不同，一步一步来！",
            "您的坚持，身体看得见！"
        ]
    
    def process(self, message: AgentMessage, memory: AgentMemory) -> AgentMessage:
        """处理消息"""
        user_text = message.content.strip()
        keywords = self.extract_keywords(user_text)
        
        # 根据关键词分发处理
        if any(k in keywords for k in ["运动", "锻炼", "步数", "走路", "跑步"]):
            return self._exercise_guidance(user_text, memory)
        elif any(k in keywords for k in ["睡眠", "失眠", "睡不着", "熬夜", "早起"]):
            return self._sleep_guidance(user_text, memory)
        elif any(k in keywords for k in ["饮食", "吃", "喝", "食物", "营养"]):
            return self._diet_guidance(user_text, memory)
        elif any(k in keywords for k in ["体重", "减肥", "瘦", "胖"]):
            return self._weight_management(user_text, memory)
        elif any(k in keywords for k in ["压力", "放松", "疲劳", "累"]):
            return self._stress_management(user_text, memory)
        else:
            return self._general_lifestyle_advice(memory)
    
    def can_handle(self, message: AgentMessage, context: Dict) -> float:
        """判断处理能力"""
        keywords = self.extract_keywords(message.content)
        
        lifestyle_keywords = [
            "运动", "锻炼", "步数", "走路", "跑步", "游泳",
            "睡眠", "失眠", "睡不着", "熬夜", "早起",
            "饮食", "吃", "喝", "食物", "营养", "蔬菜", "水果",
            "体重", "减肥", "瘦", "胖",
            "压力", "放松", "疲劳", "累", "休息"
        ]
        
        matched = sum(1 for k in keywords if k in lifestyle_keywords)
        
        if matched >= 2:
            return 0.9
        elif matched == 1:
            return 0.75
        else:
            return 0.2
    
    def _exercise_guidance(self, text: str, memory: AgentMemory) -> AgentMessage:
        """运动指导"""
        # 获取用户运动数据
        exercise_data = memory.get_context("exercise_data", {})
        
        guidance = """🏃 **运动指导方案**

📊 **运动目标设定**

对于老年朋友，我推荐以下运动目标：
- 每天步行 **6000-8000步**
- 每周累计 **150分钟** 中等强度运动
- 每天至少 **30分钟** 活动时间

📋 **个性化运动方案**

**🌅 晨间运动（6:30-8:00）**
1. 起床后喝杯温水
2. 简单拉伸5分钟
3. 太极拳或八段锦15-20分钟
4. 或者小区散步20分钟

**☀️ 上午活动（9:00-11:00）**
- 去公园走走，呼吸新鲜空气
- 和老朋友打打门球、羽毛球
- 做做园艺活动

**🌇 傍晚运动（16:00-18:00）**
- 最佳运动时间
- 快走30-40分钟
- 广场舞或健身操

📌 **运动安全提示**

1️⃣ **运动前**
- 做好热身活动（5-10分钟）
- 检查血压是否正常
- 不要空腹运动

2️⃣ **运动中**
- 注意呼吸节奏
- 保持心率在适当范围
- 感觉不适立即停止

3️⃣ **运动后**
- 做好放松拉伸
- 及时补充水分
- 休息恢复

⚠️ **特别注意**
- 天气极端时减少户外运动
- 饭后1小时再运动
- 量力而行，循序渐进

"""
        motivation = random.choice(self.motivations)
        guidance += f"\n💪 {motivation}"
        
        return self.create_response(
            content=guidance,
            emotion=EmotionState.ENCOURAGING,
            metadata={"type": "exercise_guidance"}
        )
    
    def _sleep_guidance(self, text: str, memory: AgentMemory) -> AgentMessage:
        """睡眠指导"""
        guidance = """😴 **睡眠改善方案**

📊 **健康睡眠目标**
- 每晚睡眠 **7-8小时**
- 入睡时间在 **22:00-23:00**
- 睡眠质量好，少做梦、少醒

📋 **睡眠改善计划**

**🌙 睡前准备（睡前1-2小时）**

1. **远离电子产品**
   - 蓝光会抑制褪黑素分泌
   - 建议睡前1小时放下手机

2. **营造睡眠氛围**
   - 灯光调暗
   - 保持安静
   - 温度适宜（18-22℃）

3. **放松身心**
   - 热水泡脚15分钟
   - 听轻柔音乐
   - 做几个深呼吸

**🛏️ 睡眠环境优化**

- 床铺舒适，软硬适中
- 枕头高度合适（一拳高）
- 被褥透气保暖
- 保持卧室整洁

**☕ 饮食调整**

✅ 建议：
- 晚餐7分饱，睡前3小时不进食
- 睡前可喝杯温牛奶
- 吃些助眠食物：小米、香蕉、核桃

❌ 避免：
- 睡前喝茶、咖啡
- 晚餐过于油腻
- 睡前大量饮水

**🧘 放松技巧**

1. **腹式呼吸**
   - 鼻吸气4秒，腹部隆起
   - 屏息2秒
   - 口呼气6秒，腹部收缩
   - 重复10次

2. **身体扫描放松**
   - 从脚趾开始，逐步放松到头部
   - 每个部位放松5秒

**📅 作息时间表建议**

| 时间 | 活动 |
|------|------|
| 6:30 | 起床，拉伸 |
| 7:00 | 早餐 |
| 12:00 | 午餐 |
| 13:00 | 午休（不超过30分钟）|
| 18:00 | 晚餐 |
| 21:00 | 放松活动 |
| 22:30 | 准备入睡 |
| 23:00 | 熄灯睡觉 |

💡 **温馨提示**
- 坚持固定作息，让身体形成生物钟
- 白天适当运动，有助于夜间睡眠
- 午睡不要太长，以免影响晚上
- 如果长期失眠，建议就医检查

祝您今晚好梦！🌙"""
        
        return self.create_response(
            content=guidance,
            emotion=EmotionState.CARING,
            metadata={"type": "sleep_guidance"}
        )
    
    def _diet_guidance(self, text: str, memory: AgentMemory) -> AgentMessage:
        """饮食指导"""
        guidance = """🥗 **健康饮食指南**

📊 **营养目标**
- 每日热量：约1800-2000千卡
- 蛋白质：每公斤体重1.0-1.2克
- 膳食纤维：25-30克/天
- 饮水：1500-2000ml/天

📋 **饮食原则**

**1️⃣ 食物多样化**

每天应包含：
- 🌾 谷薯类：250-400克
- 🥬 蔬菜：300-500克
- 🍎 水果：200-350克
- 🥩 肉蛋：120-200克
- 🥛 奶类：300克
- 🫘 豆类：25克

**2️⃣ 三减三健**

🚫 **减盐**
- 每天<6克（约1啤酒瓶盖）
- 少吃腌制食品
- 用醋、柠檬代替部分盐

🚫 **减油**
- 每天25-30克（约3白瓷勺）
- 少煎炸，多蒸煮
- 选用植物油

🚫 **减糖**
- 每天<25克
- 少喝含糖饮料
- 水果不要吃太多

**3️⃣ 一日三餐安排**

🌅 **早餐（7:00-8:00）**
建议：
- 全麦馒头/燕麦粥
- 鸡蛋1个
- 牛奶200ml
- 小份蔬菜

☀️ **午餐（11:30-12:30）**
建议：
- 杂粮饭1碗
- 瘦肉/鱼虾100克
- 蔬菜200克
- 豆腐/豆制品

🌙 **晚餐（17:30-18:30）**
建议：
- 米饭半碗或粥
- 蔬菜为主
- 少量肉类
- 7分饱即可

**4️⃣ 特殊人群饮食提示**

💊 **高血压**
- 限盐是关键
- 多吃高钾食物：香蕉、土豆、菠菜

🍬 **糖尿病**
- 控制主食量
- 选择低GI食物
- 避免精制糖

🫀 **高血脂**
- 减少动物脂肪
- 多吃深海鱼
- 增加膳食纤维

**5️⃣ 推荐健康食物**

| 类别 | 推荐食物 |
|------|---------|
| 主食 | 燕麦、糙米、红薯 |
| 蔬菜 | 西兰花、菠菜、番茄 |
| 水果 | 苹果、橙子、蓝莓 |
| 蛋白 | 鱼、鸡胸肉、豆腐 |
| 坚果 | 核桃、杏仁（每天一小把）|

📌 **实用小技巧**
- 先喝汤后吃饭，容易控制食量
- 细嚼慢咽，每口咀嚼20次
- 用小碗小盘，控制份量
- 专心吃饭，不要边看电视边吃

吃好每一餐，健康每一天！🌟"""
        
        return self.create_response(
            content=guidance,
            emotion=EmotionState.ENCOURAGING,
            metadata={"type": "diet_guidance"}
        )
    
    def _weight_management(self, text: str, memory: AgentMemory) -> AgentMessage:
        """体重管理"""
        guidance = """⚖️ **体重管理方案**

📊 **健康体重标准**

**BMI计算**：体重(kg) ÷ 身高(m)²

| BMI | 状态 |
|-----|------|
| <18.5 | 偏瘦 |
| 18.5-24 | 正常 ✅ |
| 24-28 | 超重 |
| >28 | 肥胖 |

**腰围标准**
- 男性：<90cm
- 女性：<85cm

📋 **科学减重方案**

**1️⃣ 目标设定**
- 每周减重0.5-1公斤为宜
- 不要追求快速减重
- 持之以恒最重要

**2️⃣ 饮食控制**

🚫 减少：
- 主食减少1/4
- 油炸食品
- 甜食、饮料
- 夜宵

✅ 增加：
- 蔬菜（餐前先吃）
- 优质蛋白（鱼、鸡胸肉）
- 水（餐前喝一杯）

**3️⃣ 运动增加**

每周运动计划：
- 有氧运动：快走/游泳 150分钟
- 力量训练：2次（简单器械）
- 柔韧性：每天拉伸10分钟

**4️⃣ 行为改变**
- 记录饮食日记
- 定期称重（每周1次）
- 寻找运动伙伴
- 设立小目标和奖励

⚠️ **注意事项**
- 老年人减重要更加谨慎
- 不建议使用减肥药物
- 保证营养均衡
- 如有慢病，先咨询医生

💪 坚持就是胜利，您可以的！"""
        
        return self.create_response(
            content=guidance,
            emotion=EmotionState.ENCOURAGING,
            metadata={"type": "weight_management"}
        )
    
    def _stress_management(self, text: str, memory: AgentMemory) -> AgentMessage:
        """压力管理"""
        guidance = """🧘 **压力管理与放松指南**

📊 **认识压力**

适度的压力是正常的，但长期高压力会影响：
- 睡眠质量
- 血压血糖
- 免疫功能
- 情绪状态

📋 **减压方法**

**1️⃣ 呼吸放松法**

**4-7-8呼吸法：**
1. 用鼻子吸气4秒
2. 屏住呼吸7秒
3. 用嘴呼气8秒
4. 重复4-6次

**2️⃣ 身心放松活动**

- 🧘 太极拳、八段锦
- 🎵 听轻音乐、戏曲
- 🎨 书法、绘画
- 🌳 园艺、养花
- 🐦 养鸟、观鸟
- ♟️ 下棋、打牌

**3️⃣ 社交活动**
- 和老朋友聚会聊天
- 参加社区活动
- 与家人视频通话
- 加入兴趣小组

**4️⃣ 正念冥想**

每天花10分钟：
1. 找一个安静的地方坐下
2. 闭上眼睛
3. 专注于呼吸
4. 觉察当下的感受
5. 不评判，只是观察

**5️⃣ 规律作息**
- 固定的起床和睡眠时间
- 保证充足睡眠
- 适度午休

📌 **日常减压小技巧**

- 到户外晒晒太阳
- 听几首喜欢的歌
- 和宠物玩耍
- 看看搞笑视频
- 泡个热水澡
- 做点自己喜欢的事

💭 **心理小贴士**
- 接受不完美的自己
- 活在当下，不过分忧虑未来
- 学会说"不"，不要过度承担
- 遇到困难向家人朋友倾诉

放松心情，享受生活！😊"""
        
        return self.create_response(
            content=guidance,
            emotion=EmotionState.CARING,
            metadata={"type": "stress_management"}
        )
    
    def _general_lifestyle_advice(self, memory: AgentMemory) -> AgentMessage:
        """一般生活方式建议"""
        advice = f"""🌟 **健康生活方式建议**

作为您的生活方式教练，我建议您从以下几方面入手：

**🏃 运动方面**
- 每天步行6000步以上
- 选择适合自己的运动方式
- 运动要循序渐进

**😴 睡眠方面**
- 每晚睡7-8小时
- 规律作息，定时入睡
- 创造良好的睡眠环境

**🥗 饮食方面**
- 清淡饮食，少盐少油
- 多吃蔬菜水果
- 定时定量，细嚼慢咽

**🧘 心态方面**
- 保持乐观积极
- 培养兴趣爱好
- 多与家人朋友交流

💪 {random.choice(self.motivations)}

您想详细了解哪方面的内容？"""
        
        return self.create_response(
            content=advice,
            emotion=EmotionState.ENCOURAGING,
            metadata={"type": "general_lifestyle"}
        )
    
    def create_weekly_plan(self, memory: AgentMemory) -> Dict:
        """创建一周健康计划"""
        plan = {
            "week_goal": "养成每天运动30分钟、规律作息的好习惯",
            "daily_plans": []
        }
        
        days = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
        
        for i, day in enumerate(days):
            daily = {
                "day": day,
                "morning": "6:30起床，拉伸5分钟",
                "exercise": "快走30分钟或太极拳20分钟",
                "meals": {
                    "breakfast": "全麦馒头+鸡蛋+牛奶",
                    "lunch": "杂粮饭+蔬菜+瘦肉",
                    "dinner": "粥/面+蔬菜（7分饱）"
                },
                "evening": "21:00放松活动，22:30准备入睡",
                "reminder": "记得测量血压并记录"
            }
            
            # 周末安排稍有不同
            if i >= 5:
                daily["exercise"] = "上午逛公园或和朋友活动"
                daily["reminder"] = "周末适当放松，但不要打乱作息"
            
            plan["daily_plans"].append(daily)
        
        return plan
