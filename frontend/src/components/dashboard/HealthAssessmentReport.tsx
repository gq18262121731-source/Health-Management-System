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

  // 获取维度名称
  const getDimensionName = (key: string) => {
    const names: Record<string, string> = {
      disease: '疾病风险',
      lifestyle: '生活方式',
      trend: '趋势变化',
    };
    return names[key] || key;
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

  // 未评估状态
  if (!assessmentResult) {
    return (
      <Card className="bg-gradient-to-br from-indigo-50 to-purple-50 border-indigo-200">
        <CardContent className="py-12">
          <div className="text-center space-y-6">
            <div className="w-20 h-20 mx-auto bg-indigo-100 rounded-full flex items-center justify-center">
              <Sparkles className="h-10 w-10 text-indigo-600" />
            </div>
            <div className="space-y-2">
              <h3 className="text-2xl font-bold text-indigo-900">AI 智能健康评估</h3>
              <p className="text-lg text-indigo-700 max-w-md mx-auto">
                基于多模型算法，对您的健康数据进行全方位分析，生成个性化评估报告
              </p>
            </div>
            
            {error && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700">
                {error}
              </div>
            )}

            <Button
              size="lg"
              className="px-8 py-6 text-lg bg-indigo-600 hover:bg-indigo-700"
              onClick={() => handleRunAssessment(false)}
              disabled={isLoading}
            >
              {isLoading ? (
                <>
                  <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                  正在评估中...
                </>
              ) : (
                <>
                  <Sparkles className="mr-2 h-5 w-5" />
                  开始智能评估
                </>
              )}
            </Button>

            <p className="text-sm text-indigo-600">
              评估将分析您的血压、血糖、心率、睡眠、运动等多维度数据
            </p>

            {/* 实时评估控制 */}
            <div className="flex flex-col items-center gap-3 pt-4 border-t border-indigo-200">
              <div className="flex items-center gap-3">
                <span className="text-sm text-indigo-700">实时评估</span>
                <button
                  onClick={toggleRealtime}
                  className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                    realtimeEnabled ? 'bg-green-500' : 'bg-gray-300'
                  }`}
                >
                  <span
                    className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                      realtimeEnabled ? 'translate-x-6' : 'translate-x-1'
                    }`}
                  />
                </button>
                {realtimeEnabled && countdown && (
                  <span className="text-xs text-green-600 font-mono bg-green-50 px-2 py-1 rounded">
                    下次: {countdown}
                  </span>
                )}
              </div>
              
              {/* 间隔选择 */}
              {realtimeEnabled && (
                <div className="flex items-center gap-2">
                  <span className="text-xs text-indigo-600">评估间隔:</span>
                  <select
                    value={intervalMinutes}
                    onChange={(e) => changeInterval(parseInt(e.target.value))}
                    className="text-xs border border-indigo-200 rounded px-2 py-1 bg-white text-indigo-700"
                  >
                    {INTERVAL_OPTIONS.map((opt) => (
                      <option key={opt.value} value={opt.value}>
                        {opt.label}
                      </option>
                    ))}
                  </select>
                </div>
              )}
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  // 评估结果展示
  return (
    <div className="space-y-6">
      {/* 综合评分卡片 */}
      <Card className={`border-2 ${getHealthLevelColor(assessmentResult.health_level)}`}>
        <CardHeader className="pb-4">
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="text-2xl">综合健康评估</CardTitle>
              <CardDescription className="text-lg mt-1">
                评估时间：{new Date(assessmentResult.assessment_date).toLocaleString('zh-CN')}
              </CardDescription>
            </div>
            <div className="flex items-center gap-4">
              {/* 实时评估状态 */}
              <div className="flex items-center gap-2">
                <span className="text-xs text-gray-500">实时</span>
                <button
                  onClick={toggleRealtime}
                  className={`relative inline-flex h-5 w-9 items-center rounded-full transition-colors ${
                    realtimeEnabled ? 'bg-green-500' : 'bg-gray-300'
                  }`}
                >
                  <span
                    className={`inline-block h-3 w-3 transform rounded-full bg-white transition-transform ${
                      realtimeEnabled ? 'translate-x-5' : 'translate-x-1'
                    }`}
                  />
                </button>
                {realtimeEnabled && countdown && (
                  <span className="text-xs text-green-600 font-mono bg-green-50 px-1.5 py-0.5 rounded">
                    {countdown}
                  </span>
                )}
                {realtimeEnabled && (
                  <select
                    value={intervalMinutes}
                    onChange={(e) => changeInterval(parseInt(e.target.value))}
                    className="text-xs border border-gray-200 rounded px-1 py-0.5 bg-white"
                  >
                    {INTERVAL_OPTIONS.map((opt) => (
                      <option key={opt.value} value={opt.value}>
                        {opt.label}
                      </option>
                    ))}
                  </select>
                )}
              </div>
              <Button
                variant="outline"
                size="sm"
                onClick={() => handleRunAssessment(false)}
                disabled={isLoading}
              >
                <RefreshCw className={`h-4 w-4 mr-1 ${isLoading ? 'animate-spin' : ''}`} />
                立即评估
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="flex items-center gap-8">
            {/* 综合评分 */}
            <div className="text-center">
              <div className="relative w-32 h-32">
                <svg className="w-full h-full transform -rotate-90">
                  <circle
                    cx="64"
                    cy="64"
                    r="56"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="12"
                    className="text-gray-200"
                  />
                  <circle
                    cx="64"
                    cy="64"
                    r="56"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="12"
                    strokeDasharray={`${(assessmentResult.overall_score / 100) * 352} 352`}
                    strokeLinecap="round"
                    className={
                      assessmentResult.overall_score >= 70
                        ? 'text-green-500'
                        : assessmentResult.overall_score >= 55
                        ? 'text-yellow-500'
                        : 'text-red-500'
                    }
                  />
                </svg>
                <div className="absolute inset-0 flex items-center justify-center">
                  <span className="text-4xl font-bold">{Math.round(assessmentResult.overall_score)}</span>
                </div>
              </div>
              <Badge className={`mt-2 text-base px-4 py-1 ${getHealthLevelColor(assessmentResult.health_level)}`}>
                {getHealthLevelLabel(assessmentResult.health_level)}
              </Badge>
            </div>

            {/* 维度评分 */}
            <div className="flex-1 space-y-4">
              {Object.entries(assessmentResult.dimension_scores).map(([key, value]) => (
                <div key={key} className="space-y-1">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      {getDimensionIcon(key)}
                      <span className="font-medium">{getDimensionName(key)}</span>
                    </div>
                    <span className="font-bold">{Math.round(value)}分</span>
                  </div>
                  <Progress value={value} className="h-2" />
                </div>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* 风险因素 */}
      {assessmentResult.top_risk_factors.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-xl flex items-center gap-2">
              <AlertTriangle className="h-5 w-5 text-orange-500" />
              需要关注的风险因素
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid gap-3">
              {assessmentResult.top_risk_factors.map((factor, index) => (
                <div
                  key={index}
                  className={`flex items-center justify-between p-4 rounded-lg border ${getRiskColor(factor.priority)}`}
                >
                  <div className="flex items-center gap-3">
                    {getRiskIcon(factor.priority)}
                    <div>
                      <div className="font-semibold">{factor.name}</div>
                      <div className="text-sm opacity-80">
                        {factor.category === 'disease' ? '疾病相关' : 
                         factor.category === 'lifestyle' ? '生活方式' : '趋势变化'}
                      </div>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="font-bold text-lg">{Math.round(factor.score)}分</div>
                    <Badge variant="outline" className="text-xs">
                      {factor.priority === 'high' ? '高优先级' : 
                       factor.priority === 'medium' ? '中优先级' : '低优先级'}
                    </Badge>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* 健康建议 */}
      {assessmentResult.recommendations.length > 0 && (
        <Card className="bg-gradient-to-br from-green-50 to-emerald-50 border-green-200">
          <CardHeader>
            <CardTitle className="text-xl flex items-center gap-2 text-green-800">
              <CheckCircle2 className="h-5 w-5" />
              个性化健康建议
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-3">
              {assessmentResult.recommendations.map((rec, index) => (
                <li key={index} className="flex items-start gap-3">
                  <ChevronRight className="h-5 w-5 text-green-600 mt-0.5 flex-shrink-0" />
                  <span className="text-lg text-green-900">{rec}</span>
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
