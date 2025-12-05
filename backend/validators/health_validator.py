"""健康数据验证器"""
from typing import Dict, Any, Optional, List
from datetime import datetime, date, time
import logging
import re

logger = logging.getLogger(__name__)


class HealthDataValidator:
    """健康数据验证器类
    
    负责验证各种健康数据的合法性和合理性
    """
    
    # 健康数据正常值范围参考
    HEALTH_DATA_RANGES = {
        "blood_pressure": {
            "systolic": {"min": 90, "max": 140},    # 收缩压
            "diastolic": {"min": 60, "max": 90},  # 舒张压
        },
        "heart_rate": {"min": 60, "max": 100},       # 心率
        "blood_sugar": {"min": 3.9, "max": 6.1},     # 血糖
        "body_temp": {"min": 36.0, "max": 37.2},     # 体温
        "oxygen": {"min": 95, "max": 100},          # 血氧
        "weight": {"min": 30, "max": 200},          # 体重
        "height": {"min": 100, "max": 220},         # 身高
        "steps": {"min": 0, "max": 50000},          # 步数
    }
    
    @classmethod
    def validate_blood_pressure(cls, systolic: int, diastolic: int) -> Dict[str, Any]:
        """验证血压数据
        
        Args:
            systolic: 收缩压
            diastolic: 舒张压
            
        Returns:
            Dict[str, Any]: 包含验证结果的字典
        """
        result = {
            "is_valid": True,
            "errors": [],
            "warnings": []
        }
        
        # 验证收缩压范围
        sys_range = cls.HEALTH_DATA_RANGES["blood_pressure"]["systolic"]
        if systolic < sys_range["min"]:
            result["errors"].append(f"收缩压过低，正常值范围: {sys_range['min']}-{sys_range['max']}")
            result["is_valid"] = False
        elif systolic > sys_range["max"]:
            result["warnings"].append(f"收缩压偏高，正常值范围: {sys_range['min']}-{sys_range['max']}")
        
        # 验证舒张压范围
        dia_range = cls.HEALTH_DATA_RANGES["blood_pressure"]["diastolic"]
        if diastolic < dia_range["min"]:
            result["errors"].append(f"舒张压过低，正常值范围: {dia_range['min']}-{dia_range['max']}")
            result["is_valid"] = False
        elif diastolic > dia_range["max"]:
            result["warnings"].append(f"舒张压偏高，正常值范围: {dia_range['min']}-{dia_range['max']}")
        
        # 验证收缩压是否大于舒张压
        if systolic <= diastolic:
            result["errors"].append("收缩压必须大于舒张压")
            result["is_valid"] = False
        
        # 计算脉压差
        pulse_pressure = systolic - diastolic
        if pulse_pressure < 30:
            result["warnings"].append("脉压差过小")
        elif pulse_pressure > 60:
            result["warnings"].append("脉压差过大")
        
        return result
    
    @classmethod
    def validate_heart_rate(cls, heart_rate: int) -> Dict[str, Any]:
        """验证心率数据
        
        Args:
            heart_rate: 心率
            
        Returns:
            Dict[str, Any]: 包含验证结果的字典
        """
        result = {
            "is_valid": True,
            "errors": [],
            "warnings": []
        }
        
        hr_range = cls.HEALTH_DATA_RANGES["heart_rate"]
        if heart_rate < hr_range["min"]:
            result["warnings"].append(f"心率偏低，正常值范围: {hr_range['min']}-{hr_range['max']}")
        elif heart_rate > hr_range["max"]:
            result["warnings"].append(f"心率偏高，正常值范围: {hr_range['min']}-{hr_range['max']}")
        
        # 极端情况标记为错误
        if heart_rate < 50:
            result["errors"].append("心率过低，请及时就医")
            result["is_valid"] = False
        elif heart_rate > 120:
            result["errors"].append("心率过高，请及时就医")
            result["is_valid"] = False
        
        return result
    
    @classmethod
    def validate_blood_sugar(cls, blood_sugar: float, is_fasting: bool = True) -> Dict[str, Any]:
        """验证血糖数据
        
        Args:
            blood_sugar: 血糖值
            is_fasting: 是否为空腹血糖
            
        Returns:
            Dict[str, Any]: 包含验证结果的字典
        """
        result = {
            "is_valid": True,
            "errors": [],
            "warnings": []
        }
        
        # 根据是否空腹调整参考范围
        if is_fasting:
            min_val, max_val = 3.9, 6.1
        else:
            min_val, max_val = 3.9, 7.8
        
        if blood_sugar < min_val:
            result["warnings"].append(f"血糖偏低，{'空腹' if is_fasting else '餐后'}正常值范围: {min_val}-{max_val} mmol/L")
        elif blood_sugar > max_val:
            result["warnings"].append(f"血糖偏高，{'空腹' if is_fasting else '餐后'}正常值范围: {min_val}-{max_val} mmol/L")
        
        # 极端情况标记为错误
        if blood_sugar < 3.0:
            result["errors"].append("血糖过低，请及时补充糖分并就医")
            result["is_valid"] = False
        elif blood_sugar > 11.1:
            result["errors"].append("血糖过高，请注意控制血糖并就医")
            result["is_valid"] = False
        
        return result
    
    @classmethod
    def validate_body_temp(cls, body_temp: float) -> Dict[str, Any]:
        """验证体温数据
        
        Args:
            body_temp: 体温
            
        Returns:
            Dict[str, Any]: 包含验证结果的字典
        """
        result = {
            "is_valid": True,
            "errors": [],
            "warnings": []
        }
        
        temp_range = cls.HEALTH_DATA_RANGES["body_temp"]
        if body_temp < temp_range["min"]:
            result["warnings"].append(f"体温偏低，正常值范围: {temp_range['min']}-{temp_range['max']} °C")
        elif body_temp > temp_range["max"]:
            result["warnings"].append(f"体温偏高，正常值范围: {temp_range['min']}-{temp_range['max']} °C")
        
        # 极端情况标记为错误
        if body_temp < 35.0:
            result["errors"].append("体温过低，请及时就医")
            result["is_valid"] = False
        elif body_temp > 38.5:
            result["errors"].append("体温过高，请注意散热并就医")
            result["is_valid"] = False
        
        return result
    
    @classmethod
    def validate_oxygen(cls, oxygen: int) -> Dict[str, Any]:
        """验证血氧数据
        
        Args:
            oxygen: 血氧饱和度
            
        Returns:
            Dict[str, Any]: 包含验证结果的字典
        """
        result = {
            "is_valid": True,
            "errors": [],
            "warnings": []
        }
        
        oxygen_range = cls.HEALTH_DATA_RANGES["oxygen"]
        if oxygen < oxygen_range["min"]:
            result["errors"].append(f"血氧偏低，正常值范围: {oxygen_range['min']}-{oxygen_range['max']}%")
            result["is_valid"] = False
        elif oxygen > oxygen_range["max"]:
            # 血氧超过100%可能是测量误差
            result["warnings"].append("血氧值可能存在测量误差")
        
        # 严重低血氧警告
        if oxygen < 90:
            result["errors"].append("血氧严重偏低，请立即就医")
            result["is_valid"] = False
        
        return result
    
    @classmethod
    def validate_weight(cls, weight: float, height: Optional[float] = None) -> Dict[str, Any]:
        """验证体重数据
        
        Args:
            weight: 体重
            height: 身高（用于计算BMI）
            
        Returns:
            Dict[str, Any]: 包含验证结果的字典
        """
        result = {
            "is_valid": True,
            "errors": [],
            "warnings": []
        }
        
        weight_range = cls.HEALTH_DATA_RANGES["weight"]
        if weight < weight_range["min"]:
            result["warnings"].append(f"体重过轻，建议范围: {weight_range['min']}-{weight_range['max']} kg")
        elif weight > weight_range["max"]:
            result["warnings"].append(f"体重过重，建议范围: {weight_range['min']}-{weight_range['max']} kg")
        
        # 计算BMI并提供建议
        if height:
            bmi = weight / ((height / 100) ** 2)
            if bmi < 18.5:
                result["warnings"].append(f"BMI为{bmi:.1f}，体重过轻，建议适当增重")
            elif 18.5 <= bmi < 24:
                result["warnings"].append(f"BMI为{bmi:.1f}，体重正常，继续保持")
            elif 24 <= bmi < 28:
                result["warnings"].append(f"BMI为{bmi:.1f}，超重，建议适当减重")
            else:
                result["warnings"].append(f"BMI为{bmi:.1f}，肥胖，建议减重并就医咨询")
        
        return result
    
    @classmethod
    def validate_steps(cls, steps: int, date_recorded: Optional[date] = None) -> Dict[str, Any]:
        """验证步数数据
        
        Args:
            steps: 步数
            date_recorded: 记录日期
            
        Returns:
            Dict[str, Any]: 包含验证结果的字典
        """
        result = {
            "is_valid": True,
            "errors": [],
            "warnings": []
        }
        
        steps_range = cls.HEALTH_DATA_RANGES["steps"]
        if steps < steps_range["min"]:
            result["warnings"].append("今日步数较少，建议适当增加运动")
        elif steps > steps_range["max"]:
            result["warnings"].append("步数异常，可能存在测量误差")
        
        # 步数建议
        if 0 < steps < 5000:
            result["warnings"].append("运动量不足，建议每天至少走6000步")
        elif steps >= 10000:
            result["warnings"].append("运动量充足，继续保持")
        
        return result
    
    @classmethod
    def validate_health_record(cls, health_data: Dict[str, Any]) -> Dict[str, Any]:
        """验证完整的健康记录
        
        Args:
            health_data: 包含各种健康数据的字典
            
        Returns:
            Dict[str, Any]: 包含整体验证结果的字典
        """
        result = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "details": {}
        }
        
        # 验证血压
        if "systolic" in health_data and "diastolic" in health_data:
            bp_validation = cls.validate_blood_pressure(
                health_data["systolic"], health_data["diastolic"]
            )
            result["details"]["blood_pressure"] = bp_validation
            if bp_validation["errors"]:
                result["errors"].extend([f"血压: {err}" for err in bp_validation["errors"]])
                result["is_valid"] = False
            if bp_validation["warnings"]:
                result["warnings"].extend([f"血压: {warn}" for warn in bp_validation["warnings"]])
        
        # 验证心率
        if "heart_rate" in health_data:
            hr_validation = cls.validate_heart_rate(health_data["heart_rate"])
            result["details"]["heart_rate"] = hr_validation
            if hr_validation["errors"]:
                result["errors"].extend([f"心率: {err}" for err in hr_validation["errors"]])
                result["is_valid"] = False
            if hr_validation["warnings"]:
                result["warnings"].extend([f"心率: {warn}" for warn in hr_validation["warnings"]])
        
        # 验证血糖
        if "blood_sugar" in health_data:
            is_fasting = health_data.get("is_fasting", True)
            bs_validation = cls.validate_blood_sugar(
                health_data["blood_sugar"], is_fasting
            )
            result["details"]["blood_sugar"] = bs_validation
            if bs_validation["errors"]:
                result["errors"].extend([f"血糖: {err}" for err in bs_validation["errors"]])
                result["is_valid"] = False
            if bs_validation["warnings"]:
                result["warnings"].extend([f"血糖: {warn}" for warn in bs_validation["warnings"]])
        
        # 验证体温
        if "body_temp" in health_data:
            temp_validation = cls.validate_body_temp(health_data["body_temp"])
            result["details"]["body_temp"] = temp_validation
            if temp_validation["errors"]:
                result["errors"].extend([f"体温: {err}" for err in temp_validation["errors"]])
                result["is_valid"] = False
            if temp_validation["warnings"]:
                result["warnings"].extend([f"体温: {warn}" for warn in temp_validation["warnings"]])
        
        # 验证血氧
        if "oxygen" in health_data:
            oxygen_validation = cls.validate_oxygen(health_data["oxygen"])
            result["details"]["oxygen"] = oxygen_validation
            if oxygen_validation["errors"]:
                result["errors"].extend([f"血氧: {err}" for err in oxygen_validation["errors"]])
                result["is_valid"] = False
            if oxygen_validation["warnings"]:
                result["warnings"].extend([f"血氧: {warn}" for warn in oxygen_validation["warnings"]])
        
        # 验证体重
        if "weight" in health_data:
            height = health_data.get("height")
            weight_validation = cls.validate_weight(
                health_data["weight"], height
            )
            result["details"]["weight"] = weight_validation
            if weight_validation["errors"]:
                result["errors"].extend([f"体重: {err}" for err in weight_validation["errors"]])
                result["is_valid"] = False
            if weight_validation["warnings"]:
                result["warnings"].extend([f"体重: {warn}" for warn in weight_validation["warnings"]])
        
        # 验证步数
        if "steps" in health_data:
            date_recorded = health_data.get("record_date")
            steps_validation = cls.validate_steps(
                health_data["steps"], date_recorded
            )
            result["details"]["steps"] = steps_validation
            if steps_validation["errors"]:
                result["errors"].extend([f"步数: {err}" for err in steps_validation["errors"]])
                result["is_valid"] = False
            if steps_validation["warnings"]:
                result["warnings"].extend([f"步数: {warn}" for warn in steps_validation["warnings"]])
        
        # 验证记录时间
        if "record_time" in health_data:
            if not isinstance(health_data["record_time"], time):
                try:
                    # 尝试转换时间格式
                    if isinstance(health_data["record_time"], str):
                        time.fromisoformat(health_data["record_time"])
                except:
                    result["errors"].append("记录时间格式不正确")
                    result["is_valid"] = False
        
        return result
    
    @classmethod
    def detect_abnormal_values(cls, health_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """检测异常健康值并生成警报
        
        Args:
            health_data: 健康数据字典
            
        Returns:
            List[Dict[str, Any]]: 异常值警报列表
        """
        alerts = []
        validation_result = cls.validate_health_record(health_data)
        
        # 根据错误和警告生成警报
        for field, details in validation_result["details"].items():
            if details["errors"]:
                for error in details["errors"]:
                    alerts.append({
                        "field": field,
                        "message": error,
                        "severity": "high",
                        "value": health_data.get(field, "N/A")
                    })
            elif details["warnings"]:
                for warning in details["warnings"]:
                    alerts.append({
                        "field": field,
                        "message": warning,
                        "severity": "medium",
                        "value": health_data.get(field, "N/A")
                    })
        
        return alerts


# 创建验证器实例供外部使用
health_validator = HealthDataValidator()