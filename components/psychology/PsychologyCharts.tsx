import React from 'react';
import { LineChart, Line, BarChart, Bar, RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Area, AreaChart } from 'recharts';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../ui/card";
import { TrendingUp, Activity, Brain, Target } from 'lucide-react';

// 情绪变化趋势数据
const moodTrendData = [
  { date: '11-20', score: 75, label: '周三' },
  { date: '11-21', score: 80, label: '周四' },
  { date: '11-22', score: 72, label: '周五' },
  { date: '11-23', score: 78, label: '周六' },
  { date: '11-24', score: 85, label: '周日' },
  { date: '11-25', score: 82, label: '周一' },
  { date: '11-26', score: 88, label: '周二' },
];

// 压力水平数据
const stressLevelData = [
  { day: '周一', stress: 45, activity: 30 },
  { day: '周二', stress: 55, activity: 40 },
  { day: '周三', stress: 65, activity: 50 },
  { day: '周四', stress: 75, activity: 60 },
  { day: '周五', stress: 85, activity: 70 },
  { day: '周六', stress: 95, activity: 80 },
  { day: '周日', stress: 100, activity: 90 },
];

// 心理健康评分数据
const mentalHealthScoreData = [
  { week: '第1周', score: 72, baseline: 70 },
  { week: '第2周', score: 75, baseline: 70 },
  { week: '第3周', score: 78, baseline: 70 },
  { week: '第4周', score: 82, baseline: 70 },
];

// 心理健康雷达图数据
const mentalHealthRadarData = [
  { dimension: '情绪稳定', current: 85, average: 70, fullMark: 100 },
  { dimension: '社交能力', current: 78, average: 75, fullMark: 100 },
  { dimension: '压力管理', current: 72, average: 68, fullMark: 100 },
  { dimension: '睡眠质量', current: 80, average: 72, fullMark: 100 },
  { dimension: '自我认知', current: 88, average: 80, fullMark: 100 },
  { dimension: '生活满意度', current: 82, average: 75, fullMark: 100 },
];

// 情绪变化趋势图
export function MoodTrendChart() {
  return (
    <Card className="bg-gradient-to-br from-green-50 to-emerald-50 border-green-200">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="space-y-1">
            <CardTitle className="text-2xl flex items-center gap-2">
              <TrendingUp className="h-6 w-6 text-green-600" />
              情绪变化趋势
            </CardTitle>
            <CardDescription className="text-lg">近7天情绪评分变化</CardDescription>
          </div>
          <div className="text-right">
            <div className="text-lg text-muted-foreground">当前评分</div>
            <div className="text-4xl font-bold text-green-600">88</div>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={moodTrendData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
            <XAxis 
              dataKey="label" 
              tick={{ fontSize: 16 }}
              stroke="#666"
            />
            <YAxis 
              domain={[0, 100]}
              tick={{ fontSize: 16 }}
              stroke="#666"
            />
            <Tooltip 
              contentStyle={{ fontSize: '16px', padding: '12px' }}
              labelStyle={{ fontWeight: 'bold', marginBottom: '8px' }}
            />
            <Legend 
              wrapperStyle={{ fontSize: '16px', paddingTop: '20px' }}
            />
            <Line 
              type="monotone" 
              dataKey="score" 
              stroke="#10b981" 
              strokeWidth={3}
              name="情绪评分"
              dot={{ fill: '#10b981', r: 6 }}
              activeDot={{ r: 8 }}
            />
          </LineChart>
        </ResponsiveContainer>
        <div className="mt-4 p-4 bg-green-100 rounded-lg">
          <p className="text-lg text-green-900">
            ✓ 您的情绪状态呈上升趋势，本周平均评分80分，较上周提升5分！
          </p>
        </div>
      </CardContent>
    </Card>
  );
}

// 压力水平分析图
export function StressLevelChart() {
  return (
    <Card className="bg-gradient-to-br from-orange-50 to-red-50 border-orange-200">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="space-y-1">
            <CardTitle className="text-2xl flex items-center gap-2">
              <Activity className="h-6 w-6 text-orange-600" />
              压力水平分析
            </CardTitle>
            <CardDescription className="text-lg">压力指数与活动强度对比</CardDescription>
          </div>
          <div className="text-right">
            <div className="text-lg text-muted-foreground">当前压力</div>
            <div className="text-4xl font-bold text-orange-600">中等</div>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={300}>
          <AreaChart data={stressLevelData}>
            <defs>
              <linearGradient id="colorStress" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#f97316" stopOpacity={0.8}/>
                <stop offset="95%" stopColor="#f97316" stopOpacity={0.1}/>
              </linearGradient>
              <linearGradient id="colorActivity" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.8}/>
                <stop offset="95%" stopColor="#3b82f6" stopOpacity={0.1}/>
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
            <XAxis 
              dataKey="day" 
              tick={{ fontSize: 16 }}
              stroke="#666"
            />
            <YAxis 
              domain={[0, 100]}
              tick={{ fontSize: 16 }}
              stroke="#666"
            />
            <Tooltip 
              contentStyle={{ fontSize: '16px', padding: '12px' }}
              labelStyle={{ fontWeight: 'bold', marginBottom: '8px' }}
            />
            <Legend 
              wrapperStyle={{ fontSize: '16px', paddingTop: '20px' }}
            />
            <Area 
              type="monotone" 
              dataKey="stress" 
              stroke="#f97316" 
              fillOpacity={1} 
              fill="url(#colorStress)"
              strokeWidth={2}
              name="压力指数"
            />
            <Area 
              type="monotone" 
              dataKey="activity" 
              stroke="#3b82f6" 
              fillOpacity={1} 
              fill="url(#colorActivity)"
              strokeWidth={2}
              name="活动强度"
            />
          </AreaChart>
        </ResponsiveContainer>
        <div className="mt-4 grid grid-cols-2 gap-3">
          <div className="p-3 bg-orange-100 rounded-lg">
            <div className="text-base text-orange-700 mb-1">平均压力</div>
            <div className="text-lg font-semibold text-orange-900">62 / 100</div>
          </div>
          <div className="p-3 bg-blue-100 rounded-lg">
            <div className="text-base text-blue-700 mb-1">活动建议</div>
            <div className="text-lg font-semibold text-blue-900">增加运动量</div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

// 心理健康评分图
export function MentalHealthScoreChart() {
  return (
    <Card className="bg-gradient-to-br from-purple-50 to-pink-50 border-purple-200">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="space-y-1">
            <CardTitle className="text-2xl flex items-center gap-2">
              <Brain className="h-6 w-6 text-purple-600" />
              心理健康评分
            </CardTitle>
            <CardDescription className="text-lg">近4周综合评分趋势</CardDescription>
          </div>
          <div className="text-right">
            <div className="text-lg text-muted-foreground">本周评分</div>
            <div className="text-4xl font-bold text-purple-600">82</div>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={mentalHealthScoreData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
            <XAxis 
              dataKey="week" 
              tick={{ fontSize: 16 }}
              stroke="#666"
            />
            <YAxis 
              domain={[0, 100]}
              tick={{ fontSize: 16 }}
              stroke="#666"
            />
            <Tooltip 
              contentStyle={{ fontSize: '16px', padding: '12px' }}
              labelStyle={{ fontWeight: 'bold', marginBottom: '8px' }}
            />
            <Legend 
              wrapperStyle={{ fontSize: '16px', paddingTop: '20px' }}
            />
            <Bar 
              dataKey="score" 
              fill="#a855f7" 
              name="评分"
              radius={[8, 8, 0, 0]}
            />
            <Line 
              type="monotone" 
              dataKey="baseline" 
              stroke="#94a3b8" 
              strokeWidth={2}
              strokeDasharray="5 5"
              name="基准线"
              dot={false}
            />
          </BarChart>
        </ResponsiveContainer>
        <div className="mt-4 p-4 bg-purple-100 rounded-lg">
          <p className="text-lg text-purple-900">
            ✓ 您的心理健康评分持续提升，已超过基准线12分，状态优秀！
          </p>
        </div>
      </CardContent>
    </Card>
  );
}

// 心理健康雷达图
export function MentalHealthRadarChart() {
  return (
    <Card className="bg-gradient-to-br from-amber-50 to-orange-50 border-amber-200">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="space-y-1">
            <CardTitle className="text-2xl flex items-center gap-2">
              <Target className="h-6 w-6 text-amber-600" />
              心理健康雷达图
            </CardTitle>
            <CardDescription className="text-lg">多维度心理健康评估</CardDescription>
          </div>
          <div className="text-right">
            <div className="text-lg text-muted-foreground">综合评分</div>
            <div className="text-4xl font-bold text-amber-600">81</div>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={400}>
          <RadarChart data={mentalHealthRadarData}>
            <PolarGrid stroke="#e0e0e0" />
            <PolarAngleAxis 
              dataKey="dimension" 
              tick={{ fontSize: 16, fill: '#666' }}
            />
            <PolarRadiusAxis 
              domain={[0, 100]}
              tick={{ fontSize: 14 }}
            />
            <Tooltip 
              contentStyle={{ fontSize: '16px', padding: '12px' }}
            />
            <Legend 
              wrapperStyle={{ fontSize: '16px', paddingTop: '20px' }}
            />
            <Radar 
              name="您的评分" 
              dataKey="current" 
              stroke="#f59e0b" 
              fill="#f59e0b" 
              fillOpacity={0.6}
              strokeWidth={2}
            />
            <Radar 
              name="平均水平" 
              dataKey="average" 
              stroke="#94a3b8" 
              fill="#94a3b8" 
              fillOpacity={0.3}
              strokeWidth={2}
            />
          </RadarChart>
        </ResponsiveContainer>
        <div className="mt-4 grid grid-cols-2 gap-3">
          <div className="p-3 bg-green-100 rounded-lg">
            <div className="text-base text-green-700 mb-1">优势维度</div>
            <div className="text-lg font-semibold text-green-900">自我认知 (88分)</div>
          </div>
          <div className="p-3 bg-blue-100 rounded-lg">
            <div className="text-base text-blue-700 mb-1">改进方向</div>
            <div className="text-lg font-semibold text-blue-900">压力管理 (72分)</div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}