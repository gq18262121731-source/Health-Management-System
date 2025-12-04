import React from 'react';
import { Users, Heart, Activity, TrendingUp, AlertTriangle, CheckCircle, Droplets, Brain } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../ui/card";
import { Badge } from "../ui/badge";
import { LineChart, Line, BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, AreaChart, Area } from 'recharts';

export function DataVisualization() {
  // 健康趋势数据
  const healthTrendData = [
    { month: '1月', 优秀: 120, 良好: 180, 一般: 80, 差: 20 },
    { month: '2月', 优秀: 135, 良好: 175, 一般: 75, 差: 15 },
    { month: '3月', 优秀: 148, 良好: 170, 一般: 70, 差: 12 },
    { month: '4月', 优秀: 160, 良好: 165, 一般: 65, 差: 10 },
    { month: '5月', 优秀: 175, 良好: 160, 一般: 55, 差: 10 },
    { month: '6月', 优秀: 188, 良好: 155, 一般: 50, 差: 7 },
  ];

  // 健康等级分布
  const healthLevelData = [
    { name: '优秀', value: 188, color: '#22c55e' },
    { name: '良好', value: 155, color: '#3b82f6' },
    { name: '一般', value: 50, color: '#f59e0b' },
    { name: '差', value: 7, color: '#ef4444' },
  ];

  // 各项指标平均值趋势
  const vitalsData = [
    { date: '11-21', 心率: 72, 血压: 118, 血糖: 5.2 },
    { date: '11-22', 心率: 71, 血压: 119, 血糖: 5.1 },
    { date: '11-23', 心率: 73, 血压: 117, 血糖: 5.3 },
    { date: '11-24', 心率: 72, 血压: 118, 血糖: 5.2 },
    { date: '11-25', 心率: 70, 血压: 116, 血糖: 5.0 },
    { date: '11-26', 心率: 71, 血压: 117, 血糖: 5.1 },
    { date: '11-27', 心率: 72, 血压: 118, 血糖: 5.2 },
  ];

  // 年龄分布数据
  const ageDistributionData = [
    { age: '60-65岁', 人数: 85 },
    { age: '66-70岁', 人数: 120 },
    { age: '71-75岁', 人数: 98 },
    { age: '76-80岁', 人数: 65 },
    { age: '80岁以上', 人数: 32 },
  ];

  // 区域分布数据
  const areaData = [
    { area: '东区', 总人数: 95, 健康: 78, 预警: 15, 异常: 2 },
    { area: '西区', 总人数: 88, 健康: 70, 预警: 16, 异常: 2 },
    { area: '南区', 总人数: 102, 健康: 85, 预警: 14, 异常: 3 },
    { area: '北区', 总人数: 115, 健康: 95, 预警: 18, 异常: 2 },
  ];

  return (
    <div className="space-y-6">
      {/* 页面标题 */}
      <div className="flex items-center justify-between">
        <div className="flex flex-col gap-2">
          <h2 className="text-3xl font-bold tracking-tight">社区健康数据可视化大屏</h2>
          <p className="text-xl text-muted-foreground">实时监控社区居民健康状况</p>
        </div>
        <Badge className="text-xl px-6 py-3 bg-green-500">
          <CheckCircle className="h-5 w-5 mr-2" />
          系统运行正常
        </Badge>
      </div>

      {/* 核心数据统计 */}
      <div className="grid grid-cols-5 gap-4">
        <Card className="bg-gradient-to-br from-blue-500 to-blue-600 text-white border-0">
          <CardContent className="pt-6">
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <div className="text-lg opacity-90">监测总人数</div>
                <Users className="h-8 w-8 opacity-75" />
              </div>
              <div className="text-5xl font-bold">400</div>
              <div className="text-base opacity-75">较上月 +12人</div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-green-500 to-green-600 text-white border-0">
          <CardContent className="pt-6">
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <div className="text-lg opacity-90">健康人数</div>
                <CheckCircle className="h-8 w-8 opacity-75" />
              </div>
              <div className="text-5xl font-bold">343</div>
              <div className="text-base opacity-75">占比 85.8%</div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-amber-500 to-amber-600 text-white border-0">
          <CardContent className="pt-6">
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <div className="text-lg opacity-90">需关注</div>
                <AlertTriangle className="h-8 w-8 opacity-75" />
              </div>
              <div className="text-5xl font-bold">48</div>
              <div className="text-base opacity-75">占比 12%</div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-red-500 to-red-600 text-white border-0">
          <CardContent className="pt-6">
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <div className="text-lg opacity-90">异常预警</div>
                <AlertTriangle className="h-8 w-8 opacity-75" />
              </div>
              <div className="text-5xl font-bold">9</div>
              <div className="text-base opacity-75">占比 2.2%</div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-purple-500 to-purple-600 text-white border-0">
          <CardContent className="pt-6">
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <div className="text-lg opacity-90">今日测量</div>
                <Activity className="h-8 w-8 opacity-75" />
              </div>
              <div className="text-5xl font-bold">387</div>
              <div className="text-base opacity-75">完成率 96.8%</div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* 第一行：健康趋势和健康等级分布 */}
      <div className="grid grid-cols-2 gap-6">
        {/* 健康等级趋势 */}
        <Card>
          <CardHeader>
            <CardTitle className="text-2xl">健康等级趋势分析</CardTitle>
            <CardDescription className="text-lg">近6个月健康状况变化</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={350}>
              <AreaChart data={healthTrendData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" style={{ fontSize: '14px' }} />
                <YAxis style={{ fontSize: '14px' }} />
                <Tooltip contentStyle={{ fontSize: '14px' }} />
                <Legend wrapperStyle={{ fontSize: '16px' }} />
                <Area type="monotone" dataKey="优秀" stackId="1" stroke="#22c55e" fill="#22c55e" />
                <Area type="monotone" dataKey="良好" stackId="1" stroke="#3b82f6" fill="#3b82f6" />
                <Area type="monotone" dataKey="一般" stackId="1" stroke="#f59e0b" fill="#f59e0b" />
                <Area type="monotone" dataKey="差" stackId="1" stroke="#ef4444" fill="#ef4444" />
              </AreaChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* 当前健康等级分布 */}
        <Card>
          <CardHeader>
            <CardTitle className="text-2xl">当前健康等级分布</CardTitle>
            <CardDescription className="text-lg">400位居民健康状况占比</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-center">
              <ResponsiveContainer width="50%" height={350}>
                <PieChart>
                  <Pie
                    data={healthLevelData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                    outerRadius={120}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {healthLevelData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip contentStyle={{ fontSize: '14px' }} />
                </PieChart>
              </ResponsiveContainer>
              <div className="space-y-4 ml-8">
                {healthLevelData.map((item, index) => (
                  <div key={index} className="flex items-center gap-4">
                    <div className="w-6 h-6 rounded" style={{ backgroundColor: item.color }}></div>
                    <div className="space-y-1">
                      <div className="text-lg font-semibold">{item.name}</div>
                      <div className="text-2xl font-bold">{item.value}人</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* 第二行：生理指标平均值趋势 */}
      <Card>
        <CardHeader>
          <CardTitle className="text-2xl">社区生理指标平均值趋势</CardTitle>
          <CardDescription className="text-lg">近7天心率、血压、血糖平均值变化</CardDescription>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={350}>
            <LineChart data={vitalsData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" style={{ fontSize: '14px' }} />
              <YAxis style={{ fontSize: '14px' }} />
              <Tooltip contentStyle={{ fontSize: '14px' }} />
              <Legend wrapperStyle={{ fontSize: '16px' }} />
              <Line type="monotone" dataKey="心率" stroke="#ef4444" strokeWidth={3} dot={{ r: 5 }} />
              <Line type="monotone" dataKey="血压" stroke="#3b82f6" strokeWidth={3} dot={{ r: 5 }} />
              <Line type="monotone" dataKey="血糖" stroke="#f59e0b" strokeWidth={3} dot={{ r: 5 }} />
            </LineChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* 第三行：年龄分布和区域分布 */}
      <div className="grid grid-cols-2 gap-6">
        {/* 年龄分布 */}
        <Card>
          <CardHeader>
            <CardTitle className="text-2xl">年龄分布统计</CardTitle>
            <CardDescription className="text-lg">社区居民年龄结构</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={350}>
              <BarChart data={ageDistributionData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="age" style={{ fontSize: '14px' }} />
                <YAxis style={{ fontSize: '14px' }} />
                <Tooltip contentStyle={{ fontSize: '14px' }} />
                <Bar dataKey="人数" fill="#8b5cf6" radius={[8, 8, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* 区域分布 */}
        <Card>
          <CardHeader>
            <CardTitle className="text-2xl">区域健康状况分布</CardTitle>
            <CardDescription className="text-lg">各区域居民健康状态统计</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={350}>
              <BarChart data={areaData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="area" style={{ fontSize: '14px' }} />
                <YAxis style={{ fontSize: '14px' }} />
                <Tooltip contentStyle={{ fontSize: '14px' }} />
                <Legend wrapperStyle={{ fontSize: '16px' }} />
                <Bar dataKey="健康" stackId="a" fill="#22c55e" radius={[8, 8, 0, 0]} />
                <Bar dataKey="预警" stackId="a" fill="#f59e0b" />
                <Bar dataKey="异常" stackId="a" fill="#ef4444" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
