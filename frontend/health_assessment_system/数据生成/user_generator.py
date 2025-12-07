"""
Step 2: 用户基础信息生成器
==========================

根据用户画像生成10个虚拟用户的基础信息
"""

import random
from datetime import datetime, timedelta
from typing import Dict, List
from dataclasses import dataclass, asdict
import json

from user_profiles import get_all_profiles, UserProfile, HealthStatus


# =============================================================================
# 姓名库
# =============================================================================

SURNAMES = [
    "张", "王", "李", "赵", "刘", "陈", "杨", "黄", "周", "吴",
    "徐", "孙", "马", "朱", "胡", "郭", "何", "林", "罗", "郑"
]

MALE_NAMES = [
    "建国", "国强", "志强", "建军", "建华", "伟", "军", "勇", "涛", "明",
    "永强", "文明", "建平", "志明", "德华", "春生", "福生", "国庆", "建成", "正"
]

FEMALE_NAMES = [
    "秀英", "桂英", "秀兰", "玉兰", "淑芬", "桂芳", "玉珍", "凤英", "秀珍", "翠花",
    "淑华", "秀华", "桂珍", "春梅", "冬梅", "玉华", "淑兰", "美华", "丽华", "秀芳"
]


# =============================================================================
# 用户数据模型
# =============================================================================

@dataclass
class User:
    """用户基础信息"""
    user_id: str
    name: str
    gender: str
    age: int
    height: float        # cm
    weight: float        # kg
    bmi: float
    
    # 健康信息
    health_status: str
    medical_history: List[str]
    medications: List[str]
    
    # 联系信息
    phone: str
    emergency_contact: str
    emergency_phone: str
    address: str
    
    # 系统信息
    registration_date: str
    profile_id: str      # 对应的画像ID
    
    def to_dict(self) -> Dict:
        return asdict(self)


# =============================================================================
# 用户生成器
# =============================================================================

class UserGenerator:
    """用户信息生成器"""
    
    def __init__(self, seed: int = 42):
        random.seed(seed)
        self.user_counter = 0
    
    def generate_name(self, is_female: bool) -> str:
        """生成中文姓名"""
        surname = random.choice(SURNAMES)
        if is_female:
            given_name = random.choice(FEMALE_NAMES)
        else:
            given_name = random.choice(MALE_NAMES)
        return surname + given_name
    
    def generate_phone(self) -> str:
        """生成手机号"""
        prefixes = ["138", "139", "136", "137", "158", "159", "188", "189"]
        return random.choice(prefixes) + "".join([str(random.randint(0, 9)) for _ in range(8)])
    
    def generate_address(self) -> str:
        """生成地址"""
        districts = ["朝阳区", "海淀区", "西城区", "东城区", "丰台区", "石景山区"]
        streets = ["幸福路", "和平街", "建设路", "人民路", "中山路", "解放路"]
        communities = ["阳光小区", "幸福家园", "和谐苑", "康乐园", "祥和里", "安居小区"]
        
        district = random.choice(districts)
        street = random.choice(streets)
        community = random.choice(communities)
        building = random.randint(1, 20)
        unit = random.randint(1, 4)
        room = random.randint(101, 2405)
        
        return f"北京市{district}{street}{community}{building}号楼{unit}单元{room}"
    
    def generate_emergency_contact(self, user_name: str, is_female: bool) -> tuple:
        """生成紧急联系人"""
        relations = ["儿子", "女儿", "儿媳", "女婿"] if random.random() > 0.3 else ["老伴"]
        relation = random.choice(relations)
        
        # 生成联系人姓名
        surname = user_name[0]  # 同姓
        if relation in ["儿子", "女婿"]:
            contact_name = surname + random.choice(MALE_NAMES[:10])
        else:
            contact_name = surname + random.choice(FEMALE_NAMES[:10])
        
        contact_info = f"{contact_name}({relation})"
        contact_phone = self.generate_phone()
        
        return contact_info, contact_phone
    
    def calculate_bmi(self, weight: float, height: float) -> float:
        """计算BMI"""
        height_m = height / 100
        return round(weight / (height_m ** 2), 1)
    
    def generate_user(self, profile: UserProfile) -> User:
        """根据画像生成用户"""
        self.user_counter += 1
        
        # 确定性别
        is_female = profile.gender_ratio >= random.random()
        gender = "女" if is_female else "男"
        
        # 生成姓名
        name = self.generate_name(is_female)
        
        # 生成年龄
        age = random.randint(profile.age_range[0], profile.age_range[1])
        
        # 生成身高体重
        if is_female:
            height = round(random.gauss(158, 5), 1)
        else:
            height = round(random.gauss(168, 6), 1)
        
        # 根据BMI范围计算体重
        target_bmi = random.uniform(profile.bmi_range[0], profile.bmi_range[1])
        height_m = height / 100
        weight = round(target_bmi * (height_m ** 2), 1)
        bmi = self.calculate_bmi(weight, height)
        
        # 紧急联系人
        emergency_contact, emergency_phone = self.generate_emergency_contact(name, is_female)
        
        # 注册日期 (过去1-12个月)
        days_ago = random.randint(30, 365)
        reg_date = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d")
        
        # 用户ID
        user_id = f"elderly_{self.user_counter:03d}"
        
        return User(
            user_id=user_id,
            name=name,
            gender=gender,
            age=age,
            height=height,
            weight=weight,
            bmi=bmi,
            health_status=profile.health_status.value,
            medical_history=profile.medical_history.copy(),
            medications=profile.medications.copy(),
            phone=self.generate_phone(),
            emergency_contact=emergency_contact,
            emergency_phone=emergency_phone,
            address=self.generate_address(),
            registration_date=reg_date,
            profile_id=profile.profile_id
        )
    
    def generate_all_users(self) -> List[User]:
        """生成所有用户"""
        profiles = get_all_profiles()
        users = []
        
        for profile in profiles:
            user = self.generate_user(profile)
            users.append(user)
        
        return users


# =============================================================================
# 导出函数
# =============================================================================

def generate_users(seed: int = 42) -> List[User]:
    """生成10个用户"""
    generator = UserGenerator(seed=seed)
    return generator.generate_all_users()


def users_to_json(users: List[User]) -> str:
    """转换为JSON字符串"""
    return json.dumps(
        [u.to_dict() for u in users],
        ensure_ascii=False,
        indent=2
    )


def save_users(users: List[User], filepath: str):
    """保存用户数据到文件"""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(
            [u.to_dict() for u in users],
            f,
            ensure_ascii=False,
            indent=2
        )


# =============================================================================
# 测试
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("用户信息生成器")
    print("=" * 60)
    
    users = generate_users(seed=42)
    
    print(f"\n成功生成 {len(users)} 个用户:\n")
    print("-" * 80)
    
    for user in users:
        print(f"  {user.user_id}: {user.name}")
        print(f"    性别: {user.gender}, 年龄: {user.age}岁")
        print(f"    身高: {user.height}cm, 体重: {user.weight}kg, BMI: {user.bmi}")
        print(f"    健康状态: {user.health_status}")
        print(f"    病史: {user.medical_history or '无'}")
        print(f"    用药: {user.medications or '无'}")
        print(f"    紧急联系人: {user.emergency_contact}")
        print(f"    画像ID: {user.profile_id}")
        print()
    
    # 保存到文件
    save_users(users, "users.json")
    print(f"✓ 用户数据已保存到 users.json")
