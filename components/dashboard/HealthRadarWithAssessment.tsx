/**
 * 健康雷达图组件 - 集成评估系统
 * 
 * 使用 health_assessment_system 的可视化数据
 * 展示多维度健康评分和风险分布
 */

import React, { useState, useEffect, useRef } from 'react';
import {
  RadarChart,
  Radar,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Legend,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from 'recharts';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../ui/card';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { 
  RefreshCw, 
  Loader2, 
  TrendingUp, 
  TrendingDown, 
  Minus,
  AlertTriangle,
  CheckCircle2,
  Activity
} from 'lucide-react';
import {
  getVisualizationData,
  VisualizationData,
  getHealthLevelLabel,
  getHealthLevelColor,
} from '../../services/healthAssessmentApi';

interface HealthRadarWithAssessmentProps {
  userId: string;
  autoRefresh?: boolean;
  refreshInterval?: number;
}

// 图表容器组件
function ChartContainer({ 
  children, 
  height = 300 
}: { 
  children: (width: number, height: number) => React.ReactNode;
  height?: number;
}) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [dimensions, setDimensions] = useState<{ width: number; height: number } | null>(null);

  useEffect(() => {
    const observer = new ResizeObserver((entries) => {
      if (!entries || entries.length === 0) return;
      const { width, height } = entries[0].contentRect;
      if (width > 0 && height > 0) {
        setDimensions({ width, height });
      }
    });

    if (containerRef.current) {
      observer.observe(containerRef.current);
    }

    return () => observer.disconnect();
  }, []);

  return (
    <div ref={containerRef} style={{ width: '100%', height }} className="w-full">
      {dimensions ? (
        children(dimensions.width, dimensions.height)
      ) : (
        <div className="w-full h-full bg-slate-50/50 animate-pulse rounded-md flex items-center justify-center">
          <Loader2 className="h-6 w-6 animate-spin text-slate-400" />
        </div>
      )}
    </div>
  );
}

export const HealthRadarWithAssessment: React.FC<HealthRadarWithAssessmentProps> = ({
  userId,
  autoRefresh = false,
  refreshInterval = 60000,
}) => {
  const [vizData, setVizData] = useState<VisualizationData | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // 获取可视化数据
  const fetchData = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const result = await getVisualizationData(userId);
      if (result.success && result.data) {
        setVizData(result.data);
      } else {
        setError(result.error || '获取数据失败');
      }
    } catch (err) {
      setError('网络错误');
    } finally {
      setIsLoading(false);
    }
  };

  // 自动刷新
  useEffect(() => {
    if (autoRefresh) {
      const interval = setInterval(fetchData, refreshInterval);
      return () => clearInterval(interval);
    }
  }, [autoRefresh, refreshInterval]);

  // 转换雷达图数据
  const getRadarData = () => {
    if (!vizData) return [];

    const { dimension_scores, risk_factors } = vizData;
    
    // 基础维度
    const data = [
      { 
        subject: '疾病风险', 
        score: 100 - dimension_scores.disease, // 转换为健康分数
        fullMark: 100 
      },
      { 
        subject: '生活方式', 
        score: 100 - dimension_scores.lifestyle,
        fullMark: 100 
      },
      { 
        subject: '趋势变化', 
        score: 100 - dimension_scores.trend,
        fullMark: 100 
      },
    ];

    // 添加风险因素维度
    risk_factors.slice(0, 3).forEach(rf => {
      data.push({
        subject: rf.name,
        score: 100 - rf.score,
        fullMark: 100,
      });
    });

    return data;
  };

  // 风险分布饼图数据
  const getRiskDistributionData = () => {
    if (!vizData?.risk_distribution) return [];

    return [
      { name: '高风险', value: vizData.risk_distribution.high, color: '#ef4444' },
      { name: '中风险', value: vizData.risk_distribution.medium, color: '#f59e0b' },
      { name: '低风险', value: vizData.risk_distribution.low, color: '#10b981' },
    ].filter(d => d.value > 0);
  };

  // 获取趋势图标
  const getTrendIcon = (direction: string) => {
    switch (direction) {
      case 'improving':
        return <TrendingUp className="h-4 w-4 text-green-500" />;
      case 'worsening':
        return <TrendingDown className="h-4 w-4 text-red-500" />;
      default:
        return <Minus className="h-4 w-4 text-slate-400" />;
    }
  };

  // 获取趋势文本
  const getTrendText = (direction: string) => {
    switch (direction) {
      case 'improving':
        return '改善中';
      case 'worsening':
        return '需关注';
      default:
        return '稳定';
    }
  };

  // 未加载状态 - 自动加载数据
  React.useEffect(() => {
    if (!vizData && !isLoading && !error) {
      fetchData();
    }
  }, []);

  // 加载中或未加载时显示加载状态
  if (!vizData || !vizData.overview || isLoading) {
    return (
      <Card className="bg-gradient-to-br from-purple-100 to-purple-50 border-purple-200">
        <CardContent className="py-8">
          <div className="text-center space-y-4">
            <Activity className={`h-12 w-12 mx-auto text-purple-500 ${isLoading ? 'animate-spin' : ''}`} />
            <div>
              <h3 className="text-xl font-semibold text-purple-900">健康数据分析</h3>
              <p className="text-purple-700 mt-1">{isLoading ? '正在加载健康数据...' : '准备加载数据'}</p>
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="grid gap-4 grid-cols-1 lg:grid-cols-2">
      {/* 健康雷达图 */}
      <Card className="bg-gradient-to-br from-indigo-100 to-purple-100 border-indigo-200">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="text-xl">多维健康评估</CardTitle>
              <CardDescription>
                {vizData ? (
                  <span className="flex items-center gap-2">
                    综合评分: 
                    <Badge className={getHealthLevelColor(vizData.overview.health_level)}>
                      {Math.round(vizData.overview.overall_score)}分 - {getHealthLevelLabel(vizData.overview.health_level)}
                    </Badge>
                  </span>
                ) : '加载中...'}
              </CardDescription>
            </div>
            <Button
              variant="ghost"
              size="sm"
              onClick={fetchData}
              disabled={isLoading}
            >
              <RefreshCw className={`h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          {error ? (
            <div className="text-center py-8 text-red-500">
              <AlertTriangle className="h-8 w-8 mx-auto mb-2" />
              <p>{error}</p>
              <Button variant="outline" size="sm" className="mt-4" onClick={fetchData}>
                重试
              </Button>
            </div>
          ) : isLoading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="h-8 w-8 animate-spin text-indigo-500" />
            </div>
          ) : vizData ? (
            <ChartContainer height={350}>
              {(width, height) => (
                <RadarChart
                  width={width}
                  height={height}
                  data={getRadarData()}
                  margin={{ top: 20, right: 30, bottom: 20, left: 30 }}
                >
                  <PolarGrid stroke="#e5e7eb" />
                  <PolarAngleAxis 
                    dataKey="subject" 
                    tick={{ fontSize: 12, fill: '#6b7280' }}
                  />
                  <PolarRadiusAxis 
                    angle={30} 
                    domain={[0, 100]} 
                    tick={{ fontSize: 10, fill: '#9ca3af' }}
                  />
                  <Radar
                    name="健康评分"
                    dataKey="score"
                    stroke="#6366f1"
                    fill="#6366f1"
                    fillOpacity={0.3}
                    strokeWidth={2}
                  />
                  <Tooltip
                    contentStyle={{
                      borderRadius: '8px',
                      border: 'none',
                      boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)',
                    }}
                    formatter={(value: number) => [`${Math.round(value)}分`, '健康评分']}
                  />
                  <Legend />
                </RadarChart>
              )}
            </ChartContainer>
          ) : null}
        </CardContent>
      </Card>

      {/* 风险分布和趋势 */}
      <div className="space-y-4">
        {/* 风险分布饼图 */}
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-lg">风险因素分布</CardTitle>
          </CardHeader>
          <CardContent>
            {vizData ? (
              <div className="flex items-center gap-4">
                <ChartContainer height={150}>
                  {(width, height) => (
                    <PieChart width={width} height={height}>
                      <Pie
                        data={getRiskDistributionData()}
                        cx="50%"
                        cy="50%"
                        innerRadius={40}
                        outerRadius={60}
                        paddingAngle={2}
                        dataKey="value"
                      >
                        {getRiskDistributionData().map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Pie>
                      <Tooltip />
                    </PieChart>
                  )}
                </ChartContainer>
                <div className="space-y-2">
                  {getRiskDistributionData().map((item, idx) => (
                    <div key={idx} className="flex items-center gap-2">
                      <div 
                        className="w-3 h-3 rounded-full" 
                        style={{ backgroundColor: item.color }}
                      />
                      <span className="text-sm">{item.name}: {item.value}项</span>
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              <div className="h-[150px] flex items-center justify-center">
                <Loader2 className="h-6 w-6 animate-spin text-slate-400" />
              </div>
            )}
          </CardContent>
        </Card>

        {/* 趋势指标 */}
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-lg">健康趋势</CardTitle>
          </CardHeader>
          <CardContent>
            {vizData?.trend_indicators ? (
              <div className="space-y-3">
                {vizData.trend_indicators.map((indicator, idx) => (
                  <div 
                    key={idx}
                    className="flex items-center justify-between p-3 rounded-lg bg-slate-50"
                  >
                    <div className="flex items-center gap-3">
                      {getTrendIcon(indicator.direction)}
                      <span className="font-medium">{indicator.metric}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Badge 
                        variant="outline"
                        className={
                          indicator.direction === 'improving' 
                            ? 'text-green-600 border-green-200' 
                            : indicator.direction === 'worsening'
                            ? 'text-red-600 border-red-200'
                            : ''
                        }
                      >
                        {getTrendText(indicator.direction)}
                      </Badge>
                      {indicator.deviation !== 0 && (
                        <span className="text-sm text-muted-foreground">
                          {indicator.deviation > 0 ? '+' : ''}{indicator.deviation.toFixed(1)}%
                        </span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="h-[120px] flex items-center justify-center">
                <Loader2 className="h-6 w-6 animate-spin text-slate-400" />
              </div>
            )}
          </CardContent>
        </Card>

        {/* 主要风险因素 */}
        {vizData?.risk_factors && vizData.risk_factors.length > 0 && (
          <Card className="border-orange-200 bg-orange-50/50">
            <CardHeader className="pb-2">
              <CardTitle className="text-lg flex items-center gap-2">
                <AlertTriangle className="h-5 w-5 text-orange-500" />
                主要风险因素
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {vizData.risk_factors.slice(0, 3).map((rf, idx) => (
                  <div 
                    key={idx}
                    className="flex items-center justify-between p-2 rounded bg-white"
                  >
                    <span className="font-medium">{rf.name}</span>
                    <Badge 
                      variant={rf.priority === 'high' ? 'destructive' : 'secondary'}
                    >
                      {rf.priority === 'high' ? '高' : rf.priority === 'medium' ? '中' : '低'}优先级
                    </Badge>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
};

export default HealthRadarWithAssessment;
