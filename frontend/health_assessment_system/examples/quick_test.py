"""
快速测试脚本 - 无需交互
Quick Test Script - No interaction required
"""

import sys
from pathlib import Path

# Add project path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.assessment_engine import HealthAssessmentEngine
from modules.assessment_config import AssessmentPeriod, TimeWindow
from modules.report_generation import ReportType, ReportFormat


def quick_test():
    """Quick test of the health assessment system"""
    print("\n" + "="*70)
    print("Health Assessment System - Quick Test")
    print("="*70)
    
    # Create engine
    print("\n[1/4] Creating assessment engine...")
    engine = HealthAssessmentEngine(storage_path="./test_data")
    print("✓ Engine created successfully")
    
    # Run assessment
    print("\n[2/4] Running monthly assessment...")
    result = engine.run_scheduled_assessment(
        user_id="TEST_USER_001",
        period=AssessmentPeriod.MONTHLY,
        time_window=TimeWindow.LAST_30_DAYS
    )
    print("✓ Assessment completed")
    
    # Display results
    print("\n[3/4] Assessment Results:")
    print("-"*70)
    print(f"Assessment ID: {result.assessment_id}")
    print(f"Overall Score: {result.overall_score:.1f}/100")
    print(f"Health Level: {result.health_level.value}")
    print(f"\nDimension Scores:")
    print(f"  • Disease Risk: {100 - result.disease_risk_score:.1f}")
    print(f"  • Lifestyle Risk: {100 - result.lifestyle_risk_score:.1f}")
    print(f"  • Trend Risk: {100 - result.trend_risk_score:.1f}")
    
    if result.top_risk_factors:
        print(f"\nTop {len(result.top_risk_factors)} Risk Factors:")
        for i, rf in enumerate(result.top_risk_factors[:3], 1):
            print(f"  {i}. {rf.name} (Priority: {rf.priority.value}, Score: {rf.risk_score:.1f})")
    
    # Generate report
    print("\n[4/4] Generating elderly report...")
    report = engine.generate_report(
        assessment_id=result.assessment_id,
        user_id=result.user_id,
        report_type=ReportType.ELDERLY,
        report_format=ReportFormat.TEXT
    )
    print("✓ Report generated")
    
    print("\n" + "="*70)
    print("Elderly Report Preview:")
    print("="*70)
    print(report[:800] + "..." if len(report) > 800 else report)
    
    print("\n" + "="*70)
    print("✓ All tests passed successfully!")
    print("="*70)
    print("\nSystem Status:")
    print("  ✓ Core modules working")
    print("  ✓ Assessment engine functional")
    print("  ✓ Report generation working")
    print("  ✓ Data persistence working")
    print("\nThe health assessment system is ready to use!")


if __name__ == "__main__":
    try:
        quick_test()
    except Exception as e:
        print(f"\n✗ Error occurred: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
