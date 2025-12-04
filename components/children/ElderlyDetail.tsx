import React from 'react';
import { ChevronLeft, Heart, Activity, Droplets, Thermometer, TrendingUp, Brain, Moon } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../ui/card";
import { Button } from "../ui/button";
import { Badge } from "../ui/badge";
import { Progress } from "../ui/progress";
import { 
  HeartRateChart, 
  SleepAnalysisChart, 
  BloodPressureChart, 
  HealthRadarChart 
} from '../dashboard/HealthCharts';

interface ElderlyDetailProps {
  elderlyId: string;
  onBack: () => void;
}

export function ElderlyDetail({ elderlyId, onBack }: ElderlyDetailProps) {
  // 根据ID获取老人详细数据（这里用模拟数据）
  const elderlyInfo = {
    id: elderlyId,
    name: elderlyId === '1' ? '张三' : elderlyId === '2' ? '李秀英' : elderlyId === '3' ? '王大爷' : '赵阿姨',
    age: elderlyId === '1' ? 68 : elderlyId === '2' ? 65 : elderlyId === '3' ? 72 : 70,
    avatar: elderlyId === '1' ? '👴' : elderlyId === '2' ? '👵' : elderlyId === '3' ? '👴' : '👵',
    relationship: elderlyId === '1' ? '父亲' : elderlyId === '2' ? '母亲' : elderlyId === '3' ? '岳父' : '岳母',
  };

  return (
    <div className="space-y-6">
      {/* 返回按钮和标题 */}
      <div className="flex items-center gap-4">
        <Button
          variant="ghost"
          size="lg"
          onClick={onBack}
          className="text-lg"
        >
          <ChevronLeft className="mr-2 h-5 w-5" />
          返回列表
        </Button>
        <div className="flex items-center gap-4">
          <div className="text-6xl">{elderlyInfo.avatar}</div>
          <div>
            <h2 className="text-3xl font-bold tracking-tight">{elderlyInfo.name}的健康详情</h2>
            <p className="text-xl text-muted-foreground">{elderlyInfo.age}岁 · {elderlyInfo.relationship}</p>
          </div>
        </div>
      </div>

      {/* 实时健康指标卡片 - 使用老人端相同的布局 */}
      <div className="grid gap-4 grid-cols-10">
        {/* 左侧：综合指标 */}
        <div className="col-span-4">
          <Card className="h-full bg-gradient-to-br from-purple-100 to-purple-50 border-purple-200">
            <CardHeader className="pb-3">
              <CardTitle className="text-lg font-medium text-muted-foreground flex items-center gap-2 text-[36px]">
                <Thermometer className="h-5 w-5 text-purple-500" />
                综合指标
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-2">
                <div className="text-base text-muted-foreground text-[32px]">体温</div>
                <div className="flex items-end justify-between">
                  <div className="flex items-baseline gap-2">
                    <span className="text-5xl font-bold">36.5</span>
                    <span className="text-xl text-muted-foreground">°C</span>
                  </div>
                  <div className="text-base text-green-600 flex items-center gap-1">
                    <span>正常</span>
                  </div>
                </div>
              </div>
              
              <div className="space-y-2 pt-4 border-t">
                <div className="text-base text-muted-foreground text-[32px]">步数</div>
                <div className="flex items-end justify-between">
                  <div className="flex items-baseline gap-2">
                    <span className="text-5xl font-bold">8,542</span>
                    <span className="text-xl text-muted-foreground">步</span>
                  </div>
                  <div className="text-base text-green-600">
                    <span>目标 10,000步</span>
                  </div>
                </div>
              </div>
              
              <div className="space-y-2 pt-4 border-t">
                <div className="text-base text-muted-foreground text-[32px]">体重</div>
                <div className="flex items-end justify-between">
                  <div className="flex items-baseline gap-2">
                    <span className="text-5xl font-bold">68.5</span>
                    <span className="text-xl text-muted-foreground">kg</span>
                  </div>
                  <div className="text-base text-blue-600">
                    <span>BMI: 22.4 正常</span>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* 右侧：血糖、血压、心率 */}
        <div className="col-span-6 space-y-4">
          <Card className="bg-gradient-to-br from-amber-100 to-amber-50 border-amber-200">
            <CardContent className="pt-6 pb-4">
              <div className="space-y-4">
                <div className="flex items-center gap-8">
                  <Droplets className="h-8 w-8 text-amber-500 flex-shrink-0" />
                  <div className="flex items-baseline gap-2 w-64">
                    <span className="text-6xl font-bold">5.2</span>
                    <span className="text-xl text-muted-foreground">mmol/L</span>
                  </div>
                  <div className="font-semibold leading-tight ml-auto pr-6 text-[64px] text-[rgb(58,56,56)]">血糖</div>
                </div>
                <div className="text-xl text-muted-foreground text-center pt-2 border-t">
                  正常 空腹血糖
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-blue-100 to-blue-50 border-blue-200">
            <CardContent className="pt-6 pb-4">
              <div className="space-y-4">
                <div className="flex items-center gap-8">
                  <Activity className="h-8 w-8 text-blue-500 flex-shrink-0" />
                  <div className="flex items-baseline gap-2 w-64">
                    <span className="text-6xl font-bold">118/75</span>
                    <span className="text-xl text-muted-foreground">mmHg</span>
                  </div>
                  <div className="font-semibold leading-tight ml-auto pr-6 text-[64px]">血压</div>
                </div>
                <div className="text-xl text-muted-foreground text-center pt-2 border-t">
                  正常 范围内
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-rose-100 to-rose-50 border-rose-200">
            <CardContent className="pt-6 pb-4">
              <div className="space-y-4">
                <div className="flex items-center gap-8">
                  <Heart className="h-8 w-8 text-rose-500 flex-shrink-0" />
                  <div className="flex items-baseline gap-2 w-64">
                    <span className="text-6xl font-bold">72</span>
                    <span className="text-xl text-muted-foreground">bpm</span>
                  </div>
                  <div className="font-semibold leading-tight ml-auto pr-6 text-[64px]">平均心率</div>
                </div>
                <div className="text-xl text-green-600 text-center pt-2 border-t">
                  +2bpm 较昨日
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* 健康趋势图表 */}
      <div className="space-y-4">
        <h3 className="text-2xl font-bold">健康趋势分析</h3>
        <HeartRateChart />
        <SleepAnalysisChart />
        <BloodPressureChart />
        <HealthRadarChart />
      </div>

      {/* 心理健康状态 */}
      <Card className="bg-gradient-to-br from-purple-50 to-pink-50 border-purple-200">
        <CardHeader>
          <div className="flex items-center gap-3">
            <Brain className="h-7 w-7 text-purple-600" />
            <CardTitle className="text-2xl">心理健康状态</CardTitle>
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-3 gap-4">
            <div className="space-y-2">
              <div className="text-lg text-muted-foreground">今日心情</div>
              <div className="text-3xl font-bold text-green-600">😊 愉快</div>
            </div>
            <div className="space-y-2">
              <div className="text-lg text-muted-foreground">压力水平</div>
              <div className="space-y-2">
                <Progress value={30} className="h-3" />
                <div className="text-base text-muted-foreground">低 (30%)</div>
              </div>
            </div>
            <div className="space-y-2">
              <div className="text-lg text-muted-foreground">睡眠质量</div>
              <div className="text-3xl font-bold text-blue-600">良好</div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* 健康建议 */}
      <Card className="bg-gradient-to-br from-green-50 to-teal-50 border-green-200">
        <CardHeader>
          <div className="flex items-center gap-3">
            <TrendingUp className="h-7 w-7 text-green-600" />
            <CardTitle className="text-2xl">AI健康建议</CardTitle>
          </div>
        </CardHeader>
        <CardContent>
          <ul className="space-y-3 text-lg">
            <li className="flex items-start gap-3">
              <span className="text-green-500 text-xl mt-1">✓</span>
              <span>各项健康指标正常，继续保持良好的生活习惯</span>
            </li>
            <li className="flex items-start gap-3">
              <span className="text-green-500 text-xl mt-1">✓</span>
              <span>建议每天坚持散步，保持适量运动</span>
            </li>
            <li className="flex items-start gap-3">
              <span className="text-green-500 text-xl mt-1">✓</span>
              <span>注意饮食均衡，适量摄入蔬菜水果</span>
            </li>
            <li className="flex items-start gap-3">
              <span className="text-green-500 text-xl mt-1">✓</span>
              <span>保持规律作息，每天睡眠7-8小时</span>
            </li>
          </ul>
        </CardContent>
      </Card>
    </div>
  );
}
