import React from 'react';
import { Bell, AlertTriangle, Heart, Pill, Activity, Clock, CheckCircle, TrendingUp } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../ui/card";
import { Badge } from "../ui/badge";
import { Button } from "../ui/button";

// ============================================================================
// 组件说明：子女端 - 智能提醒
// 
// 涉及API:
// - GET /api/v1/children/reminders/list - 获取提醒列表
// - POST /api/v1/children/reminders/create - 创建新提醒
// - PUT /api/v1/children/reminders/{reminderId}/status - 标记提醒状态（已读/已处理）
// - DELETE /api/v1/children/reminders/{reminderId} - 删除提醒
// 
// 数据结构：
// Response: {
//   success: true,
//   data: {
//     total: 5,
//     unread: 2,
//     reminders: [
//       {
//         reminderId: "reminder_001",
//         elderlyId: "elderly_002",
//         elderlyName: "李秀英",
//         type: "health_alert" | "medication" | "appointment" | "exercise",
//         priority: "high" | "medium" | "low",
//         title: "血压偏高提醒",
//         description: "今日血压测量值为 135/88 mmHg，高于正常范围",
//         timestamp: "2024-11-26T14:30:00Z",
//         status: "unread" | "read" | "handled"
//       }
//     ]
//   }
// }
// 
// 功能：
// 1. 显示所有提醒（健康告警、用药提醒、复诊提醒、运动提醒）
// 2. 按优先级分类（高/中/低）
// 3. 标记已读/已处理
// 4. 创建自定义提醒
// ============================================================================

export function SmartReminders() {
  // TODO: Call GET /api/v1/children/reminders/list
  // 模拟提醒数据
  const reminders = [
    {
      id: '1',
      type: 'warning', // warning, info, success
      priority: 'high', // high, medium, low
      elderly: '李秀英',
      title: '血压偏高提醒',
      description: '今日血压测量值为 135/88 mmHg，高于正常范围。建议减少盐分摄入，保持心情平和。',
      time: '10分钟前',
      icon: Activity,
      color: 'text-red-500',
      bgColor: 'bg-red-50',
      borderColor: 'border-red-200',
    },
    {
      id: '2',
      type: 'warning',
      priority: 'high',
      elderly: '赵阿姨',
      title: '血糖偏高提醒',
      description: '空腹血糖 7.2 mmol/L，略高于正常值。建议控制碳水化合物摄入，增加运动量。',
      time: '25分钟前',
      icon: AlertTriangle,
      color: 'text-amber-500',
      bgColor: 'bg-amber-50',
      borderColor: 'border-amber-200',
    },
    {
      id: '3',
      type: 'info',
      priority: 'medium',
      elderly: '张三',
      title: '服药提醒',
      description: '降压药应在每日早上8:00服用，请提醒按时服药。',
      time: '1小时前',
      icon: Pill,
      color: 'text-blue-500',
      bgColor: 'bg-blue-50',
      borderColor: 'border-blue-200',
    },
    {
      id: '4',
      type: 'info',
      priority: 'medium',
      elderly: '王大爷',
      title: '运动量不足',
      description: '今日步数 3,200步，未达到目标10,000步。建议增加户外活动时间。',
      time: '2小时前',
      icon: TrendingUp,
      color: 'text-purple-500',
      bgColor: 'bg-purple-50',
      borderColor: 'border-purple-200',
    },
    {
      id: '5',
      type: 'success',
      priority: 'low',
      elderly: '张三',
      title: '体检提醒',
      description: '距离下次体检还有7天，已预约11月27日上午9:00。',
      time: '3小时前',
      icon: CheckCircle,
      color: 'text-green-500',
      bgColor: 'bg-green-50',
      borderColor: 'border-green-200',
    },
    {
      id: '6',
      type: 'warning',
      priority: 'medium',
      elderly: '李秀英',
      title: '睡眠质量下降',
      description: '近三日平均睡眠时长5.5小时，深度睡眠不足。建议改善睡眠环境，睡前避免过度兴奋。',
      time: '5小时前',
      icon: Clock,
      color: 'text-indigo-500',
      bgColor: 'bg-indigo-50',
      borderColor: 'border-indigo-200',
    },
  ];

  const getPriorityBadge = (priority: string) => {
    switch (priority) {
      case 'high':
        return <Badge className="text-base px-3 py-1 bg-red-500">紧急</Badge>;
      case 'medium':
        return <Badge className="text-base px-3 py-1 bg-amber-500">重要</Badge>;
      case 'low':
        return <Badge className="text-base px-3 py-1 bg-blue-500">一般</Badge>;
      default:
        return null;
    }
  };

  return (
    <div className="space-y-6">
      {/* 页面标题 */}
      <div className="flex items-center justify-between">
        <div className="flex flex-col gap-2">
          <h2 className="text-3xl font-bold tracking-tight">智能健康提醒</h2>
          <p className="text-xl text-muted-foreground">及时关注家人的健康状况变化</p>
        </div>
        <Button size="lg" variant="outline" className="text-lg px-6">
          <CheckCircle className="mr-2 h-5 w-5" />
          标记全部已读
        </Button>
      </div>

      {/* 提醒统计 */}
      <div className="grid grid-cols-3 gap-4">
        <Card className="bg-gradient-to-br from-red-50 to-red-100 border-red-200">
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div className="space-y-2">
                <div className="text-lg text-muted-foreground">紧急提醒</div>
                <div className="text-5xl font-bold text-red-600">
                  {reminders.filter(r => r.priority === 'high').length}
                </div>
              </div>
              <AlertTriangle className="h-12 w-12 text-red-500" />
            </div>
          </CardContent>
        </Card>
        <Card className="bg-gradient-to-br from-amber-50 to-amber-100 border-amber-200">
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div className="space-y-2">
                <div className="text-lg text-muted-foreground">重要提醒</div>
                <div className="text-5xl font-bold text-amber-600">
                  {reminders.filter(r => r.priority === 'medium').length}
                </div>
              </div>
              <Bell className="h-12 w-12 text-amber-500" />
            </div>
          </CardContent>
        </Card>
        <Card className="bg-gradient-to-br from-green-50 to-green-100 border-green-200">
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div className="space-y-2">
                <div className="text-lg text-muted-foreground">今日已处理</div>
                <div className="text-5xl font-bold text-green-600">12</div>
              </div>
              <CheckCircle className="h-12 w-12 text-green-500" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* 提醒列表 */}
      <div className="space-y-3">
        {reminders.map((reminder) => (
          <Card 
            key={reminder.id} 
            className={`hover:shadow-lg transition-all border-l-4 ${reminder.borderColor}`}
          >
            <CardContent className="py-6">
              <div className="flex items-start gap-6">
                {/* 图标 */}
                <div className={`w-16 h-16 rounded-full ${reminder.bgColor} flex items-center justify-center flex-shrink-0`}>
                  <reminder.icon className={`h-8 w-8 ${reminder.color}`} />
                </div>

                {/* 内容 */}
                <div className="flex-1 space-y-3">
                  <div className="flex items-start justify-between">
                    <div className="space-y-2">
                      <div className="flex items-center gap-3">
                        <h3 className="text-2xl font-semibold">{reminder.title}</h3>
                        {getPriorityBadge(reminder.priority)}
                      </div>
                      <div className="flex items-center gap-3 text-lg text-muted-foreground">
                        <span className="font-semibold text-blue-600">{reminder.elderly}</span>
                        <span>·</span>
                        <span>{reminder.time}</span>
                      </div>
                    </div>
                  </div>
                  <p className="text-lg text-muted-foreground leading-relaxed">
                    {reminder.description}
                  </p>
                </div>

                {/* 操作按钮 */}
                <div className="flex gap-2 flex-shrink-0">
                  <Button size="lg" variant="outline" className="text-lg">
                    查看详情
                  </Button>
                  <Button size="lg" className="text-lg">
                    标记已读
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* 历史提醒 */}
      <Card className="bg-gradient-to-br from-slate-50 to-slate-100 border-slate-200">
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="text-2xl">历史提醒记录</CardTitle>
            <Button variant="ghost" size="lg" className="text-lg">
              查看全部
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <div className="text-lg text-muted-foreground text-center py-8">
            共有 156 条历史提醒记录
          </div>
        </CardContent>
      </Card>
    </div>
  );
}