import React from 'react';
import { Heart, Activity, Droplets, TrendingUp, TrendingDown, AlertTriangle, CheckCircle } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from "../ui/card";
import { Button } from "../ui/button";
import { Badge } from "../ui/badge";

// ============================================================================
// 组件说明：子女端 - 老人列表
// 
// 涉及API:
// - GET /api/v1/children/elders/list - 获取关联的所有老人及健康概况
// 
// 数据结构：
// Response: {
//   success: true,
//   data: {
//     total: 2,
//     elders: [
//       {
//         elderId: "elderly_001",
//         elderName: "张三",
//         age: 72,
//         relationship: "父亲",
//         healthStatus: "normal" | "warning" | "danger",
//         lastUpdate: "2024-11-26T14:30:00Z",
//         latestVitalSigns: {
//           temperature: 36.5,
//           bloodPressure: { systolic: 118, diastolic: 75 },
//           heartRate: 72,
//           bloodSugar: 5.2
//         },
//         alerts: ["血压偏高", "血糖需注意"] 
//       }
//     ]
//   }
// }
// 
// 功能：
// 1. 展示所有关联老人的健康状态卡片
// 2. 实时显示关键健康指标（心率、血压、血糖、体温）
// 3. 告警提示（血压偏高、心率异常等）
// 4. 点击卡片查看详情
// ============================================================================

interface ElderlyListProps {
  onViewDetail: (elderlyId: string) => void;
}

export function ElderlyList({ onViewDetail }: ElderlyListProps) {
  // TODO: Call GET /api/v1/children/elders/list
  // 模拟老人数据
  const elderlyData = [
    {
      id: '1',
      name: '张三',
      age: 68,
      avatar: '👴',
      relationship: '父亲',
      health: {
        heartRate: 72,
        bloodPressure: '118/75',
        bloodSugar: 5.2,
        temperature: 36.5,
      },
      status: 'good', // good, warning, danger
      alerts: [],
      lastUpdate: '2分钟前',
    },
    {
      id: '2',
      name: '李秀英',
      age: 65,
      avatar: '👵',
      relationship: '母亲',
      health: {
        heartRate: 78,
        bloodPressure: '135/88',
        bloodSugar: 6.8,
        temperature: 36.7,
      },
      status: 'warning',
      alerts: ['血压偏高', '血糖需注意'],
      lastUpdate: '5分钟前',
    },
    {
      id: '3',
      name: '王大爷',
      age: 72,
      avatar: '👴',
      relationship: '岳父',
      health: {
        heartRate: 68,
        bloodPressure: '122/78',
        bloodSugar: 5.5,
        temperature: 36.6,
      },
      status: 'good',
      alerts: [],
      lastUpdate: '10分钟前',
    },
    {
      id: '4',
      name: '赵阿姨',
      age: 70,
      avatar: '👵',
      relationship: '岳母',
      health: {
        heartRate: 85,
        bloodPressure: '140/92',
        bloodSugar: 7.2,
        temperature: 37.1,
      },
      status: 'warning',
      alerts: ['血压偏高', '血糖偏高', '体温略高'],
      lastUpdate: '1分钟前',
    },
  ];

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'good':
        return <Badge className="text-base px-4 py-1 bg-green-500"><CheckCircle className="h-4 w-4 mr-1" />健康</Badge>;
      case 'warning':
        return <Badge className="text-base px-4 py-1 bg-amber-500"><AlertTriangle className="h-4 w-4 mr-1" />需关注</Badge>;
      case 'danger':
        return <Badge className="text-base px-4 py-1 bg-red-500"><AlertTriangle className="h-4 w-4 mr-1" />异常</Badge>;
      default:
        return null;
    }
  };

  return (
    <div className="space-y-6">
      {/* 页面标题 */}
      <div className="flex flex-col gap-2">
        <h2 className="text-3xl font-bold tracking-tight">老人健康监测列表</h2>
        <p className="text-xl text-muted-foreground">实时查看家人的健康状况</p>
      </div>

      {/* 统计概览 */}
      <div className="grid grid-cols-4 gap-4">
        <Card className="bg-gradient-to-br from-blue-50 to-blue-100 border-blue-200">
          <CardContent className="pt-6">
            <div className="text-center space-y-2">
              <div className="text-lg text-muted-foreground">监测总人数</div>
              <div className="text-5xl font-bold text-blue-600">{elderlyData.length}</div>
            </div>
          </CardContent>
        </Card>
        <Card className="bg-gradient-to-br from-green-50 to-green-100 border-green-200">
          <CardContent className="pt-6">
            <div className="text-center space-y-2">
              <div className="text-lg text-muted-foreground">健康状态良好</div>
              <div className="text-5xl font-bold text-green-600">
                {elderlyData.filter(e => e.status === 'good').length}
              </div>
            </div>
          </CardContent>
        </Card>
        <Card className="bg-gradient-to-br from-amber-50 to-amber-100 border-amber-200">
          <CardContent className="pt-6">
            <div className="text-center space-y-2">
              <div className="text-lg text-muted-foreground">需要关注</div>
              <div className="text-5xl font-bold text-amber-600">
                {elderlyData.filter(e => e.status === 'warning').length}
              </div>
            </div>
          </CardContent>
        </Card>
        <Card className="bg-gradient-to-br from-purple-50 to-purple-100 border-purple-200">
          <CardContent className="pt-6">
            <div className="text-center space-y-2">
              <div className="text-lg text-muted-foreground">今日提醒</div>
              <div className="text-5xl font-bold text-purple-600">
                {elderlyData.reduce((sum, e) => sum + e.alerts.length, 0)}
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* 老人列表 */}
      <div className="grid gap-4">
        {elderlyData.map((elderly) => (
          <Card 
            key={elderly.id} 
            className={`hover:shadow-lg transition-all cursor-pointer ${
              elderly.status === 'warning' ? 'border-l-4 border-l-amber-500' :
              elderly.status === 'danger' ? 'border-l-4 border-l-red-500' :
              'border-l-4 border-l-green-500'
            }`}
            onClick={() => onViewDetail(elderly.id)}
          >
            <CardContent className="py-6">
              <div className="flex items-center gap-8">
                {/* 头像和基本信息 */}
                <div className="flex items-center gap-6 w-80">
                  <div className="text-6xl">{elderly.avatar}</div>
                  <div className="space-y-2">
                    <div className="flex items-center gap-3">
                      <h3 className="text-3xl font-bold">{elderly.name}</h3>
                      {getStatusBadge(elderly.status)}
                    </div>
                    <div className="flex items-center gap-4 text-lg text-muted-foreground">
                      <span>{elderly.age}岁</span>
                      <span>·</span>
                      <span>{elderly.relationship}</span>
                    </div>
                    <div className="text-base text-muted-foreground">
                      更新于 {elderly.lastUpdate}
                    </div>
                  </div>
                </div>

                {/* 健康指标 */}
                <div className="flex-1 grid grid-cols-4 gap-6">
                  <div className="space-y-2">
                    <div className="flex items-center gap-2 text-base text-muted-foreground">
                      <Heart className="h-5 w-5 text-rose-500" />
                      心率
                    </div>
                    <div className="text-3xl font-bold">{elderly.health.heartRate}</div>
                    <div className="text-base text-muted-foreground">bpm</div>
                  </div>
                  <div className="space-y-2">
                    <div className="flex items-center gap-2 text-base text-muted-foreground">
                      <Activity className="h-5 w-5 text-blue-500" />
                      血压
                    </div>
                    <div className="text-3xl font-bold">{elderly.health.bloodPressure}</div>
                    <div className="text-base text-muted-foreground">mmHg</div>
                  </div>
                  <div className="space-y-2">
                    <div className="flex items-center gap-2 text-base text-muted-foreground">
                      <Droplets className="h-5 w-5 text-amber-500" />
                      血糖
                    </div>
                    <div className="text-3xl font-bold">{elderly.health.bloodSugar}</div>
                    <div className="text-base text-muted-foreground">mmol/L</div>
                  </div>
                  <div className="space-y-2">
                    <div className="flex items-center gap-2 text-base text-muted-foreground">
                      <Activity className="h-5 w-5 text-purple-500" />
                      体温
                    </div>
                    <div className="text-3xl font-bold">{elderly.health.temperature}</div>
                    <div className="text-base text-muted-foreground">°C</div>
                  </div>
                </div>

                {/* 提醒和操作 */}
                <div className="w-64 space-y-3">
                  {elderly.alerts.length > 0 ? (
                    <div className="space-y-2">
                      <div className="text-base text-amber-600 font-semibold">健康提醒：</div>
                      {elderly.alerts.map((alert, idx) => (
                        <div key={idx} className="text-base text-muted-foreground flex items-center gap-2">
                          <span className="text-amber-500">•</span>
                          {alert}
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-base text-green-600">✓ 各项指标正常</div>
                  )}
                  <Button size="lg" className="w-full text-lg mt-3">
                    查看详情
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}