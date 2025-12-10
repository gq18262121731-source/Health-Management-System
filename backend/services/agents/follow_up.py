"""
多轮追问模块
============

让智能体能够主动追问用户，获取更多信息以提供更准确的建议。
"""
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class FollowUpQuestion:
    """追问问题"""
    question: str           # 追问内容
    reason: str            # 追问原因
    priority: int          # 优先级 (1-5, 5最高)
    category: str          # 类别
    required_info: str     # 需要获取的信息


class FollowUpManager:
    """
    多轮追问管理器
    
    功能：
    1. 检测用户输入是否缺少关键信息
    2. 生成合适的追问问题
    3. 管理追问状态
    """
    
    def __init__(self):
        # 各类问题需要的关键信息
        self.required_info_rules = {
            "blood_pressure": {
                "required": ["数值"],
                "optional": ["测量时间", "症状", "用药情况"],
                "questions": {
                    "数值": "请问您的血压是多少呢？（如：130/85）",
                    "测量时间": "这是什么时候测的？早上还是晚上？",
                    "症状": "有没有头晕、头痛等不舒服？",
                    "用药情况": "目前有在吃降压药吗？"
                }
            },
            "blood_sugar": {
                "required": ["数值"],
                "optional": ["测量时间", "空腹/餐后", "用药情况"],
                "questions": {
                    "数值": "请问您的血糖是多少？",
                    "测量时间": "这是空腹测的还是餐后测的？",
                    "用药情况": "目前有在吃降糖药或打胰岛素吗？"
                }
            },
            "symptom_report": {
                "required": ["症状描述"],
                "optional": ["持续时间", "严重程度", "伴随症状"],
                "questions": {
                    "持续时间": "这种情况持续多久了？",
                    "严重程度": "严重吗？影响日常生活吗？",
                    "伴随症状": "还有其他不舒服吗？"
                }
            },
            "sleep": {
                "required": [],
                "optional": ["入睡时间", "睡眠时长", "睡眠质量"],
                "questions": {
                    "入睡时间": "您一般几点睡觉？",
                    "睡眠时长": "大概能睡几个小时？",
                    "睡眠质量": "睡眠质量怎么样？容易醒吗？"
                }
            },
            "diet": {
                "required": [],
                "optional": ["饮食习惯", "健康状况", "忌口"],
                "questions": {
                    "健康状况": "您有什么慢性病吗？比如高血压、糖尿病？",
                    "忌口": "有什么不能吃的吗？"
                }
            },
            "exercise": {
                "required": [],
                "optional": ["身体状况", "运动习惯", "年龄"],
                "questions": {
                    "身体状况": "您身体有什么不方便的地方吗？比如膝盖不好？",
                    "运动习惯": "平时有运动的习惯吗？"
                }
            },
            "anxiety": {
                "required": [],
                "optional": ["原因", "持续时间", "影响"],
                "questions": {
                    "原因": "是什么事情让您担心呢？",
                    "持续时间": "这种感觉持续多久了？",
                    "影响": "有影响到睡眠或食欲吗？"
                }
            },
            "depression": {
                "required": [],
                "optional": ["原因", "持续时间", "支持系统"],
                "questions": {
                    "原因": "发生什么事了吗？愿意说说吗？",
                    "支持系统": "家人朋友知道您的情况吗？"
                }
            }
        }
        
        # 追问状态缓存 {session_id: {asked_questions: [], pending_info: []}}
        self.session_states: Dict[str, Dict] = {}
    
    def analyze_missing_info(
        self, 
        user_input: str, 
        intent: str,
        entities: Dict,
        session_id: str = None
    ) -> Optional[FollowUpQuestion]:
        """
        分析用户输入，判断是否需要追问
        
        Args:
            user_input: 用户输入
            intent: 识别的意图
            entities: 提取的实体
            session_id: 会话ID
            
        Returns:
            需要追问时返回 FollowUpQuestion，否则返回 None
        """
        # 获取该意图的信息规则
        rules = self.required_info_rules.get(intent)
        if not rules:
            return None
        
        # 获取会话状态
        state = self._get_session_state(session_id)
        asked = state.get("asked_questions", [])
        
        # 检查必需信息
        for info in rules.get("required", []):
            if not self._has_info(info, user_input, entities) and info not in asked:
                question = rules["questions"].get(info)
                if question:
                    self._mark_asked(session_id, info)
                    return FollowUpQuestion(
                        question=question,
                        reason=f"缺少{info}",
                        priority=5,
                        category=intent,
                        required_info=info
                    )
        
        # 检查可选信息（只在首次交互时追问一个）
        if len(asked) < 2:  # 最多追问2次
            for info in rules.get("optional", []):
                if not self._has_info(info, user_input, entities) and info not in asked:
                    question = rules["questions"].get(info)
                    if question:
                        self._mark_asked(session_id, info)
                        return FollowUpQuestion(
                            question=question,
                            reason=f"补充{info}可提供更好建议",
                            priority=3,
                            category=intent,
                            required_info=info
                        )
        
        return None
    
    def _has_info(self, info_type: str, user_input: str, entities: Dict) -> bool:
        """检查是否已有某类信息"""
        info_keywords = {
            "数值": ["systolic", "diastolic", "blood_sugar", "number"],
            "测量时间": ["早上", "晚上", "上午", "下午", "刚才", "今天"],
            "症状": ["头晕", "头痛", "恶心", "难受", "不舒服"],
            "用药情况": ["吃药", "服药", "降压药", "降糖药", "胰岛素"],
            "持续时间": ["天", "周", "月", "小时", "一直", "最近"],
            "严重程度": ["严重", "厉害", "轻微", "一点点"],
            "空腹/餐后": ["空腹", "餐后", "饭前", "饭后"],
            "入睡时间": ["点睡", "点钟", "晚上"],
            "睡眠时长": ["小时", "个钟"],
            "原因": ["因为", "由于", "是因为"],
        }
        
        # 检查实体
        for key in info_keywords.get(info_type, []):
            if key in entities:
                return True
        
        # 检查文本
        keywords = info_keywords.get(info_type, [])
        for kw in keywords:
            if kw in user_input:
                return True
        
        return False
    
    def _get_session_state(self, session_id: str) -> Dict:
        """获取会话状态"""
        if not session_id:
            return {"asked_questions": []}
        
        if session_id not in self.session_states:
            self.session_states[session_id] = {"asked_questions": []}
        
        return self.session_states[session_id]
    
    def _mark_asked(self, session_id: str, info_type: str):
        """标记已追问"""
        if session_id:
            state = self._get_session_state(session_id)
            state["asked_questions"].append(info_type)
    
    def reset_session(self, session_id: str):
        """重置会话追问状态"""
        if session_id in self.session_states:
            del self.session_states[session_id]
    
    def generate_follow_up_prompt(self, question: FollowUpQuestion) -> str:
        """生成追问提示词片段"""
        return f"""
【追问提示】
在回答用户问题后，请自然地追问以下问题以获取更多信息：
追问：{question.question}
原因：{question.reason}

请将追问自然地融入回答中，不要生硬。例如：
"...另外，{question.question}"
或
"...对了，想问一下，{question.question}"
"""

    def should_follow_up(
        self,
        user_input: str,
        intent: str,
        entities: Dict,
        session_id: str = None
    ) -> Tuple[bool, Optional[str]]:
        """
        判断是否需要追问，返回追问提示
        
        Returns:
            (是否追问, 追问提示词)
        """
        question = self.analyze_missing_info(user_input, intent, entities, session_id)
        
        if question:
            prompt = self.generate_follow_up_prompt(question)
            logger.info(f"[追问] {question.question} (原因: {question.reason})")
            return True, prompt
        
        return False, None


# 单例实例
follow_up_manager = FollowUpManager()
