"""
控制质量评分雷达图 - 完整示例
运行方式: python 雷达图示例.py
"""

import matplotlib.pyplot as plt
import numpy as np
from math import pi

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False


def draw_control_quality_radar():
    """绘制控制质量三维雷达图"""
    
    # ========== 1. 准备数据 ==========
    # 三个维度
    categories = ['达标率\n(权重40%)', '稳定性\n(权重30%)', '血压水平\n(权重30%)']
    
    # 两个患者的数据（0-100分）
    patient_A = {
        'name': '患者A',
        'scores': [90, 60, 70],  # 达标率高，但波动大
        'color': '#FF6B6B',
        'desc': '达标率90%, CV=15%(波动大)'
    }
    
    patient_B = {
        'name': '患者B', 
        'scores': [80, 95, 75],  # 达标率稍低，但很稳定
        'color': '#4ECDC4',
        'desc': '达标率80%, CV=5%(稳定)'
    }
    
    # ========== 2. 计算综合得分 ==========
    weights = [0.4, 0.3, 0.3]
    
    score_A = sum(s * w for s, w in zip(patient_A['scores'], weights))
    score_B = sum(s * w for s, w in zip(patient_B['scores'], weights))
    
    print(f"患者A综合得分: {score_A:.1f}分")
    print(f"患者B综合得分: {score_B:.1f}分")
    
    # ========== 3. 绘制雷达图 ==========
    N = len(categories)
    
    # 计算角度（均匀分布）
    angles = [n / float(N) * 2 * pi for n in range(N)]
    angles += angles[:1]  # 闭合图形
    
    # 数据也要闭合
    values_A = patient_A['scores'] + patient_A['scores'][:1]
    values_B = patient_B['scores'] + patient_B['scores'][:1]
    
    # 创建图形
    fig, ax = plt.subplots(figsize=(10, 8), subplot_kw=dict(projection='polar'))
    
    # 绘制患者A
    ax.plot(angles, values_A, 'o-', linewidth=2.5, 
            label=f"{patient_A['name']} (总分:{score_A:.0f})", 
            color=patient_A['color'])
    ax.fill(angles, values_A, alpha=0.25, color=patient_A['color'])
    
    # 绘制患者B
    ax.plot(angles, values_B, 's-', linewidth=2.5,
            label=f"{patient_B['name']} (总分:{score_B:.0f})", 
            color=patient_B['color'])
    ax.fill(angles, values_B, alpha=0.25, color=patient_B['color'])
    
    # 设置刻度标签
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, fontsize=13, fontweight='bold')
    
    # 设置径向刻度
    ax.set_ylim(0, 100)
    ax.set_yticks([20, 40, 60, 80, 100])
    ax.set_yticklabels(['20', '40', '60', '80', '100'], fontsize=10, color='gray')
    
    # 网格
    ax.grid(True, linestyle='--', alpha=0.5)
    
    # 标题
    ax.set_title('控制质量三维评分对比\n', fontsize=18, fontweight='bold', pad=20)
    
    # 图例
    ax.legend(loc='upper right', bbox_to_anchor=(1.35, 1.05), fontsize=12)
    
    # 添加说明文字
    fig.text(0.5, 0.02, 
             f"● {patient_A['name']}: {patient_A['desc']}\n"
             f"● {patient_B['name']}: {patient_B['desc']}\n"
             f"结论: 虽然患者A达标率更高，但患者B因稳定性好，综合得分更高！",
             ha='center', fontsize=11, style='italic',
             bbox=dict(boxstyle='round,pad=0.5', facecolor='lightyellow', alpha=0.8))
    
    plt.tight_layout()
    plt.savefig('control_quality_radar.png', dpi=300, bbox_inches='tight')
    print("\n✓ 雷达图已保存: control_quality_radar.png")
    plt.show()


def draw_single_patient_radar(compliance_rate, cv, sbp):
    """
    绘制单个患者的雷达图
    
    参数:
        compliance_rate: 达标率 (0-1)
        cv: 变异系数 (0-1)
        sbp: 平均收缩压 (mmHg)
    """
    # 计算三个维度的得分
    compliance_score = compliance_rate * 100
    stability_score = max(0, 100 - cv * 100)
    
    if sbp < 120:
        bp_score = 100
    elif sbp < 140:
        bp_score = 80 - (sbp - 120) * 2
    else:
        bp_score = max(0, 40 - (sbp - 140))
    
    scores = [compliance_score, stability_score, bp_score]
    
    # 计算综合得分
    weights = [0.4, 0.3, 0.3]
    total_score = sum(s * w for s, w in zip(scores, weights))
    
    print(f"达标率得分: {compliance_score:.1f}")
    print(f"稳定性得分: {stability_score:.1f}")
    print(f"血压水平得分: {bp_score:.1f}")
    print(f"综合得分: {total_score:.1f}")
    
    # 绘制雷达图
    categories = ['达标率', '稳定性', '血压水平']
    N = len(categories)
    angles = [n / float(N) * 2 * pi for n in range(N)]
    angles += angles[:1]
    scores += scores[:1]
    
    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(projection='polar'))
    
    # 根据得分选择颜色
    if total_score >= 80:
        color = '#2ECC71'  # 绿色 - 优秀
        level = '优秀'
    elif total_score >= 60:
        color = '#3498DB'  # 蓝色 - 良好
        level = '良好'
    elif total_score >= 40:
        color = '#F39C12'  # 橙色 - 一般
        level = '一般'
    else:
        color = '#E74C3C'  # 红色 - 较差
        level = '较差'
    
    ax.plot(angles, scores, 'o-', linewidth=2.5, color=color)
    ax.fill(angles, scores, alpha=0.3, color=color)
    
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, fontsize=14, fontweight='bold')
    ax.set_ylim(0, 100)
    ax.set_yticks([20, 40, 60, 80, 100])
    ax.grid(True, linestyle='--', alpha=0.5)
    
    ax.set_title(f'控制质量评分: {total_score:.0f}分 ({level})\n', 
                 fontsize=16, fontweight='bold', color=color)
    
    plt.tight_layout()
    plt.savefig('patient_radar.png', dpi=300, bbox_inches='tight')
    print(f"\n✓ 患者雷达图已保存: patient_radar.png")
    plt.show()
    
    return total_score


if __name__ == '__main__':
    print("=" * 50)
    print("控制质量雷达图示例")
    print("=" * 50)
    
    # 示例1: 两个患者对比
    print("\n【示例1: 两个患者对比】")
    draw_control_quality_radar()
    
    # 示例2: 单个患者评估
    print("\n" + "=" * 50)
    print("【示例2: 单个患者评估】")
    print("输入: 达标率=75%, CV=10%, 平均血压=135mmHg")
    print("-" * 50)
    draw_single_patient_radar(
        compliance_rate=0.75,  # 75%达标率
        cv=0.10,               # 10%变异系数
        sbp=135                # 平均收缩压135
    )
