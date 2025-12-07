import React from 'react';
import { Users, Heart, Activity, Droplets, Brain, TrendingUp, TrendingDown, AlertCircle } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../ui/card";
import { Badge } from "../ui/badge";
import { Progress } from "../ui/progress";
import { BarChart, Bar, LineChart, Line, RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

export function GroupHealthAnalysis() {
  // 疾病分布数据
  const diseaseData = [
    { disease: '高血压', 人数: 68, 占比: 17 },
    { disease: '糖尿病', 人数: 45, 占比: 11.2 },
    { disease: '冠心病', 人数: 32, 占比: 8 },
    { disease: '慢性支气管炎', 人数: 28, 占比: 7 },
    { disease: '骨质疏松', 人数: 52, 占比: 13 },
    { disease: '关节炎', 人数: 38, 占比: 9.5 },
  ];

  // 健康指标达标率
  const complianceData = [
    { indicator: '血压', 达标: 340, 未达标: 60 },
    { indicator: '血糖', 达标: 355, 未达标: 45 },
    { indicator: '心率', 达标: 370, 未达标: 30 },
    { indicator: '体重', 达标: 320, 未达标: 80 },
    { indicator: '血脂', 达标: 330, 未达标: 70 },
  ];

  // 各年龄段健康指标对比
  const ageHealthData = [
    { age: '60-65', 心率: 70, 血压: 115, 血糖: 5.0, 健康度: 88 },
    { age: '66-70', 心率: 72, 血压: 118, 血糖: 5.2, 健康度: 82 },
    { age: '71-75', 心率: 74, 血压: 122, 血糖: 5.5, 健康度: 75 },
    { age: '76-80', 心率: 76, 血压: 128, 血糖: 5.8, 健康度: 68 },
    { age: '80+', 心率: 78, 血压: 132, 血糖: 6.0, 健康度: 62 },
  ];

  // 综合健康评分雷达图
  const healthRadarData = [
    { subject: '生理健康', 平均分: 82, 满分: 100 },
    { subject: '心理健康', 平均分: 75, 满分: 100 },
    { subject: '运动能力', 平均分: 68, 满分: 100 },
    { subject: '睡眠质量', 平均分: 72, 满分: 100 },
    { subject: '营养状况', 平均分: 78, 满分: 100 },
    { subject: '社交活动', 平均分: 65, 满分: 100 },
  ];

  // 健康改善趋势
  const improvementData = [
    { month: '1月', 健康改善人数: 12, 健康下降人数: 8 },
    { month: '2月', 健康改善人数: 18, 健康下降人数: 6 },
    { month: '3月', 健康改善人数: 22, 健康下降人数: 5 },
    { month: '4月', 健康改善人数: 28, 健康下降人数: 4 },
    { month: '5月', 健康改善人数: 35, 健康下降人数: 3 },
    { month: '6月', 健康改善人数: 42, 健康下降人数: 2 },
  ];

  return (
    <div className="space-y-6">
      {/* 页面标题 */}
      <div className="flex flex-col gap-2">
        <h2 className="text-3xl font-bold tracking-tight">群体健康分析</h2>
        <p className="text-xl text-muted-foreground">深度分析社区居民整体健康状况与趋势</p>
      </div>

      {/* 健康概况统计 */}
      <div className="grid grid-cols-4 gap-4">
        <Card className="bg-gradient-to-br from-rose-50 to-rose-100 border-rose-200">
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div className="space-y-2">
                <div className="text-lg text-muted-foreground">平均心率</div>
                <div className="text-4xl font-bold text-rose-600">73 <span className="text-xl">bpm</span></div>
                <div className="flex items-center gap-2 text-base text-green-600">
                  <TrendingDown className="h-4 w-4" />
                  <span>较上月下降2%</span>
                </div>
              </div>
              <Heart className="h-12 w-12 text-rose-400" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-blue-50 to-blue-100 border-blue-200">
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div className="space-y-2">
                <div className="text-lg text-muted-foreground">平均血压</div>
                <div className="text-4xl font-bold text-blue-600">120<span className="text-2xl">/78</span></div>
                <div className="flex items-center gap-2 text-base text-green-600">
                  <TrendingDown className="h-4 w-4" />
                  <span>较上月下降3%</span>
                </div>
              </div>
              <Activity className="h-12 w-12 text-blue-400" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-amber-50 to-amber-100 border-amber-200">
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div className="space-y-2">
                <div className="text-lg text-muted-foreground">平均血糖</div>
                <div className="text-4xl font-bold text-amber-600">5.4 <span className="text-xl">mmol/L</span></div>
                <div className="flex items-center gap-2 text-base text-green-600">
                  <TrendingDown className="h-4 w-4" />
                  <span>较上月下降1%</span>
                </div>
              </div>
              <Droplets className="h-12 w-12 text-amber-400" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-purple-50 to-purple-100 border-purple-200">
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div className="space-y-2">
                <div className="text-lg text-muted-foreground">心理健康评分</div>
                <div className="text-4xl font-bold text-purple-600">75 <span className="text-xl">分</span></div>
                <div className="flex items-center gap-2 text-base text-green-600">
                  <TrendingUp className="h-4 w-4" />
                  <span>较上月提升5%</span>
                </div>
              </div>
              <Brain className="h-12 w-12 text-purple-400" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* 第一行：疾病分布和健康指标达标率 */}
      <div className="grid grid-cols-2 gap-6">
        {/* 常见疾病分布 */}
        <Card>
          <CardHeader>
            <CardTitle className="text-2xl">常见慢性疾病分布</CardTitle>
            <CardDescription className="text-lg">社区居民主要健康问题统计</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {diseaseData.map((item, index) => (
                <div key={index} className="space-y-2">
                  <div className="flex items-center justify-between text-lg">
                    <div className="flex items-center gap-3">
                      <AlertCircle className="h-5 w-5 text-red-500" />
                      <span className="font-semibold">{item.disease}</span>
                    </div>
                    <div className="flex items-center gap-4">
                      <span className="text-muted-foreground">{item.人数}人</span>
                      <Badge variant="outline" className="text-base">{item.占比}%</Badge>
                    </div>
                  </div>
                  <Progress value={item.占比 * 5} className="h-3" />
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* 健康指标达标率 */}
        <Card>
          <CardHeader>
            <CardTitle className="text-2xl">健康指标达标率</CardTitle>
            <CardDescription className="text-lg">各项生理指标达标情况分析</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={400}>
              <BarChart data={complianceData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="indicator" style={{ fontSize: '14px' }} />
                <YAxis style={{ fontSize: '14px' }} />
                <Tooltip contentStyle={{ fontSize: '14px' }} />
                <Legend wrapperStyle={{ fontSize: '16px' }} />
                <Bar dataKey="达标" fill="#22c55e" radius={[8, 8, 0, 0]} />
                <Bar dataKey="未达标" fill="#ef4444" radius={[8, 8, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* 第二行：各年龄段健康对比和综合健康评分 */}
      <div className="grid grid-cols-2 gap-6">
        {/* 各年龄段健康指标对比 */}
        <Card>
          <CardHeader>
            <CardTitle className="text-2xl">各年龄段健康指标对比</CardTitle>
            <CardDescription className="text-lg">不同年龄组健康状况差异分析</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={350}>
              <LineChart data={ageHealthData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="age" style={{ fontSize: '14px' }} />
                <YAxis style={{ fontSize: '14px' }} />
                <Tooltip contentStyle={{ fontSize: '14px' }} />
                <Legend wrapperStyle={{ fontSize: '16px' }} />
                <Line type="monotone" dataKey="心率" stroke="#ef4444" strokeWidth={2} />
                <Line type="monotone" dataKey="血压" stroke="#3b82f6" strokeWidth={2} />
                <Line type="monotone" dataKey="血糖" stroke="#f59e0b" strokeWidth={2} />
                <Line type="monotone" dataKey="健康度" stroke="#22c55e" strokeWidth={3} />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* 综合健康评分雷达图 */}
        <Card>
          <CardHeader>
            <CardTitle className="text-2xl">综合健康评分</CardTitle>
            <CardDescription className="text-lg">多维度健康状况评估</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={350}>
              <RadarChart data={healthRadarData}>
                <PolarGrid />
                <PolarAngleAxis dataKey="subject" style={{ fontSize: '14px' }} />
                <PolarRadiusAxis style={{ fontSize: '12px' }} />
                <Radar name="平均分" dataKey="平均分" stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.6} />
                <Tooltip contentStyle={{ fontSize: '14px' }} />
                <Legend wrapperStyle={{ fontSize: '16px' }} />
              </RadarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* 第三行：健康改善趋势 */}
      <Card>
        <CardHeader>
          <CardTitle className="text-2xl">健康改善趋势分析</CardTitle>
          <CardDescription className="text-lg">近6个月居民健康改善与下降人数变化</CardDescription>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={350}>
            <LineChart data={improvementData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="month" style={{ fontSize: '14px' }} />
              <YAxis style={{ fontSize: '14px' }} />
              <Tooltip contentStyle={{ fontSize: '14px' }} />
              <Legend wrapperStyle={{ fontSize: '16px' }} />
              <Line type="monotone" dataKey="健康改善人数" stroke="#22c55e" strokeWidth={3} dot={{ r: 6 }} />
              <Line type="monotone" dataKey="健康下降人数" stroke="#ef4444" strokeWidth={3} dot={{ r: 6 }} />
            </LineChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* 健康分析总结 */}
      <Card className="bg-gradient-to-br from-blue-50 to-cyan-50 border-blue-200">
        <CardHeader>
          <div className="flex items-center gap-3">
            <TrendingUp className="h-7 w-7 text-blue-600" />
            <CardTitle className="text-2xl">健康分析总结</CardTitle>
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-4 text-lg leading-relaxed">
            <p className="text-muted-foreground">
              <strong className="text-blue-600">整体趋势：</strong>
              社区居民整体健康状况呈现稳中向好的趋势，近6个月健康改善人数持续增长，健康下降人数逐步减少。
            </p>
            <p className="text-muted-foreground">
              <strong className="text-green-600">主要优势：</strong>
              各项生理指标平均值均在正常范围内，健康指标达标率保持在85%以上，心理健康评分有明显提升。
            </p>
            <p className="text-muted-foreground">
              <strong className="text-amber-600">关注重点：</strong>
              高血压和糖尿病仍是主要慢性疾病，需加强日常监测和健康干预。76岁以上高龄老人健康状况相对较弱，需重点关注。
            </p>
            <p className="text-muted-foreground">
              <strong className="text-purple-600">改进建议：</strong>
              加强健康教育，提高居民健康意识；优化运动和社交活动方案，提升整体生活质量；针对高风险人群制定个性化健康管理计划。
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
