"""
模糊逻辑血压评估演示代码
用于现场演讲展示核心算法原理
"""

def membership_normal(x, low, high):
    """正常隶属度函数：渐变评估，不是一刀切"""
    if x <= low:
        return 1.0  # 完全正常
    elif x >= high:
        return 0.0  # 完全不正常
    else:
        return (high - x) / (high - low)  # 渐变过渡


def membership_high(x, low, high):
    """偏高隶属度函数"""
    if x <= low:
        return 0.0
    elif x >= high:
        return 1.0
    else:
        return (x - low) / (high - low)


def fuzzy_evaluate(systolic):
    """模糊逻辑评估血压"""
    # 计算隶属度（不是简单的大于/小于）
    normal_degree = membership_normal(systolic, 120, 140)
    high_degree = membership_high(systolic, 120, 140)
    
    # 风险评分
    risk_score = high_degree * 100
    
    print(f"收缩压: {systolic} mmHg")
    print(f"→ 正常隶属度: {normal_degree:.1%}")
    print(f"→ 偏高隶属度: {high_degree:.1%}")
    print(f"→ 风险评分: {risk_score:.0f}/100")
    print("-" * 40)


if __name__ == "__main__":
    print("=" * 40)
    print("模糊逻辑血压评估演示")
    print("=" * 40)
    print()
    
    # 测试对比：展示渐变评估的效果
    print("【对比测试】传统方法 vs 模糊逻辑\n")
    
    fuzzy_evaluate(125)  # 轻微偏高
    fuzzy_evaluate(139)  # 临界值
    fuzzy_evaluate(140)  # 刚超标
    fuzzy_evaluate(150)  # 明显超标
    
    print()
    print("【关键发现】")
    print("传统方法：125和139都是'正常'，140突然变'高血压'")
    print("模糊逻辑：125已有25分风险，139有95分风险，提前预警")
    print("=" * 40)
