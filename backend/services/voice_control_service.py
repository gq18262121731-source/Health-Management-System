"""
语音控制服务
============

处理语音控制命令，支持：
1. 页面导航控制
2. 数据查询控制
3. 提醒设置控制
4. 通话控制
5. 设备控制
6. 播放控制
7. 音量控制
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
    NAVIGATE_SETTINGS = "navigate_settings"
    NAVIGATE_PROFILE = "navigate_profile"
    NAVIGATE_MESSAGES = "navigate_messages"
    NAVIGATE_REPORT = "navigate_report"
    NAVIGATE_BACK = "navigate_back"
    
    # 查询
    QUERY_HEALTH_DATA = "query_health_data"
    QUERY_BLOOD_PRESSURE = "query_blood_pressure"
    QUERY_BLOOD_SUGAR = "query_blood_sugar"
    QUERY_TODAY = "query_today"
    QUERY_HISTORY = "query_history"
    
    # 提醒
    SET_REMINDER = "set_reminder"
    CANCEL_REMINDER = "cancel_reminder"
    SET_MEDICATION_REMINDER = "set_medication_reminder"
    
    # 通话
    CALL_FAMILY = "call_family"
    CALL_DOCTOR = "call_doctor"
    CALL_COMMUNITY = "call_community"
    
    # 设备
    MEASURE_BLOOD_PRESSURE = "measure_blood_pressure"
    MEASURE_BLOOD_SUGAR = "measure_blood_sugar"
    MEASURE_HEART_RATE = "measure_heart_rate"
    CONNECT_DEVICE = "connect_device"
    
    # 播放
    PLAY_MUSIC = "play_music"
    PLAY_VIDEO = "play_video"
    PLAY_EXERCISE = "play_exercise"
    
    # 音量
    VOLUME_UP = "volume_up"
    VOLUME_DOWN = "volume_down"
    VOLUME_MUTE = "volume_mute"
    
    # 停止
    STOP = "stop"
    PAUSE = "pause"
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
    
    # 页面导航映射
    NAVIGATE_PAGES = {
        "首页": ("navigate_home", "/home", "好的，正在为您打开首页"),
        "主页": ("navigate_home", "/home", "好的，正在为您打开首页"),
        "健康": ("navigate_health", "/health", "好的，正在为您打开健康页面"),
        "健康页": ("navigate_health", "/health", "好的，正在为您打开健康页面"),
        "设置": ("navigate_settings", "/settings", "好的，正在为您打开设置"),
        "个人中心": ("navigate_profile", "/profile", "好的，正在为您打开个人中心"),
        "消息": ("navigate_messages", "/messages", "好的，正在为您打开消息页面"),
        "报告": ("navigate_report", "/report", "好的，正在为您打开健康报告"),
        "健康报告": ("navigate_report", "/report", "好的，正在为您打开健康报告"),
        "看报告": ("navigate_report", "/report", "好的，正在为您打开健康报告"),
        "打开报告": ("navigate_report", "/report", "好的，正在为您打开健康报告"),
        "返回": ("navigate_back", "back", "好的，正在返回上一页"),
        "返回上一页": ("navigate_back", "back", "好的，正在返回上一页"),
    }
    
    # 查询数据映射
    QUERY_DATA = {
        "血压": ("query_blood_pressure", "blood_pressure", "好的，正在为您查询血压数据"),
        "血糖": ("query_blood_sugar", "blood_sugar", "好的，正在为您查询血糖数据"),
        "心率": ("query_heart_rate", "heart_rate", "好的，正在为您查询心率数据"),
        "健康数据": ("query_health_data", "all", "好的，正在为您查询健康数据"),
        "今天": ("query_today", "today", "好的，正在为您查询今天的数据"),
    }
    
    # 设备测量映射
    DEVICE_MEASURE = {
        "血压": ("measure_blood_pressure", "blood_pressure", "好的，请将血压计戴好，即将开始测量"),
        "血糖": ("measure_blood_sugar", "blood_sugar", "好的，请准备好血糖仪，即将开始测量"),
        "心率": ("measure_heart_rate", "heart_rate", "好的，请保持安静，即将测量心率"),
        "体温": ("measure_temperature", "temperature", "好的，请将体温计放置好，即将开始测量"),
    }
    
    # 通话对象映射
    CALL_TARGETS = {
        "儿子": ("call_family", "son", "好的，正在为您拨打儿子的电话"),
        "女儿": ("call_family", "daughter", "好的，正在为您拨打女儿的电话"),
        "子女": ("call_family", "children", "好的，正在为您拨打子女的电话"),
        "医生": ("call_doctor", "doctor", "好的，正在为您拨打医生的电话"),
        "社区": ("call_community", "community", "好的，正在为您拨打社区的电话"),
        "家人": ("call_family", "family", "好的，正在为您拨打家人的电话"),
    }
    
    # 紧急呼救关键词
    EMERGENCY_KEYWORDS = ["呼救", "救命", "帮帮我", "紧急呼叫", "一键呼救", "求助", "sos"]
    
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
        
        # 根据意图类型分发处理
        if intent == "control_navigate":
            return self._parse_navigate(text)
        elif intent == "control_query":
            return self._parse_query(text)
        elif intent == "control_reminder":
            return self._parse_reminder(text)
        elif intent == "control_call":
            return self._parse_call(text)
        elif intent == "control_device":
            return self._parse_device(text)
        elif intent == "control_play":
            return self._parse_play(text)
        elif intent == "control_volume":
            return self._parse_volume(text)
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
            params={"route": "/home"},
            confidence=0.6,
            response_text="好的，正在为您打开首页",
            frontend_event="navigate",
            frontend_data={"route": "/home"}
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
    
    def _parse_call(self, text: str) -> ControlCommand:
        """解析通话命令（包含一键呼救）"""
        text_lower = text.lower()
        
        # 检查是否是紧急呼救
        if any(kw in text_lower for kw in self.EMERGENCY_KEYWORDS):
            return ControlCommand(
                action=ControlAction.CALL_FAMILY,
                params={"target": "emergency", "is_emergency": True},
                confidence=0.99,
                response_text="🚨 紧急呼救已触发！正在通知您的紧急联系人和社区！请保持冷静！",
                frontend_event="emergency_call",
                frontend_data={
                    "is_emergency": True,
                    "targets": ["family", "community", "120"],
                    "message": "用户触发紧急呼救"
                }
            )
        
        # 普通通话
        for keyword, (action, target, response) in self.CALL_TARGETS.items():
            if keyword in text:
                return ControlCommand(
                    action=ControlAction[action.upper()],
                    params={"target": target},
                    confidence=0.9,
                    response_text=response,
                    frontend_event="make_call",
                    frontend_data={"target": target, "label": keyword}
                )
        
        return ControlCommand(
            action=ControlAction.CALL_FAMILY,
            params={},
            confidence=0.6,
            response_text="请问您想打给谁？可以说打给儿子、女儿、医生或社区",
            frontend_event="make_call",
            frontend_data={"target": None}
        )
    
    def _parse_device(self, text: str) -> ControlCommand:
        """解析设备命令"""
        for keyword, (action, device_type, response) in self.DEVICE_MEASURE.items():
            if keyword in text:
                return ControlCommand(
                    action=ControlAction[action.upper()],
                    params={"device": device_type},
                    confidence=0.9,
                    response_text=response,
                    frontend_event="start_measure",
                    frontend_data={"device": device_type}
                )
        
        if "连接" in text:
            return ControlCommand(
                action=ControlAction.CONNECT_DEVICE,
                params={},
                confidence=0.85,
                response_text="好的，正在搜索并连接设备",
                frontend_event="connect_device",
                frontend_data={}
            )
        
        return ControlCommand(
            action=ControlAction.MEASURE_BLOOD_PRESSURE,
            params={"device": "blood_pressure"},
            confidence=0.7,
            response_text="请问您想测量什么？可以说测血压、测血糖或测心率",
            frontend_event="start_measure",
            frontend_data={}
        )
    
    def _parse_play(self, text: str) -> ControlCommand:
        """解析播放命令"""
        if any(w in text for w in ["音乐", "歌", "曲"]):
            return ControlCommand(
                action=ControlAction.PLAY_MUSIC,
                params={"type": "music"},
                confidence=0.9,
                response_text="好的，正在为您播放轻松的音乐",
                frontend_event="play_media",
                frontend_data={"type": "music"}
            )
        
        if any(w in text for w in ["视频", "电视"]):
            return ControlCommand(
                action=ControlAction.PLAY_VIDEO,
                params={"type": "video"},
                confidence=0.9,
                response_text="好的，正在为您播放视频",
                frontend_event="play_media",
                frontend_data={"type": "video"}
            )
        
        if any(w in text for w in ["养生操", "太极", "健身操"]):
            return ControlCommand(
                action=ControlAction.PLAY_EXERCISE,
                params={"type": "exercise"},
                confidence=0.9,
                response_text="好的，正在为您播放养生操视频",
                frontend_event="play_media",
                frontend_data={"type": "exercise", "name": "养生操"}
            )
        
        return ControlCommand(
            action=ControlAction.PLAY_MUSIC,
            params={"type": "music"},
            confidence=0.7,
            response_text="好的，正在为您播放内容",
            frontend_event="play_media",
            frontend_data={"type": "music"}
        )
    
    def _parse_volume(self, text: str) -> ControlCommand:
        """解析音量命令"""
        if any(w in text for w in ["大", "高", "调大", "大声"]):
            return ControlCommand(
                action=ControlAction.VOLUME_UP,
                params={"direction": "up"},
                confidence=0.9,
                response_text="好的，已为您调大音量",
                frontend_event="volume_control",
                frontend_data={"action": "up"}
            )
        
        if any(w in text for w in ["小", "低", "调小", "小声"]):
            return ControlCommand(
                action=ControlAction.VOLUME_DOWN,
                params={"direction": "down"},
                confidence=0.9,
                response_text="好的，已为您调小音量",
                frontend_event="volume_control",
                frontend_data={"action": "down"}
            )
        
        if "静音" in text:
            if "取消" in text:
                return ControlCommand(
                    action=ControlAction.VOLUME_UP,
                    params={"direction": "unmute"},
                    confidence=0.9,
                    response_text="好的，已为您取消静音",
                    frontend_event="volume_control",
                    frontend_data={"action": "unmute"}
                )
            return ControlCommand(
                action=ControlAction.VOLUME_MUTE,
                params={"direction": "mute"},
                confidence=0.9,
                response_text="好的，已为您静音",
                frontend_event="volume_control",
                frontend_data={"action": "mute"}
            )
        
        return ControlCommand(
            action=ControlAction.VOLUME_UP,
            params={},
            confidence=0.6,
            response_text="请问您想调大还是调小音量？",
            frontend_event="volume_control",
            frontend_data={}
        )
    
    def _parse_stop(self, text: str) -> ControlCommand:
        """解析停止命令"""
        if any(w in text for w in ["暂停"]):
            return ControlCommand(
                action=ControlAction.PAUSE,
                params={},
                confidence=0.9,
                response_text="好的，已暂停",
                frontend_event="playback_control",
                frontend_data={"action": "pause"}
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
        
        return ControlCommand(
            action=ControlAction.STOP,
            params={},
            confidence=0.9,
            response_text="好的，已停止",
            frontend_event="playback_control",
            frontend_data={"action": "stop"}
        )
    
    def get_supported_commands(self) -> Dict[str, List[str]]:
        """获取支持的控制命令列表"""
        return {
            "导航控制": ["打开首页", "去设置", "返回上一页", "打开个人中心"],
            "查询控制": ["查看血压", "看看今天的数据", "查一下血糖记录"],
            "提醒控制": ["8点提醒我吃药", "设置吃药提醒", "取消提醒"],
            "通话控制": ["打给儿子", "打电话给医生", "联系社区"],
            "设备控制": ["测血压", "测一下血糖", "连接设备"],
            "播放控制": ["放音乐", "播放养生操", "放一首歌"],
            "音量控制": ["大声点", "小声点", "静音"],
            "停止控制": ["停止", "暂停", "取消"]
        }


# 单例实例
voice_control_service = VoiceControlService()
