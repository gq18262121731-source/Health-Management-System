"""
算法可视化代码 - 用于演讲PPT制作
Visualization Code for Presentation
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from scipy import stats

# 设置中文字体
matplotlib.rcParams['font.sans-serif'] = ['SimHei']  # 用黑体显示中文
matplotlib.rcParams['axes.unicode_minus'] = False  # 正常显示负号

# 设置全局样式
plt.style.use('seaborn-v0_8-darkgrid')


def visualize_iqr_outlier_detection():
    """可视化IQR异常值检测"""
    # 生成模拟血压数据
    np.random.seed(42)
    normal_data = np.random.normal(125, 5, 50)  # 正常血压
    outliers = np.array([200, 95, 180])  # 异常值
    data = np.concatenate([normal_data, outliers])
    
    # 计算IQR
    Q1 = np.percentile(data, 25)
    Q3 = np.percentile(data, 75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    
    # 绘图
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # 左图：箱线图
    bp = ax1.boxplot(data, vert=True, patch_artist=True)
    bp['boxes'][0].set_facecolor('lightblue')
    bp['medians'][0].set_color('red')
    bp['medians'][0].set_linewidth(2)
    
    # 标注异常值
    outlier_mask = (data < lower_bound) | (data > upper_bound)
    outlier_values = data[outlier_mask]
    for val in outlier_values:
        ax1.plot(1, val, 'ro', markersize=10, label='异常值' if val == outlier_values[0] else '')
    
    ax1.set_ylabel('血压 (mmHg)', fontsize=14)
    ax1.set_title('IQR异常值检测 - 箱线图', fontsize=16, fontweight='bold')
    ax1.axhline(y=upper_bound, color='r', linestyle='--', alpha=0.5, label=f'上界={upper_bound:.1f}')
    ax1.axhline(y=lower_bound, color='r', linestyle='--', alpha=0.5, label=f'下界={lower_bound:.1f}')
    ax1.legend(fontsize=10)
    ax1.grid(True, alpha=0.3)
    
    # 右图：散点图
    x = np.arange(len(data))
    colors = ['red' if outlier else 'blue' for outlier in outlier_mask]
    ax2.scatter(x, data, c=colors, s=50, alpha=0.6)
    ax2.axhline(y=upper_bound, color='r', linestyle='--', linewidth=2, label=f'上界={upper_bound:.1f}')
    ax2.axhline(y=lower_bound, color='r', linestyle='--', linewidth=2, label=f'下界={lower_bound:.1f}')
    ax2.axhline(y=Q1, color='g', linestyle=':', alpha=0.5, label=f'Q1={Q1:.1f}')
    ax2.axhline(y=Q3, color='g', linestyle=':', alpha=0.5, label=f'Q3={Q3:.1f}')
    ax2.set_xlabel('数据点索引', fontsize=14)
    ax2.set_ylabel('血压 (mmHg)', fontsize=14)
    ax2.set_title('IQR异常值检测 - 散点图', fontsize=16, fontweight='bold')
    ax2.legend(fontsize=10)
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('iqr_outlier_detection.png', dpi=300, bbox_inches='tight')
    print("✓ IQR异常值检测图已保存: iqr_outlier_detection.png")
    plt.close()


def visualize_zscore():
    """可视化Z-score标准化"""
    # 生成正态分布数据
    mu, sigma = 125, 10
    x = np.linspace(mu - 4*sigma, mu + 4*sigma, 1000)
    y = stats.norm.pdf(x, mu, sigma)
    
    fig, ax = plt.subplots(figsize=(12, 7))
    
    # 绘制正态分布曲线
    ax.plot(x, y, 'b-', linewidth=2, label='正态分布')
    ax.fill_between(x, y, where=(x >= mu-3*sigma) & (x <= mu+3*sigma), 
                     alpha=0.3, color='green', label='±3σ (99.7%)')
    ax.fill_between(x, y, where=(x >= mu-2*sigma) & (x <= mu+2*sigma), 
                     alpha=0.3, color='yellow', label='±2σ (95%)')
    ax.fill_between(x, y, where=(x >= mu-sigma) & (x <= mu+sigma), 
                     alpha=0.3, color='orange', label='±1σ (68%)')
    
    # 标注关键点
    for i in range(-3, 4):
        x_pos = mu + i * sigma
        ax.axvline(x=x_pos, color='gray', linestyle='--', alpha=0.5)
        ax.text(x_pos, -0.002, f'μ{i:+d}σ\n{x_pos:.0f}', 
                ha='center', fontsize=10)
    
    # 标注异常区域
    ax.fill_between(x, y, where=(x < mu-3*sigma), alpha=0.5, color='red', label='极端异常')
    ax.fill_between(x, y, where=(x > mu+3*sigma), alpha=0.5, color='red')
    
    ax.set_xlabel('血压 (mmHg)', fontsize=14)
    ax.set_ylabel('概率密度', fontsize=14)
    ax.set_title('Z-score标准化与3σ原则', fontsize=16, fontweight='bold')
    ax.legend(fontsize=11, loc='upper right')
    ax.grid(True, alpha=0.3)
    
    # 添加说明文本
    ax.text(0.02, 0.98, 
            'Z-score = (x - μ) / σ\n|Z| > 3 → 极端异常\n|Z| > 2 → 可疑异常',
            transform=ax.transAxes, fontsize=12,
            verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.tight_layout()
    plt.savefig('zscore_visualization.png', dpi=300, bbox_inches='tight')
    print("✓ Z-score可视化图已保存: zscore_visualization.png")
    plt.close()


def visualize_fuzzy_membership():
    """可视化模糊逻辑隶属度函数"""
    sbp = np.linspace(100, 180, 1000)
    
    # 定义隶属度函数
    def normal(x):
        return np.where(x < 120, 1.0, 
                       np.where(x < 140, 1 - (x - 120) / 20, 0.0))
    
    def elevated(x):
        return np.where(x < 120, 0.0,
                       np.where(x < 140, (x - 120) / 20,
                               np.where(x < 160, 1 - (x - 140) / 20, 0.0)))
    
    def hypertension(x):
        return np.where(x < 140, 0.0,
                       np.where(x < 160, (x - 140) / 20, 1.0))
    
    fig, ax = plt.subplots(figsize=(12, 7))
    
    # 绘制隶属度函数
    ax.plot(sbp, normal(sbp), 'g-', linewidth=2, label='正常')
    ax.plot(sbp, elevated(sbp), 'y-', linewidth=2, label='偏高')
    ax.plot(sbp, hypertension(sbp), 'r-', linewidth=2, label='高血压')
    
    # 标注关键点
    key_points = [120, 140, 160]
    for point in key_points:
        ax.axvline(x=point, color='gray', linestyle='--', alpha=0.5)
        ax.text(point, -0.08, f'{point}', ha='center', fontsize=11)
    
    # 示例：血压135的隶属度
    example_sbp = 135
    ax.axvline(x=example_sbp, color='blue', linestyle=':', linewidth=2, alpha=0.7)
    normal_val = normal(np.array([example_sbp]))[0]
    elevated_val = elevated(np.array([example_sbp]))[0]
    ax.plot(example_sbp, normal_val, 'go', markersize=10)
    ax.plot(example_sbp, elevated_val, 'yo', markersize=10)
    ax.text(example_sbp + 2, 0.5, 
            f'血压{example_sbp}:\n{normal_val*100:.0f}%正常\n{elevated_val*100:.0f}%偏高',
            fontsize=11, bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.7))
    
    ax.set_xlabel('收缩压 (mmHg)', fontsize=14)
    ax.set_ylabel('隶属度', fontsize=14)
    ax.set_title('模糊逻辑隶属度函数', fontsize=16, fontweight='bold')
    ax.set_ylim(-0.1, 1.1)
    ax.legend(fontsize=12, loc='upper right')
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('fuzzy_membership.png', dpi=300, bbox_inches='tight')
    print("✓ 模糊逻辑隶属度函数图已保存: fuzzy_membership.png")
    plt.close()


def visualize_control_quality_radar():
    """可视化控制质量雷达图"""
    from math import pi
    
    # 数据
    categories = ['达标率\n(40%)', '稳定性\n(30%)', '血压水平\n(30%)']
    patient_A = [90, 60, 70]  # 达标率高但波动大
    patient_B = [80, 90, 75]  # 达标率稍低但稳定
    
    # 计算角度
    N = len(categories)
    angles = [n / float(N) * 2 * pi for n in range(N)]
    angles += angles[:1]
    
    patient_A += patient_A[:1]
    patient_B += patient_B[:1]
    
    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))
    
    # 绘制患者A
    ax.plot(angles, patient_A, 'o-', linewidth=2, label='患者A', color='red')
    ax.fill(angles, patient_A, alpha=0.25, color='red')
    
    # 绘制患者B
    ax.plot(angles, patient_B, 'o-', linewidth=2, label='患者B', color='blue')
    ax.fill(angles, patient_B, alpha=0.25, color='blue')
    
    # 设置标签
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, fontsize=12)
    ax.set_ylim(0, 100)
    ax.set_yticks([20, 40, 60, 80, 100])
    ax.set_yticklabels(['20', '40', '60', '80', '100'], fontsize=10)
    ax.grid(True)
    
    ax.set_title('控制质量三维评分对比', fontsize=16, fontweight='bold', pad=20)
    ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), fontsize=12)
    
    # 添加说明
    fig.text(0.5, 0.02, 
             '患者A: 达标率90%, CV=15% (波动大)\n患者B: 达标率80%, CV=5% (稳定)',
             ha='center', fontsize=11,
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.tight_layout()
    plt.savefig('control_quality_radar.png', dpi=300, bbox_inches='tight')
    print("✓ 控制质量雷达图已保存: control_quality_radar.png")
    plt.close()


def visualize_isolation_forest():
    """可视化Isolation Forest原理"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # 左图：正常点的分割
    ax1.set_xlim(0, 10)
    ax1.set_ylim(0, 10)
    ax1.set_aspect('equal')
    
    # 绘制多次分割
    ax1.axvline(x=5, color='gray', linestyle='-', linewidth=1, alpha=0.5)
    ax1.axhline(y=5, color='gray', linestyle='-', linewidth=1, alpha=0.5)
    ax1.axvline(x=2.5, ymin=0.5, color='gray', linestyle='-', linewidth=1, alpha=0.5)
    ax1.axhline(y=7.5, xmin=0.5, color='gray', linestyle='-', linewidth=1, alpha=0.5)
    
    # 正常点
    ax1.plot(6, 6, 'bo', markersize=15, label='正常点')
    ax1.text(6, 5.5, '深度=8', ha='center', fontsize=11)
    
    ax1.set_title('正常点需要多次分割', fontsize=14, fontweight='bold')
    ax1.legend(fontsize=11)
    ax1.grid(True, alpha=0.3)
    
    # 右图：异常点的分割
    ax2.set_xlim(0, 10)
    ax2.set_ylim(0, 10)
    ax2.set_aspect('equal')
    
    # 只需少数分割
    ax2.axvline(x=8, color='gray', linestyle='-', linewidth=1, alpha=0.5)
    
    # 异常点
    ax2.plot(9, 9, 'ro', markersize=15, label='异常点')
    ax2.text(9, 8.5, '深度=2', ha='center', fontsize=11)
    
    ax2.set_title('异常点快速被孤立', fontsize=14, fontweight='bold')
    ax2.legend(fontsize=11)
    ax2.grid(True, alpha=0.3)
    
    fig.suptitle('Isolation Forest 原理示意', fontsize=16, fontweight='bold')
    plt.tight_layout()
    plt.savefig('isolation_forest_principle.png', dpi=300, bbox_inches='tight')
    print("✓ Isolation Forest原理图已保存: isolation_forest_principle.png")
    plt.close()


def visualize_topsis():
    """可视化TOPSIS多准则决策"""
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # 风险因素数据（严重性，紧迫性）
    risks = {
        '高血压': (0.85, 0.90),
        '运动不足': (0.60, 0.50),
        '睡眠不足': (0.50, 0.60),
        '饮食不当': (0.55, 0.45)
    }
    
    # 理想解和负理想解
    ideal_best = (1.0, 1.0)
    ideal_worst = (0.0, 0.0)
    
    # 绘制理想解
    ax.plot(*ideal_best, 'g*', markersize=20, label='理想最优解 A+')
    ax.plot(*ideal_worst, 'r*', markersize=20, label='理想最劣解 A-')
    
    # 绘制风险因素
    colors = ['red', 'orange', 'yellow', 'blue']
    for (name, (x, y)), color in zip(risks.items(), colors):
        ax.plot(x, y, 'o', markersize=15, color=color, label=name)
        ax.text(x + 0.02, y + 0.02, name, fontsize=11)
        
        # 绘制到理想解的距离
        ax.plot([x, ideal_best[0]], [y, ideal_best[1]], 
                'g--', alpha=0.3, linewidth=1)
        ax.plot([x, ideal_worst[0]], [y, ideal_worst[1]], 
                'r--', alpha=0.3, linewidth=1)
    
    ax.set_xlabel('严重性', fontsize=14)
    ax.set_ylabel('紧迫性', fontsize=14)
    ax.set_title('TOPSIS多准则决策可视化', fontsize=16, fontweight='bold')
    ax.set_xlim(-0.1, 1.1)
    ax.set_ylim(-0.1, 1.1)
    ax.legend(fontsize=11, loc='lower left')
    ax.grid(True, alpha=0.3)
    
    # 添加说明
    ax.text(0.5, -0.15, 
            '相对接近度 = d- / (d+ + d-)\n高血压最接近理想解，优先级最高',
            ha='center', fontsize=11, transform=ax.transAxes,
            bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.7))
    
    plt.tight_layout()
    plt.savefig('topsis_visualization.png', dpi=300, bbox_inches='tight')
    print("✓ TOPSIS可视化图已保存: topsis_visualization.png")
    plt.close()


def visualize_system_architecture():
    """可视化系统架构（使用文本图）"""
    fig, ax = plt.subplots(figsize=(12, 10))
    ax.axis('off')
    
    # 定义层次和模块
    layers = [
        {'name': '应用层', 'y': 0.9, 'modules': ['老人端', '家属端', '社区端']},
        {'name': '核心引擎层', 'y': 0.7, 'modules': ['HealthAssessmentEngine']},
        {'name': '业务模块层', 'y': 0.5, 'modules': ['配置', '数据', '疾病', '生活', '融合', '报告']},
        {'name': '算法层', 'y': 0.3, 'modules': ['IQR', 'Z-score', '模糊逻辑', 'IF', 'AHP', 'TOPSIS']},
        {'name': '数据层', 'y': 0.1, 'modules': ['健康档案', '评估记录', '配置数据']}
    ]
    
    colors = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6']
    
    for layer, color in zip(layers, colors):
        # 绘制层次背景
        rect = plt.Rectangle((0.05, layer['y'] - 0.08), 0.9, 0.12,
                            facecolor=color, alpha=0.3, edgecolor=color, linewidth=2)
        ax.add_patch(rect)
        
        # 层次名称
        ax.text(0.02, layer['y'], layer['name'], fontsize=14, fontweight='bold',
               verticalalignment='center')
        
        # 模块
        n_modules = len(layer['modules'])
        for i, module in enumerate(layer['modules']):
            x = 0.15 + (0.8 / n_modules) * (i + 0.5)
            ax.text(x, layer['y'], module, fontsize=10,
                   ha='center', va='center',
                   bbox=dict(boxstyle='round', facecolor='white', 
                           edgecolor=color, linewidth=1.5))
    
    # 绘制箭头
    for i in range(len(layers) - 1):
        ax.annotate('', xy=(0.5, layers[i+1]['y'] + 0.04),
                   xytext=(0.5, layers[i]['y'] - 0.04),
                   arrowprops=dict(arrowstyle='->', lw=2, color='gray'))
    
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_title('多模型健康评估系统架构', fontsize=18, fontweight='bold', pad=20)
    
    plt.tight_layout()
    plt.savefig('system_architecture.png', dpi=300, bbox_inches='tight')
    print("✓ 系统架构图已保存: system_architecture.png")
    plt.close()


def generate_all_visualizations():
    """生成所有可视化图表"""
    print("\n" + "="*60)
    print("开始生成演讲用可视化图表")
    print("="*60 + "\n")
    
    visualize_iqr_outlier_detection()
    visualize_zscore()
    visualize_fuzzy_membership()
    visualize_control_quality_radar()
    visualize_isolation_forest()
    visualize_topsis()
    visualize_system_architecture()
    
    print("\n" + "="*60)
    print("✓ 所有可视化图表生成完成！")
    print("="*60)
    print("\n生成的图表：")
    print("1. iqr_outlier_detection.png - IQR异常值检测")
    print("2. zscore_visualization.png - Z-score标准化")
    print("3. fuzzy_membership.png - 模糊逻辑隶属度函数")
    print("4. control_quality_radar.png - 控制质量雷达图")
    print("5. isolation_forest_principle.png - Isolation Forest原理")
    print("6. topsis_visualization.png - TOPSIS多准则决策")
    print("7. system_architecture.png - 系统架构图")
    print("\n这些图表可以直接插入到PPT中使用！")


if __name__ == "__main__":
    generate_all_visualizations()
