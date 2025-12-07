import React, { useState, useRef, useEffect } from 'react';
import { Smile, Frown, Meh, Heart, TrendingUp, BookOpen, Sun, Cloud, Sparkles } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../ui/card";
import { Button } from "../ui/button";
import { Badge } from "../ui/badge";
import { Progress } from "../ui/progress";
import { MoodTrendChart, StressLevelChart } from "./PsychologyCharts";

// ============================================================================
// 组件说明：老人端心理健康页面
// 
// 涉及API:
// - POST /api/v1/elderly/psychology/mood - 提交心情记录
// - GET /api/v1/elderly/psychology/mood/history?period=month - 获取心情历史
// - GET /api/v1/elderly/psychology/stress - 获取压力水平数据
// 
// 功能：
// 1. 心情记录：选择今日心情（很好/愉快/一般/低落）并添加备注
// 2. 心情趋势图：显示最近30天的心情变化
// 3. 压力水平图：显示压力水平趋势
// 4. 心理健康建议：展示个性化建议
// 5. 情绪日记：查看历史心情记录
// 
// 语音功能：
// - 所有按钮点击都有语音反馈
// - 提交心情后播报确认信息
// ============================================================================

interface PsychologyPageProps {
  initialMood?: string | null;
}

export function PsychologyPage({ initialMood }: PsychologyPageProps) {
  const [selectedMood, setSelectedMood] = useState<string | null>(initialMood || null);
  const moodRecordRef = useRef<HTMLDivElement>(null);

  // 当从今日健康跳转过来时，跳转到页面顶端
  useEffect(() => {
    if (initialMood) {
      window.scrollTo(0, 0);
    }
  }, [initialMood]);

  // 情绪选项
  const moodOptions = [
    { icon: Heart, label: '很好', color: 'text-rose-500', bg: 'bg-rose-50', value: 'excellent' },
    { icon: Smile, label: '愉快', color: 'text-green-500', bg: 'bg-green-50', value: 'good' },
    { icon: Meh, label: '一般', color: 'text-amber-500', bg: 'bg-amber-50', value: 'normal' },
    { icon: Frown, label: '低落', color: 'text-slate-500', bg: 'bg-slate-50', value: 'bad' },
  ];

  // 情绪日记
  const moodDiary = [
    { date: '2024-11-26', mood: 'happy', note: '今天天气很好，散步感觉很愉快', color: 'bg-green-100' },
    { date: '2024-11-25', mood: 'calm', note: '平静的一天，做了瑜伽', color: 'bg-blue-100' },
    { date: '2024-11-24', mood: 'neutral', note: '普通的一天', color: 'bg-gray-100' },
  ];

  // 心理健康建议
  const mentalHealthTips = [
    '保持规律的作息时间',
    '每天进行适量的户外活动',
    '与家人朋友保持联系',
    '培养兴趣爱好，丰富生活',
    '遇到困扰及时倾诉',
  ];

  // 情绪趋势数据
  const emotionTrend = [
    { label: '积极情绪', value: 65, color: 'bg-green-500' },
    { label: '平静状态', value: 25, color: 'bg-blue-500' },
    { label: '消极情绪', value: 10, color: 'bg-orange-500' },
  ];

  return (
    <div className="space-y-6">
      {/* 页面标题 */}
      <div className="flex flex-col gap-2">
        <h2 className="text-3xl font-bold tracking-tight">心理健康中心</h2>
        <p className="text-xl text-muted-foreground">关注您的心理健康，保持身心平衡</p>
      </div>

      {/* 今日心情记录 */}
      <Card className="bg-gradient-to-br from-purple-50 to-pink-50 border-purple-200" ref={moodRecordRef}>
        <CardHeader>
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-full bg-purple-100 flex items-center justify-center">
              <Sparkles className="h-7 w-7 text-purple-600" />
            </div>
            <div>
              <CardTitle className="text-2xl">今日心情记录</CardTitle>
              <CardDescription className="text-lg mt-1">记录您今天的心情状态</CardDescription>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-4 gap-4">
            {moodOptions.map((mood) => (
              <Button
                key={mood.value}
                variant={selectedMood === mood.value ? 'default' : 'outline'}
                className={`h-auto py-6 px-4 flex flex-col items-center gap-3 transition-all ${
                  selectedMood === mood.value 
                    ? 'bg-purple-500 text-white shadow-lg scale-105' 
                    : `hover:${mood.bg} hover:border-purple-300`
                }`}
                onClick={() => setSelectedMood(mood.value)}
              >
                <mood.icon className={`h-10 w-10 ${selectedMood === mood.value ? 'text-white' : mood.color}`} />
                <span className="text-xl font-medium">{mood.label}</span>
              </Button>
            ))}
          </div>
          {selectedMood && (
            <div className="mt-6 p-4 bg-white rounded-lg border border-purple-200">
              <p className="text-lg text-muted-foreground mb-3">今天有什么想说的吗？</p>
              <textarea 
                className="w-full min-h-[100px] p-4 text-lg border rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-purple-400"
                placeholder="写下您今天的感受..."
              />
              <div className="mt-4 flex justify-end">
                <Button size="lg" className="text-lg px-8 py-6 bg-purple-500 hover:bg-purple-600">
                  保存日记
                </Button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* 心理健康可视化图表 - 对应今日健康的四个图表 */}
      <div className="space-y-4">
        <MoodTrendChart />
        <StressLevelChart />
      </div>

      {/* 主要内容区 - 2列布局 */}
      <div className="grid grid-cols-2 gap-6">
        {/* 左侧：情绪趋势 */}
        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <TrendingUp className="h-6 w-6 text-blue-600" />
              <CardTitle className="text-xl">本周情绪趋势</CardTitle>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {emotionTrend.map((trend, idx) => (
                <div key={idx} className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-base font-medium">{trend.label}</span>
                    <span className="text-lg font-bold">{trend.value}%</span>
                  </div>
                  <Progress value={trend.value} className="h-3" />
                </div>
              ))}
            </div>
            <div className="mt-6 p-4 bg-green-50 rounded-lg">
              <p className="text-base text-green-900">
                ✓ 您本周的情绪状态整体良好，继续保持！
              </p>
            </div>
          </CardContent>
        </Card>

        {/* 右侧：心理健康建议 */}
        <Card className="bg-gradient-to-br from-amber-50 to-orange-50 border-amber-200">
          <CardHeader>
            <div className="flex items-center gap-2">
              <Sun className="h-6 w-6 text-amber-600" />
              <CardTitle className="text-xl">心理健康建议</CardTitle>
            </div>
          </CardHeader>
          <CardContent>
            <ul className="space-y-3">
              {mentalHealthTips.map((tip, idx) => (
                <li key={idx} className="flex items-start gap-3 text-base text-amber-900">
                  <Heart className="h-5 w-5 text-amber-500 mt-0.5 flex-shrink-0" />
                  <span className="leading-relaxed">{tip}</span>
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      </div>

      {/* 情绪日记 */}
      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <BookOpen className="h-6 w-6 text-purple-600" />
            <CardTitle className="text-2xl">情绪日记</CardTitle>
          </div>
          <CardDescription className="text-lg">查看您的历史情绪记录</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {moodDiary.map((entry, idx) => (
              <Card key={idx} className="hover:shadow-md transition-all cursor-pointer">
                <CardContent className="py-5">
                  <div className="flex items-center gap-6">
                    <div className={`w-4 h-20 ${entry.color} rounded-full flex-shrink-0`} />
                    <div className="flex-1">
                      <div className="flex items-baseline gap-4 mb-2">
                        <h3 className="text-xl font-semibold">{entry.date}</h3>
                        {entry.mood === 'happy' && <Badge className="text-base bg-green-500">开心</Badge>}
                        {entry.mood === 'calm' && <Badge className="text-base bg-blue-500">平静</Badge>}
                        {entry.mood === 'neutral' && <Badge className="text-base bg-gray-500">一般</Badge>}
                      </div>
                      <p className="text-lg text-muted-foreground leading-relaxed">{entry.note}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </CardContent>
      </Card>

    </div>
  );
}