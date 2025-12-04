/**
 * 健康评估报告组件
 * 
 * 集成 health_assessment_system 的评估结果展示
 * 包含综合评分、维度分析、风险因素、健康建议等
 */

import React, { useState, useEffect } from 'react';
import { 
  Activity, 
  Heart, 
  TrendingUp, 
  AlertTriangle, 
  CheckCircle2, 
  Loader2,
  RefreshCw,
  FileText,
  Download,
  ChevronRight,
  Sparkles
} from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { Progress } from '../ui/progress';
import {
  runAssessment,
  getVisualizationData,
  generateReport,
  AssessmentResult,
  VisualizationData,
  RiskFactor,
  HealthLevel,
  getHealthLevelLabel,
  getHealthLevelColor,
} from '../../services/healthAssessmentApi';

interface HealthAssessmentReportProps {
  userId: string;
  userName?: string;
  onReportGenerated?: (report: string) => void;
  autoAssess?: boolean; // 是否自动评估
}

// 本地存储键
const REALTIME_ASSESS_KEY = 'health_realtime_assess_enabled';
const ASSESS_INTERVAL_KEY = 'health_assess_interval'; // 分钟

// 评估间隔选项（分钟）
const INTERVAL_OPTIONS = [
  { value: 1, label: '1分钟' },
  { value: 5, label: '5分钟' },
  { value: 15, label: '15分钟' },
  { value: 30, label: '30分钟' },
  { value: 60, label: '1小时' },
];

export const HealthAssessmentReport: React.FC<HealthAssessmentReportProps> = ({
  userId,
  userName = '用户',
  onReportGenerated,
  autoAssess = true, // 默认开启实时评估
}) => {
  const [isLoading, setIsLoading] = useState(false);
  const [isGeneratingReport, setIsGeneratingReport] = useState(false);
  const [assessmentResult, setAssessmentResult] = useState<AssessmentResult | null>(null);
  const [vizData, setVizData] = useState<VisualizationData | null>(null);
  const [error, setError] = useState<string | null>(null);
  
  // 实时评估状态
  const [realtimeEnabled, setRealtimeEnabled] = useState(() => {
    const saved = localStorage.getItem(REALTIME_ASSESS_KEY);
    return saved !== null ? saved === 'true' : autoAssess;
  });
  const [intervalMinutes, setIntervalMinutes] = useState(() => {
    const saved = localStorage.getItem(ASSESS_INTERVAL_KEY);
    return saved ? parseInt(saved) : 5; // 默认5分钟
  });
  const [nextAssessTime, setNextAssessTime] = useState<Date | null>(null);
  const [countdown, setCountdown] = useState<string>('');
  const intervalRef = React.useRef<NodeJS.Timeout | null>(null);
  const countdownRef = React.useRef<NodeJS.Timeout | null>(null);

  // 切换实时评估开关
  const toggleRealtime = () => {
    const newValue = !realtimeEnabled;
    setRealtimeEnabled(newValue);
    localStorage.setItem(REALTIME_ASSESS_KEY, String(newValue));
    
    if (!newValue) {
      // 关闭时清除定时器
      if (intervalRef.current) clearInterval(intervalRef.current);
      if (countdownRef.current) clearInterval(countdownRef.current);
      setNextAssessTime(null);
      setCountdown('');
    }
  };

  // 修改评估间隔
  const changeInterval = (minutes: number) => {
    setIntervalMinutes(minutes);
    localStorage.setItem(ASSESS_INTERVAL_KEY, String(minutes));
  };

  // 更新倒计时显示
  const updateCountdown = () => {
    if (!nextAssessTime) return;
    
    const now = new Date();
    const diff = nextAssessTime.getTime() - now.getTime();
    
    if (diff <= 0) {
      setCountdown('评估中...');
      return;
    }
    
    const minutes = Math.floor(diff / 60000);
    const seconds = Math.floor((diff % 60000) / 1000);
    setCountdown(`${minutes}:${seconds.toString().padStart(2, '0')}`);
  };

  // 启动实时评估定时器
  useEffect(() => {
    if (!realtimeEnabled) return;

    // 首次立即评估
    console.log('🔄 启动实时健康评估...');
    handleRunAssessment(true);

    // 设置定时评估
    const startInterval = () => {
      const next = new Date(Date.now() + intervalMinutes * 60 * 1000);
      setNextAssessTime(next);
      
      intervalRef.current = setInterval(() => {
        console.log('⏰ 定时健康评估触发');
        handleRunAssessment(true);
        const nextTime = new Date(Date.now() + intervalMinutes * 60 * 1000);
        setNextAssessTime(nextTime);
      }, intervalMinutes * 60 * 1000);
    };

    startInterval();

    // 倒计时更新
    countdownRef.current = setInterval(updateCountdown, 1000);

    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
      if (countdownRef.current) clearInterval(countdownRef.current);
    };
  }, [realtimeEnabled, intervalMinutes, userId]);

  // 更新倒计时
  useEffect(() => {
    updateCountdown();
  }, [nextAssessTime]);

  // 运行健康评估
  const handleRunAssessment = async (isAuto: boolean = false) => {
    setIsLoading(true);
    setError(null);

    try {
      const result = await runAssessment(userId, {
        assessmentType: isAuto ? 'scheduled' : 'on_demand',
        triggeredBy: isAuto ? 'system' : 'self',
      });

      if (result.success && result.data) {
        setAssessmentResult(result.data);
        
        // 获取可视化数据
        const vizResult = await getVisualizationData(userId, result.data.assessment_id);
        if (vizResult.success && vizResult.data) {
          setVizData(vizResult.data);
        }
        
        if (isAuto) {
          console.log('✅ 实时健康评估完成');
        }
      } else {
        setError(result.error || '评估失败');
      }
    } catch (err) {
      setError('网络错误，请检查后端服务是否运行');
    } finally {
      setIsLoading(false);
    }
  };

  // 生成完整报告
  const handleGenerateReport = async () => {
    if (!assessmentResult) return;

    setIsGeneratingReport(true);
    try {
      const result = await generateReport(userId, {
        assessmentId: assessmentResult.assessment_id,
        reportType: 'elderly',
        reportFormat: 'text',
      });

      if (result.success && result.data) {
        onReportGenerated?.(result.data.content);
      }
    } catch (err) {
      console.error('生成报告失败:', err);
    } finally {
      setIsGeneratingReport(false);
    }
  };

  // 获取风险等级图标
  const getRiskIcon = (priority: string) => {
    switch (priority) {
      case 'high':
        return <AlertTriangle className="h-5 w-5 text-red-500" />;
      case 'medium':
        return <Activity className="h-5 w-5 text-orange-500" />;
      default:
        return <CheckCircle2 className="h-5 w-5 text-green-500" />;
    }
  };

  // 获取风险等级颜色
  const getRiskColor = (priority: string) => {
    switch (priority) {
      case 'high':
        return 'bg-red-50 border-red-200 text-red-700';
      case 'medium':
        return 'bg-orange-50 border-orange-200 text-orange-700';
      default:
        return 'bg-green-50 border-green-200 text-green-700';
    }
  };

  // 获取维度名称（老年人友好版本）
  const getDimensionName = (key: string) => {
    const names: Record<string, string> = {
      disease: '身体状况',
      lifestyle: '生活习惯',
      trend: '近期变化',
    };
    return names[key] || key;
  };

  // 获取分数评语（让老人更容易理解）
  const getScoreComment = (score: number) => {
    if (score >= 85) return '非常好';
    if (score >= 70) return '良好';
    if (score >= 55) return '一般';
    return '需注意';
  };

  // 获取维度图标
  const getDimensionIcon = (key: string) => {
    switch (key) {
      case 'disease':
        return <Heart className="h-5 w-5" />;
      case 'lifestyle':
        return <Activity className="h-5 w-5" />;
      case 'trend':
        return <TrendingUp className="h-5 w-5" />;
      default:
        return <Activity className="h-5 w-5" />;
    }
  };

  // 未评估状态（老年人友好版本）
  if (!assessmentResult) {
    return (
      <Card className="bg-gradient-to-br from-blue-50 to-green-50 border-blue-300 border-2">
        <CardContent className="py-16">
          <div className="text-center space-y-8">
            <div className="w-24 h-24 mx-auto bg-blue-100 rounded-full flex items-center justify-center">
              <Heart className="h-12 w-12 text-blue-600" />
            </div>
            <div className="space-y-4">
              <h3 className="text-3xl font-bold text-blue-900">健康体检</h3>
              <p className="text-xl text-blue-700 max-w-md mx-auto leading-relaxed">
                点击下方按钮，为您检查身体状况
              </p>
            </div>
            
            {error && (
              <div className="bg-red-50 border-2 border-red-300 rounded-xl p-6 text-red-700 text-xl">
                ⚠️ {error}
              </div>
            )}

            <Button
              size="lg"
              className="px-12 py-8 text-2xl bg-blue-600 hover:bg-blue-700 rounded-xl shadow-lg"
              onClick={() => handleRunAssessment(false)}
              disabled={isLoading}
            >
              {isLoading ? (
                <>
                  <Loader2 className="mr-3 h-8 w-8 animate-spin" />
                  正在检查...
                </>
              ) : (
                <>
                  <Heart className="mr-3 h-8 w-8" />
                  开始检查身体
                </>
              )}
            </Button>

            <p className="text-lg text-blue-600">
              检查内容：血压、血糖、心跳、睡眠、运动
            </p>
          </div>
        </CardContent>
      </Card>
    );
  }

  // 评估结果展示（老年人友好版本）
  return (
    <div className="space-y-8">
      {/* 综合评分卡片 */}
      <Card className={`border-3 ${getHealthLevelColor(assessmentResult.health_level)}`}>
        <CardHeader className="pb-6">
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="text-3xl">您的健康报告</CardTitle>
              <CardDescription className="text-xl mt-2">
                检查时间：{new Date(assessmentResult.assessment_date).toLocaleString('zh-CN')}
              </CardDescription>
            </div>
            <Button
              variant="outline"
              size="lg"
              className="text-lg px-6 py-3"
              onClick={() => handleRunAssessment(false)}
              disabled={isLoading}
            >
              <RefreshCw className={`h-5 w-5 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
              重新检查
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col md:flex-row items-center gap-10">
            {/* 综合评分 - 更大更醒目 */}
            <div className="text-center">
              <div className="relative w-40 h-40">
                <svg className="w-full h-full transform -rotate-90" viewBox="0 0 160 160">
                  <circle
                    cx="80"
                    cy="80"
                    r="70"
                    fill="none"
                    stroke="#e5e7eb"
                    strokeWidth="12"
                  />
                  <circle
                    cx="80"
                    cy="80"
                    r="70"
                    fill="none"
                    stroke={
                      assessmentResult.overall_score >= 70
                        ? '#22c55e'
                        : assessmentResult.overall_score >= 55
                        ? '#eab308'
                        : '#ef4444'
                    }
                    strokeWidth="12"
                    strokeDasharray={`${(assessmentResult.overall_score / 100) * 440} 440`}
                    strokeLinecap="round"
                  />
                </svg>
                <div className="absolute inset-0 flex flex-col items-center justify-center">
                  <span className="text-5xl font-bold text-gray-800">{Math.round(assessmentResult.overall_score)}</span>
                  <span className="text-lg text-gray-500">分</span>
                </div>
              </div>
              <div className="mt-4 space-y-2">
                <Badge className={`text-xl px-6 py-2 ${getHealthLevelColor(assessmentResult.health_level)}`}>
                  {getHealthLevelLabel(assessmentResult.health_level)}
                </Badge>
                <p className="text-lg text-gray-600">
                  {assessmentResult.overall_score >= 85 ? '👍 身体很棒，继续保持！' :
                   assessmentResult.overall_score >= 70 ? '😊 身体不错，注意保养' :
                   assessmentResult.overall_score >= 55 ? '😐 还可以，需要改善' :
                   '⚠️ 请多注意身体'}
                </p>
              </div>
            </div>

            {/* 维度评分 - 更大字体和间距 */}
            <div className="flex-1 space-y-6 w-full">
              <h4 className="text-xl font-bold text-gray-700 border-b pb-2">详细情况</h4>
              {Object.entries(assessmentResult.dimension_scores).map(([key, value]) => (
                <div key={key} className="space-y-2">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <span className="text-2xl">
                        {key === 'disease' ? '❤️' : key === 'lifestyle' ? '🏃' : '📈'}
                      </span>
                      <span className="text-xl font-medium">{getDimensionName(key)}</span>
                    </div>
                    <div className="text-right">
                      <span className="text-2xl font-bold">{Math.round(value)}</span>
                      <span className="text-lg text-gray-500 ml-1">分</span>
                      <span className={`ml-3 text-lg font-medium ${
                        value >= 70 ? 'text-green-600' : value >= 55 ? 'text-yellow-600' : 'text-red-600'
                      }`}>
                        {getScoreComment(value)}
                      </span>
                    </div>
                  </div>
                  <Progress value={value} className="h-4 rounded-full" />
                </div>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* 风险因素（老年人友好版本） */}
      {assessmentResult.top_risk_factors.length > 0 && (
        <Card className="border-2 border-orange-200">
          <CardHeader className="bg-orange-50">
            <CardTitle className="text-2xl flex items-center gap-3">
              <span className="text-3xl">⚠️</span>
              需要注意的地方
            </CardTitle>
          </CardHeader>
          <CardContent className="pt-6">
            <div className="grid gap-4">
              {assessmentResult.top_risk_factors.map((factor, index) => (
                <div
                  key={index}
                  className={`flex items-center justify-between p-5 rounded-xl border-2 ${getRiskColor(factor.priority)}`}
                >
                  <div className="flex items-center gap-4">
                    <span className="text-3xl">
                      {factor.priority === 'high' ? '🔴' : factor.priority === 'medium' ? '🟡' : '🟢'}
                    </span>
                    <div>
                      <div className="text-xl font-bold">{factor.name}</div>
                      <div className="text-lg opacity-80">
                        {factor.category === 'disease' ? '身体方面' : 
                         factor.category === 'lifestyle' ? '生活习惯' : '近期变化'}
                      </div>
                    </div>
                  </div>
                  <div className="text-right">
                    <Badge className={`text-lg px-4 py-2 ${
                      factor.priority === 'high' ? 'bg-red-500 text-white' : 
                      factor.priority === 'medium' ? 'bg-orange-500 text-white' : 
                      'bg-green-500 text-white'
                    }`}>
                      {factor.priority === 'high' ? '要重视' : 
                       factor.priority === 'medium' ? '需留意' : '还好'}
                    </Badge>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* 健康建议（老年人友好版本） */}
      {assessmentResult.recommendations.length > 0 && (
        <Card className="bg-gradient-to-br from-green-50 to-emerald-50 border-2 border-green-300">
          <CardHeader className="bg-green-100">
            <CardTitle className="text-2xl flex items-center gap-3 text-green-800">
              <span className="text-3xl">💡</span>
              医生建议您
            </CardTitle>
          </CardHeader>
          <CardContent className="pt-6">
            <ul className="space-y-5">
              {assessmentResult.recommendations.map((rec, index) => (
                <li key={index} className="flex items-start gap-4 p-4 bg-white rounded-xl border border-green-200">
                  <span className="text-2xl flex-shrink-0">
                    {index === 0 ? '1️⃣' : index === 1 ? '2️⃣' : '3️⃣'}
                  </span>
                  <span className="text-xl text-green-900 leading-relaxed">{rec}</span>
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      )}

    </div>
  );
};

export default HealthAssessmentReport;
