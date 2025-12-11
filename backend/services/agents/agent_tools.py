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
            
            # 返回健康数据
            health_data = self._get_mock_health_records(record_type, days)
            return ToolResult(True, health_data, "查询成功")
            
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
    
    # ==================== 多轮对话工具调用 ====================
    
    def analyze_user_intent(self, user_input: str, conversation_history: List[Dict] = None) -> Dict:
        """
        分析用户意图，决定是反问、调用工具还是直接回答
        
        流程：
        1. 用户问健康问题（如"血压高不高"）→ 反问收集数据
        2. 用户说"查一下/有没有记录" → 调用工具查询
        3. 用户直接给数值 → 基于数值分析
        
        Returns:
            {
                "action": "ask_for_data" | "call_tool" | "analyze_data" | "direct_answer",
                "response": 回复内容,
                "tool_name": 需要调用的工具（如有）,
                "data": 提取的数据（如有）
            }
        """
        text = user_input.strip()
        history = conversation_history or []
        
        # 检查是否在等待用户提供数据（上一轮是反问）
        waiting_for_data = False
        last_question_topic = None
        if history:
            last_msg = history[-1] if history else {}
            if last_msg.get("action") == "ask_for_data":
                waiting_for_data = True
                last_question_topic = last_msg.get("topic")
        
        # 1. 用户请求查询历史数据 或 用户反问"我的数据是多少"
        query_keywords = [
            "查一下", "查查", "有没有记录", "最近的数据", "测试数据", 
            "历史记录", "帮我查", "看看记录", "是多少啊", "是多少呢",
            "多少啊", "多少呢", "不知道", "不记得", "忘了", "帮我看看"
        ]
        if any(kw in text for kw in query_keywords):
            # 确定要查询的类型
            if "血压" in text or last_question_topic == "blood_pressure":
                return {
                    "action": "call_tool",
                    "tool_name": "query_health_records",
                    "tool_params": {"record_type": "blood_pressure", "days": 7},
                    "response": None,
                    "topic": "blood_pressure"
                }
            elif "血糖" in text or last_question_topic == "blood_sugar":
                return {
                    "action": "call_tool",
                    "tool_name": "query_health_records",
                    "tool_params": {"record_type": "blood_sugar", "days": 7},
                    "response": None,
                    "topic": "blood_sugar"
                }
            elif "心率" in text or last_question_topic == "heart_rate":
                return {
                    "action": "call_tool",
                    "tool_name": "query_health_records",
                    "tool_params": {"record_type": "heart_rate", "days": 7},
                    "response": None,
                    "topic": "heart_rate"
                }
            else:
                return {
                    "action": "call_tool",
                    "tool_name": "query_health_records",
                    "tool_params": {"record_type": "all", "days": 7},
                    "response": None,
                    "topic": "all"
                }
        
        # 2. 用户直接提供了数值
        import re
        bp_match = re.search(r'(\d{2,3})[/／](\d{2,3})', text)
        glucose_match = re.search(r'血糖[是为]?\s*(\d+\.?\d*)', text)
        
        if bp_match:
            systolic = int(bp_match.group(1))
            diastolic = int(bp_match.group(2))
            return {
                "action": "analyze_data",
                "data": {"blood_pressure": {"systolic": systolic, "diastolic": diastolic}},
                "response": self._analyze_blood_pressure(systolic, diastolic),
                "topic": "blood_pressure"
            }
        
        if glucose_match:
            value = float(glucose_match.group(1))
            return {
                "action": "analyze_data",
                "data": {"blood_sugar": {"fasting": value}},
                "response": self._analyze_blood_sugar(value),
                "topic": "blood_sugar"
            }
        
        # 3. 用户问健康问题但没提供数据 → 反问
        if any(kw in text for kw in ["高不高", "正常吗", "怎么样", "有问题吗", "危险吗"]):
            if "血压" in text:
                return {
                    "action": "ask_for_data",
                    "response": "请问您的血压是多少呢？或者我可以帮您查一下最近的测量记录。",
                    "topic": "blood_pressure"
                }
            elif "血糖" in text:
                return {
                    "action": "ask_for_data",
                    "response": "请问您的血糖是多少呢？是空腹还是餐后测的？或者我帮您查一下最近的记录。",
                    "topic": "blood_sugar"
                }
            elif "心率" in text:
                return {
                    "action": "ask_for_data",
                    "response": "请问您的心率是多少呢？或者我帮您查一下最近的测量记录。",
                    "topic": "heart_rate"
                }
        
        # 4. 其他情况，直接回答或转给LLM
        return {
            "action": "direct_answer",
            "response": None,
            "topic": None
        }
    
    def _analyze_blood_pressure(self, systolic: int, diastolic: int) -> str:
        """分析血压数值"""
        if systolic < 120 and diastolic < 80:
            level = "正常"
            advice = "您的血压很好，请继续保持健康的生活方式。"
        elif systolic < 140 and diastolic < 90:
            level = "正常高值"
            advice = "血压处于正常高值，建议注意饮食清淡、适量运动、保持良好作息。"
        elif systolic < 160 and diastolic < 100:
            level = "1级高血压（轻度）"
            advice = "建议：①减少盐摄入 ②规律运动 ③监测血压 ④必要时就医。"
        elif systolic < 180 and diastolic < 110:
            level = "2级高血压（中度）"
            advice = "⚠️ 血压偏高，建议尽快就医，在医生指导下用药控制。"
        else:
            level = "3级高血压（重度）"
            advice = "⚠️ 血压较高，请尽快就医！避免剧烈活动，保持情绪稳定。"
        
        return f"""📊 **血压分析结果**

您的血压 **{systolic}/{diastolic} mmHg**，属于【{level}】

{advice}

💡 老年人（≥65岁）血压控制目标可适当放宽至 <150/90 mmHg"""
    
    def _analyze_blood_sugar(self, value: float, is_fasting: bool = True) -> str:
        """分析血糖数值"""
        if is_fasting:
            if value < 6.1:
                level = "正常"
                advice = "空腹血糖正常，请继续保持。"
            elif value < 7.0:
                level = "糖耐量受损（糖尿病前期）"
                advice = "建议：①控制饮食 ②增加运动 ③定期复查 ④避免高糖食物。"
            else:
                level = "偏高（达到糖尿病诊断标准）"
                advice = "⚠️ 空腹血糖偏高，建议就医进一步检查，必要时药物治疗。"
        else:
            if value < 7.8:
                level = "正常"
                advice = "餐后血糖正常。"
            elif value < 11.1:
                level = "糖耐量受损"
                advice = "餐后血糖偏高，注意控制饮食。"
            else:
                level = "偏高"
                advice = "⚠️ 餐后血糖偏高，建议就医。"
        
        return f"""📊 **血糖分析结果**

您的{'空腹' if is_fasting else '餐后'}血糖 **{value} mmol/L**，属于【{level}】

{advice}

💡 控制目标：空腹 4.4-7.0 mmol/L，餐后 <10.0 mmol/L"""
    
    def process_conversation(
        self, 
        user_input: str, 
        conversation_history: List[Dict] = None
    ) -> Dict:
        """
        处理多轮对话
        
        这是主入口方法，整合意图分析和工具调用
        
        Returns:
            {
                "response": 回复文本,
                "action": 执行的动作,
                "tool_called": 是否调用了工具,
                "tool_result": 工具结果（如有）,
                "topic": 当前话题,
                "need_llm": 是否需要LLM进一步处理
            }
        """
        # 分析用户意图
        intent = self.analyze_user_intent(user_input, conversation_history)
        
        result = {
            "action": intent["action"],
            "topic": intent.get("topic"),
            "tool_called": False,
            "tool_result": None,
            "need_llm": False
        }
        
        if intent["action"] == "ask_for_data":
            # 反问用户
            result["response"] = intent["response"]
            
        elif intent["action"] == "call_tool":
            # 调用工具查询数据
            tool_result = self.call(intent["tool_name"], **intent["tool_params"])
            result["tool_called"] = True
            result["tool_result"] = tool_result
            
            if tool_result.success:
                # 基于查询结果生成回复
                result["response"] = self._format_query_result(
                    intent["tool_name"], 
                    tool_result.data,
                    intent.get("topic")
                )
            else:
                result["response"] = "抱歉，查询数据时出现问题，请稍后再试。"
                
        elif intent["action"] == "analyze_data":
            # 直接分析用户提供的数据
            result["response"] = intent["response"]
            result["data"] = intent.get("data")
            
        else:
            # 需要LLM处理
            result["need_llm"] = True
            result["response"] = None
        
        return result
    
    def _format_query_result(self, tool_name: str, data: Dict, topic: str, original_question: str = None) -> str:
        """格式化工具查询结果，并回答用户原始问题"""
        if tool_name == "query_health_records":
            records = data.get("records", [])
            summary = data.get("summary", {})
            
            if not records:
                return "暂时没有找到您的健康记录，建议您测量后记录一下。"
            
            response = f"📋 **您最近{data.get('period', '7天')}的健康记录**\n\n"
            
            # 显示最近几条记录
            for r in records[:3]:
                date = r.get("date", "")
                if "blood_pressure" in r:
                    bp = r["blood_pressure"]
                    response += f"• {date}: 血压 {bp['systolic']}/{bp['diastolic']} mmHg\n"
                if "blood_sugar" in r:
                    bs = r["blood_sugar"]
                    response += f"• {date}: 血糖 空腹{bs.get('fasting', '-')} / 餐后{bs.get('after_meal', '-')} mmol/L\n"
                if "heart_rate" in r:
                    response += f"• {date}: 心率 {r['heart_rate']} 次/分\n"
            
            # 根据数据回答原始问题
            if topic == "blood_pressure" and summary:
                avg_bp = summary.get('blood_pressure_avg', '')
                status = summary.get('blood_pressure_status', '')
                
                response += f"\n📊 **回答您的问题：血压高不高？**\n\n"
                response += f"根据您最近的记录，平均血压为 **{avg_bp}**，"
                
                if status == "偏高":
                    response += "**血压偏高**。\n\n"
                    response += "⚠️ **建议：**\n"
                    response += "• 减少盐分摄入，每日不超过5g\n"
                    response += "• 保持规律作息，避免熬夜\n"
                    response += "• 适当运动，如散步、太极\n"
                    response += "• 保持情绪平稳，避免激动\n"
                    response += "• 建议就医检查，遵医嘱用药"
                elif status == "正常范围":
                    response += "**血压正常**。\n\n"
                    response += "✅ 您的血压控制得很好，请继续保持健康的生活方式！"
                else:
                    response += f"状态为【{status}】。"
                    
            elif topic == "blood_sugar" and records:
                # 计算平均血糖
                fasting_values = [r["blood_sugar"]["fasting"] for r in records if "blood_sugar" in r]
                if fasting_values:
                    avg_fasting = sum(fasting_values) / len(fasting_values)
                    
                    response += f"\n📊 **回答您的问题：血糖正常吗？**\n\n"
                    response += f"根据您最近的记录，平均空腹血糖为 **{avg_fasting:.1f} mmol/L**，"
                    
                    if avg_fasting < 6.1:
                        response += "**血糖正常**。\n\n"
                        response += "✅ 您的血糖控制得很好，请继续保持！"
                    elif avg_fasting < 7.0:
                        response += "**处于糖尿病前期**。\n\n"
                        response += "⚠️ **建议：**\n"
                        response += "• 控制饮食，减少糖分摄入\n"
                        response += "• 增加运动，每天30分钟\n"
                        response += "• 定期监测血糖\n"
                        response += "• 建议就医进一步检查"
                    else:
                        response += "**血糖偏高**。\n\n"
                        response += "⚠️ **建议：**\n"
                        response += "• 严格控制饮食\n"
                        response += "• 规律运动\n"
                        response += "• 尽快就医，遵医嘱治疗"
            
            return response
        
        return "查询完成。"
    
    def get_clarification_questions(self, tool_name: str, provided_params: Dict) -> Optional[Dict]:
        """
        获取工具调用前需要反问用户的问题
        
        实现多轮对话：先收集必要信息，再调用工具
        
        Returns:
            {
                "question": 反问问题,
                "missing_params": 缺失的参数列表,
                "collected_params": 已收集的参数
            }
            如果信息足够则返回 None
        """
        # 定义每个工具需要的参数及对应的反问
        tool_requirements = {
            "query_health_records": {
                "required": [],  # 无必须参数
                "optional_questions": {
                    "record_type": "您想查询哪类健康记录呢？（血压/血糖/心率/全部）",
                    "days": "您想查看最近几天的记录？（默认7天）"
                },
                "default_question": "请问您想查询哪方面的健康记录？血压、血糖还是心率？"
            },
            "query_health_trend": {
                "required": ["metric"],
                "param_questions": {
                    "metric": "您想查看哪个指标的趋势？（血压/血糖/心率）",
                    "period": "您想看多长时间的趋势？（7天/30天）"
                },
                "default_question": "请问您想查看哪个健康指标的变化趋势？"
            },
            "get_health_advice": {
                "required": [],
                "optional_questions": {
                    "health_data": "为了给您更准确的建议，能告诉我您最近的血压或血糖数值吗？"
                },
                "default_question": "请问您目前有什么健康困扰？或者告诉我您的血压、血糖数值，我来给您分析。"
            },
            "query_medications": {
                "required": [],
                "optional_questions": {},
                "default_question": None  # 无需反问，直接查询
            },
            "query_recent_alerts": {
                "required": [],
                "optional_questions": {
                    "days": "您想查看最近几天的预警记录？"
                },
                "default_question": None  # 无需反问，直接查询
            }
        }
        
        if tool_name not in tool_requirements:
            return None
        
        req = tool_requirements[tool_name]
        
        # 检查必需参数
        missing_required = [p for p in req.get("required", []) if p not in provided_params]
        
        if missing_required:
            # 有必需参数缺失，需要反问
            param = missing_required[0]
            question = req.get("param_questions", {}).get(param, req.get("default_question"))
            return {
                "question": question,
                "missing_params": missing_required,
                "collected_params": provided_params,
                "tool_name": tool_name
            }
        
        # 如果没有提供任何参数，且有默认问题，则反问
        if not provided_params and req.get("default_question"):
            return {
                "question": req["default_question"],
                "missing_params": list(req.get("optional_questions", {}).keys()),
                "collected_params": {},
                "tool_name": tool_name
            }
        
        return None  # 信息足够，可以调用工具
    
    def smart_tool_call(
        self, 
        tool_name: str, 
        user_input: str,
        conversation_context: List[Dict] = None,
        collected_params: Dict = None
    ) -> Dict:
        """
        智能工具调用 - 支持多轮对话
        
        流程：
        1. 检查是否需要更多信息
        2. 如需要，返回反问问题
        3. 信息足够时，执行工具调用
        
        Args:
            tool_name: 工具名称
            user_input: 用户当前输入
            conversation_context: 对话上下文
            collected_params: 已收集的参数
        
        Returns:
            {
                "status": "need_clarification" | "ready" | "executed",
                "question": 反问问题（如需要）,
                "result": 工具执行结果（如已执行）,
                "params": 当前收集的参数
            }
        """
        collected_params = collected_params or {}
        
        # 从用户输入中提取参数
        extracted = self._extract_params_from_input(tool_name, user_input)
        collected_params.update(extracted)
        
        # 检查是否需要反问
        clarification = self.get_clarification_questions(tool_name, collected_params)
        
        if clarification:
            return {
                "status": "need_clarification",
                "question": clarification["question"],
                "missing_params": clarification["missing_params"],
                "params": collected_params,
                "tool_name": tool_name
            }
        
        # 信息足够，执行工具调用
        # 过滤掉不属于该工具的参数
        valid_params = self._filter_params_for_tool(tool_name, collected_params)
        result = self.call(tool_name, **valid_params)
        
        return {
            "status": "executed",
            "result": result,
            "params": collected_params,
            "tool_name": tool_name
        }
    
    def _extract_params_from_input(self, tool_name: str, user_input: str) -> Dict:
        """从用户输入中提取工具参数"""
        params = {}
        text = user_input.lower()
        
        # 提取记录类型
        if "血压" in text:
            params["record_type"] = "blood_pressure"
            params["metric"] = "blood_pressure"
        elif "血糖" in text:
            params["record_type"] = "blood_sugar"
            params["metric"] = "blood_sugar"
        elif "心率" in text:
            params["record_type"] = "heart_rate"
            params["metric"] = "heart_rate"
        elif "全部" in text or "所有" in text:
            params["record_type"] = "all"
        
        # 提取时间周期
        import re
        days_match = re.search(r'(\d+)\s*天', text)
        if days_match:
            params["days"] = int(days_match.group(1))
        
        if "一周" in text or "7天" in text:
            params["days"] = 7
            params["period"] = "7d"
        elif "一个月" in text or "30天" in text:
            params["days"] = 30
            params["period"] = "30d"
        
        # 提取健康数值
        bp_match = re.search(r'(\d{2,3})[/／](\d{2,3})', text)
        if bp_match:
            params["health_data"] = {
                "blood_pressure": {
                    "systolic": int(bp_match.group(1)),
                    "diastolic": int(bp_match.group(2))
                }
            }
        
        glucose_match = re.search(r'血糖[是为]?\s*(\d+\.?\d*)', text)
        if glucose_match:
            if "health_data" not in params:
                params["health_data"] = {}
            params["health_data"]["blood_sugar"] = {
                "fasting": float(glucose_match.group(1))
            }
        
        return params
    
    def _filter_params_for_tool(self, tool_name: str, params: Dict) -> Dict:
        """过滤参数，只保留工具接受的参数"""
        tool_params = {
            "query_health_records": ["user_id", "record_type", "days"],
            "query_health_trend": ["user_id", "metric", "period"],
            "query_recent_alerts": ["user_id", "days"],
            "query_medications": ["user_id"],
            "get_health_advice": ["user_id", "health_data"],
        }
        
        allowed = tool_params.get(tool_name, [])
        return {k: v for k, v in params.items() if k in allowed}
    
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
