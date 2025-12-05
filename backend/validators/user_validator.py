"""用户数据验证器"""
from typing import Dict, Any, List, Optional
import re
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class UserDataValidator:
    """用户数据验证器类
    
    负责验证用户相关数据的合法性
    """
    
    # 用户名正则表达式：4-20位字母、数字、下划线，不能以数字开头
    USERNAME_PATTERN = re.compile(r'^[a-zA-Z_][a-zA-Z0-9_]{3,19}$')
    
    # 手机号正则表达式（中国大陆）
    PHONE_PATTERN = re.compile(r'^1[3-9]\d{9}$')
    
    # 身份证号正则表达式（中国大陆18位）
    ID_CARD_PATTERN = re.compile(r'^[1-9]\d{5}(18|19|20)\d{2}(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])\d{3}[0-9Xx]$')
    
    # 密码强度规则：至少8位，包含字母和数字
    PASSWORD_PATTERN = re.compile(r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d@$!%*#?&]{8,}$')
    
    # 姓名正则表达式：2-20位中文或英文
    NAME_PATTERN = re.compile(r'^[\u4e00-\u9fa5a-zA-Z]{2,20}$')
    
    @classmethod
    def validate_username(cls, username: str) -> Dict[str, Any]:
        """验证用户名
        
        Args:
            username: 用户名
            
        Returns:
            Dict[str, Any]: 验证结果
        """
        result = {
            "is_valid": True,
            "errors": []
        }
        
        if not username:
            result["errors"].append("用户名不能为空")
            result["is_valid"] = False
        elif not cls.USERNAME_PATTERN.match(username):
            result["errors"].append("用户名格式不正确：4-20位字母、数字或下划线，不能以数字开头")
            result["is_valid"] = False
        
        return result
    
    @classmethod
    def validate_phone(cls, phone: str) -> Dict[str, Any]:
        """验证手机号
        
        Args:
            phone: 手机号
            
        Returns:
            Dict[str, Any]: 验证结果
        """
        result = {
            "is_valid": True,
            "errors": []
        }
        
        if not phone:
            result["errors"].append("手机号不能为空")
            result["is_valid"] = False
        elif not cls.PHONE_PATTERN.match(phone):
            result["errors"].append("手机号格式不正确，请输入有效的中国大陆手机号")
            result["is_valid"] = False
        
        return result
    
    @classmethod
    def validate_id_card(cls, id_card: str) -> Dict[str, Any]:
        """验证身份证号
        
        Args:
            id_card: 身份证号
            
        Returns:
            Dict[str, Any]: 验证结果
        """
        result = {
            "is_valid": True,
            "errors": []
        }
        
        if not id_card:
            result["errors"].append("身份证号不能为空")
            result["is_valid"] = False
        elif not cls.ID_CARD_PATTERN.match(id_card):
            result["errors"].append("身份证号格式不正确，请输入有效的18位身份证号")
            result["is_valid"] = False
        else:
            # 验证校验码
            if not cls._validate_id_card_checksum(id_card):
                result["errors"].append("身份证号校验失败，请检查输入")
                result["is_valid"] = False
            
            # 验证出生日期
            birth_date_str = id_card[6:14]
            try:
                birth_date = datetime.strptime(birth_date_str, "%Y%m%d")
                # 检查是否是未来日期或年龄过大
                today = datetime.now()
                age = today.year - birth_date.year
                if birth_date > today:
                    result["errors"].append("出生日期不能是未来日期")
                    result["is_valid"] = False
                elif age > 120:
                    result["errors"].append("年龄超出合理范围")
                    result["is_valid"] = False
                elif age < 0:
                    result["errors"].append("出生日期无效")
                    result["is_valid"] = False
            except ValueError:
                result["errors"].append("身份证号中的出生日期无效")
                result["is_valid"] = False
        
        return result
    
    @classmethod
    def _validate_id_card_checksum(cls, id_card: str) -> bool:
        """验证身份证号校验码
        
        Args:
            id_card: 18位身份证号
            
        Returns:
            bool: 校验是否通过
        """
        # 权重系数
        weights = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
        # 校验码映射
        check_codes = ["1", "0", "X", "9", "8", "7", "6", "5", "4", "3", "2"]
        
        # 计算校验和
        check_sum = 0
        for i in range(17):
            check_sum += int(id_card[i]) * weights[i]
        
        # 计算校验码
        check_code = check_codes[check_sum % 11]
        
        # 比较校验码
        return id_card[17].upper() == check_code
    
    @classmethod
    def validate_password(cls, password: str) -> Dict[str, Any]:
        """验证密码强度
        
        Args:
            password: 密码
            
        Returns:
            Dict[str, Any]: 验证结果
        """
        result = {
            "is_valid": True,
            "errors": [],
            "strength": "weak"
        }
        
        if not password:
            result["errors"].append("密码不能为空")
            result["is_valid"] = False
        elif not cls.PASSWORD_PATTERN.match(password):
            result["errors"].append("密码强度不足：至少8位，必须包含字母和数字")
            result["is_valid"] = False
        else:
            # 评估密码强度
            result["strength"] = cls._evaluate_password_strength(password)
        
        return result
    
    @classmethod
    def _evaluate_password_strength(cls, password: str) -> str:
        """评估密码强度
        
        Args:
            password: 密码
            
        Returns:
            str: 强度评级（weak, medium, strong）
        """
        score = 0
        
        # 长度检查
        if len(password) >= 12:
            score += 3
        elif len(password) >= 8:
            score += 1
        
        # 包含小写字母
        if re.search(r'[a-z]', password):
            score += 1
        
        # 包含大写字母
        if re.search(r'[A-Z]', password):
            score += 2
        
        # 包含数字
        if re.search(r'[0-9]', password):
            score += 1
        
        # 包含特殊字符
        if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            score += 3
        
        # 评级
        if score >= 8:
            return "strong"
        elif score >= 5:
            return "medium"
        else:
            return "weak"
    
    @classmethod
    def validate_name(cls, name: str) -> Dict[str, Any]:
        """验证姓名
        
        Args:
            name: 姓名
            
        Returns:
            Dict[str, Any]: 验证结果
        """
        result = {
            "is_valid": True,
            "errors": []
        }
        
        if not name:
            result["errors"].append("姓名不能为空")
            result["is_valid"] = False
        elif not cls.NAME_PATTERN.match(name):
            result["errors"].append("姓名格式不正确：2-20位中文或英文字符")
            result["is_valid"] = False
        
        return result
    
    @classmethod
    def validate_avatar_url(cls, avatar_url: Optional[str]) -> Dict[str, Any]:
        """验证头像URL
        
        Args:
            avatar_url: 头像URL
            
        Returns:
            Dict[str, Any]: 验证结果
        """
        result = {
            "is_valid": True,
            "errors": []
        }
        
        if avatar_url:
            # 简单验证URL格式
            url_pattern = re.compile(r'^(https?://).*\.(jpg|jpeg|png|gif|webp)$', re.IGNORECASE)
            if not url_pattern.match(avatar_url):
                result["errors"].append("头像URL格式不正确，请输入有效的图片URL")
                result["is_valid"] = False
        
        return result
    
    @classmethod
    def validate_email(cls, email: Optional[str]) -> Dict[str, Any]:
        """验证邮箱
        
        Args:
            email: 邮箱地址
            
        Returns:
            Dict[str, Any]: 验证结果
        """
        result = {
            "is_valid": True,
            "errors": []
        }
        
        if email:
            email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
            if not email_pattern.match(email):
                result["errors"].append("邮箱格式不正确")
                result["is_valid"] = False
        
        return result
    
    @classmethod
    def validate_user_registration(cls, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """验证用户注册数据
        
        Args:
            user_data: 用户注册数据字典
            
        Returns:
            Dict[str, Any]: 整体验证结果
        """
        result = {
            "is_valid": True,
            "errors": [],
            "details": {}
        }
        
        # 验证用户名
        if "username" in user_data:
            username_result = cls.validate_username(user_data["username"])
            result["details"]["username"] = username_result
            if not username_result["is_valid"]:
                result["errors"].extend([f"用户名: {err}" for err in username_result["errors"]])
                result["is_valid"] = False
        
        # 验证手机号
        if "phone" in user_data:
            phone_result = cls.validate_phone(user_data["phone"])
            result["details"]["phone"] = phone_result
            if not phone_result["is_valid"]:
                result["errors"].extend([f"手机号: {err}" for err in phone_result["errors"]])
                result["is_valid"] = False
        
        # 验证密码
        if "password" in user_data:
            password_result = cls.validate_password(user_data["password"])
            result["details"]["password"] = password_result
            if not password_result["is_valid"]:
                result["errors"].extend([f"密码: {err}" for err in password_result["errors"]])
                result["is_valid"] = False
        
        # 验证姓名
        if "name" in user_data and user_data["name"]:
            name_result = cls.validate_name(user_data["name"])
            result["details"]["name"] = name_result
            if not name_result["is_valid"]:
                result["errors"].extend([f"姓名: {err}" for err in name_result["errors"]])
                result["is_valid"] = False
        
        # 验证身份证号
        if "id_card" in user_data and user_data["id_card"]:
            id_card_result = cls.validate_id_card(user_data["id_card"])
            result["details"]["id_card"] = id_card_result
            if not id_card_result["is_valid"]:
                result["errors"].extend([f"身份证号: {err}" for err in id_card_result["errors"]])
                result["is_valid"] = False
        
        # 验证头像URL
        if "avatar" in user_data:
            avatar_result = cls.validate_avatar_url(user_data["avatar"])
            result["details"]["avatar"] = avatar_result
            if not avatar_result["is_valid"]:
                result["errors"].extend([f"头像: {err}" for err in avatar_result["errors"]])
                result["is_valid"] = False
        
        # 验证邮箱
        if "email" in user_data:
            email_result = cls.validate_email(user_data["email"])
            result["details"]["email"] = email_result
            if not email_result["is_valid"]:
                result["errors"].extend([f"邮箱: {err}" for err in email_result["errors"]])
                result["is_valid"] = False
        
        return result
    
    @classmethod
    def validate_user_update(cls, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """验证用户更新数据
        
        Args:
            user_data: 用户更新数据字典
            
        Returns:
            Dict[str, Any]: 整体验证结果
        """
        result = {
            "is_valid": True,
            "errors": [],
            "details": {}
        }
        
        # 验证各项可选字段
        if "username" in user_data:
            username_result = cls.validate_username(user_data["username"])
            result["details"]["username"] = username_result
            if not username_result["is_valid"]:
                result["errors"].extend([f"用户名: {err}" for err in username_result["errors"]])
                result["is_valid"] = False
        
        if "phone" in user_data:
            phone_result = cls.validate_phone(user_data["phone"])
            result["details"]["phone"] = phone_result
            if not phone_result["is_valid"]:
                result["errors"].extend([f"手机号: {err}" for err in phone_result["errors"]])
                result["is_valid"] = False
        
        if "password" in user_data:
            password_result = cls.validate_password(user_data["password"])
            result["details"]["password"] = password_result
            if not password_result["is_valid"]:
                result["errors"].extend([f"密码: {err}" for err in password_result["errors"]])
                result["is_valid"] = False
        
        if "name" in user_data and user_data["name"]:
            name_result = cls.validate_name(user_data["name"])
            result["details"]["name"] = name_result
            if not name_result["is_valid"]:
                result["errors"].extend([f"姓名: {err}" for err in name_result["errors"]])
                result["is_valid"] = False
        
        if "id_card" in user_data and user_data["id_card"]:
            id_card_result = cls.validate_id_card(user_data["id_card"])
            result["details"]["id_card"] = id_card_result
            if not id_card_result["is_valid"]:
                result["errors"].extend([f"身份证号: {err}" for err in id_card_result["errors"]])
                result["is_valid"] = False
        
        if "avatar" in user_data:
            avatar_result = cls.validate_avatar_url(user_data["avatar"])
            result["details"]["avatar"] = avatar_result
            if not avatar_result["is_valid"]:
                result["errors"].extend([f"头像: {err}" for err in avatar_result["errors"]])
                result["is_valid"] = False
        
        if "email" in user_data:
            email_result = cls.validate_email(user_data["email"])
            result["details"]["email"] = email_result
            if not email_result["is_valid"]:
                result["errors"].extend([f"邮箱: {err}" for err in email_result["errors"]])
                result["is_valid"] = False
        
        return result


# 创建验证器实例供外部使用
user_validator = UserDataValidator()