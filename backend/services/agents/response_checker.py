"""
回答质量检查模块
================

确保AI回答的安全性和质量，特别是医疗健康场景。

功能：
1. 安全检查 - 防止危险的医疗建议
2. 幻觉检测 - 检测不合理的内容
3. 格式规范 - 确保回答结构正确
4. 敏感词过滤 - 过滤不当内容
"""
import re
import logging
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class RiskLevel(Enum):
    """风险等级"""
    SAFE = "safe"           # 安全
    LOW = "low"             # 低风险
    MEDIUM = "medium"       # 中风险
    HIGH = "high"           # 高风险
    CRITICAL = "critical"   # 危险，需要拦截


@dataclass
class CheckResult:
    """检查结果"""
    passed: bool            # 是否通过
    risk_level: RiskLevel   # 风险等级
    issues: List[str]       # 发现的问题
    suggestions: List[str]  # 修改建议
    modified_response: str  # 修改后的回答（如果需要）


class ResponseChecker:
    """
    回答质量检查器
    
    医疗健康场景的安全守护
    """
    
    def __init__(self):
        # 危险药物关键词（不应该直接推荐具体药物）
        self.dangerous_drug_patterns = [
            r"建议.*服用.*(?:mg|毫克|片|粒)",
            r"可以吃.*(?:药|片|胶囊)",
            r"推荐.*(?:药物|用药).*(?:剂量|用量)",
        ]
        
        # 危险建议关键词
        self.dangerous_advice = [
            "停药", "减药", "加药", "换药",  # 用药调整需医生指导
            "不用去医院", "不需要看医生",    # 可能延误病情
            "保证", "一定能", "肯定会",       # 过度承诺
        ]
        
        # 必须就医的情况
        self.emergency_keywords = [
            "胸痛持续", "呼吸困难", "意识模糊", "大量出血",
            "剧烈头痛", "突然瘫痪", "抽搐", "高烧不退",
            "血压超过180", "血糖低于3", "心率超过150"
        ]
        
        # 安全提醒短语
        self.safety_reminders = {
            "medication": "【温馨提示】用药请遵医嘱，不要自行调整药物剂量。",
            "emergency": "【紧急提醒】您的情况可能需要立即就医，请拨打120或前往最近医院！",
            "general": "【健康提示】以上建议仅供参考，如有不适请及时就医。",
            "diet": "【饮食提示】饮食建议因人而异，请根据自身情况调整。",
        }
        
        # 不合理数值范围
        self.value_ranges = {
            "blood_pressure_systolic": (60, 250),   # 收缩压
            "blood_pressure_diastolic": (40, 150),  # 舒张压
            "blood_sugar": (1.0, 35.0),             # 血糖
            "heart_rate": (30, 220),                # 心率
            "temperature": (34.0, 43.0),            # 体温
        }
    
    def check(self, response: str, context: Dict = None) -> CheckResult:
        """
        检查回答质量
        
        Args:
            response: AI的回答
            context: 上下文信息（意图、用户输入等）
            
        Returns:
            CheckResult 检查结果
        """
        context = context or {}
        issues = []
        suggestions = []
        risk_level = RiskLevel.SAFE
        modified_response = response
        
        # 1. 检查危险药物建议
        drug_issues = self._check_dangerous_drugs(response)
        if drug_issues:
            issues.extend(drug_issues)
            risk_level = self._elevate_risk(risk_level, RiskLevel.HIGH)
            suggestions.append("移除具体药物推荐，建议用户咨询医生")
        
        # 2. 检查危险建议
        advice_issues = self._check_dangerous_advice(response)
        if advice_issues:
            issues.extend(advice_issues)
            risk_level = self._elevate_risk(risk_level, RiskLevel.MEDIUM)
            suggestions.append("修改过于绝对的表述")
        
        # 3. 检查是否需要紧急就医提醒
        user_input = context.get("user_input", "")
        if self._needs_emergency_reminder(user_input, response):
            if "就医" not in response and "医院" not in response and "120" not in response:
                issues.append("紧急情况未提醒就医")
                risk_level = self._elevate_risk(risk_level, RiskLevel.HIGH)
                modified_response = self._add_emergency_reminder(response)
        
        # 4. 检查数值合理性
        value_issues = self._check_value_reasonability(response)
        if value_issues:
            issues.extend(value_issues)
            risk_level = self._elevate_risk(risk_level, RiskLevel.LOW)
        
        # 5. 添加安全提醒（如果没有）
        intent = context.get("intent", "")
        modified_response = self._ensure_safety_reminder(modified_response, intent)
        
        # 6. 检查回答长度
        if len(response) < 10:
            issues.append("回答过短")
            risk_level = self._elevate_risk(risk_level, RiskLevel.LOW)
        
        passed = risk_level in [RiskLevel.SAFE, RiskLevel.LOW]
        
        if issues:
            logger.warning(f"[质量检查] 发现问题: {issues}, 风险等级: {risk_level.value}")
        
        return CheckResult(
            passed=passed,
            risk_level=risk_level,
            issues=issues,
            suggestions=suggestions,
            modified_response=modified_response
        )
    
    def _check_dangerous_drugs(self, response: str) -> List[str]:
        """检查危险药物建议"""
        issues = []
        for pattern in self.dangerous_drug_patterns:
            if re.search(pattern, response):
                issues.append(f"包含具体药物剂量建议")
                break
        return issues
    
    def _check_dangerous_advice(self, response: str) -> List[str]:
        """检查危险建议"""
        issues = []
        for keyword in self.dangerous_advice:
            if keyword in response:
                # 排除否定句
                if f"不要{keyword}" not in response and f"不能{keyword}" not in response:
                    issues.append(f"包含危险建议关键词: {keyword}")
        return issues
    
    def _needs_emergency_reminder(self, user_input: str, response: str) -> bool:
        """判断是否需要紧急就医提醒"""
        combined = user_input + response
        for keyword in self.emergency_keywords:
            if keyword in combined:
                return True
        
        # 检查危险数值
        # 血压 > 180
        bp_match = re.search(r'(\d{3})[/／](\d{2,3})', combined)
        if bp_match:
            systolic = int(bp_match.group(1))
            if systolic >= 180:
                return True
        
        return False
    
    def _add_emergency_reminder(self, response: str) -> str:
        """添加紧急就医提醒"""
        reminder = self.safety_reminders["emergency"]
        return f"{reminder}\n\n{response}"
    
    def _check_value_reasonability(self, response: str) -> List[str]:
        """检查数值合理性"""
        issues = []
        
        # 检查血压
        bp_matches = re.findall(r'(\d{2,3})[/／](\d{2,3})\s*(?:mmHg)?', response)
        for match in bp_matches:
            systolic, diastolic = int(match[0]), int(match[1])
            if not (60 <= systolic <= 250) or not (40 <= diastolic <= 150):
                issues.append(f"血压数值不合理: {systolic}/{diastolic}")
        
        return issues
    
    def _ensure_safety_reminder(self, response: str, intent: str) -> str:
        """确保有安全提醒"""
        # 如果已经有提醒，不重复添加
        if "【" in response and "提示" in response:
            return response
        if "温馨提示" in response or "健康提示" in response:
            return response
        
        # 根据意图添加对应提醒
        if intent in ["medication", "blood_pressure", "blood_sugar"]:
            reminder = self.safety_reminders.get("medication", self.safety_reminders["general"])
        elif intent in ["diet"]:
            reminder = self.safety_reminders["diet"]
        else:
            reminder = self.safety_reminders["general"]
        
        # 添加到末尾
        return f"{response}\n\n{reminder}"
    
    def _elevate_risk(self, current: RiskLevel, new: RiskLevel) -> RiskLevel:
        """提升风险等级（取更高的）"""
        levels = [RiskLevel.SAFE, RiskLevel.LOW, RiskLevel.MEDIUM, RiskLevel.HIGH, RiskLevel.CRITICAL]
        current_idx = levels.index(current)
        new_idx = levels.index(new)
        return levels[max(current_idx, new_idx)]
    
    def quick_check(self, response: str) -> Tuple[bool, str]:
        """
        快速检查（简化版）
        
        Returns:
            (是否安全, 修改后的回答)
        """
        result = self.check(response)
        return result.passed, result.modified_response


# 单例实例
response_checker = ResponseChecker()
