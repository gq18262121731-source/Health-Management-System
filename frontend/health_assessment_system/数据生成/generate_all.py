"""
Step 6: 一键生成全部数据
========================

运行此脚本生成10个用户30天的完整健康数据
"""

import os
import json
import csv
from datetime import datetime
from typing import List, Dict
from collections import defaultdict

# 导入生成器
from user_profiles import get_all_profiles, HealthStatus
from user_generator import generate_users, save_users, User
from health_generator import generate_health_data, save_records, HealthRecord


# =============================================================================
# 数据验证
# =============================================================================

def validate_data(users: List[User], records: List[HealthRecord]) -> Dict:
    """验证生成的数据质量"""
    
    report = {
        "user_count": len(users),
        "record_count": len(records),
        "validation_passed": True,
        "issues": [],
        "statistics": {}
    }
    
    # 1. 检查用户数量
    if len(users) != 10:
        report["issues"].append(f"用户数量异常: {len(users)} != 10")
        report["validation_passed"] = False
    
    # 2. 按类型统计
    type_counts = defaultdict(int)
    user_record_counts = defaultdict(int)
    outlier_count = 0
    
    for r in records:
        type_counts[r.data_type] += 1
        user_record_counts[r.user_id] += 1
        if r.is_outlier:
            outlier_count += 1
    
    report["statistics"]["by_type"] = dict(type_counts)
    report["statistics"]["by_user"] = dict(user_record_counts)
    report["statistics"]["outliers"] = outlier_count
    report["statistics"]["outlier_rate"] = f"{outlier_count/len(records)*100:.2f}%"
    
    # 3. 检查每个用户是否有数据
    for user in users:
        if user.user_id not in user_record_counts:
            report["issues"].append(f"用户 {user.user_id} 没有健康记录")
            report["validation_passed"] = False
    
    # 4. 检查数据类型是否完整
    expected_types = ["blood_pressure", "glucose", "heart_rate", "sleep", "steps", "weight", "temperature", "spo2"]
    for dtype in expected_types:
        if dtype not in type_counts:
            report["issues"].append(f"缺少数据类型: {dtype}")
            report["validation_passed"] = False
    
    return report


# =============================================================================
# 导出为CSV
# =============================================================================

def export_to_csv(records: List[HealthRecord], filepath: str):
    """导出为CSV格式"""
    
    # 按数据类型分组
    by_type = defaultdict(list)
    for r in records:
        by_type[r.data_type].append(r)
    
    # 为每种类型创建CSV
    for dtype, dtype_records in by_type.items():
        csv_path = filepath.replace(".csv", f"_{dtype}.csv")
        
        if not dtype_records:
            continue
        
        # 获取所有字段
        all_keys = set()
        for r in dtype_records:
            all_keys.update(r.values.keys())
        
        fieldnames = ["record_id", "user_id", "timestamp"] + sorted(all_keys) + ["is_outlier"]
        
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for r in dtype_records:
                row = {
                    "record_id": r.record_id,
                    "user_id": r.user_id,
                    "timestamp": r.timestamp,
                    "is_outlier": r.is_outlier
                }
                row.update(r.values)
                writer.writerow(row)
    
    print(f"  ✓ 导出CSV: {len(by_type)} 个文件")


# =============================================================================
# 生成报告
# =============================================================================

def generate_report(users: List[User], records: List[HealthRecord], validation: Dict) -> str:
    """生成数据报告"""
    
    report_lines = [
        "# 数据生成报告",
        "",
        f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "---",
        "",
        "## 1. 用户统计",
        "",
        f"| 指标 | 数值 |",
        f"|------|------|",
        f"| 用户总数 | {len(users)} |",
    ]
    
    # 按健康状态统计
    status_counts = defaultdict(int)
    for u in users:
        status_counts[u.health_status] += 1
    
    for status, count in status_counts.items():
        report_lines.append(f"| {status} | {count} |")
    
    # 年龄分布
    ages = [u.age for u in users]
    report_lines.extend([
        "",
        f"年龄范围: {min(ages)} - {max(ages)} 岁",
        f"平均年龄: {sum(ages)/len(ages):.1f} 岁",
        "",
    ])
    
    # 用户列表
    report_lines.extend([
        "### 用户列表",
        "",
        "| ID | 姓名 | 性别 | 年龄 | 健康状态 | 病史 |",
        "|-----|------|------|------|----------|------|",
    ])
    
    for u in users:
        history = ", ".join(u.medical_history) if u.medical_history else "无"
        report_lines.append(
            f"| {u.user_id} | {u.name} | {u.gender} | {u.age} | {u.health_status} | {history} |"
        )
    
    # 数据统计
    report_lines.extend([
        "",
        "---",
        "",
        "## 2. 健康数据统计",
        "",
        f"| 指标 | 数值 |",
        f"|------|------|",
        f"| 记录总数 | {len(records)} |",
        f"| 异常值数量 | {validation['statistics']['outliers']} |",
        f"| 异常值比例 | {validation['statistics']['outlier_rate']} |",
        "",
        "### 按类型分布",
        "",
        "| 数据类型 | 记录数 |",
        "|----------|--------|",
    ])
    
    for dtype, count in sorted(validation['statistics']['by_type'].items()):
        report_lines.append(f"| {dtype} | {count} |")
    
    # 按用户分布
    report_lines.extend([
        "",
        "### 按用户分布",
        "",
        "| 用户ID | 记录数 |",
        "|--------|--------|",
    ])
    
    for uid, count in sorted(validation['statistics']['by_user'].items()):
        report_lines.append(f"| {uid} | {count} |")
    
    # 验证结果
    report_lines.extend([
        "",
        "---",
        "",
        "## 3. 数据验证",
        "",
        f"验证结果: {'✅ 通过' if validation['validation_passed'] else '❌ 失败'}",
        "",
    ])
    
    if validation['issues']:
        report_lines.append("问题列表:")
        for issue in validation['issues']:
            report_lines.append(f"- {issue}")
    else:
        report_lines.append("无问题")
    
    # 文件列表
    report_lines.extend([
        "",
        "---",
        "",
        "## 4. 输出文件",
        "",
        "| 文件 | 说明 |",
        "|------|------|",
        "| users.json | 用户基础信息 |",
        "| health_records.json | 健康记录(JSON) |",
        "| health_data_*.csv | 健康记录(CSV) |",
        "| 生成报告.md | 本报告 |",
    ])
    
    return "\n".join(report_lines)


# =============================================================================
# 主函数
# =============================================================================

def main():
    print("=" * 70)
    print("  智能诊断系统 - 虚拟数据生成器")
    print("=" * 70)
    print()
    
    # 设置输出目录
    output_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Step 1: 生成用户
    print("Step 1: 生成用户基础信息...")
    users = generate_users(seed=42)
    print(f"  ✓ 生成 {len(users)} 个用户")
    
    # Step 2: 生成健康数据
    print("\nStep 2: 生成30天健康数据...")
    records = generate_health_data(users, days=30, seed=42)
    print(f"  ✓ 生成 {len(records)} 条记录")
    
    # Step 3: 验证数据
    print("\nStep 3: 验证数据质量...")
    validation = validate_data(users, records)
    if validation['validation_passed']:
        print("  ✓ 数据验证通过")
    else:
        print("  ⚠ 数据验证有问题:")
        for issue in validation['issues']:
            print(f"    - {issue}")
    
    # Step 4: 保存文件
    print("\nStep 4: 保存数据文件...")
    
    # JSON
    users_path = os.path.join(output_dir, "users.json")
    save_users(users, users_path)
    print(f"  ✓ 保存: users.json")
    
    records_path = os.path.join(output_dir, "health_records.json")
    save_records(records, records_path)
    print(f"  ✓ 保存: health_records.json")
    
    # CSV
    csv_path = os.path.join(output_dir, "health_data.csv")
    export_to_csv(records, csv_path)
    
    # 报告
    print("\nStep 5: 生成数据报告...")
    report = generate_report(users, records, validation)
    report_path = os.path.join(output_dir, "生成报告.md")
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"  ✓ 保存: 生成报告.md")
    
    # 完成
    print("\n" + "=" * 70)
    print("  ✅ 数据生成完成!")
    print("=" * 70)
    print()
    print(f"  用户数量: {len(users)}")
    print(f"  记录总数: {len(records)}")
    print(f"  异常值: {validation['statistics']['outliers']} ({validation['statistics']['outlier_rate']})")
    print()
    print("  输出文件:")
    print(f"    - {users_path}")
    print(f"    - {records_path}")
    print(f"    - {report_path}")
    print()


if __name__ == "__main__":
    main()
