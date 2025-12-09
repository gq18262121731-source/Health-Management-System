"""
语音控制服务
============

处理语音控制命令，支持：
1. 页面导航控制
2. 数据查询播报
3. 提醒设置控制
4. 报告生成
5. 紧急呼救
6. 停止语音
"""

import re
import logging
from typing import Dict, Optional, Any, List
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class ControlAction(Enum):
    """控制动作类型"""
    # 导航
    NAVIGATE_HOME = "navigate_home"
    NAVIGATE_HEALTH = "navigate_health"
    NAVIGATE_CONSULTATION = "navigate_consultation"
    NAVIGATE_REPORT = "navigate_report"
    NAVIGATE_PSYCHOLOGY = "navigate_psychology"
    NAVIGATE_MYINFO = "navigate_myinfo"
    NAVIGATE_BACK = "navigate_back"
    
    # 查询播报
    QUERY_HEALTH_DATA = "query_health_data"
    QUERY_BLOOD_PRESSURE = "query_blood_pressure"
    QUERY_BLOOD_SUGAR = "query_blood_sugar"
    QUERY_HEART_RATE = "query_heart_rate"
    QUERY_SLEEP = "query_sleep"
    QUERY_TODAY = "query_today"
    
    # 提醒（前端需实现）
    SET_REMINDER = "set_reminder"
    CANCEL_REMINDER = "cancel_reminder"
    SET_MEDICATION_REMINDER = "set_medication_reminder"
    
    # 紧急呼救（模拟通知）
    EMERGENCY_CALL = "emergency_call"
    
    # 报告
    GENERATE_REPORT = "generate_report"
    
    # 停止
    STOP = "stop"
    STOP_SPEAKING = "stop_speaking"
    CANCEL = "cancel"
    
    # 未知
    UNKNOWN = "unknown"


@dataclass
class ControlCommand:
    """控制命令"""
    action: ControlAction
    params: Dict[str, Any]
    confidence: float
    response_text: str      # 语音回复文本
    frontend_event: str     # 前端事件名称
    frontend_data: Dict     # 前端事件数据


class VoiceControlService:
    """语音控制服务"""
    
    # 页面导航映射（与前端 App.tsx 的 activeTab 对应）
    NAVIGATE_PAGES = {
        # 首页/健康分析
        "首页": ("navigate_home", "analysis", "好的，正在为您打开首页"),
        "主页": ("navigate_home", "analysis", "好的，正在为您打开首页"),
        "健康": ("navigate_health", "analysis", "好的，正在为您打开健康页面"),
        "健康分析": ("navigate_health", "analysis", "好的，正在为您打开健康分析"),
        # AI咨询
        "AI对话": ("navigate_consultation", "consultation", "好的，正在为您打开AI对话"),
        "AI咨询": ("navigate_consultation", "consultation", "好的，正在为您打开AI咨询"),
        "对话": ("navigate_consultation", "consultation", "好的，正在为您打开对话页面"),
        "咨询": ("navigate_consultation", "consultation", "好的，正在为您打开咨询页面"),
        # 报告
        "报告": ("navigate_report", "reports", "好的，正在为您打开健康报告"),
        "健康报告": ("navigate_report", "reports", "好的，正在为您打开健康报告"),
        "看报告": ("navigate_report", "reports", "好的，正在为您打开健康报告"),
        "打开报告": ("navigate_report", "reports", "好的，正在为您打开健康报告"),
        # 心理健康
        "心理": ("navigate_psychology", "psychology", "好的，正在为您打开心理健康"),
        "心理健康": ("navigate_psychology", "psychology", "好的，正在为您打开心理健康"),
        "心情": ("navigate_psychology", "psychology", "好的，正在为您打开心理健康"),
        # 个人信息
        "个人信息": ("navigate_myinfo", "myinfo", "好的，正在为您打开个人信息"),
        "我的信息": ("navigate_myinfo", "myinfo", "好的，正在为您打开个人信息"),
        "设置": ("navigate_myinfo", "myinfo", "好的，正在为您打开设置"),
        # 返回
        "返回": ("navigate_back", "back", "好的，正在返回上一页"),
        "返回上一页": ("navigate_back", "back", "好的，正在返回上一页"),
    }
    
    # 查询数据映射（语音播报健康数据）
    QUERY_DATA = {
        "血压": ("query_blood_pressure", "blood_pressure", "好的，正在为您播报血压数据"),
        "血糖": ("query_blood_sugar", "blood_sugar", "好的，正在为您播报血糖数据"),
        "心率": ("query_heart_rate", "heart_rate", "好的，正在为您播报心率数据"),
        "睡眠": ("query_sleep", "sleep", "好的，正在为您播报睡眠数据"),
        "昨晚睡眠": ("query_sleep", "sleep", "好的，正在为您播报昨晚的睡眠情况"),
        "健康数据": ("query_health_data", "all", "好的，正在为您播报健康数据"),
        "今天": ("query_today", "today", "好的，正在为您播报今天的数据"),
        "身体情况": ("query_health_data", "all", "好的，正在为您播报身体情况"),
    }
    
    # 紧急呼救关键词
    EMERGENCY_KEYWORDS = ["呼救", "救命", "帮帮我", "紧急呼叫", "一键呼救", "求助", "sos", "不舒服", "难受"]
    
    def parse_control_command(self, text: str, intent: str) -> ControlCommand:
        """
        解析控制命令
        
        Args:
            text: 用户输入文本
            intent: 识别的意图类型
            
        Returns:
            ControlCommand 控制命令
        """
        text = text.strip()
        
        # 检查紧急呼救（最高优先级）
        if any(kw in text.lower() for kw in self.EMERGENCY_KEYWORDS):
            return self._parse_emergency(text)
        
        # 根据意图类型分发处理
        if intent == "control_navigate":
            return self._parse_navigate(text)
        elif intent == "control_query":
            return self._parse_query(text)
        elif intent == "control_reminder":
            return self._parse_reminder(text)
        elif intent == "control_report":
            return self._parse_report(text)
        elif intent == "control_stop":
            return self._parse_stop(text)
        else:
            return ControlCommand(
                action=ControlAction.UNKNOWN,
                params={},
                confidence=0.3,
                response_text="抱歉，我没有理解您的指令",
                frontend_event="unknown",
                frontend_data={}
            )
    
    def _parse_navigate(self, text: str) -> ControlCommand:
        """解析导航命令"""
        for keyword, (action, route, response) in self.NAVIGATE_PAGES.items():
            if keyword in text:
                return ControlCommand(
                    action=ControlAction[action.upper()],
                    params={"route": route},
                    confidence=0.9,
                    response_text=response,
                    frontend_event="navigate",
                    frontend_data={"route": route, "page": keyword}
                )
        
        return ControlCommand(
            action=ControlAction.NAVIGATE_HOME,
            params={"route": "analysis"},
            confidence=0.6,
            response_text="好的，正在为您打开首页",
            frontend_event="navigate",
            frontend_data={"route": "analysis"}
        )
    
    def _parse_query(self, text: str) -> ControlCommand:
        """解析查询命令"""
        for keyword, (action, data_type, response) in self.QUERY_DATA.items():
            if keyword in text:
                return ControlCommand(
                    action=ControlAction[action.upper()],
                    params={"data_type": data_type},
                    confidence=0.9,
                    response_text=response,
                    frontend_event="query_data",
                    frontend_data={"type": data_type}
                )
        
        return ControlCommand(
            action=ControlAction.QUERY_HEALTH_DATA,
            params={"data_type": "all"},
            confidence=0.7,
            response_text="好的，正在为您查询健康数据",
            frontend_event="query_data",
            frontend_data={"type": "all"}
        )
    
    def _parse_reminder(self, text: str) -> ControlCommand:
        """解析提醒命令"""
        # 提取时间
        time_match = re.search(r'(\d{1,2})[点时](\d{0,2})?', text)
        time_str = None
        if time_match:
            hour = time_match.group(1)
            minute = time_match.group(2) or "00"
            time_str = f"{hour}:{minute}"
        
        # 判断是设置还是取消
        if any(w in text for w in ["取消", "删除", "不要"]):
            return ControlCommand(
                action=ControlAction.CANCEL_REMINDER,
                params={},
                confidence=0.85,
                response_text="好的，已为您取消提醒",
                frontend_event="cancel_reminder",
                frontend_data={}
            )
        
        # 判断提醒类型
        if "吃药" in text or "药" in text:
            return ControlCommand(
                action=ControlAction.SET_MEDICATION_REMINDER,
                params={"time": time_str, "type": "medication"},
                confidence=0.9,
                response_text=f"好的，已为您设置{time_str or ''}吃药提醒" if time_str else "好的，请问您想几点提醒吃药？",
                frontend_event="set_reminder",
                frontend_data={"type": "medication", "time": time_str}
            )
        
        return ControlCommand(
            action=ControlAction.SET_REMINDER,
            params={"time": time_str},
            confidence=0.8,
            response_text=f"好的，已为您设置{time_str}的提醒" if time_str else "好的，请问您想设置什么时间的提醒？",
            frontend_event="set_reminder",
            frontend_data={"time": time_str}
        )
    
    def _parse_emergency(self, text: str) -> ControlCommand:
        """解析紧急呼救命令"""
        return ControlCommand(
            action=ControlAction.EMERGENCY_CALL,
            params={"is_emergency": True},
            confidence=0.99,
            response_text="🚨 紧急呼救已触发！正在通知您的紧急联系人！请保持冷静！",
            frontend_event="emergency_call",
            frontend_data={
                "is_emergency": True,
                "message": "用户触发紧急呼救"
            }
        )
    
    def _parse_report(self, text: str) -> ControlCommand:
        """解析报告命令"""
        return ControlCommand(
            action=ControlAction.GENERATE_REPORT,
            params={},
            confidence=0.9,
            response_text="好的，正在为您生成健康报告",
            frontend_event="generate_report",
            frontend_data={}
        )
    
    def _parse_stop(self, text: str) -> ControlCommand:
        """解析停止命令（主要用于停止语音播报）"""
        if any(w in text for w in ["停止说话", "别说了", "闭嘴", "安静"]):
            return ControlCommand(
                action=ControlAction.STOP_SPEAKING,
                params={},
                confidence=0.95,
                response_text="",  # 停止说话时不需要回复
                frontend_event="stop_speaking",
                frontend_data={}
            )
        
        if any(w in text for w in ["取消", "算了", "不要了"]):
            return ControlCommand(
                action=ControlAction.CANCEL,
                params={},
                confidence=0.9,
                response_text="好的，已取消",
                frontend_event="cancel_action",
                frontend_data={}
            )
        
        # 默认停止语音
        return ControlCommand(
            action=ControlAction.STOP_SPEAKING,
            params={},
            confidence=0.9,
            response_text="",
            frontend_event="stop_speaking",
            frontend_data={}
        )
    
    def get_supported_commands(self) -> Dict[str, List[str]]:
        """获取支持的控制命令列表"""
        return {
            "导航控制": ["打开首页", "打开报告", "打开心理健康", "打开AI对话", "打开个人信息", "返回"],
            "健康播报": ["查看血压", "查看血糖", "查看心率", "昨晚睡眠", "今天身体情况"],
            "提醒设置": ["8点提醒我吃药", "设置吃药提醒", "取消提醒"],
            "报告生成": ["生成报告", "生成健康报告"],
            "紧急呼救": ["救命", "帮帮我", "不舒服", "紧急呼救"],
            "停止语音": ["停止", "别说了", "取消"]
        }


# 单例实例
voice_control_service = VoiceControlService()
