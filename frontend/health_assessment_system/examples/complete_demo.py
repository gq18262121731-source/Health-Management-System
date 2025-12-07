"""
完整的健康评估系统演示
Complete Health Assessment System Demo

演示所有功能：
1. 定期评估
2. 按需评估
3. 多种报告生成
4. 历史记录查询
5. 可视化数据获取
"""

import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.assessment_engine import HealthAssessmentEngine
from modules.assessment_config import AssessmentPeriod, TimeWindow
from modules.report_generation import ReportType, ReportFormat


def demo_scheduled_assessment():
    """演示定期评估"""
    print("\n" + "="*70)
    print("演示1: 定期健康评估（每月评估）")
    print("="*70)
    
    engine = HealthAssessmentEngine(storage_path="./demo_data")
    
    # 运行月度评估
    result = engine.run_scheduled_assessment(
        user_id="USER001",
        period=AssessmentPeriod.MONTHLY,
        time_window=TimeWindow.LAST_30_DAYS
    )
    
    # 显示结果摘要
    print("\n" + "-"*70)
    print("评估结果摘要")
    print("-"*70)
    print(f"评估ID: {result.assessment_id}")
    print(f"综合评分: {result.overall_score:.1f}/100")
    print(f"健康等级: {result.health_level.value}")
    print(f"\n各维度评分:")
    print(f"  • 疾病风险: {100 - result.disease_risk_score:.1f}")
    print(f"  • 生活方式: {100 - result.lifestyle_risk_score:.1f}")
    print(f"  • 趋势风险: {100 - result.trend_risk_score:.1f}")
    
    print(f"\nTOP {len(result.top_risk_factors)} 风险因素:")
    for i, rf in enumerate(result.top_risk_factors, 1):
        print(f"  {i}. {rf.name}")
        print(f"     优先级: {rf.priority.value} | 评分: {rf.risk_score:.1f}")
        if rf.evidence:
            print(f"     依据: {rf.evidence[0]}")
    
    print(f"\n优先建议:")
    for i, rec in enumerate(result.priority_recommendations, 1):
        print(f"  {i}. {rec}")
    
    return engine, result


def demo_on_demand_assessment():
    """演示按需评估"""
    print("\n" + "="*70)
    print("演示2: 按需健康评估（家属触发）")
    print("="*70)
    
    engine = HealthAssessmentEngine(storage_path="./demo_data")
    
    # 家属触发的14天评估
    result = engine.run_on_demand_assessment(
        user_id="USER002",
        triggered_by="family_member",
        custom_days=14
    )
    
    print(f"\n评估完成!")
    print(f"评估ID: {result.assessment_id}")
    print(f"综合评分: {result.overall_score:.1f}/100")
    print(f"健康等级: {result.health_level.value}")
    
    return engine, result


def demo_report_generation(engine, result):
    """演示报告生成"""
    print("\n" + "="*70)
    print("演示3: 生成不同版本的报告")
    print("="*70)
    
    # 1. 老人版报告
    print("\n" + "-"*70)
    print("【老人版报告】- 简短易懂")
    print("-"*70)
    elderly_report = engine.generate_report(
        assessment_id=result.assessment_id,
        user_id=result.user_id,
        report_type=ReportType.ELDERLY,
        report_format=ReportFormat.TEXT
    )
    print(elderly_report)
    
    # 2. 家属版报告
    print("\n" + "-"*70)
    print("【家属版报告】- 详细完整")
    print("-"*70)
    family_report = engine.generate_report(
        assessment_id=result.assessment_id,
        user_id=result.user_id,
        report_type=ReportType.FAMILY,
        report_format=ReportFormat.TEXT
    )
    print(family_report)
    
    # 3. 社区版报告
    print("\n" + "-"*70)
    print("【社区版报告】- 简洁摘要")
    print("-"*70)
    community_report = engine.generate_report(
        assessment_id=result.assessment_id,
        user_id=result.user_id,
        report_type=ReportType.COMMUNITY,
        report_format=ReportFormat.TEXT
    )
    print(community_report)
    
    # 4. JSON格式（用于API）
    print("\n" + "-"*70)
    print("【JSON格式】- 用于API接口")
    print("-"*70)
    json_report = engine.generate_report(
        assessment_id=result.assessment_id,
        user_id=result.user_id,
        report_type=ReportType.ELDERLY,
        report_format=ReportFormat.JSON
    )
    print(json_report[:500] + "...")  # 只显示前500字符


def demo_visualization_data(engine, result):
    """演示可视化数据获取"""
    print("\n" + "="*70)
    print("演示4: 获取可视化数据")
    print("="*70)
    
    viz_data = engine.get_visualization_data(
        assessment_id=result.assessment_id,
        user_id=result.user_id
    )
    
    print("\n可视化数据结构:")
    print(f"  • 总览数据: {list(viz_data['overview'].keys())}")
    print(f"  • 维度评分: {viz_data['dimension_scores']}")
    print(f"  • 风险因素数量: {len(viz_data['risk_factors'])}")
    print(f"  • 趋势指标数量: {len(viz_data['trend_indicators'])}")
    
    print("\n风险因素详情:")
    for rf in viz_data['risk_factors'][:3]:
        print(f"  • {rf['name']}: {rf['score']:.1f}分 ({rf['priority']})")
    
    if viz_data['trend_indicators']:
        print("\n趋势指标:")
        for ti in viz_data['trend_indicators']:
            print(f"  • {ti['metric']}: {ti['direction']} (偏离: {ti['deviation']:.1f})")
    
    return viz_data


def demo_history_query(engine):
    """演示历史记录查询"""
    print("\n" + "="*70)
    print("演示5: 查询评估历史记录")
    print("="*70)
    
    # 查询USER001的历史记录
    history = engine.get_user_assessment_history(
        user_id="USER001",
        limit=5
    )
    
    if history:
        print(f"\n找到 {len(history)} 条历史记录:\n")
        for i, record in enumerate(history, 1):
            print(f"{i}. 评估日期: {record.assessment_date.strftime('%Y-%m-%d %H:%M')}")
            print(f"   评估ID: {record.assessment_id}")
            print(f"   综合评分: {record.overall_score:.1f}")
            print(f"   健康等级: {record.health_level}")
            print(f"   评估类型: {record.assessment_type}")
            print()
    else:
        print("\n暂无历史记录")


def demo_trend_analysis(engine):
    """演示趋势分析"""
    print("\n" + "="*70)
    print("演示6: 健康趋势分析")
    print("="*70)
    
    history = engine.get_user_assessment_history(
        user_id="USER001",
        limit=10
    )
    
    if len(history) >= 2:
        print("\n健康评分趋势:")
        scores = [(r.assessment_date, r.overall_score) for r in history]
        scores.reverse()  # 按时间正序
        
        for date, score in scores:
            bar_length = int(score / 2)  # 每2分一个字符
            bar = "█" * bar_length
            print(f"{date.strftime('%Y-%m-%d')}: {bar} {score:.1f}")
        
        # 计算趋势
        if len(scores) >= 2:
            first_score = scores[0][1]
            last_score = scores[-1][1]
            change = last_score - first_score
            
            print(f"\n趋势分析:")
            if change > 5:
                print(f"  ✅ 健康状况改善 (+{change:.1f}分)")
            elif change < -5:
                print(f"  ⚠️  健康状况下降 ({change:.1f}分)")
            else:
                print(f"  ➡️  健康状况稳定 ({change:+.1f}分)")
    else:
        print("\n历史记录不足，无法进行趋势分析")


def demo_risk_factor_analysis(engine, result):
    """演示风险因素分析"""
    print("\n" + "="*70)
    print("演示7: 风险因素详细分析")
    print("="*70)
    
    print("\n风险分布:")
    risk_dist = result.risk_distribution
    
    print("\n按类别分布:")
    for category, count in risk_dist['by_category'].items():
        print(f"  • {category}: {count} 个")
    
    print("\n按优先级分布:")
    for priority, count in risk_dist['by_priority'].items():
        print(f"  • {priority}: {count} 个")
    
    print("\n特征重要性分析:")
    if result.feature_importance:
        sorted_features = sorted(
            result.feature_importance.items(),
            key=lambda x: x[1],
            reverse=True
        )
        for feature, importance in sorted_features[:5]:
            bar_length = int(importance * 50)
            bar = "▓" * bar_length
            print(f"  {feature:20s} {bar} {importance:.3f}")


def demo_intervention_suggestions():
    """演示干预建议生成"""
    print("\n" + "="*70)
    print("演示8: 个性化干预建议")
    print("="*70)
    
    print("\n基于评估结果的干预建议分类:\n")
    
    print("【紧急干预】（需立即采取行动）")
    print("  1. 血压持续偏高 → 立即就医，调整用药")
    print("  2. 血糖严重超标 → 紧急就医，监测并发症")
    
    print("\n【重点关注】（需要密切监测）")
    print("  1. 睡眠严重不足 → 调整作息，必要时就医")
    print("  2. 运动严重不足 → 制定运动计划，逐步增加")
    
    print("\n【生活方式改善】（可自主调整）")
    print("  1. 饮食不合理 → 减少盐油糖，增加蔬菜水果")
    print("  2. 作息不规律 → 固定睡眠时间，避免熬夜")
    
    print("\n【持续监测】（定期复查）")
    print("  1. 血脂轻度异常 → 低脂饮食，3个月后复查")
    print("  2. 体重轻度超标 → 控制饮食，增加运动")


def main():
    """主函数：运行所有演示"""
    print("\n" + "="*70)
    print("多模型健康评估系统 - 完整功能演示")
    print("="*70)
    print("\n本演示将展示系统的所有核心功能:")
    print("  1. 定期评估")
    print("  2. 按需评估")
    print("  3. 多版本报告生成")
    print("  4. 可视化数据获取")
    print("  5. 历史记录查询")
    print("  6. 健康趋势分析")
    print("  7. 风险因素分析")
    print("  8. 干预建议生成")
    
    input("\n按回车键开始演示...")
    
    # 演示1: 定期评估
    engine, result1 = demo_scheduled_assessment()
    input("\n按回车键继续...")
    
    # 演示2: 按需评估
    engine, result2 = demo_on_demand_assessment()
    input("\n按回车键继续...")
    
    # 演示3: 报告生成
    demo_report_generation(engine, result1)
    input("\n按回车键继续...")
    
    # 演示4: 可视化数据
    viz_data = demo_visualization_data(engine, result1)
    input("\n按回车键继续...")
    
    # 演示5: 历史记录查询
    demo_history_query(engine)
    input("\n按回车键继续...")
    
    # 演示6: 趋势分析
    demo_trend_analysis(engine)
    input("\n按回车键继续...")
    
    # 演示7: 风险因素分析
    demo_risk_factor_analysis(engine, result1)
    input("\n按回车键继续...")
    
    # 演示8: 干预建议
    demo_intervention_suggestions()
    
    print("\n" + "="*70)
    print("演示完成！")
    print("="*70)
    print("\n系统功能总结:")
    print("  ✅ 支持定期和按需两种评估模式")
    print("  ✅ 整合6大评估子模块，10+种算法")
    print("  ✅ 提供3种角色的个性化报告")
    print("  ✅ 完整的评估记录管理和查询")
    print("  ✅ 丰富的可视化数据接口")
    print("  ✅ 智能的风险因素排序和建议生成")
    print("\n感谢使用多模型健康评估系统！")


if __name__ == "__main__":
    main()
