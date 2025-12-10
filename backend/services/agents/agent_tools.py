"""
智能体工具系统
==============

为智能体提供可调用的工具，如查询健康数据、获取提醒等。
"""
import logging
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass
import json

logger = logging.getLogger(__name__)


@dataclass
class ToolResult:
    """工具调用结果"""
    success: bool
    data: Any
    message: str = ""
    
    def to_context(self) -> str:
        """转换为可注入到提示词的上下文"""
        if not self.success:
            return f"[工具调用失败: {self.message}]"
        
        if isinstance(self.data, dict):
            return json.dumps(self.data, ensure_ascii=False, indent=2)
        elif isinstance(self.data, list):
            return json.dumps(self.data, ensure_ascii=False, indent=2)
        return str(self.data)


class AgentTools:
    """智能体工具集"""
    
    def __init__(self):
        self.tools: Dict[str, Callable] = {}
        self._register_default_tools()
    
    def _register_default_tools(self):
        """注册默认工具"""
        self.register("query_health_records", self.query_health_records, 
                     "查询用户健康记录（血压、血糖、心率等）")
        self.register("query_recent_alerts", self.query_recent_alerts,
                     "查询用户最近的健康预警")
        self.register("query_medications", self.query_medications,
                     "查询用户的用药记录和提醒")
        self.register("query_health_trend", self.query_health_trend,
                     "查询健康指标趋势（7天/30天）")
        self.register("get_health_advice", self.get_health_advice,
                     "根据健康数据获取个性化建议")
    
    def register(self, name: str, func: Callable, description: str):
        """注册工具"""
        self.tools[name] = {
            "func": func,
            "description": description
        }
        logger.debug(f"注册工具: {name}")
    
    def get_tools_description(self) -> str:
        """获取所有工具的描述，用于提示词"""
        lines = ["【可用工具】"]
        for name, info in self.tools.items():
            lines.append(f"- {name}: {info['description']}")
        return "\n".join(lines)
    
    def call(self, tool_name: str, **kwargs) -> ToolResult:
        """调用工具"""
        if tool_name not in self.tools:
            return ToolResult(False, None, f"工具 {tool_name} 不存在")
        
        try:
            result = self.tools[tool_name]["func"](**kwargs)
            logger.info(f"工具调用成功: {tool_name}")
            return result
        except Exception as e:
            logger.error(f"工具调用失败: {tool_name}, 错误: {e}")
            return ToolResult(False, None, str(e))
    
    # ==================== 健康数据工具 ====================
    
    def query_health_records(
        self, 
        user_id: str = None,
        record_type: str = "all",
        days: int = 7
    ) -> ToolResult:
        """
        查询用户健康记录
        
        Args:
            user_id: 用户ID
            record_type: 记录类型 (blood_pressure/blood_sugar/heart_rate/all)
            days: 查询天数
        """
        try:
            # 尝试从数据库查询真实数据
            records = self._fetch_health_records(user_id, record_type, days)
            
            if records:
                return ToolResult(True, records, "查询成功")
            
            # 如果没有数据，返回模拟数据（演示用）
            mock_data = self._get_mock_health_records(record_type, days)
            return ToolResult(True, mock_data, "返回示例数据")
            
        except Exception as e:
            return ToolResult(False, None, str(e))
    
    def _fetch_health_records(
        self, 
        user_id: str, 
        record_type: str, 
        days: int
    ) -> Optional[Dict]:
        """从数据库获取健康记录"""
        try:
            from database.connection import get_db
            from sqlalchemy import text
            
            # 这里可以根据实际数据库结构查询
            # 暂时返回None，使用模拟数据
            return None
        except:
            return None
    
    def _get_mock_health_records(self, record_type: str, days: int) -> Dict:
        """获取模拟健康记录"""
        import random
        
        records = {
            "period": f"最近{days}天",
            "records": []
        }
        
        for i in range(min(days, 7)):
            date = (datetime.now() - timedelta(days=i)).strftime("%m-%d")
            record = {"date": date}
            
            if record_type in ["blood_pressure", "all"]:
                record["blood_pressure"] = {
                    "systolic": random.randint(125, 155),
                    "diastolic": random.randint(80, 95)
                }
            
            if record_type in ["blood_sugar", "all"]:
                record["blood_sugar"] = {
                    "fasting": round(random.uniform(5.5, 7.5), 1),
                    "after_meal": round(random.uniform(7.0, 11.0), 1)
                }
            
            if record_type in ["heart_rate", "all"]:
                record["heart_rate"] = random.randint(65, 85)
            
            records["records"].append(record)
        
        # 计算统计
        if records["records"]:
            if record_type in ["blood_pressure", "all"]:
                sys_values = [r["blood_pressure"]["systolic"] for r in records["records"] if "blood_pressure" in r]
                dia_values = [r["blood_pressure"]["diastolic"] for r in records["records"] if "blood_pressure" in r]
                records["summary"] = {
                    "blood_pressure_avg": f"{sum(sys_values)//len(sys_values)}/{sum(dia_values)//len(dia_values)} mmHg",
                    "blood_pressure_status": "偏高" if sum(sys_values)/len(sys_values) > 140 else "正常范围"
                }
        
        return records
    
    def query_recent_alerts(self, user_id: str = None, days: int = 7) -> ToolResult:
        """查询最近的健康预警"""
        # 模拟预警数据
        alerts = [
            {
                "date": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"),
                "type": "blood_pressure",
                "level": "warning",
                "message": "血压偏高 (152/95 mmHg)",
                "suggestion": "建议休息，避免剧烈运动"
            },
            {
                "date": (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d"),
                "type": "blood_sugar",
                "level": "info",
                "message": "餐后血糖略高 (9.2 mmol/L)",
                "suggestion": "注意控制碳水化合物摄入"
            }
        ]
        
        return ToolResult(True, {
            "total": len(alerts),
            "alerts": alerts
        })
    
    def query_medications(self, user_id: str = None) -> ToolResult:
        """查询用药记录"""
        # 模拟用药数据
        medications = [
            {
                "name": "硝苯地平缓释片",
                "dosage": "30mg",
                "frequency": "每日1次",
                "time": "早餐后",
                "purpose": "降压"
            },
            {
                "name": "阿司匹林肠溶片",
                "dosage": "100mg", 
                "frequency": "每日1次",
                "time": "晚餐后",
                "purpose": "预防血栓"
            }
        ]
        
        return ToolResult(True, {
            "medications": medications,
            "next_reminder": "今日 18:00 - 阿司匹林肠溶片"
        })
    
    def query_health_trend(
        self, 
        user_id: str = None,
        metric: str = "blood_pressure",
        period: str = "7d"
    ) -> ToolResult:
        """查询健康指标趋势"""
        import random
        
        days = 7 if period == "7d" else 30
        
        trend_data = {
            "metric": metric,
            "period": period,
            "trend": [],
            "analysis": ""
        }
        
        if metric == "blood_pressure":
            for i in range(days):
                date = (datetime.now() - timedelta(days=days-1-i)).strftime("%m-%d")
                trend_data["trend"].append({
                    "date": date,
                    "systolic": random.randint(130, 150),
                    "diastolic": random.randint(82, 92)
                })
            
            # 分析趋势
            first_week_avg = sum(t["systolic"] for t in trend_data["trend"][:3]) / 3
            last_week_avg = sum(t["systolic"] for t in trend_data["trend"][-3:]) / 3
            
            if last_week_avg < first_week_avg - 5:
                trend_data["analysis"] = "血压呈下降趋势，控制效果良好"
            elif last_week_avg > first_week_avg + 5:
                trend_data["analysis"] = "血压呈上升趋势，需要关注"
            else:
                trend_data["analysis"] = "血压相对稳定"
        
        return ToolResult(True, trend_data)
    
    def get_health_advice(
        self, 
        user_id: str = None,
        health_data: Dict = None
    ) -> ToolResult:
        """根据健康数据获取个性化建议"""
        advice = []
        
        if health_data:
            bp = health_data.get("blood_pressure", {})
            if bp.get("systolic", 0) > 140:
                advice.append({
                    "category": "血压管理",
                    "priority": "high",
                    "suggestions": [
                        "减少盐分摄入，每日不超过5g",
                        "适量运动，每天散步30分钟",
                        "保持情绪稳定，避免激动",
                        "按时服用降压药物"
                    ]
                })
            
            bs = health_data.get("blood_sugar", {})
            if bs.get("fasting", 0) > 7.0:
                advice.append({
                    "category": "血糖管理",
                    "priority": "medium",
                    "suggestions": [
                        "控制主食量，增加粗粮比例",
                        "餐后适当活动",
                        "定期监测血糖"
                    ]
                })
        
        if not advice:
            advice.append({
                "category": "日常保健",
                "priority": "low",
                "suggestions": [
                    "保持规律作息",
                    "均衡饮食",
                    "适量运动"
                ]
            })
        
        return ToolResult(True, {"advice": advice})
    
    # ==================== 工具调用解析 ====================
    
    def parse_tool_calls(self, text: str) -> List[Dict]:
        """
        从文本中解析工具调用请求
        
        格式: [TOOL:tool_name(param1=value1, param2=value2)]
        """
        import re
        
        pattern = r'\[TOOL:(\w+)\((.*?)\)\]'
        matches = re.findall(pattern, text)
        
        calls = []
        for tool_name, params_str in matches:
            params = {}
            if params_str:
                for param in params_str.split(','):
                    if '=' in param:
                        key, value = param.split('=', 1)
                        params[key.strip()] = value.strip().strip('"\'')
            
            calls.append({
                "tool": tool_name,
                "params": params
            })
        
        return calls
    
    def execute_tool_calls(self, calls: List[Dict]) -> str:
        """执行工具调用并返回结果上下文"""
        results = []
        
        for call in calls:
            tool_name = call["tool"]
            params = call["params"]
            
            result = self.call(tool_name, **params)
            results.append(f"【{tool_name}结果】\n{result.to_context()}")
        
        return "\n\n".join(results)


# 创建全局实例
agent_tools = AgentTools()
