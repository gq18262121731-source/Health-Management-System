"""提醒数据验证器"""
from typing import Dict, Any, List, Optional
import re
import logging
from datetime import datetime, time

logger = logging.getLogger(__name__)


class ReminderDataValidator:
    """提醒数据验证器类
    
    负责验证提醒相关数据的合法性
    """
    
    # 提醒标题正则表达式：1-50个字符
    TITLE_PATTERN = re.compile(r'^.{1,50}$')
    
    # 提醒内容正则表达式：0-500个字符
    CONTENT_PATTERN = re.compile(r'^.{0,500}$')
    
    # 允许的提醒类型
    ALLOWED_REMINDER_TYPES = [
        "medication",      # 用药提醒
        "exercise",        # 运动提醒
        "meal",            # 用餐提醒
        "checkup",         # 体检提醒
        "water",           # 喝水提醒
        "rest",            # 休息提醒
        "other"            # 其他提醒
    ]
    
    # 允许的重复频率
    ALLOWED_FREQUENCIES = [
        "once",            # 一次性
        "daily",           # 每天
        "weekly",          # 每周
        "monthly",         # 每月
        "custom"           # 自定义
    ]
    
    # 允许的状态值
    ALLOWED_STATUS = [
        "pending",         # 待执行
        "completed",       # 已完成
        "missed",          # 已错过
        "canceled"         # 已取消
    ]
    
    # 允许的星期几
    ALLOWED_WEEKDAYS = [0, 1, 2, 3, 4, 5, 6]
    
    @classmethod
    def validate_title(cls, title: str) -> Dict[str, Any]:
        """验证提醒标题
        
        Args:
            title: 提醒标题
            
        Returns:
            Dict[str, Any]: 验证结果
        """
        result = {
            "is_valid": True,
            "errors": []
        }
        
        if not title:
            result["errors"].append("提醒标题不能为空")
            result["is_valid"] = False
        elif not cls.TITLE_PATTERN.match(title):
            result["errors"].append("提醒标题长度必须在1-50个字符之间")
            result["is_valid"] = False
        
        return result
    
    @classmethod
    def validate_content(cls, content: Optional[str]) -> Dict[str, Any]:
        """验证提醒内容
        
        Args:
            content: 提醒内容
            
        Returns:
            Dict[str, Any]: 验证结果
        """
        result = {
            "is_valid": True,
            "errors": []
        }
        
        if content and not cls.CONTENT_PATTERN.match(content):
            result["errors"].append("提醒内容长度不能超过500个字符")
            result["is_valid"] = False
        
        return result
    
    @classmethod
    def validate_reminder_type(cls, reminder_type: str) -> Dict[str, Any]:
        """验证提醒类型
        
        Args:
            reminder_type: 提醒类型
            
        Returns:
            Dict[str, Any]: 验证结果
        """
        result = {
            "is_valid": True,
            "errors": []
        }
        
        if not reminder_type:
            result["errors"].append("提醒类型不能为空")
            result["is_valid"] = False
        elif reminder_type not in cls.ALLOWED_REMINDER_TYPES:
            result["errors"].append(f"无效的提醒类型，允许的类型：{', '.join(cls.ALLOWED_REMINDER_TYPES)}")
            result["is_valid"] = False
        
        return result
    
    @classmethod
    def validate_remind_time(cls, remind_time: str) -> Dict[str, Any]:
        """验证提醒时间格式
        
        Args:
            remind_time: 提醒时间字符串，格式为HH:MM
            
        Returns:
            Dict[str, Any]: 验证结果
        """
        result = {
            "is_valid": True,
            "errors": []
        }
        
        if not remind_time:
            result["errors"].append("提醒时间不能为空")
            result["is_valid"] = False
        else:
            # 验证时间格式
            time_pattern = re.compile(r'^([01]?[0-9]|2[0-3]):[0-5][0-9]$')
            if not time_pattern.match(remind_time):
                result["errors"].append("提醒时间格式不正确，请使用HH:MM格式")
                result["is_valid"] = False
            else:
                try:
                    # 尝试解析时间
                    hour, minute = map(int, remind_time.split(':'))
                    if not (0 <= hour <= 23 and 0 <= minute <= 59):
                        result["errors"].append("提醒时间超出有效范围")
                        result["is_valid"] = False
                except ValueError:
                    result["errors"].append("提醒时间格式错误")
                    result["is_valid"] = False
        
        return result
    
    @classmethod
    def validate_start_date(cls, start_date: str) -> Dict[str, Any]:
        """验证开始日期
        
        Args:
            start_date: 开始日期字符串，格式为YYYY-MM-DD
            
        Returns:
            Dict[str, Any]: 验证结果
        """
        result = {
            "is_valid": True,
            "errors": []
        }
        
        if not start_date:
            result["errors"].append("开始日期不能为空")
            result["is_valid"] = False
        else:
            try:
                # 尝试解析日期
                start_datetime = datetime.strptime(start_date, "%Y-%m-%d")
                today = datetime.now().date()
                # 检查是否是过去日期（除了今天）
                if start_datetime.date() < today:
                    result["errors"].append("开始日期不能早于今天")
                    result["is_valid"] = False
            except ValueError:
                result["errors"].append("开始日期格式错误，请使用YYYY-MM-DD格式")
                result["is_valid"] = False
        
        return result
    
    @classmethod
    def validate_end_date(cls, end_date: Optional[str], start_date: str = None) -> Dict[str, Any]:
        """验证结束日期
        
        Args:
            end_date: 结束日期字符串，格式为YYYY-MM-DD
            start_date: 开始日期字符串，用于验证结束日期不能早于开始日期
            
        Returns:
            Dict[str, Any]: 验证结果
        """
        result = {
            "is_valid": True,
            "errors": []
        }
        
        if end_date:
            try:
                # 尝试解析日期
                end_datetime = datetime.strptime(end_date, "%Y-%m-%d")
                
                # 如果提供了开始日期，验证结束日期不能早于开始日期
                if start_date:
                    start_datetime = datetime.strptime(start_date, "%Y-%m-%d")
                    if end_datetime.date() < start_datetime.date():
                        result["errors"].append("结束日期不能早于开始日期")
                        result["is_valid"] = False
            except ValueError:
                result["errors"].append("结束日期格式错误，请使用YYYY-MM-DD格式")
                result["is_valid"] = False
        
        return result
    
    @classmethod
    def validate_frequency(cls, frequency: str) -> Dict[str, Any]:
        """验证提醒频率
        
        Args:
            frequency: 提醒频率
            
        Returns:
            Dict[str, Any]: 验证结果
        """
        result = {
            "is_valid": True,
            "errors": []
        }
        
        if not frequency:
            result["errors"].append("提醒频率不能为空")
            result["is_valid"] = False
        elif frequency not in cls.ALLOWED_FREQUENCIES:
            result["errors"].append(f"无效的提醒频率，允许的频率：{', '.join(cls.ALLOWED_FREQUENCIES)}")
            result["is_valid"] = False
        
        return result
    
    @classmethod
    def validate_weekdays(cls, weekdays: List[int], frequency: str) -> Dict[str, Any]:
        """验证重复的星期几
        
        Args:
            weekdays: 星期几列表，0表示周日，1-6表示周一到周六
            frequency: 提醒频率，用于判断是否需要验证
            
        Returns:
            Dict[str, Any]: 验证结果
        """
        result = {
            "is_valid": True,
            "errors": []
        }
        
        # 只有当频率为weekly时需要验证weekdays
        if frequency == "weekly":
            if not weekdays:
                result["errors"].append("每周提醒必须指定星期几")
                result["is_valid"] = False
            else:
                for day in weekdays:
                    if day not in cls.ALLOWED_WEEKDAYS:
                        result["errors"].append(f"无效的星期几：{day}，有效范围：0-6")
                        result["is_valid"] = False
                
                # 检查是否有重复的星期几
                if len(set(weekdays)) != len(weekdays):
                    result["errors"].append("星期几列表中存在重复值")
                    result["is_valid"] = False
        
        return result
    
    @classmethod
    def validate_monthly_day(cls, monthly_day: int, frequency: str) -> Dict[str, Any]:
        """验证每月提醒的日期
        
        Args:
            monthly_day: 每月的第几天（1-31）
            frequency: 提醒频率，用于判断是否需要验证
            
        Returns:
            Dict[str, Any]: 验证结果
        """
        result = {
            "is_valid": True,
            "errors": []
        }
        
        # 只有当频率为monthly时需要验证monthly_day
        if frequency == "monthly":
            if monthly_day is None:
                result["errors"].append("每月提醒必须指定日期")
                result["is_valid"] = False
            elif not (1 <= monthly_day <= 31):
                result["errors"].append("每月提醒的日期必须在1-31之间")
                result["is_valid"] = False
        
        return result
    
    @classmethod
    def validate_status(cls, status: str) -> Dict[str, Any]:
        """验证提醒状态
        
        Args:
            status: 提醒状态
            
        Returns:
            Dict[str, Any]: 验证结果
        """
        result = {
            "is_valid": True,
            "errors": []
        }
        
        if not status:
            result["errors"].append("状态不能为空")
            result["is_valid"] = False
        elif status not in cls.ALLOWED_STATUS:
            result["errors"].append(f"无效的状态值，允许的状态：{', '.join(cls.ALLOWED_STATUS)}")
            result["is_valid"] = False
        
        return result
    
    @classmethod
    def validate_elderly_id(cls, elderly_id: int) -> Dict[str, Any]:
        """验证老人ID
        
        Args:
            elderly_id: 老人ID
            
        Returns:
            Dict[str, Any]: 验证结果
        """
        result = {
            "is_valid": True,
            "errors": []
        }
        
        if elderly_id is None:
            result["errors"].append("老人ID不能为空")
            result["is_valid"] = False
        elif not isinstance(elderly_id, int) or elderly_id <= 0:
            result["errors"].append("老人ID必须是正整数")
            result["is_valid"] = False
        
        return result
    
    @classmethod
    def validate_reminder_creation(cls, reminder_data: Dict[str, Any]) -> Dict[str, Any]:
        """验证提醒创建数据
        
        Args:
            reminder_data: 提醒创建数据字典
            
        Returns:
            Dict[str, Any]: 整体验证结果
        """
        result = {
            "is_valid": True,
            "errors": [],
            "details": {}
        }
        
        # 验证老人ID
        if "elderly_id" in reminder_data:
            elderly_id_result = cls.validate_elderly_id(reminder_data["elderly_id"])
            result["details"]["elderly_id"] = elderly_id_result
            if not elderly_id_result["is_valid"]:
                result["errors"].extend([f"老人ID: {err}" for err in elderly_id_result["errors"]])
                result["is_valid"] = False
        else:
            result["errors"].append("缺少必需的老人ID")
            result["is_valid"] = False
        
        # 验证标题
        if "title" in reminder_data:
            title_result = cls.validate_title(reminder_data["title"])
            result["details"]["title"] = title_result
            if not title_result["is_valid"]:
                result["errors"].extend([f"标题: {err}" for err in title_result["errors"]])
                result["is_valid"] = False
        else:
            result["errors"].append("缺少必需的标题")
            result["is_valid"] = False
        
        # 验证内容（可选）
        if "content" in reminder_data:
            content_result = cls.validate_content(reminder_data["content"])
            result["details"]["content"] = content_result
            if not content_result["is_valid"]:
                result["errors"].extend([f"内容: {err}" for err in content_result["errors"]])
                result["is_valid"] = False
        
        # 验证提醒类型
        if "reminder_type" in reminder_data:
            reminder_type_result = cls.validate_reminder_type(reminder_data["reminder_type"])
            result["details"]["reminder_type"] = reminder_type_result
            if not reminder_type_result["is_valid"]:
                result["errors"].extend([f"提醒类型: {err}" for err in reminder_type_result["errors"]])
                result["is_valid"] = False
        else:
            result["errors"].append("缺少必需的提醒类型")
            result["is_valid"] = False
        
        # 验证提醒时间
        if "remind_time" in reminder_data:
            remind_time_result = cls.validate_remind_time(reminder_data["remind_time"])
            result["details"]["remind_time"] = remind_time_result
            if not remind_time_result["is_valid"]:
                result["errors"].extend([f"提醒时间: {err}" for err in remind_time_result["errors"]])
                result["is_valid"] = False
        else:
            result["errors"].append("缺少必需的提醒时间")
            result["is_valid"] = False
        
        # 验证开始日期
        start_date = reminder_data.get("start_date", None)
        if start_date:
            start_date_result = cls.validate_start_date(start_date)
            result["details"]["start_date"] = start_date_result
            if not start_date_result["is_valid"]:
                result["errors"].extend([f"开始日期: {err}" for err in start_date_result["errors"]])
                result["is_valid"] = False
        else:
            result["errors"].append("缺少必需的开始日期")
            result["is_valid"] = False
        
        # 验证结束日期（可选）
        if "end_date" in reminder_data:
            end_date_result = cls.validate_end_date(reminder_data["end_date"], start_date)
            result["details"]["end_date"] = end_date_result
            if not end_date_result["is_valid"]:
                result["errors"].extend([f"结束日期: {err}" for err in end_date_result["errors"]])
                result["is_valid"] = False
        
        # 验证频率
        frequency = reminder_data.get("frequency", "once")
        frequency_result = cls.validate_frequency(frequency)
        result["details"]["frequency"] = frequency_result
        if not frequency_result["is_valid"]:
            result["errors"].extend([f"提醒频率: {err}" for err in frequency_result["errors"]])
            result["is_valid"] = False
        else:
            # 根据频率验证特定字段
            # 验证星期几（每周提醒）
            if "weekdays" in reminder_data:
                weekdays_result = cls.validate_weekdays(reminder_data["weekdays"], frequency)
                result["details"]["weekdays"] = weekdays_result
                if not weekdays_result["is_valid"]:
                    result["errors"].extend([f"星期几: {err}" for err in weekdays_result["errors"]])
                    result["is_valid"] = False
            elif frequency == "weekly":
                result["errors"].append("每周提醒必须指定星期几")
                result["is_valid"] = False
            
            # 验证每月日期（每月提醒）
            if "monthly_day" in reminder_data:
                monthly_day_result = cls.validate_monthly_day(reminder_data["monthly_day"], frequency)
                result["details"]["monthly_day"] = monthly_day_result
                if not monthly_day_result["is_valid"]:
                    result["errors"].extend([f"每月日期: {err}" for err in monthly_day_result["errors"]])
                    result["is_valid"] = False
            elif frequency == "monthly":
                result["errors"].append("每月提醒必须指定日期")
                result["is_valid"] = False
        
        # 验证状态（可选，默认为pending）
        if "status" in reminder_data:
            status_result = cls.validate_status(reminder_data["status"])
            result["details"]["status"] = status_result
            if not status_result["is_valid"]:
                result["errors"].extend([f"状态: {err}" for err in status_result["errors"]])
                result["is_valid"] = False
        
        return result
    
    @classmethod
    def validate_reminder_update(cls, reminder_data: Dict[str, Any]) -> Dict[str, Any]:
        """验证提醒更新数据
        
        Args:
            reminder_data: 提醒更新数据字典
            
        Returns:
            Dict[str, Any]: 整体验证结果
        """
        result = {
            "is_valid": True,
            "errors": [],
            "details": {}
        }
        
        # 验证可选字段
        if "title" in reminder_data:
            title_result = cls.validate_title(reminder_data["title"])
            result["details"]["title"] = title_result
            if not title_result["is_valid"]:
                result["errors"].extend([f"标题: {err}" for err in title_result["errors"]])
                result["is_valid"] = False
        
        if "content" in reminder_data:
            content_result = cls.validate_content(reminder_data["content"])
            result["details"]["content"] = content_result
            if not content_result["is_valid"]:
                result["errors"].extend([f"内容: {err}" for err in content_result["errors"]])
                result["is_valid"] = False
        
        if "reminder_type" in reminder_data:
            reminder_type_result = cls.validate_reminder_type(reminder_data["reminder_type"])
            result["details"]["reminder_type"] = reminder_type_result
            if not reminder_type_result["is_valid"]:
                result["errors"].extend([f"提醒类型: {err}" for err in reminder_type_result["errors"]])
                result["is_valid"] = False
        
        if "remind_time" in reminder_data:
            remind_time_result = cls.validate_remind_time(reminder_data["remind_time"])
            result["details"]["remind_time"] = remind_time_result
            if not remind_time_result["is_valid"]:
                result["errors"].extend([f"提醒时间: {err}" for err in remind_time_result["errors"]])
                result["is_valid"] = False
        
        start_date = reminder_data.get("start_date", None)
        if start_date is not None:
            start_date_result = cls.validate_start_date(start_date)
            result["details"]["start_date"] = start_date_result
            if not start_date_result["is_valid"]:
                result["errors"].extend([f"开始日期: {err}" for err in start_date_result["errors"]])
                result["is_valid"] = False
        
        if "end_date" in reminder_data:
            # 如果同时更新了开始日期和结束日期，使用新的开始日期进行验证
            if start_date is not None:
                end_date_result = cls.validate_end_date(reminder_data["end_date"], start_date)
            else:
                # 否则使用原有数据中的开始日期（这里无法验证，依赖调用方提供正确的开始日期）
                end_date_result = cls.validate_end_date(reminder_data["end_date"])
            result["details"]["end_date"] = end_date_result
            if not end_date_result["is_valid"]:
                result["errors"].extend([f"结束日期: {err}" for err in end_date_result["errors"]])
                result["is_valid"] = False
        
        frequency = reminder_data.get("frequency", None)
        if frequency is not None:
            frequency_result = cls.validate_frequency(frequency)
            result["details"]["frequency"] = frequency_result
            if not frequency_result["is_valid"]:
                result["errors"].extend([f"提醒频率: {err}" for err in frequency_result["errors"]])
                result["is_valid"] = False
            else:
                # 根据频率验证特定字段
                if "weekdays" in reminder_data:
                    weekdays_result = cls.validate_weekdays(reminder_data["weekdays"], frequency)
                    result["details"]["weekdays"] = weekdays_result
                    if not weekdays_result["is_valid"]:
                        result["errors"].extend([f"星期几: {err}" for err in weekdays_result["errors"]])
                        result["is_valid"] = False
                
                if "monthly_day" in reminder_data:
                    monthly_day_result = cls.validate_monthly_day(reminder_data["monthly_day"], frequency)
                    result["details"]["monthly_day"] = monthly_day_result
                    if not monthly_day_result["is_valid"]:
                        result["errors"].extend([f"每月日期: {err}" for err in monthly_day_result["errors"]])
                        result["is_valid"] = False
        
        if "status" in reminder_data:
            status_result = cls.validate_status(reminder_data["status"])
            result["details"]["status"] = status_result
            if not status_result["is_valid"]:
                result["errors"].extend([f"状态: {err}" for err in status_result["errors"]])
                result["is_valid"] = False
        
        return result


# 创建验证器实例供外部使用
reminder_validator = ReminderDataValidator()