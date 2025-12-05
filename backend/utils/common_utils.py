"""通用工具类"""
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, date
import uuid
import re
from decimal import Decimal
from pydantic import BaseModel

from config.settings import settings


class ResponseUtils:
    """响应工具类"""
    
    @staticmethod
    def success_response(data: Any = None, message: str = "操作成功") -> Dict[str, Any]:
        """成功响应
        
        Args:
            data: 响应数据
            message: 响应消息
            
        Returns:
            dict: 格式化的响应字典
        """
        return {
            "code": 200,
            "message": message,
            "data": data
        }
    
    @staticmethod
    def error_response(code: int, message: str, error_data: Any = None) -> Dict[str, Any]:
        """错误响应
        
        Args:
            code: 错误码
            message: 错误消息
            error_data: 错误数据
            
        Returns:
            dict: 格式化的错误响应字典
        """
        response = {
            "code": code,
            "message": message
        }
        
        if error_data:
            response["error_data"] = error_data
        
        return response
    
    @staticmethod
    def pagination_response(data: List[Any], total: int, page: int, size: int) -> Dict[str, Any]:
        """分页响应
        
        Args:
            data: 数据列表
            total: 总数
            page: 当前页码
            size: 每页大小
            
        Returns:
            dict: 分页响应字典
        """
        # 计算总页数
        total_pages = (total + size - 1) // size
        
        return {
            "code": 200,
            "message": "操作成功",
            "data": {
                "items": data,
                "total": total,
                "page": page,
                "size": size,
                "total_pages": total_pages
            }
        }


class ValidationUtils:
    """数据验证工具类"""
    
    @staticmethod
    def validate_phone_number(phone_number: str) -> bool:
        """验证手机号格式
        
        Args:
            phone_number: 手机号
            
        Returns:
            bool: 是否有效
        """
        # 中国大陆手机号格式验证
        pattern = r"^1[3-9]\d{9}$"
        return bool(re.match(pattern, phone_number))
    
    @staticmethod
    def validate_id_card(id_card: str) -> bool:
        """验证身份证号格式
        
        Args:
            id_card: 身份证号
            
        Returns:
            bool: 是否有效
        """
        # 简单的18位身份证号格式验证
        pattern = r"^[1-9]\d{5}(19|20)\d{2}(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])\d{3}[\dXx]$"
        return bool(re.match(pattern, id_card))
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """验证邮箱格式
        
        Args:
            email: 邮箱地址
            
        Returns:
            bool: 是否有效
        """
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return bool(re.match(pattern, email))
    
    @staticmethod
    def validate_username(username: str) -> bool:
        """验证用户名格式
        
        Args:
            username: 用户名
            
        Returns:
            bool: 是否有效
        """
        # 用户名长度3-20，只能包含字母、数字、中文和下划线
        if len(username) < 3 or len(username) > 20:
            return False
        
        pattern = r"^[a-zA-Z0-9_\u4e00-\u9fa5]+$"
        return bool(re.match(pattern, username))


class DataUtils:
    """数据处理工具类"""
    
    @staticmethod
    def model_to_dict(model: Any) -> Dict[str, Any]:
        """将SQLAlchemy模型转换为字典
        
        Args:
            model: SQLAlchemy模型实例
            
        Returns:
            dict: 转换后的字典
        """
        if not model:
            return None
        
        result = {}
        for column in model.__table__.columns:
            value = getattr(model, column.name)
            result[column.name] = DataUtils.convert_value(value)
        
        return result
    
    @staticmethod
    def models_to_list(models: List[Any]) -> List[Dict[str, Any]]:
        """将SQLAlchemy模型列表转换为字典列表
        
        Args:
            models: SQLAlchemy模型实例列表
            
        Returns:
            list: 转换后的字典列表
        """
        return [DataUtils.model_to_dict(model) for model in models]
    
    @staticmethod
    def convert_value(value: Any) -> Any:
        """转换值类型
        
        Args:
            value: 要转换的值
            
        Returns:
            Any: 转换后的值
        """
        if isinstance(value, (datetime, date)):
            return value.isoformat()
        elif isinstance(value, uuid.UUID):
            return str(value)
        elif isinstance(value, Decimal):
            return float(value)
        elif hasattr(value, '__dict__'):
            # 处理嵌套对象
            return DataUtils.model_to_dict(value)
        else:
            return value
    
    @staticmethod
    def sanitize_data(data: Dict[str, Any], allowed_fields: List[str]) -> Dict[str, Any]:
        """清理数据，只保留允许的字段
        
        Args:
            data: 输入数据
            allowed_fields: 允许的字段列表
            
        Returns:
            dict: 清理后的数据
        """
        return {k: v for k, v in data.items() if k in allowed_fields}
    
    @staticmethod
    def format_pagination_params(page: int = 1, size: int = 10) -> tuple[int, int]:
        """格式化分页参数
        
        Args:
            page: 页码
            size: 每页大小
            
        Returns:
            tuple: (page, size)
        """
        # 确保页码至少为1
        page = max(1, page)
        
        # 确保每页大小在合理范围内
        size = max(1, min(size, 100))
        
        return page, size
    
    @staticmethod
    def calculate_skip(page: int, size: int) -> int:
        """计算跳过的记录数
        
        Args:
            page: 页码
            size: 每页大小
            
        Returns:
            int: 跳过的记录数
        """
        return (page - 1) * size


class FileUtils:
    """文件处理工具类"""
    
    @staticmethod
    def validate_file_extension(filename: str, allowed_extensions: List[str]) -> bool:
        """验证文件扩展名
        
        Args:
            filename: 文件名
            allowed_extensions: 允许的扩展名列表
            
        Returns:
            bool: 是否有效
        """
        # 获取文件扩展名（小写）
        extension = filename.split('.')[-1].lower() if '.' in filename else ''
        return extension in [ext.lower() for ext in allowed_extensions]
    
    @staticmethod
    def validate_file_size(file_size: int, max_size_mb: float = 5.0) -> bool:
        """验证文件大小
        
        Args:
            file_size: 文件大小（字节）
            max_size_mb: 最大文件大小（MB）
            
        Returns:
            bool: 是否有效
        """
        max_size_bytes = max_size_mb * 1024 * 1024
        return file_size <= max_size_bytes
    
    @staticmethod
    def generate_filename(original_filename: str, prefix: str = "") -> str:
        """生成唯一文件名
        
        Args:
            original_filename: 原始文件名
            prefix: 文件名前缀
            
        Returns:
            str: 唯一文件名
        """
        # 获取文件扩展名
        extension = original_filename.split('.')[-1].lower() if '.' in original_filename else ''
        
        # 生成唯一标识符
        unique_id = str(uuid.uuid4())[:8]
        
        # 生成时间戳
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        
        # 构建文件名
        if extension:
            filename = f"{prefix}{timestamp}_{unique_id}.{extension}"
        else:
            filename = f"{prefix}{timestamp}_{unique_id}"
        
        return filename


class DateUtils:
    """日期时间工具类"""
    
    @staticmethod
    def calculate_age(birth_date: date) -> int:
        """计算年龄
        
        Args:
            birth_date: 出生日期
            
        Returns:
            int: 年龄
        """
        today = date.today()
        age = today.year - birth_date.year
        
        # 调整未到生日的情况
        if (today.month, today.day) < (birth_date.month, birth_date.day):
            age -= 1
        
        return age
    
    @staticmethod
    def get_today_start_and_end() -> tuple[datetime, datetime]:
        """获取今天的开始和结束时间
        
        Returns:
            tuple: (开始时间, 结束时间)
        """
        today = date.today()
        start_time = datetime.combine(today, datetime.min.time())
        end_time = datetime.combine(today, datetime.max.time())
        
        return start_time, end_time
    
    @staticmethod
    def get_week_start_and_end() -> tuple[datetime, datetime]:
        """获取本周的开始和结束时间
        
        Returns:
            tuple: (开始时间, 结束时间)
        """
        today = date.today()
        # 获取本周一
        start_date = today - timedelta(days=today.weekday())
        # 获取本周日
        end_date = start_date + timedelta(days=6)
        
        start_time = datetime.combine(start_date, datetime.min.time())
        end_time = datetime.combine(end_date, datetime.max.time())
        
        return start_time, end_time


# 添加缺失的导入
from datetime import timedelta