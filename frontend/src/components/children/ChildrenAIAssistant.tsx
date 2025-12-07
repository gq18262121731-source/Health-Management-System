import React, { useState } from 'react';
import { MessageSquare, Send, Bot, User, Sparkles, Heart, Activity, Brain } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../ui/card";
import { Button } from "../ui/button";
import { Input } from "../ui/input";
import { Badge } from "../ui/badge";
import { ScrollArea } from "../ui/scroll-area";

export function ChildrenAIAssistant() {
  const [messages, setMessages] = useState([
    {
      id: '1',
      type: 'ai',
      content: '您好！我是AI健康助手，专门为子女端用户提供关于老人健康的咨询服务。您可以询问关于父母健康数据的解读、健康建议，或者任何关于老人护理的问题。',
      timestamp: '14:30',
    },
    {
      id: '2',
      type: 'user',
      content: '我母亲李秀英最近血压有些偏高，应该注意什么？',
      timestamp: '14:32',
    },
    {
      id: '3',
      type: 'ai',
      content: '根据李秀英女士的健康数据，她的血压为135/88 mmHg，确实略高于正常范围。建议：\n\n1. **饮食调整**：减少盐分摄入，每日控制在6克以内\n2. **规律运动**：每天散步30分钟，避免剧烈运动\n3. **情绪管理**：保持心情平和，避免过度紧张\n4. **定期监测**：每天早晚各测一次血压\n5. **按时服药**：如有降压药物，请确保按时服用\n\n如果血压持续偏高，建议尽快就医咨询。',
      timestamp: '14:32',
    },
  ]);

  const [inputMessage, setInputMessage] = useState('');

  const handleSendMessage = (messageText?: string) => {
    const textToSend = messageText || inputMessage;
    if (!textToSend.trim()) return;

    // 添加用户消息
    const newUserMessage = {
      id: Date.now().toString(),
      type: 'user' as const,
      content: textToSend,
      timestamp: new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' }),
    };

    setMessages(prev => [...prev, newUserMessage]);
    setInputMessage('');

    // 模拟AI回复
    setTimeout(() => {
      const aiResponse = {
        id: (Date.now() + 1).toString(),
        type: 'ai' as const,
        content: getAIResponse(textToSend),
        timestamp: new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' }),
      };
      setMessages(prev => [...prev, aiResponse]);
    }, 1000);
  };

  // 根据问题生成AI回复
  const getAIResponse = (question: string): string => {
    if (question.includes('心率')) {
      return '关于改善父母心率的建议：\n\n1. **规律作息**：保证每天7-8小时睡眠，避免熬夜\n2. **适度运动**：每天散步20-30分钟，太极拳等轻柔运动\n3. **情绪管理**：避免情绪激动，保持心态平和\n4. **饮食调节**：少吃刺激性食物，多吃富含钾的食物如香蕉\n5. **定期监测**：每天固定时间测量心率，记录变化趋势\n\n如果心率持续异常（过快>100次/分或过慢<60次/分），建议及时就医。';
    } else if (question.includes('血压')) {
      return '血压偏高的注意事项：\n\n1. **低盐饮食**：每日盐摄入控制在6克以内\n2. **控制体重**：保持健康体重，BMI在18.5-24之间\n3. **戒烟限酒**：完全戒烟，限制酒精摄入\n4. **规律运动**：每周至少150分钟中等强度运动\n5. **按时服药**：如有降压药，务必按医嘱服用\n6. **监测记录**：每天早晚各测一次血压并记录\n\n血压持续≥140/90mmHg应及时就医调整治疗方案。';
    } else if (question.includes('睡眠')) {
      return '帮助老人改善睡眠的建议：\n\n1. **规律作息**：每天固定时间睡觉和起床\n2. **睡前准备**：睡前1小时避免看手机、电视\n3. **环境优化**：保持卧室安静、黑暗、温度适宜（18-22°C）\n4. **饮食注意**：晚餐不宜过饱，睡前避免咖啡、浓茶\n5. **适度活动**：白天适当运动，但避免睡前剧烈运动\n6. **放松技巧**：可尝试深呼吸、听轻音乐等放松方式\n\n如果失眠持续超过2周，建议咨询医生是否需要药物辅助。';
    }
    return '我已经收到您的问题，正在分析相关健康数据。根据目前的情况，建议您保持关注老人的日常健康指标，如有异常及时就医咨询专业医生。';
  };

  // 快捷问题
  const quickQuestions = [
    { icon: Heart, text: '如何改善父母的心率？', color: 'text-rose-500' },
    { icon: Activity, text: '血压偏高的注意事项', color: 'text-blue-500' },
    { icon: Brain, text: '如何帮助老人改善睡眠？', color: 'text-purple-500' },
  ];

  return (
    <div className="space-y-6">
      {/* 页面标题 */}
      <div className="flex flex-col gap-2">
        <h2 className="text-3xl font-bold tracking-tight">AI健康小助手（子女端）</h2>
        <p className="text-xl text-muted-foreground">专业的老人健康咨询服务</p>
      </div>

      {/* 主聊天区域 */}
      <div className="grid grid-cols-3 gap-6">
        {/* 左侧：聊天窗口 */}
        <div className="col-span-2">
          <Card className="h-[700px] flex flex-col">
            <CardHeader className="border-b">
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 rounded-full bg-gradient-to-br from-blue-500 to-cyan-500 flex items-center justify-center">
                  <Bot className="h-7 w-7 text-white" />
                </div>
                <div>
                  <CardTitle className="text-2xl">AI健康助手</CardTitle>
                  <CardDescription className="text-lg">在线 · 随时为您服务</CardDescription>
                </div>
                <Badge className="ml-auto text-base px-4 py-1 bg-green-500">
                  <Sparkles className="h-4 w-4 mr-1" />
                  智能分析
                </Badge>
              </div>
            </CardHeader>

            {/* 消息列表 */}
            <ScrollArea className="flex-1 p-6">
              <div className="space-y-6">
                {messages.map((message) => (
                  <div
                    key={message.id}
                    className={`flex gap-4 ${message.type === 'user' ? 'flex-row-reverse' : ''}`}
                  >
                    {/* 头像 */}
                    <div className={`w-12 h-12 rounded-full flex items-center justify-center flex-shrink-0 ${
                      message.type === 'ai' 
                        ? 'bg-gradient-to-br from-blue-500 to-cyan-500' 
                        : 'bg-gradient-to-br from-teal-500 to-green-500'
                    }`}>
                      {message.type === 'ai' ? (
                        <Bot className="h-6 w-6 text-white" />
                      ) : (
                        <User className="h-6 w-6 text-white" />
                      )}
                    </div>

                    {/* 消息内容 */}
                    <div className={`flex-1 ${message.type === 'user' ? 'flex justify-end' : ''}`}>
                      <div className={`max-w-[80%] ${
                        message.type === 'ai' 
                          ? 'bg-slate-100' 
                          : 'bg-blue-500 text-white'
                      } rounded-2xl p-5`}>
                        <p className="text-lg leading-relaxed whitespace-pre-line">{message.content}</p>
                        <p className={`text-sm mt-2 ${
                          message.type === 'ai' ? 'text-muted-foreground' : 'text-blue-100'
                        }`}>
                          {message.timestamp}
                        </p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </ScrollArea>

            {/* 输入框 */}
            <div className="border-t p-6">
              <div className="flex gap-3">
                <Input
                  placeholder="输入您想咨询的问题..."
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                  className="text-lg h-14 px-6"
                />
                <Button 
                  size="lg" 
                  onClick={handleSendMessage}
                  className="text-lg px-8 h-14"
                >
                  <Send className="h-5 w-5" />
                </Button>
              </div>
            </div>
          </Card>
        </div>

        {/* 右侧：快捷功能和建议 */}
        <div className="space-y-6">
          {/* 快捷问题 */}
          <Card>
            <CardHeader>
              <CardTitle className="text-xl">快捷问题</CardTitle>
              <CardDescription className="text-base">点击快速询问</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              {quickQuestions.map((question, idx) => (
                <Button
                  key={idx}
                  variant="outline"
                  className="w-full justify-start text-left h-auto py-4 text-base hover:bg-slate-50"
                  onClick={() => handleSendMessage(question.text)}
                >
                  <question.icon className={`h-5 w-5 mr-3 ${question.color}`} />
                  {question.text}
                </Button>
              ))}
            </CardContent>
          </Card>

          {/* AI能力说明 */}
          <Card className="bg-gradient-to-br from-blue-50 to-cyan-50 border-blue-200">
            <CardHeader>
              <div className="flex items-center gap-2">
                <Sparkles className="h-6 w-6 text-blue-600" />
                <CardTitle className="text-xl">AI助手能力</CardTitle>
              </div>
            </CardHeader>
            <CardContent>
              <ul className="space-y-3 text-base text-muted-foreground">
                <li className="flex items-start gap-2">
                  <span className="text-blue-500 mt-1">✓</span>
                  <span>解读老人健康数据</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-blue-500 mt-1">✓</span>
                  <span>提供个性化健康建议</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-blue-500 mt-1">✓</span>
                  <span>分析健康趋势变化</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-blue-500 mt-1">✓</span>
                  <span>解答护理相关问题</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-blue-500 mt-1">✓</span>
                  <span>紧急情况处理建议</span>
                </li>
              </ul>
            </CardContent>
          </Card>

          {/* 使用提示 */}
          <Card className="bg-gradient-to-br from-amber-50 to-orange-50 border-amber-200">
            <CardHeader>
              <CardTitle className="text-xl">温馨提示</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-base text-muted-foreground leading-relaxed">
                AI助手提供的建议仅供参考，如遇紧急情况或严重健康问题，请及时就医咨询专业医生。
              </p>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
