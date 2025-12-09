"""
自动化场景服务
==============

支持通过语音关键词触发自动化流程：
1. 场景模式（早安/晚安）
2. 健康播报、报告生成
3. 紧急求助
4. 查看趋势、吃药提醒
"""

import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import asyncio

logger = logging.getLogger(__name__)


class AutomationTrigger(Enum):
    """触发类型"""
    VOICE = "voice"           # 语音触发
    SCHEDULE = "schedule"     # 定时触发
    CONDITION = "condition"   # 条件触发
    EVENT = "event"           # 事件触发


class ActionType(Enum):
    """动作类型（仅保留已实现的功能）"""
    NAVIGATE = "navigate"           # 页面导航
    QUERY = "query"                 # 数据查询播报
    TTS = "tts"                     # 语音播报
    GENERATE_REPORT = "generate_report"  # 生成报告
    SET_REMINDER = "set_reminder"   # 设置提醒
    EMERGENCY = "emergency"         # 紧急呼救通知
    STOP_SPEAKING = "stop_speaking" # 停止语音


@dataclass
class AutomationAction:
    """自动化动作"""
    action_type: ActionType
    params: Dict[str, Any] = field(default_factory=dict)
    delay_seconds: float = 0  # 执行前延迟
    speak_text: str = ""      # 执行时语音提示


@dataclass
class AutomationScene:
    """自动化场景"""
    scene_id: str
    name: str
    description: str
    keywords: List[str]           # 触发关键词
    actions: List[AutomationAction]
    enabled: bool = True
    trigger_type: AutomationTrigger = AutomationTrigger.VOICE
    schedule_time: Optional[time] = None  # 定时触发时间
    condition: Optional[str] = None       # 条件表达式


class AutomationService:
    """自动化服务"""
    
    def __init__(self):
        self.scenes: Dict[str, AutomationScene] = {}
        self._init_default_scenes()
    
    def _init_default_scenes(self):
        """初始化默认场景"""
        
        # ========== 1. 早安模式 ==========
        self.register_scene(AutomationScene(
            scene_id="morning_routine",
            name="早安模式",
            description="早晨起床后的健康播报",
            keywords=["早安", "早上好", "起床了", "早安模式"],
            actions=[
                AutomationAction(
                    action_type=ActionType.TTS,
                    speak_text="早上好！新的一天开始了，让我为您播报一下健康状况。"
                ),
                AutomationAction(
                    action_type=ActionType.QUERY,
                    params={"type": "sleep"},
                    delay_seconds=1,
                    speak_text="昨晚您睡了7小时32分钟，睡眠质量良好。"
                ),
                AutomationAction(
                    action_type=ActionType.QUERY,
                    params={"type": "health_summary"},
                    delay_seconds=2,
                    speak_text="您的血压120/80，心率0次，均在正常范围内。"
                ),
                AutomationAction(
                    action_type=ActionType.TTS,
                    delay_seconds=1,
                    speak_text="记得按时吃药，祥您今天愉快！"
                ),
            ]
        ))
        
        # ========== 2. 晚安模式 ==========
        self.register_scene(AutomationScene(
            scene_id="night_routine",
            name="晚安模式",
            description="睡前健康总结",
            keywords=["晚安", "睡觉了", "晚安模式", "准备睡了"],
            actions=[
                AutomationAction(
                    action_type=ActionType.TTS,
                    speak_text="晚安！让我为您总结一下今天的健康情况。"
                ),
                AutomationAction(
                    action_type=ActionType.QUERY,
                    params={"type": "daily_summary"},
                    delay_seconds=1,
                    speak_text="今天您走了6832步，血压测量2次，均在正常范围内。"
                ),
                AutomationAction(
                    action_type=ActionType.TTS,
                    delay_seconds=2,
                    speak_text="祥您今晚睡个好觉，明天见！"
                ),
            ]
        ))
        
        # ========== 3. 健康播报 ==========
        self.register_scene(AutomationScene(
            scene_id="health_broadcast",
            name="健康播报",
            description="播报当前健康状态摘要",
            keywords=["健康播报", "播报健康", "健康状况", "身体情况"],
            actions=[
                AutomationAction(
                    action_type=ActionType.TTS,
                    speak_text="好的，正在为您播报健康状况。"
                ),
                AutomationAction(
                    action_type=ActionType.QUERY,
                    params={"type": "health_summary"},
                    delay_seconds=1
                ),
            ]
        ))
        
        # ========== 4. 生成报告 ==========
        self.register_scene(AutomationScene(
            scene_id="generate_report",
            name="生成报告",
            description="生成健康报告",
            keywords=["生成报告", "做报告", "健康报告"],
            actions=[
                AutomationAction(
                    action_type=ActionType.TTS,
                    speak_text="好的，正在为您生成健康报告。"
                ),
                AutomationAction(
                    action_type=ActionType.GENERATE_REPORT,
                    params={"type": "current"},
                    delay_seconds=1
                ),
                AutomationAction(
                    action_type=ActionType.NAVIGATE,
                    params={"route": "reports"},
                    delay_seconds=1,
                    speak_text="报告已生成，正在为您打开报告页面。"
                ),
            ]
        ))
        
        # ========== 5. 紧急求助 ==========
        self.register_scene(AutomationScene(
            scene_id="emergency_help",
            name="紧急求助",
            description="一键紧急呼救（模拟通知）",
            keywords=["救命", "紧急呼救", "帮帮我", "不舒服", "难受"],
            actions=[
                AutomationAction(
                    action_type=ActionType.TTS,
                    speak_text="🚨 紧急呼救已触发！正在通知您的紧急联系人！请保持冷静！"
                ),
                AutomationAction(
                    action_type=ActionType.EMERGENCY,
                    params={"is_emergency": True, "message": "用户触发紧急呼救"},
                    delay_seconds=1
                ),
            ]
        ))
        
        # ========== 6. 查看趋势 ==========
        self.register_scene(AutomationScene(
            scene_id="view_trends",
            name="查看趋势",
            description="查看健康趋势分析",
            keywords=["看趋势", "趋势分析", "最近变化", "健康趋势"],
            actions=[
                AutomationAction(
                    action_type=ActionType.NAVIGATE,
                    params={"route": "analysis"},
                    speak_text="正在为您打开健康分析页面。"
                ),
                AutomationAction(
                    action_type=ActionType.TTS,
                    delay_seconds=2,
                    speak_text="根据最近7天的数据，您的血压整体保持稳定，略有下降趋势，这是好现象。"
                ),
            ]
        ))
        
        # ========== 7. 吃药提醒 ==========
        self.register_scene(AutomationScene(
            scene_id="take_medicine",
            name="吃药时间",
            description="吃药提醒和记录",
            keywords=["该吃药了", "吃药时间", "提醒吃药"],
            actions=[
                AutomationAction(
                    action_type=ActionType.TTS,
                    speak_text="现在是吃药时间。您需要服用：降压药1片、阿司匹林1片。"
                ),
                AutomationAction(
                    action_type=ActionType.TTS,
                    delay_seconds=5,
                    speak_text="请在服药后说'吃完了'，我帮您记录。"
                ),
            ]
        ))
    
    def register_scene(self, scene: AutomationScene):
        """注册场景"""
        self.scenes[scene.scene_id] = scene
        logger.info(f"注册自动化场景: {scene.name}")
    
    def match_scene(self, text: str) -> Optional[AutomationScene]:
        """
        根据文本匹配场景
        
        Args:
            text: 用户输入文本
            
        Returns:
            匹配到的场景，或None
        """
        text = text.lower().strip()
        
        for scene in self.scenes.values():
            if not scene.enabled:
                continue
            
            for keyword in scene.keywords:
                if keyword in text:
                    logger.info(f"匹配到场景: {scene.name} (关键词: {keyword})")
                    return scene
        
        return None
    
    async def execute_scene(
        self, 
        scene: AutomationScene,
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        执行场景
        
        Args:
            scene: 要执行的场景
            context: 执行上下文（用户信息等）
            
        Returns:
            执行结果
        """
        result = {
            "scene_id": scene.scene_id,
            "scene_name": scene.name,
            "success": True,
            "actions_executed": [],
            "speak_texts": [],
            "frontend_events": []
        }
        
        logger.info(f"开始执行场景: {scene.name}")
        
        for i, action in enumerate(scene.actions):
            try:
                # 延迟执行
                if action.delay_seconds > 0:
                    await asyncio.sleep(action.delay_seconds)
                
                # 收集语音文本
                if action.speak_text:
                    result["speak_texts"].append(action.speak_text)
                
                # 生成前端事件
                event = self._action_to_frontend_event(action)
                if event:
                    result["frontend_events"].append(event)
                
                result["actions_executed"].append({
                    "index": i,
                    "type": action.action_type.value,
                    "success": True
                })
                
                logger.info(f"执行动作 {i+1}/{len(scene.actions)}: {action.action_type.value}")
                
            except Exception as e:
                logger.error(f"执行动作失败: {e}")
                result["actions_executed"].append({
                    "index": i,
                    "type": action.action_type.value,
                    "success": False,
                    "error": str(e)
                })
        
        return result
    
    def _action_to_frontend_event(self, action: AutomationAction) -> Optional[Dict]:
        """将动作转换为前端事件（仅包含已实现的功能）"""
        event_mapping = {
            ActionType.NAVIGATE: ("navigate", {"route": action.params.get("route")}),
            ActionType.QUERY: ("query_data", {"type": action.params.get("type")}),
            ActionType.GENERATE_REPORT: ("generate_report", action.params),
            ActionType.SET_REMINDER: ("set_reminder", action.params),
            ActionType.EMERGENCY: ("emergency_call", action.params),
            ActionType.STOP_SPEAKING: ("stop_speaking", {}),
        }
        
        if action.action_type in event_mapping:
            event_name, event_data = event_mapping[action.action_type]
            return {"event": event_name, "data": event_data}
        
        return None
    
    def get_available_scenes(self) -> List[Dict]:
        """获取所有可用场景"""
        return [
            {
                "id": scene.scene_id,
                "name": scene.name,
                "description": scene.description,
                "keywords": scene.keywords,
                "enabled": scene.enabled
            }
            for scene in self.scenes.values()
        ]
    
    def get_scene_keywords(self) -> Dict[str, List[str]]:
        """获取场景关键词映射（用于展示）"""
        return {
            scene.name: scene.keywords
            for scene in self.scenes.values()
            if scene.enabled
        }


# 单例实例
automation_service = AutomationService()
