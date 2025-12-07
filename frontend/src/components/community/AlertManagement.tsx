import React, { useState } from 'react';
import { AlertTriangle, Bell, CheckCircle, Clock, User, Activity, TrendingUp, Shield, FileText } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../ui/card";
import { Badge } from "../ui/badge";
import { Button } from "../ui/button";
import { Progress } from "../ui/progress";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "../ui/tabs";

export function AlertManagement() {
  const [selectedAlert, setSelectedAlert] = useState<string | null>(null);

  // 预警数据
  const alertsData = [
    {
      id: '1',
      level: 'critical', // critical, warning, info
      name: '赵阿姨',
      age: 70,
      issue: '血压持续偏高',
      value: '145/95 mmHg',
      duration: '持续3天',
      area: '北区',
      status: 'pending', // pending, processing, resolved
      time: '10分钟前',
      description: '连续3天血压测量值超过140/90，建议立即安排医疗干预。',
      suggestions: ['立即联系家属', '预约社区医生', '调整降压药物', '监测饮食和运动'],
    },
    {
      id: '2',
      level: 'critical',
      name: '王大爷',
      age: 75,
      issue: '心率异常',
      value: '105 bpm',
      duration: '1天',
      area: '东区',
      status: 'processing',
      time: '25分钟前',
      description: '静息心率持续超过100次/分钟，可能存在心律失常风险。',
      suggestions: ['安排心电图检查', '联系心内科医生', '避免剧烈运动', '密切观察'],
    },
    {
      id: '3',
      level: 'warning',
      name: '李秀英',
      age: 65,
      issue: '血糖偏高',
      value: '7.5 mmol/L',
      duration: '2天',
      area: '南区',
      status: 'pending',
      time: '1小时前',
      description: '空腹血糖略高于正常范围，建议调整饮食和增加运动。',
      suggestions: ['控制碳水化合物摄入', '增加运动量', '定期监测血糖', '营养师咨询'],
    },
    {
      id: '4',
      level: 'warning',
      name: '张三',
      age: 68,
      issue: '睡眠质量下降',
      value: '平均5小时/天',
      duration: '1周',
      area: '西区',
      status: 'pending',
      time: '2小时前',
      description: '近一周睡眠时长不足，可能影响整体健康状况。',
      suggestions: ['改善睡眠环境', '规律作息时间', '睡前避免过度兴奋', '必要时心理咨询'],
    },
    {
      id: '5',
      level: 'info',
      name: '刘阿姨',
      age: 62,
      issue: '运动量不足',
      value: '3000步/天',
      duration: '3天',
      area: '东区',
      status: 'resolved',
      time: '3小时前',
      description: '日均步数未达到健康目标，建议增加户外活动。',
      suggestions: ['增加散步时间', '参加社区活动', '设定运动目标', '定期回访'],
    },
  ];

  // 干预记录
  const interventionRecords = [
    {
      id: '1',
      date: '2024-11-27 10:30',
      name: '陈奶奶',
      issue: '高血压预警',
      action: '上门健康指导',
      result: '已调整降压药物剂量，血压恢复正常',
      staff: '社区医生 李医生',
      status: 'success',
    },
    {
      id: '2',
      date: '2024-11-26 15:20',
      name: '孙大爷',
      issue: '血糖异常',
      action: '营养咨询与饮食调整',
      result: '制定个性化饮食方案，血糖逐步改善',
      staff: '营养师 王营养师',
      status: 'success',
    },
    {
      id: '3',
      date: '2024-11-25 09:00',
      name: '周阿姨',
      issue: '心理健康问题',
      action: '心理咨询',
      result: '进行3次心理疏导，情绪明显好转',
      staff: '心理咨询师 张老师',
      status: 'success',
    },
    {
      id: '4',
      date: '2024-11-24 14:45',
      name: '吴大爷',
      issue: '运动能力下降',
      action: '康复训练指导',
      result: '制定康复计划，正在执行中',
      staff: '康复师 刘康复师',
      status: 'processing',
    },
  ];

  // 风险等级统计
  const riskStats = [
    { level: '高风险', count: 9, color: 'bg-red-500', percentage: 2.2 },
    { level: '中风险', count: 48, color: 'bg-amber-500', percentage: 12 },
    { level: '低风险', count: 105, color: 'bg-blue-500', percentage: 26.2 },
    { level: '健康', count: 238, color: 'bg-green-500', percentage: 59.6 },
  ];

  const getLevelBadge = (level: string) => {
    switch (level) {
      case 'critical':
        return <Badge className="text-base px-3 py-1 bg-red-500">紧急</Badge>;
      case 'warning':
        return <Badge className="text-base px-3 py-1 bg-amber-500">警告</Badge>;
      case 'info':
        return <Badge className="text-base px-3 py-1 bg-blue-500">提示</Badge>;
      default:
        return null;
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'pending':
        return <Badge variant="outline" className="text-base px-3 py-1">待处理</Badge>;
      case 'processing':
        return <Badge className="text-base px-3 py-1 bg-blue-500">处理中</Badge>;
      case 'resolved':
        return <Badge className="text-base px-3 py-1 bg-green-500">已解决</Badge>;
      default:
        return null;
    }
  };

  return (
    <div className="space-y-6">
      {/* 页面标题 */}
      <div className="flex items-center justify-between">
        <div className="flex flex-col gap-2">
          <h2 className="text-3xl font-bold tracking-tight">预警与干预管理</h2>
          <p className="text-xl text-muted-foreground">智能健康预警系统与干预措施管理</p>
        </div>
        <Button size="lg" className="text-lg px-8">
          <FileText className="mr-2 h-5 w-5" />
          生成干预报告
        </Button>
      </div>

      {/* 风险等级统计 */}
      <div className="grid grid-cols-4 gap-4">
        {riskStats.map((stat, index) => (
          <Card key={index}>
            <CardContent className="pt-6">
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <div className="text-lg text-muted-foreground">{stat.level}人群</div>
                  <div className={`w-4 h-4 rounded-full ${stat.color}`}></div>
                </div>
                <div className="text-5xl font-bold">{stat.count}</div>
                <div className="space-y-2">
                  <Progress value={stat.percentage * 1.5} className="h-2" />
                  <div className="text-base text-muted-foreground">占比 {stat.percentage}%</div>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* 标签页：预警列表和干预记录 */}
      <Tabs defaultValue="alerts" className="space-y-6">
        <TabsList className="grid w-full grid-cols-2 h-14">
          <TabsTrigger value="alerts" className="text-lg">
            <AlertTriangle className="mr-2 h-5 w-5" />
            实时预警列表
          </TabsTrigger>
          <TabsTrigger value="interventions" className="text-lg">
            <CheckCircle className="mr-2 h-5 w-5" />
            干预记录
          </TabsTrigger>
        </TabsList>

        {/* 预警列表 */}
        <TabsContent value="alerts" className="space-y-4">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="text-2xl">当前预警事项</CardTitle>
                <div className="flex gap-3">
                  <Badge className="text-base px-4 py-2 bg-red-500">
                    <AlertTriangle className="h-4 w-4 mr-2" />
                    紧急 2条
                  </Badge>
                  <Badge className="text-base px-4 py-2 bg-amber-500">
                    <Bell className="h-4 w-4 mr-2" />
                    警告 2条
                  </Badge>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {alertsData.map((alert) => (
                  <Card
                    key={alert.id}
                    className={`hover:shadow-lg transition-all cursor-pointer border-l-4 ${
                      alert.level === 'critical'
                        ? 'border-l-red-500'
                        : alert.level === 'warning'
                        ? 'border-l-amber-500'
                        : 'border-l-blue-500'
                    }`}
                    onClick={() => setSelectedAlert(alert.id)}
                  >
                    <CardContent className="py-5">
                      <div className="flex items-start gap-6">
                        {/* 头像 */}
                        <div className="w-16 h-16 rounded-full bg-gradient-to-br from-blue-100 to-blue-50 flex items-center justify-center flex-shrink-0">
                          <User className="h-8 w-8 text-blue-600" />
                        </div>

                        {/* 内容 */}
                        <div className="flex-1 space-y-3">
                          <div className="flex items-start justify-between">
                            <div className="space-y-2">
                              <div className="flex items-center gap-3">
                                <h3 className="text-2xl font-semibold">{alert.name}</h3>
                                <span className="text-lg text-muted-foreground">{alert.age}岁</span>
                                {getLevelBadge(alert.level)}
                                {getStatusBadge(alert.status)}
                              </div>
                              <div className="flex items-center gap-4 text-lg text-muted-foreground">
                                <span className="flex items-center gap-2">
                                  <Activity className="h-5 w-5 text-red-500" />
                                  {alert.issue}
                                </span>
                                <span>·</span>
                                <span>{alert.area}</span>
                                <span>·</span>
                                <span>{alert.time}</span>
                              </div>
                            </div>
                          </div>

                          <div className="grid grid-cols-3 gap-4 p-4 bg-slate-50 rounded-lg">
                            <div>
                              <div className="text-base text-muted-foreground">异常值</div>
                              <div className="text-xl font-bold text-red-600">{alert.value}</div>
                            </div>
                            <div>
                              <div className="text-base text-muted-foreground">持续时间</div>
                              <div className="text-xl font-bold">{alert.duration}</div>
                            </div>
                            <div>
                              <div className="text-base text-muted-foreground">所属区域</div>
                              <div className="text-xl font-bold">{alert.area}</div>
                            </div>
                          </div>

                          <p className="text-lg text-muted-foreground">{alert.description}</p>

                          {selectedAlert === alert.id && (
                            <div className="space-y-3 pt-4 border-t">
                              <h4 className="text-lg font-semibold">干预建议：</h4>
                              <ul className="space-y-2">
                                {alert.suggestions.map((suggestion, idx) => (
                                  <li key={idx} className="flex items-center gap-3 text-base">
                                    <CheckCircle className="h-5 w-5 text-green-500 flex-shrink-0" />
                                    <span>{suggestion}</span>
                                  </li>
                                ))}
                              </ul>
                            </div>
                          )}
                        </div>

                        {/* 操作按钮 */}
                        <div className="flex flex-col gap-2 flex-shrink-0">
                          <Button size="lg" className="text-lg px-6">
                            立即处理
                          </Button>
                          <Button size="lg" variant="outline" className="text-lg px-6">
                            查看详情
                          </Button>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* 干预记录 */}
        <TabsContent value="interventions" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-2xl">历史干预记录</CardTitle>
              <CardDescription className="text-lg">已完成和进行中的健康干预措施</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {interventionRecords.map((record) => (
                  <Card key={record.id} className="hover:shadow-lg transition-all">
                    <CardContent className="py-5">
                      <div className="flex items-start gap-6">
                        {/* 图标 */}
                        <div
                          className={`w-16 h-16 rounded-full flex items-center justify-center flex-shrink-0 ${
                            record.status === 'success'
                              ? 'bg-green-100'
                              : 'bg-blue-100'
                          }`}
                        >
                          {record.status === 'success' ? (
                            <CheckCircle className="h-8 w-8 text-green-600" />
                          ) : (
                            <Clock className="h-8 w-8 text-blue-600" />
                          )}
                        </div>

                        {/* 内容 */}
                        <div className="flex-1 space-y-3">
                          <div className="flex items-start justify-between">
                            <div className="space-y-2">
                              <div className="flex items-center gap-3">
                                <h3 className="text-2xl font-semibold">{record.name}</h3>
                                <Badge
                                  className={`text-base px-3 py-1 ${
                                    record.status === 'success'
                                      ? 'bg-green-500'
                                      : 'bg-blue-500'
                                  }`}
                                >
                                  {record.status === 'success' ? '已完成' : '进行中'}
                                </Badge>
                              </div>
                              <div className="text-lg text-muted-foreground">{record.date}</div>
                            </div>
                          </div>

                          <div className="grid grid-cols-2 gap-6">
                            <div className="space-y-2">
                              <div className="text-base text-muted-foreground">问题类型</div>
                              <div className="text-lg font-semibold">{record.issue}</div>
                            </div>
                            <div className="space-y-2">
                              <div className="text-base text-muted-foreground">干预措施</div>
                              <div className="text-lg font-semibold">{record.action}</div>
                            </div>
                          </div>

                          <div className="space-y-2">
                            <div className="text-base text-muted-foreground">处理结果</div>
                            <div className="text-lg">{record.result}</div>
                          </div>

                          <div className="flex items-center gap-2 text-base text-muted-foreground">
                            <Shield className="h-4 w-4" />
                            <span>负责人：{record.staff}</span>
                          </div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* 干预效果统计 */}
          <Card className="bg-gradient-to-br from-green-50 to-teal-50 border-green-200">
            <CardHeader>
              <div className="flex items-center gap-3">
                <TrendingUp className="h-7 w-7 text-green-600" />
                <CardTitle className="text-2xl">干预效果统计</CardTitle>
              </div>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-3 gap-6">
                <div className="text-center space-y-2">
                  <div className="text-lg text-muted-foreground">本月干预次数</div>
                  <div className="text-5xl font-bold text-green-600">156</div>
                  <div className="text-base text-muted-foreground">较上月 +18次</div>
                </div>
                <div className="text-center space-y-2">
                  <div className="text-lg text-muted-foreground">成功解决率</div>
                  <div className="text-5xl font-bold text-blue-600">92%</div>
                  <div className="text-base text-muted-foreground">较上月 +5%</div>
                </div>
                <div className="text-center space-y-2">
                  <div className="text-lg text-muted-foreground">平均响应时间</div>
                  <div className="text-5xl font-bold text-purple-600">28</div>
                  <div className="text-base text-muted-foreground">分钟</div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
