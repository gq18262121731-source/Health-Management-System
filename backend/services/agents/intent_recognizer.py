"""
意图识别模块
============

三层混合意图识别系统：
1. 规则匹配（快速）
2. 语义匹配（理解同义表达）
3. LLM 兆底（最准）
"""

import re
import logging
from enum import Enum
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


class IntentType(Enum):
    """意图类型枚举"""
    # 健康咨询类
    HEALTH_QUERY = "health_query"              # 一般健康问题
    SYMPTOM_REPORT = "symptom_report"          # 症状报告
    DATA_INTERPRET = "data_interpret"          # 数据解读
    
    # 慢病管理类
    BLOOD_PRESSURE = "blood_pressure"          # 血压相关
    BLOOD_SUGAR = "blood_sugar"                # 血糖相关
    BLOOD_LIPID = "blood_lipid"                # 血脂相关
    HEART_DISEASE = "heart_disease"            # 心脏相关
    MEDICATION = "medication"                  # 用药相关
    
    # 生活方式类
    EXERCISE = "exercise"                      # 运动锻炼
    DIET = "diet"                              # 饮食营养
    SLEEP = "sleep"                            # 睡眠问题
    WEIGHT = "weight"                          # 体重管理
    
    # 情绪心理类
    ANXIETY = "anxiety"                        # 焦虑担忧
    LONELINESS = "loneliness"                  # 孤独寂寞
    DEPRESSION = "depression"                  # 情绪低落
    STRESS = "stress"                          # 压力疲惫
    POSITIVE_EMOTION = "positive_emotion"      # 积极情绪
    
    # 交互类
    GREETING = "greeting"                      # 问候
    THANKS = "thanks"                          # 感谢
    GOODBYE = "goodbye"                        # 告别
    CHITCHAT = "chitchat"                      # 闲聊
    
    # ========== 语音控制类 ==========
    CONTROL_NAVIGATE = "control_navigate"      # 导航控制（去某页面）
    CONTROL_QUERY = "control_query"            # 查询控制（查看数据）
    CONTROL_REMINDER = "control_reminder"      # 提醒控制（设置/取消提醒）
    CONTROL_STOP = "control_stop"              # 停止控制
    
    # 以下功能暂未实现，保留用于扩展
    # CONTROL_CALL = "control_call"            # 通话控制（需要电话系统）
    # CONTROL_DEVICE = "control_device"        # 设备控制（需要蓝牙）
    # CONTROL_PLAY = "control_play"            # 播放控制（需要媒体播放器）
    # CONTROL_VOLUME = "control_volume"        # 音量控制（需要系统权限）
    
    # 其他
    EMERGENCY = "emergency"                    # 紧急情况
    UNKNOWN = "unknown"                        # 未知意图


@dataclass
class IntentResult:
    """意图识别结果"""
    intent: IntentType
    confidence: float
    sub_intents: List[IntentType]  # 可能的次要意图
    entities: Dict[str, str]       # 提取的实体（如数值、时间等）
    requires_multi_agent: bool     # 是否需要多智能体协作
    
    def to_dict(self) -> dict:
        return {
            "intent": self.intent.value,
            "confidence": self.confidence,
            "sub_intents": [i.value for i in self.sub_intents],
            "entities": self.entities,
            "requires_multi_agent": self.requires_multi_agent
        }


class IntentRecognizer:
    """
    意图识别器
    
    三层混合策略：
    1. 规则匹配（快速，精确关键词）
    2. 语义匹配（理解同义表达，如"走路少"→运动）
    3. LLM 兜底（复杂/模糊情况）
    """
    
    def __init__(self):
        # 语义匹配器（延迟加载）
        self.semantic_matcher = None
        self._init_semantic_matcher()
        # 意图关键词规则库
        self.intent_rules: Dict[IntentType, List[str]] = {
            # 慢病管理
            IntentType.BLOOD_PRESSURE: [
                "血压", "高血压", "低血压", "降压", "收缩压", "舒张压", 
                "mmHg", "高压", "低压"
            ],
            IntentType.BLOOD_SUGAR: [
                "血糖", "糖尿病", "降糖", "胰岛素", "糖化", "空腹血糖",
                "餐后血糖", "低血糖", "高血糖"
            ],
            IntentType.BLOOD_LIPID: [
                "血脂", "胆固醇", "甘油三酯", "低密度", "高密度", "LDL", "HDL"
            ],
            IntentType.HEART_DISEASE: [
                "心脏", "心血管", "冠心病", "心梗", "心绞痛", "心律", "心悸",
                "胸闷", "胸痛", "心跳"
            ],
            IntentType.MEDICATION: [
                "吃药", "服药", "药物", "降压药", "降糖药", "用药", "停药",
                "副作用", "药效"
            ],
            
            # 生活方式
            IntentType.EXERCISE: [
                "运动", "锻炼", "健身", "走路", "散步", "太极", "游泳",
                "跑步", "活动量", "步数"
            ],
            IntentType.DIET: [
                "饮食", "吃什么", "食物", "营养", "蔬菜", "水果", "蛋白质",
                "热量", "卡路里", "忌口", "能吃", "不能吃"
            ],
            IntentType.SLEEP: [
                "睡眠", "失眠", "睡不着", "睡不好", "早醒", "多梦", "熬夜",
                "午睡", "睡眠质量"
            ],
            IntentType.WEIGHT: [
                "体重", "减肥", "肥胖", "瘦", "BMI", "超重", "增重"
            ],
            
            # 情绪心理
            IntentType.ANXIETY: [
                "担心", "害怕", "焦虑", "紧张", "烦躁", "不安", "恐惧"
            ],
            IntentType.LONELINESS: [
                "孤独", "寂寞", "没人", "一个人", "冷清", "想家"
            ],
            IntentType.DEPRESSION: [
                "难过", "伤心", "不开心", "郁闷", "烦", "没意思", "绝望"
            ],
            IntentType.STRESS: [
                "压力", "累", "疲惫", "撑不住", "坚持不下去", "喘不过气"
            ],
            IntentType.POSITIVE_EMOTION: [
                "开心", "高兴", "快乐", "幸福", "满足", "感谢"
            ],
            
            # 症状报告
            IntentType.SYMPTOM_REPORT: [
                "难受", "不舒服", "疼", "痛", "头晕", "头痛", "恶心",
                "呕吐", "发烧", "咳嗽", "乏力"
            ],
            
            # 数据解读
            IntentType.DATA_INTERPRET: [
                "数据", "指标", "报告", "结果", "正常吗", "高吗", "低吗",
                "偏高", "偏低", "什么意思"
            ],
            
            # 交互
            IntentType.GREETING: [
                "你好", "您好", "早上好", "晚上好", "下午好", "hi", "hello"
            ],
            IntentType.THANKS: [
                "谢谢", "感谢", "多谢", "太感谢"
            ],
            IntentType.GOODBYE: [
                "再见", "拜拜", "88", "下次见"
            ],
            
            # 紧急
            IntentType.EMERGENCY: [
                "急救", "120", "晕倒", "昏迷", "抽搐", "大出血", "呼吸困难",
                "胸痛持续", "中风", "心梗",
                "救命", "帮帮我", "呼救", "紧急呼叫", "一键呼救", "求助", "SOS",
                "不舒服", "难受"
            ],
            
            # ========== 语音控制类 ==========
            # 导航控制
            IntentType.CONTROL_NAVIGATE: [
                "打开", "去", "进入", "跳转", "切换到", "返回",
                "首页", "主页", "健康页", "设置", "个人中心", "消息",
                "返回上一页", "回到首页", "打开报告", "看报告", "健康报告"
            ],
            # 查询控制
            IntentType.CONTROL_QUERY: [
                "查看", "查一下", "看看", "显示", "告诉我",
                "今天的", "最近的", "我的数据", "健康数据", "血压记录", "血糖记录",
                "历史数据", "数据记录", "查数据"
            ],
            # 提醒控制
            IntentType.CONTROL_REMINDER: [
                "提醒我", "设置提醒", "设个闹钟", "取消提醒", "删除提醒",
                "吃药提醒", "测量提醒", "定时", "几点提醒"
            ],
            # 停止控制
            IntentType.CONTROL_STOP: [
                "停止", "暂停", "停", "别说了", "闭嘴", "安静",
                "取消", "算了", "不要了"
            ],
        }
        
        # 数值提取正则
        self.entity_patterns = {
            "blood_pressure": r"(\d{2,3})[/／](\d{2,3})",  # 120/80
            "blood_sugar": r"血糖[是为]?(\d+\.?\d*)",       # 血糖6.5
            "heart_rate": r"心率[是为]?(\d+)",              # 心率80
            "weight": r"体重[是为]?(\d+\.?\d*)",            # 体重65
            "temperature": r"体温[是为]?(\d+\.?\d*)",       # 体温37.5
            "number": r"(\d+\.?\d*)",                       # 通用数值
        }
    
    def recognize(self, text: str, use_llm: bool = False) -> IntentResult:
        """
        识别用户意图
        
        Args:
            text: 用户输入文本
            use_llm: 是否在置信度低时调用LLM
            
        Returns:
            IntentResult 意图识别结果
        """
        text = text.strip().lower()
        
        if not text:
            return IntentResult(
                intent=IntentType.UNKNOWN,
                confidence=0.0,
                sub_intents=[],
                entities={},
                requires_multi_agent=False
            )
        
        # 1. 规则匹配
        matched_intents = self._rule_match(text)
        
        # 2. 提取实体
        entities = self._extract_entities(text)
        
        # 3. 确定主意图和置信度
        if not matched_intents:
            primary_intent = IntentType.UNKNOWN
            confidence = 0.3
        elif len(matched_intents) == 1:
            primary_intent = matched_intents[0][0]
            confidence = matched_intents[0][1]
        else:
            # 多个匹配，取置信度最高的
            matched_intents.sort(key=lambda x: x[1], reverse=True)
            primary_intent = matched_intents[0][0]
            confidence = matched_intents[0][1]
        
        # 4. 判断是否需要多智能体协作
        requires_multi_agent = len(matched_intents) >= 2 and matched_intents[1][1] >= 0.6
        
        # 5. 如果置信度低，尝试语义匹配
        if confidence < 0.7 and self.semantic_matcher:
            semantic_result = self._semantic_match(text)
            if semantic_result and semantic_result[1] > confidence:
                primary_intent = semantic_result[0]
                confidence = semantic_result[1]
                logger.info(f"🧠 语义匹配提升: {primary_intent.value} ({confidence:.2f})")
        
        # 6. 如果仍然置信度低且允许，调用LLM
        if use_llm and confidence < 0.6:
            llm_result = self._llm_recognize(text)
            if llm_result and llm_result[1] > confidence:
                primary_intent = llm_result[0]
                confidence = llm_result[1]
        
        return IntentResult(
            intent=primary_intent,
            confidence=confidence,
            sub_intents=[m[0] for m in matched_intents[1:3]],
            entities=entities,
            requires_multi_agent=requires_multi_agent
        )
    
    def _rule_match(self, text: str) -> List[Tuple[IntentType, float]]:
        """规则匹配（控制命令优先）"""
        matches = []
        
        # 控制动词列表（用于提升控制命令的优先级）
        control_verbs = ["打开", "去", "进入", "跳转", "返回", "查看", "看看", 
                         "提醒", "设置", "取消", "打给", "拨打", "联系",
                         "测量", "测一下", "量一下", "播放", "放",
                         "大声", "小声", "调大", "调小", "停止", "暂停"]
        
        has_control_verb = any(v in text for v in control_verbs)
        
        for intent, keywords in self.intent_rules.items():
            match_count = sum(1 for kw in keywords if kw in text)
            if match_count > 0:
                # 基础置信度
                confidence = min(0.5 + match_count * 0.15, 0.95)
                
                # 如果存在控制动词，提升控制类意图的置信度
                if has_control_verb and intent.value.startswith("control_"):
                    confidence = min(confidence + 0.2, 0.98)
                
                matches.append((intent, confidence))
        
        return matches
    
    def _extract_entities(self, text: str) -> Dict[str, str]:
        """提取实体"""
        entities = {}
        
        for entity_name, pattern in self.entity_patterns.items():
            match = re.search(pattern, text)
            if match:
                if entity_name == "blood_pressure":
                    entities["systolic"] = match.group(1)
                    entities["diastolic"] = match.group(2)
                else:
                    entities[entity_name] = match.group(1)
        
        return entities
    
    def _init_semantic_matcher(self):
        """初始化语义匹配器（禁用，避免HuggingFace下载问题）"""
        # 禁用语义匹配器，使用规则匹配 + LLM 兜底
        self.semantic_matcher = None
        logger.info("ℹ️ 语义匹配已禁用，使用规则匹配 + LLM")
    
    def _semantic_match(self, text: str) -> Optional[Tuple[IntentType, float]]:
        """使用语义匹配识别意图"""
        if not self.semantic_matcher:
            return None
        
        try:
            result = self.semantic_matcher.match_best(text)
            if result and result.confidence >= 0.5:
                # 将字符串意图转换为 IntentType
                intent_str = result.intent
                for intent_type in IntentType:
                    if intent_type.value == intent_str:
                        return (intent_type, result.confidence)
            return None
        except Exception as e:
            logger.error(f"语义匹配失败: {e}")
            return None
    
    def _llm_recognize(self, text: str) -> Optional[Tuple[IntentType, float]]:
        """调用LLM识别意图（基础版）"""
        result = self._llm_recognize_advanced(text)
        if result:
            return (result["intent"], result["confidence"])
        return None
    
    def _llm_recognize_advanced(self, text: str) -> Optional[Dict]:
        """
        高级LLM意图识别
        
        返回：
        - intent: 主意图
        - confidence: 置信度
        - sub_intents: 次要意图列表
        - entities: 提取的实体
        - reasoning: 推理过程
        """
        try:
            from services.spark_service import spark_service
            import json
            
            prompt = f"""你是一个专业的健康助手意图识别系统。请分析用户输入，识别意图并提取关键信息。

【用户输入】
{text}

【意图类别说明】
1. 慢病管理类：
   - blood_pressure: 血压相关（高血压、低血压、血压数值）
   - blood_sugar: 血糖相关（糖尿病、血糖数值）
   - blood_lipid: 血脂相关（胆固醇、甘油三酯）
   - heart_disease: 心脏相关（心悸、胸闷、心律不齐）
   - medication: 用药相关（吃药、药物副作用）

2. 生活方式类：
   - exercise: 运动锻炼（走路、健身、活动量）
   - diet: 饮食营养（吃什么、忌口、营养）
   - sleep: 睡眠问题（失眠、睡不好、早醒）
   - weight: 体重管理（减肥、超重）

3. 情绪心理类：
   - anxiety: 焦虑担忧（害怕、紧张、担心）
   - loneliness: 孤独寂寞（一个人、没人陪）
   - depression: 情绪低落（难过、不开心）
   - stress: 压力疲惫（累、撑不住）
   - positive_emotion: 积极情绪（开心、感谢）

4. 健康咨询类：
   - symptom_report: 症状报告（不舒服、疼痛、头晕）
   - data_interpret: 数据解读（指标、报告、正常吗）
   - health_query: 一般健康问题

5. 交互类：
   - greeting: 问候
   - thanks: 感谢
   - goodbye: 告别
   - chitchat: 闲聊

6. 特殊类：
   - emergency: 紧急情况（急救、晕倒、胸痛持续）
   - unknown: 无法识别

【输出格式】
请严格按照以下JSON格式输出：
{{
    "intent": "主意图类别名称",
    "confidence": 0.0-1.0之间的置信度,
    "sub_intents": ["次要意图1", "次要意图2"],
    "entities": {{
        "数值类型": "数值",
        "症状": "症状描述"
    }},
    "reasoning": "简短的推理说明"
}}

【示例】
输入："我血压150/95，有点头晕，是不是太高了"
输出：
{{
    "intent": "blood_pressure",
    "confidence": 0.95,
    "sub_intents": ["symptom_report", "data_interpret"],
    "entities": {{
        "systolic": "150",
        "diastolic": "95",
        "symptom": "头晕"
    }},
    "reasoning": "用户提供了具体血压数值150/95，并询问是否偏高，同时伴有头晕症状"
}}

请分析并输出JSON："""

            response = spark_service.chat(
                user_input=prompt,
                system_prompt="你是一个精准的意图识别系统，只输出JSON格式结果，不要其他内容。",
                temperature=0.2,
                max_tokens=300
            )
            
            # 解析JSON
            result = self._parse_llm_response(response)
            if result:
                logger.info(f"🤖 LLM意图识别: {result['intent']} ({result['confidence']:.2f}) - {result.get('reasoning', '')}")
                return result
            
            return None
            
        except Exception as e:
            logger.error(f"LLM意图识别失败: {e}")
            return None
    
    def _parse_llm_response(self, response: str) -> Optional[Dict]:
        """解析LLM返回的JSON"""
        import json
        import re
        
        try:
            # 尝试直接解析
            result = json.loads(response)
        except:
            # 尝试提取JSON部分
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                try:
                    result = json.loads(json_match.group())
                except:
                    return None
            else:
                return None
        
        # 验证并转换意图
        intent_str = result.get("intent", "unknown")
        intent_type = IntentType.UNKNOWN
        
        for it in IntentType:
            if it.value == intent_str:
                intent_type = it
                break
        
        # 转换次要意图
        sub_intents = []
        for sub in result.get("sub_intents", []):
            for it in IntentType:
                if it.value == sub:
                    sub_intents.append(it)
                    break
        
        return {
            "intent": intent_type,
            "confidence": min(max(float(result.get("confidence", 0.7)), 0.0), 1.0),
            "sub_intents": sub_intents,
            "entities": result.get("entities", {}),
            "reasoning": result.get("reasoning", "")
        }
    
    def recognize_with_llm(self, text: str) -> IntentResult:
        """
        使用LLM进行完整意图识别（推荐用于复杂输入）
        
        与 recognize() 的区别：
        - recognize(): 规则优先，LLM兜底
        - recognize_with_llm(): LLM优先，更准确但更慢
        """
        text = text.strip()
        
        if not text:
            return IntentResult(
                intent=IntentType.UNKNOWN,
                confidence=0.0,
                sub_intents=[],
                entities={},
                requires_multi_agent=False
            )
        
        # 1. 先用规则快速提取实体
        entities = self._extract_entities(text)
        
        # 2. 调用LLM识别
        llm_result = self._llm_recognize_advanced(text)
        
        if llm_result:
            # 合并实体
            merged_entities = {**entities, **llm_result.get("entities", {})}
            
            # 判断是否需要多智能体
            requires_multi = len(llm_result.get("sub_intents", [])) >= 1
            
            return IntentResult(
                intent=llm_result["intent"],
                confidence=llm_result["confidence"],
                sub_intents=llm_result.get("sub_intents", []),
                entities=merged_entities,
                requires_multi_agent=requires_multi
            )
        
        # LLM失败，回退到规则匹配
        return self.recognize(text, use_llm=False)
    
    def get_agent_for_intent(self, intent: IntentType) -> str:
        """根据意图返回推荐的智能体"""
        agent_mapping = {
            # 慢病专家
            IntentType.BLOOD_PRESSURE: "chronic_expert",
            IntentType.BLOOD_SUGAR: "chronic_expert",
            IntentType.BLOOD_LIPID: "chronic_expert",
            IntentType.HEART_DISEASE: "chronic_expert",
            IntentType.MEDICATION: "chronic_expert",
            
            # 生活教练
            IntentType.EXERCISE: "lifestyle_coach",
            IntentType.DIET: "lifestyle_coach",
            IntentType.SLEEP: "lifestyle_coach",
            IntentType.WEIGHT: "lifestyle_coach",
            
            # 心理关怀师
            IntentType.ANXIETY: "emotional_care",
            IntentType.LONELINESS: "emotional_care",
            IntentType.DEPRESSION: "emotional_care",
            IntentType.STRESS: "emotional_care",
            IntentType.POSITIVE_EMOTION: "emotional_care",
            
            # 健康管家（默认）
            IntentType.GREETING: "health_butler",
            IntentType.THANKS: "health_butler",
            IntentType.GOODBYE: "health_butler",
            IntentType.CHITCHAT: "health_butler",
            IntentType.HEALTH_QUERY: "health_butler",
            IntentType.SYMPTOM_REPORT: "health_butler",
            IntentType.DATA_INTERPRET: "health_butler",
            IntentType.UNKNOWN: "health_butler",
            
            # 紧急情况
            IntentType.EMERGENCY: "health_butler",  # 先由健康管家提醒就医
        }
        
        return agent_mapping.get(intent, "health_butler")


# 单例实例
intent_recognizer = IntentRecognizer()
