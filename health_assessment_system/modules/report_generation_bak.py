"""
模块6：评估结果管理与报告生成子模块
Assessment Result Management and Report Generation Module

功能：
- 评估结果记录与存储
- 分角色报告生成（老人版/家属版/社区版）
- 可视化数据接口
- 历史记录管理

算法分配：无复杂算法，主要是数据管理和报告格式化
"""

import json
from enum import Enum
from typing import Dict, List, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path


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
    """评估记录"""
    assessment_id: str
    user_id: str
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
        data['assessment_date'] = self.assessment_date.isoformat()
        data['created_at'] = self.created_at.isoformat()
        data['updated_at'] = self.updated_at.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'AssessmentRecord':
        """从字典创建"""
        data['assessment_date'] = datetime.fromisoformat(data['assessment_date'])
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        data['updated_at'] = datetime.fromisoformat(data['updated_at'])
        return cls(**data)


class AssessmentRecordManager:
    """评估记录管理器"""
    
    def __init__(self, storage_path: str = "./assessment_records"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.records_cache: Dict[str, AssessmentRecord] = {}
    
    def save_record(self, record: AssessmentRecord) -> bool:
        """
        保存评估记录
        
        Args:
            record: 评估记录
        
        Returns:
            是否保存成功
        """
        try:
            # 更新时间戳
            record.updated_at = datetime.now()
            
            # 保存到文件
            user_dir = self.storage_path / record.user_id
            user_dir.mkdir(exist_ok=True)
            
            file_path = user_dir / f"{record.assessment_id}.json"
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(record.to_dict(), f, ensure_ascii=False, indent=2)
            
            # 更新缓存
            self.records_cache[record.assessment_id] = record
            
            return True
        except Exception as e:
            print(f"保存记录失败: {e}")
            return False
    
    def load_record(self, assessment_id: str, user_id: str) -> Optional[AssessmentRecord]:
        """
        加载评估记录
        
        Args:
            assessment_id: 评估ID
            user_id: 用户ID
        
        Returns:
            评估记录或None
        """
        # 先查缓存
        if assessment_id in self.records_cache:
            return self.records_cache[assessment_id]
        
        # 从文件加载
        try:
            file_path = self.storage_path / user_id / f"{assessment_id}.json"
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                record = AssessmentRecord.from_dict(data)
                self.records_cache[assessment_id] = record
                return record
        except Exception as e:
            print(f"加载记录失败: {e}")
        
        return None
    
    def get_user_records(
        self, 
        user_id: str, 
        limit: int = 10,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[AssessmentRecord]:
        """
        获取用户的评估记录列表
        
        Args:
            user_id: 用户ID
            limit: 返回记录数量限制
            start_date: 开始日期
            end_date: 结束日期
        
        Returns:
            评估记录列表
        """
        records = []
        user_dir = self.storage_path / user_id
        
        if not user_dir.exists():
            return records
        
        try:
            for file_path in user_dir.glob("*.json"):
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                record = AssessmentRecord.from_dict(data)
                
                # 日期过滤
                if start_date and record.assessment_date < start_date:
                    continue
                if end_date and record.assessment_date > end_date:
                    continue
                
                records.append(record)
        except Exception as e:
            print(f"获取用户记录失败: {e}")
        
        # 按日期排序（最新的在前）
        records.sort(key=lambda x: x.assessment_date, reverse=True)
        
        return records[:limit]
    
    def delete_record(self, assessment_id: str, user_id: str) -> bool:
        """删除评估记录"""
        try:
            file_path = self.storage_path / user_id / f"{assessment_id}.json"
            if file_path.exists():
                file_path.unlink()
            
            if assessment_id in self.records_cache:
                del self.records_cache[assessment_id]
            
            return True
        except Exception as e:
            print(f"删除记录失败: {e}")
            return False


class ReportGenerator:
    """报告生成器"""
    
    def __init__(self):
        self.templates = self._load_templates()
    
    def generate_report(
        self,
        assessment_result: Dict,
        report_type: ReportType,
        report_format: ReportFormat = ReportFormat.TEXT
    ) -> str:
        """
        生成评估报告
        
        Args:
            assessment_result: 评估结果
            report_type: 报告类型
            report_format: 报告格式
        
        Returns:
            报告内容
        """
        if report_type == ReportType.ELDERLY:
            return self._generate_elderly_report(assessment_result, report_format)
        elif report_type == ReportType.FAMILY:
            return self._generate_family_report(assessment_result, report_format)
        elif report_type == ReportType.COMMUNITY:
            return self._generate_community_report(assessment_result, report_format)
        else:
            return self._generate_detailed_report(assessment_result, report_format)
    
    def _generate_elderly_report(
        self, 
        result: Dict, 
        format: ReportFormat
    ) -> str:
        """
        生成老人版报告（简短易懂）
        
        特点：
        - 结论简明
        - 字体大
        - 重点突出
        - 避免专业术语
        """
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
            # 添加TOP风险（最多3个，用简单语言）
            top_risks = result.get('top_risk_factors', [])[:3]
            for i, risk in enumerate(top_risks, 1):
                report += f"\n{i}. {self._simplify_risk_description(risk)}"
            
            report += "\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            report += "\n【健康建议】\n"
            
            # 添加建议（最多3条）
            recommendations = result.get('priority_recommendations', [])[:3]
            for i, rec in enumerate(recommendations, 1):
                report += f"\n{i}. {rec}"
            
            report += "\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            report += "\n💡 温馨提示：请按照建议调整生活习惯，定期复查。\n"
            
            return report
        
        elif format == ReportFormat.JSON:
            return json.dumps({
                'assessment_date': result.get('assessment_date'),
                'overall_score': result.get('overall_score'),
                'health_level': self._translate_health_level(result.get('health_level')),
                'key_issues': [self._simplify_risk_description(r) for r in result.get('top_risk_factors', [])[:3]],
                'recommendations': result.get('priority_recommendations', [])[:3]
            }, ensure_ascii=False, indent=2)
        
        return "不支持的格式"
    
    def _generate_family_report(
        self, 
        result: Dict, 
        format: ReportFormat
    ) -> str:
        """
        生成家属版报告（详细但易懂）
        
        特点：
        - 包含分维度评分
        - 趋势说明
        - 详细建议
        - 就医提醒
        """
        if format == ReportFormat.TEXT:
            report = f"""
╔══════════════════════════════════════════════════╗
║              健康评估报告（家属版）                ║
╚══════════════════════════════════════════════════╝

评估对象：{result.get('user_id', '未知')}
评估日期：{result.get('assessment_date', '未知')}
评估ID：{result.get('assessment_id', '未知')}

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
            # 详细的风险因素
            top_risks = result.get('top_risk_factors', [])
            for i, risk in enumerate(top_risks, 1):
                report += f"\n{i}. {risk.get('name', '未知风险')}"
                report += f"\n   风险等级：{self._translate_priority(risk.get('priority', 'medium'))}"
                report += f"\n   风险评分：{risk.get('risk_score', 0):.1f}分"
                
                evidence = risk.get('evidence', [])
                if evidence:
                    report += "\n   具体表现："
                    for ev in evidence[:2]:
                        report += f"\n   - {ev}"
                report += "\n"
            
            report += "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            report += "\n【健康建议】\n"
            
            recommendations = result.get('priority_recommendations', [])
            for i, rec in enumerate(recommendations, 1):
                report += f"\n{i}. {rec}"
            
            # 就医提醒
            if result.get('health_level') in ['high_risk', 'attention_needed']:
                report += "\n\n⚠️  重要提醒：建议尽快安排就医咨询，进行专业评估。"
            
            report += "\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            report += "\n【趋势分析】\n"
            
            # 添加趋势信息
            trend_results = result.get('trend_results', {})
            if trend_results:
                for metric, trend in trend_results.items():
                    direction = trend.get('trend_direction', 'stable')
                    if direction != 'stable':
                        report += f"• {metric}: {self._translate_trend(direction)}\n"
            else:
                report += "暂无明显趋势变化\n"
            
            return report
        
        elif format == ReportFormat.JSON:
            return json.dumps(result, ensure_ascii=False, indent=2)
        
        return "不支持的格式"
    
    def _generate_community_report(
        self, 
        result: Dict, 
        format: ReportFormat
    ) -> str:
        """
        生成社区版报告（简洁摘要）
        
        特点：
        - 仅综合等级和重点问题
        - 用于群体视图
        - 便于筛查
        """
        if format == ReportFormat.TEXT:
            report = f"""
【社区健康评估摘要】

用户ID：{result.get('user_id', '未知')}
评估日期：{result.get('assessment_date', '未知')}

综合等级：{self._translate_health_level(result.get('health_level', 'good'))}
综合评分：{result.get('overall_score', 0):.0f}分

重点问题：
"""
            top_risks = result.get('top_risk_factors', [])[:2]
            for risk in top_risks:
                report += f"• {risk.get('name', '未知')}\n"
            
            # 是否需要干预
            if result.get('health_level') in ['high_risk', 'attention_needed']:
                report += "\n⚠️  需要重点关注和干预\n"
            
            return report
        
        elif format == ReportFormat.JSON:
            # 社区版只返回关键信息
            return json.dumps({
                'user_id': result.get('user_id'),
                'assessment_date': result.get('assessment_date'),
                'health_level': result.get('health_level'),
                'overall_score': result.get('overall_score'),
                'top_issues': [r.get('name') for r in result.get('top_risk_factors', [])[:2]],
                'needs_intervention': result.get('health_level') in ['high_risk', 'attention_needed']
            }, ensure_ascii=False, indent=2)
        
        return "不支持的格式"
    
    def _generate_detailed_report(
        self, 
        result: Dict, 
        format: ReportFormat
    ) -> str:
        """生成详细版报告（完整信息）"""
        if format == ReportFormat.JSON:
            return json.dumps(result, ensure_ascii=False, indent=2)
        
        return "详细版报告仅支持JSON格式"
    
    def generate_visualization_data(self, result: Dict) -> Dict:
        """
        生成可视化数据接口
        
        Returns:
            用于前端可视化的结构化数据
        """
        viz_data = {
            'overview': {
                'overall_score': result.get('overall_score', 0),
                'health_level': result.get('health_level', 'good'),
                'assessment_date': result.get('assessment_date', '')
            },
            'dimension_scores': {
                'disease': 100 - result.get('disease_risk_score', 0),
                'lifestyle': 100 - result.get('lifestyle_risk_score', 0),
                'trend': 100 - result.get('trend_risk_score', 0)
            },
            'risk_factors': [
                {
                    'name': rf.get('name', ''),
                    'score': rf.get('risk_score', 0),
                    'priority': rf.get('priority', 'medium'),
                    'category': rf.get('category', 'unknown')
                }
                for rf in result.get('top_risk_factors', [])
            ],
            'risk_distribution': result.get('risk_distribution', {}),
            'feature_importance': result.get('feature_importance', {}),
            'trend_indicators': []
        }
        
        # 添加趋势指标
        trend_results = result.get('trend_results', {})
        for metric, trend in trend_results.items():
            viz_data['trend_indicators'].append({
                'metric': metric,
                'direction': trend.get('trend_direction', 'stable'),
                'deviation': trend.get('deviation_from_baseline', 0)
            })
        
        return viz_data
    
    def _load_templates(self) -> Dict:
        """加载报告模板"""
        # 这里可以从文件加载模板
        return {}
    
    def _translate_health_level(self, level: str) -> str:
        """翻译健康等级"""
        translations = {
            'excellent': '优秀',
            'good': '良好',
            'suboptimal': '亚健康',
            'attention_needed': '需重点关注',
            'high_risk': '高风险'
        }
        return translations.get(level, level)
    
    def _translate_priority(self, priority: str) -> str:
        """翻译优先级"""
        translations = {
            'critical': '紧急',
            'high': '高',
            'medium': '中',
            'low': '低'
        }
        return translations.get(priority, priority)
    
    def _translate_trend(self, trend: str) -> str:
        """翻译趋势"""
        translations = {
            'improving': '改善中',
            'worsening': '恶化中',
            'stable': '稳定'
        }
        return translations.get(trend, trend)
    
    def _simplify_risk_description(self, risk: Dict) -> str:
        """简化风险描述（老人版使用）"""
        name = risk.get('name', '')
        
        # 简化专业术语
        simplifications = {
            '高血压': '血压偏高',
            '糖代谢异常': '血糖偏高',
            '血脂异常': '血脂偏高',
            '睡眠质量': '睡眠不好',
            '运动不足': '活动太少',
            '饮食不合理': '饮食需要调整'
        }
        
        for key, value in simplifications.items():
            if key in name:
                return value
        
        return name


# 使用示例
if __name__ == "__main__":
    # 创建记录管理器
    record_manager = AssessmentRecordManager()
    
    # 创建模拟评估记录
    record = AssessmentRecord(
        assessment_id="ASSESS_20231125_001",
        user_id="USER001",
        assessment_date=datetime.now(),
        assessment_type="scheduled",
        time_window={'days': 30},
        data_completeness={'rate': 0.85},
        overall_score=65.5,
        health_level="suboptimal",
        disease_risk_score=55,
        lifestyle_risk_score=45,
        trend_risk_score=30,
        top_risk_factors=[
            {'name': '高血压', 'risk_score': 65, 'priority': 'high', 'evidence': ['血压控制不佳']},
            {'name': '运动不足', 'risk_score': 55, 'priority': 'medium', 'evidence': ['日均步数低']}
        ],
        recommendations=['加强血压监测', '增加运动量', '改善饮食']
    )
    
    # 保存记录
    record_manager.save_record(record)
    print("评估记录已保存")
    
    # 生成报告
    report_generator = ReportGenerator()
    
    result_dict = record.to_dict()
    result_dict['top_risk_factors'] = record.top_risk_factors
    result_dict['priority_recommendations'] = record.recommendations
    
    # 生成老人版报告
    elderly_report = report_generator.generate_report(
        result_dict,
        ReportType.ELDERLY,
        ReportFormat.TEXT
    )
    print("\n" + "="*50)
    print("老人版报告:")
    print(elderly_report)
    
    # 生成家属版报告
    family_report = report_generator.generate_report(
        result_dict,
        ReportType.FAMILY,
        ReportFormat.TEXT
    )
    print("\n" + "="*50)
    print("家属版报告:")
    print(family_report)
    
    # 生成可视化数据
    viz_data = report_generator.generate_visualization_data(result_dict)
    print("\n" + "="*50)
    print("可视化数据:")
    print(json.dumps(viz_data, ensure_ascii=False, indent=2))
