"""
模块6：评估结果管理与报告生成子模块
Assessment Result Management and Report Generation Module

功能：
- 评估结果记录与存储（MySQL）
- 分角色报告生成（老人版/家属版/社区版）
- 可视化数据接口
- 历史记录管理

算法分配：无复杂算法，主要是数据管理和报告格式化
"""

import json
from enum import Enum
from typing import Dict, List, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime, date
import sys
from pathlib import Path

# 添加项目根路径以导入 core 模块
sys.path.append(str(Path(__file__).parent.parent))
try:
    from core.database_manager import DatabaseManager
except ImportError:
    # 降级处理或Mock，避免直接报错导致无法运行
    print("Warning: DatabaseManager not found, using mock mode.")
    DatabaseManager = None


class ReportType(Enum):
    """报告类型"""
    ELDERLY = "elderly"  # 老人版
    FAMILY = "family"  # 家属版
    COMMUNITY = "community"  # 社区版
    DETAILED = "detailed"  # 详细版


class ReportFormat(Enum):
    """报告格式"""
    JSON = "json"
    TEXT = "text"
    HTML = "html"
    PDF = "pdf"


@dataclass
class AssessmentRecord:
    """评估记录（数据传输对象）"""
    assessment_id: str
    user_id: str  # 对应 elder_id
    assessment_date: datetime
    assessment_type: str
    time_window: Dict
    data_completeness: Dict
    
    # 评估结果
    overall_score: float
    health_level: str
    disease_risk_score: float
    lifestyle_risk_score: float
    trend_risk_score: float
    
    # TOP风险
    top_risk_factors: List[Dict]
    
    # 建议
    recommendations: List[str]
    
    # 元数据
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        data = asdict(self)
        # 转换datetime为字符串
        if isinstance(self.assessment_date, (datetime, date)):
            data['assessment_date'] = self.assessment_date.isoformat()
        if isinstance(self.created_at, (datetime, date)):
            data['created_at'] = self.created_at.isoformat()
        if isinstance(self.updated_at, (datetime, date)):
            data['updated_at'] = self.updated_at.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'AssessmentRecord':
        """从字典创建"""
        # 处理时间格式
        if isinstance(data.get('assessment_date'), str):
            try:
                data['assessment_date'] = datetime.fromisoformat(data['assessment_date'])
            except ValueError:
                pass
                
        if isinstance(data.get('created_at'), str):
            try:
                data['created_at'] = datetime.fromisoformat(data['created_at'])
            except ValueError:
                pass
                
        if isinstance(data.get('updated_at'), str):
            try:
                data['updated_at'] = datetime.fromisoformat(data['updated_at'])
            except ValueError:
                pass
                
        return cls(**data)


class AssessmentRecordManager:
    """评估记录管理器（MySQL版）"""
    
    def __init__(self):
        self.db_manager = DatabaseManager() if DatabaseManager else None
    
    def save_record(self, record: AssessmentRecord) -> bool:
        """
        保存评估记录到数据库
        
        Args:
            record: 评估记录对象
            
        Returns:
            是否保存成功
        """
        if not self.db_manager:
            print("数据库未连接，无法保存记录")
            return False
            
        try:
            # 准备插入 assessment_result 表的数据
            # 注意：需要将 AssessmentRecord 的字段映射到数据库表结构
            result_data = {
                'elder_id': record.user_id,
                'assessment_time': record.assessment_date,
                'window_start_date': record.time_window.get('start'),
                'window_end_date': record.time_window.get('end'),
                'data_quality_flag': 'OK',  # 默认值或从 completeness 获取
                'overall_risk_level': record.health_level,
                'overall_risk_score': record.overall_score,
                'disease_overall_score': record.disease_risk_score,
                'lifestyle_risk_score': record.lifestyle_risk_score,
                'trend_risk_score': record.trend_risk_score,
                'disease_summary_json': {'top_risks': record.top_risk_factors},  # 简化存储
                'advice_text_elder': "\n".join(record.recommendations),
                'extra_meta_json': {
                    'assessment_id': record.assessment_id,
                    'assessment_type': record.assessment_type,
                    'data_completeness': record.data_completeness
                }
            }
            
            self.db_manager.save_assessment_result(result_data)
            return True
            
        except Exception as e:
            print(f"保存记录失败: {e}")
            return False
    
    def load_record(self, assessment_id: str, user_id: str) -> Optional[AssessmentRecord]:
        """
        加载评估记录
        
        注意：由于数据库结构变化，这里主要演示获取最新记录的逻辑
        实际生产中需要根据 assessment_id 查询具体记录
        """
        if not self.db_manager:
            return None
            
        try:
            # 这里简化为获取该用户最新一条记录
            row = self.db_manager.get_latest_assessment(user_id)
            if not row:
                return None
                
            # 将数据库行转换为 AssessmentRecord 对象
            extra_meta = row.get('extra_meta_json', {}) or {}
            disease_json = row.get('disease_summary_json', {}) or {}
            
            record = AssessmentRecord(
                assessment_id=extra_meta.get('assessment_id', str(row['id'])),
                user_id=str(row['elder_id']),
                assessment_date=row['assessment_time'],
                assessment_type=extra_meta.get('assessment_type', 'unknown'),
                time_window={
                    'start': str(row['window_start_date']), 
                    'end': str(row['window_end_date'])
                },
                data_completeness=extra_meta.get('data_completeness', {}),
                overall_score=float(row['overall_risk_score'] or 0),
                health_level=row['overall_risk_level'],
                disease_risk_score=float(row['disease_overall_score'] or 0),
                lifestyle_risk_score=float(row['lifestyle_risk_score'] or 0),
                trend_risk_score=float(row['trend_risk_score'] or 0),
                top_risk_factors=disease_json.get('top_risks', []),
                recommendations=str(row['advice_text_elder']).split('\n') if row['advice_text_elder'] else []
            )
            return record
            
        except Exception as e:
            print(f"加载记录失败: {e}")
            return None
    
    def get_user_records(self, user_id: str, limit: int = 10) -> List[AssessmentRecord]:
        """获取用户历史记录（暂未完全实现多条查询，仅演示结构）"""
        # 实际应调用 db_manager.execute_query 查询多条
        latest = self.load_record("latest", user_id)
        return [latest] if latest else []


class ReportGenerator:
    """报告生成器"""
    
    def __init__(self):
        self.templates = {}
    
    def generate_report(
        self,
        assessment_result: Dict,
        report_type: ReportType,
        report_format: ReportFormat = ReportFormat.TEXT
    ) -> str:
        """生成评估报告"""
        if report_type == ReportType.ELDERLY:
            return self._generate_elderly_report(assessment_result, report_format)
        elif report_type == ReportType.FAMILY:
            return self._generate_family_report(assessment_result, report_format)
        elif report_type == ReportType.COMMUNITY:
            return self._generate_community_report(assessment_result, report_format)
        else:
            return self._generate_detailed_report(assessment_result, report_format)
    
    def _generate_elderly_report(self, result: Dict, format: ReportFormat) -> str:
        """生成老人版报告"""
        if format == ReportFormat.TEXT:
            report = f"""
╔══════════════════════════════════════╗
║          健康评估报告（简版）          ║
╚══════════════════════════════════════╝

评估日期：{result.get('assessment_date', '未知')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【健康状况】
您的健康评分：{result.get('overall_score', 0):.0f}分
健康等级：{self._translate_health_level(result.get('health_level', 'good'))}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【需要注意的问题】
"""
            top_risks = result.get('top_risk_factors', [])[:3]
            for i, risk in enumerate(top_risks, 1):
                report += f"\n{i}. {self._simplify_risk_description(risk)}"
            
            report += "\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            report += "\n【健康建议】\n"
            
            recommendations = result.get('priority_recommendations', [])[:3]
            for i, rec in enumerate(recommendations, 1):
                report += f"\n{i}. {rec}"
            
            report += "\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            report += "\n💡 温馨提示：请按照建议调整生活习惯，定期复查。\n"
            return report
            
        elif format == ReportFormat.JSON:
            return json.dumps(result, ensure_ascii=False, indent=2)
            
        return "不支持的格式"
    
    def _generate_family_report(self, result: Dict, format: ReportFormat) -> str:
        """生成家属版报告"""
        if format == ReportFormat.TEXT:
            report = f"""
╔══════════════════════════════════════════════════╗
║              健康评估报告（家属版）                ║
╚══════════════════════════════════════════════════╝

评估对象：{result.get('user_id', '未知')}
评估日期：{result.get('assessment_date', '未知')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【综合评估】
综合健康评分：{result.get('overall_score', 0):.1f}分
健康等级：{self._translate_health_level(result.get('health_level', 'good'))}

【分维度评分】
• 疾病风险评分：{result.get('disease_risk_score', 0):.1f}分
• 生活方式评分：{100 - result.get('lifestyle_risk_score', 0):.1f}分
• 趋势风险评分：{100 - result.get('trend_risk_score', 0):.1f}分

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【重点关注问题】
"""
            top_risks = result.get('top_risk_factors', [])
            for i, risk in enumerate(top_risks, 1):
                report += f"\n{i}. {risk.get('name', '未知风险')}"
                report += f"\n   风险等级：{self._translate_priority(risk.get('priority', 'medium'))}"
                
            report += "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            report += "\n【健康建议】\n"
            
            recommendations = result.get('priority_recommendations', [])
            for i, rec in enumerate(recommendations, 1):
                report += f"\n{i}. {rec}"
                
            if result.get('health_level') in ['high_risk', 'attention_needed']:
                report += "\n\n⚠️  重要提醒：建议尽快安排就医咨询。"
                
            return report
            
        return "不支持的格式"

    def _generate_community_report(self, result: Dict, format: ReportFormat) -> str:
        """生成社区版报告"""
        if format == ReportFormat.TEXT:
            return f"""
【社区健康评估摘要】
用户ID：{result.get('user_id', '未知')}
综合等级：{self._translate_health_level(result.get('health_level', 'good'))}
综合评分：{result.get('overall_score', 0):.0f}分
"""
        return "不支持的格式"
    
    def _generate_detailed_report(self, result: Dict, format: ReportFormat) -> str:
        return json.dumps(result, ensure_ascii=False, indent=2)
    
    def generate_visualization_data(self, result: Dict) -> Dict:
        """生成可视化数据接口"""
        return {
            'overview': {
                'overall_score': result.get('overall_score', 0),
                'health_level': result.get('health_level', 'good')
            },
            'dimension_scores': {
                'disease': 100 - result.get('disease_risk_score', 0),
                'lifestyle': 100 - result.get('lifestyle_risk_score', 0),
                'trend': 100 - result.get('trend_risk_score', 0)
            },
            'risk_factors': result.get('top_risk_factors', [])
        }

    def _translate_health_level(self, level: str) -> str:
        translations = {
            'excellent': '优秀', 'good': '良好',
            'suboptimal': '亚健康', 'attention_needed': '需重点关注',
            'high_risk': '高风险'
        }
        return translations.get(level, level)

    def _translate_priority(self, priority: str) -> str:
        translations = {'critical': '紧急', 'high': '高', 'medium': '中', 'low': '低'}
        return translations.get(priority, priority)
    
    def _simplify_risk_description(self, risk: Dict) -> str:
        name = risk.get('name', '')
        simplifications = {
            '高血压': '血压偏高', '糖代谢异常': '血糖偏高',
            '血脂异常': '血脂偏高', '睡眠质量': '睡眠不好',
            '运动不足': '活动太少', '饮食不合理': '饮食需要调整'
        }
        for key, value in simplifications.items():
            if key in name: return value
        return name
