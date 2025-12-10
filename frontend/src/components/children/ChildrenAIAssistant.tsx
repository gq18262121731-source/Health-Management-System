import React, { useState, useRef, useEffect } from 'react';
import { MessageSquare, Send, Bot, User, Sparkles, Heart, Activity, Brain, Loader2, Stethoscope, Apple, Smile } from 'lucide-react';

// 智能体配置 - 独特标识
const AGENT_CONFIG: Record<string, { icon: any; gradient: string; badgeColor: string; label: string }> = {
  '健康管家': {
    icon: Bot,
    gradient: 'from-blue-500 to-cyan-500',
    badgeColor: 'bg-blue-50 text-blue-600 border-blue-200',
    label: '🏠 健康管家'
  },
  '慢病专家': {
    icon: Stethoscope,
    gradient: 'from-red-500 to-rose-500',
    badgeColor: 'bg-red-50 text-red-600 border-red-200',
    label: '🩺 慢病专家'
  },
  '生活教练': {
    icon: Apple,
    gradient: 'from-green-500 to-emerald-500',
    badgeColor: 'bg-green-50 text-green-600 border-green-200',
    label: '🥗 生活教练'
  },
  '情感关怀': {
    icon: Smile,
    gradient: 'from-purple-500 to-pink-500',
    badgeColor: 'bg-purple-50 text-purple-600 border-purple-200',
    label: '💜 情感关怀'
  },
  '心理关怀师': {
    icon: Smile,
    gradient: 'from-purple-500 to-pink-500',
    badgeColor: 'bg-purple-50 text-purple-600 border-purple-200',
    label: '💜 心理关怀师'
  },
  '系统': {
    icon: Bot,
    gradient: 'from-gray-400 to-gray-500',
    badgeColor: 'bg-gray-50 text-gray-600 border-gray-200',
    label: '⚙️ 系统'
  }
};

// 获取智能体配置
const getAgentConfig = (agent: string) => {
  return AGENT_CONFIG[agent] || AGENT_CONFIG['健康管家'];
};
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../ui/card";
import { Button } from "../ui/button";
import { Input } from "../ui/input";
import { Badge } from "../ui/badge";
import { ScrollArea } from "../ui/scroll-area";

// API基础URL（通过Vite代理，使用相对路径）
const API_BASE_URL = '';

export function ChildrenAIAssistant() {
  const [messages, setMessages] = useState([
    {
      id: '1',
      type: 'ai',
      content: '您好！我是AI健康助手，由多智能体系统驱动。我可以帮您：\n\n• 解读父母的健康数据\n• 提供专业的健康建议\n• 分析健康趋势变化\n• 解答护理相关问题\n\n请问有什么可以帮您的？',
      timestamp: new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' }),
      agent: '健康管家',
    },
  ]);

  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId] = useState(() => `children_${Date.now().toString(36)}`);
  const scrollRef = useRef<HTMLDivElement>(null);

  // 自动滚动到底部
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSendMessage = async (messageText?: string) => {
    const textToSend = messageText || inputMessage;
    if (!textToSend.trim() || isLoading) return;

    // 添加用户消息
    const newUserMessage = {
      id: Date.now().toString(),
      type: 'user' as const,
      content: textToSend,
      timestamp: new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' }),
    };

    setMessages(prev => [...prev, newUserMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      // 调用多智能体API
      const response = await fetch(`${API_BASE_URL}/api/v1/ai/consult/public`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_input: textToSend,
          user_role: 'children',  // 子女角色
          session_id: sessionId,
        }),
      });

      if (!response.ok) {
        throw new Error('AI服务暂时不可用');
      }

      const data = await response.json();
      
      const aiResponse = {
        id: (Date.now() + 1).toString(),
        type: 'ai' as const,
        content: data.data?.response || '抱歉，我暂时无法回答这个问题。',
        timestamp: new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' }),
        agent: data.data?.agent || '健康管家',
      };
      
      setMessages(prev => [...prev, aiResponse]);
    } catch (error) {
      console.error('AI请求失败:', error);
      const errorResponse = {
        id: (Date.now() + 1).toString(),
        type: 'ai' as const,
        content: '抱歉，AI服务暂时不可用，请稍后再试。',
        timestamp: new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' }),
        agent: '系统',
      };
      setMessages(prev => [...prev, errorResponse]);
    } finally {
      setIsLoading(false);
    }
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
            <ScrollArea className="flex-1 p-6" ref={scrollRef}>
              <div className="space-y-6">
                {messages.map((message: any) => {
                  const agentConfig = message.type === 'ai' ? getAgentConfig(message.agent) : null;
                  const AgentIcon = agentConfig?.icon || Bot;
                  
                  return (
                    <div
                      key={message.id}
                      className={`flex gap-4 ${message.type === 'user' ? 'flex-row-reverse' : ''}`}
                    >
                      {/* 头像 - 根据智能体显示不同颜色 */}
                      <div className={`w-12 h-12 rounded-full flex items-center justify-center flex-shrink-0 bg-gradient-to-br ${
                        message.type === 'ai' 
                          ? agentConfig?.gradient || 'from-blue-500 to-cyan-500'
                          : 'from-teal-500 to-green-500'
                      }`}>
                        {message.type === 'ai' ? (
                          <AgentIcon className="h-6 w-6 text-white" />
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
                          {/* 智能体标签 - 独特颜色 */}
                          {message.type === 'ai' && message.agent && (
                            <Badge variant="outline" className={`mb-2 text-xs ${agentConfig?.badgeColor || 'bg-blue-50 text-blue-600 border-blue-200'}`}>
                              {agentConfig?.label || message.agent}
                            </Badge>
                          )}
                          <p className="text-lg leading-relaxed whitespace-pre-line">{message.content}</p>
                          <p className={`text-sm mt-2 ${
                            message.type === 'ai' ? 'text-muted-foreground' : 'text-blue-100'
                          }`}>
                            {message.timestamp}
                          </p>
                        </div>
                      </div>
                    </div>
                  );
                })}
                
                {/* 加载状态 */}
                {isLoading && (
                  <div className="flex gap-4">
                    <div className="w-12 h-12 rounded-full bg-gradient-to-br from-blue-500 to-cyan-500 flex items-center justify-center flex-shrink-0">
                      <Bot className="h-6 w-6 text-white" />
                    </div>
                    <div className="bg-slate-100 rounded-2xl p-5 flex items-center gap-2">
                      <Loader2 className="h-5 w-5 animate-spin text-blue-500" />
                      <span className="text-muted-foreground">AI正在思考...</span>
                    </div>
                  </div>
                )}
              </div>
            </ScrollArea>

            {/* 输入框 */}
            <div className="border-t p-6">
              <div className="flex gap-3">
                <Input
                  placeholder="输入您想咨询的问题..."
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && !isLoading && handleSendMessage()}
                  className="text-lg h-14 px-6"
                  disabled={isLoading}
                />
                <Button 
                  size="lg" 
                  onClick={() => handleSendMessage()}
                  className="text-lg px-8 h-14"
                  disabled={isLoading}
                >
                  {isLoading ? <Loader2 className="h-5 w-5 animate-spin" /> : <Send className="h-5 w-5" />}
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
