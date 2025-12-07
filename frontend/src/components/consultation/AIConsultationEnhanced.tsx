import React, { useState, useRef, useEffect } from 'react';
import { Bot, Send, Mic, MicOff, Volume2, VolumeX, StopCircle, AlertCircle, History, BookOpen, TrendingUp, Lightbulb, Clock, Star, Heart, Activity, Brain, Loader2 } from 'lucide-react';
import { useVoiceService } from '../../hooks/useVoiceService';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../ui/card";
import { Button } from "../ui/button";
import { Input } from "../ui/input";
import { ScrollArea } from "../ui/scroll-area";
import { Badge } from "../ui/badge";

interface Message {
  id: string;
  type: 'user' | 'ai';
  content: string;
  timestamp: Date;
}

export function AIConsultationEnhanced() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      type: 'ai',
      content: '您好，我是您的AI健康助手。我注意到您最近的健康数据显示血压略高（118/75 mmHg），且深睡时间较短。请问您有什么不舒服的地方吗？',
      timestamp: new Date()
    }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [autoSpeak, setAutoSpeak] = useState(true); // AI回复自动播报
  const scrollAreaRef = useRef<HTMLDivElement>(null);
  
  // 使用语音服务 Hook
  const {
    isRecording,
    isProcessing,
    transcript,
    isSpeaking,
    startRecording,
    stopRecording,
    cancelRecording,
    speak,
    stopSpeaking,
    resetTranscript,
    error: voiceError,
    clearError
  } = useVoiceService();

  // 健康状态摘要
  const healthSummary = "您目前的总体状态：中等风险，血压略高、睡眠不足。";

  // 历史会话
  const historySessions = [
    { id: 1, title: '关于头晕的咨询', date: '今天 10:30', summary: '讨论了头晕症状和可能原因' },
    { id: 2, title: '睡眠质量改善方案', date: '昨天 15:20', summary: '获得了改善睡眠的建议' },
    { id: 3, title: '血压管理建议', date: '11-24 14:15', summary: '了解血压管理的方法' },
  ];

  // 健康知识库
  const knowledgeBase = [
    { icon: Heart, title: '心血管健康', desc: '了解如何保持心血管健康', color: 'text-rose-500' },
    { icon: Activity, title: '运动与健身', desc: '适合老年人的运动建议', color: 'text-blue-500' },
    { icon: Brain, title: '睡眠质量', desc: '改善睡眠质量的方法', color: 'text-purple-500' },
  ];

  // 今日健康提示
  const dailyTips = [
    '每天保持7-8小时睡眠',
    '适量饮水，每天1500-2000ml',
    '坚持每天散步30分钟',
    '避免高盐高糖饮食',
  ];

  // 滚动到底部
  const scrollToBottom = () => {
    if (scrollAreaRef.current) {
      const scrollElement = scrollAreaRef.current.querySelector('[data-radix-scroll-area-viewport]');
      if (scrollElement) {
        scrollElement.scrollTop = scrollElement.scrollHeight;
      }
    }
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // 语音播报健康摘要
  const handleSpeakSummary = async () => {
    if (isSpeaking) {
      stopSpeaking();
    } else {
      await speak(healthSummary);
    }
  };

  // 当语音识别结果变化时，更新输入框
  useEffect(() => {
    if (transcript) {
      setInputValue(transcript);
      resetTranscript();
    }
  }, [transcript, resetTranscript]);

  // 显示语音错误提示
  useEffect(() => {
    if (voiceError) {
      console.error('语音错误:', voiceError);
      // 3秒后清除错误
      const timer = setTimeout(clearError, 3000);
      return () => clearTimeout(timer);
    }
  }, [voiceError, clearError]);

  // 发送消息
  const handleSendMessage = (content: string) => {
    if (!content.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: content,
      timestamp: new Date()
    };
    setMessages(prev => [...prev, userMessage]);
    setInputValue('');

    setTimeout(async () => {
      const aiResponse = generateAIResponse(content);
      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'ai',
        content: aiResponse,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, aiMessage]);
      
      // 自动语音播报 AI 回复
      if (autoSpeak) {
        await speak(aiResponse);
      }
    }, 1000);
  };

  // 快速问题处理
  const handleQuickQuestion = (question: string) => {
    handleSendMessage(question);
  };

  // 语音输入 - 使用后端 ASR
  const handleVoiceInput = async () => {
    if (isRecording) {
      // 停止录音并识别
      const text = await stopRecording();
      if (text) {
        setInputValue(text);
      }
    } else {
      // 开始录音
      await startRecording();
    }
  };

  // 取消录音
  const handleCancelRecording = () => {
    cancelRecording();
  };

  // 生成AI回复
  const generateAIResponse = (userInput: string): string => {
    const input = userInput.toLowerCase();
    
    if (input.includes('头晕') || input.includes('晕')) {
      return '根据您的描述和近期健康数据，头晕可能与以下因素有关：\n\n1. 睡眠不足：您近期深睡时间较短，这会影响大脑休息\n2. 血压波动：虽然您的血压118/75属于正常范围，但如果有波动也可能导致头晕\n3. 血糖问题：建议检查是否按时进餐\n\n建议您：保证每晚7-8小时睡眠，避免突然起身，多喝温水。如果症状持续或加重，请及时就医。';
    }
    
    if (input.includes('为什么') || input.includes('原因')) {
      return '您目前血压略高和睡眠不足的主要原因可能包括：\n\n1. 生活作息不规律\n2. 精神压力较大\n3. 饮食中盐分摄入偏高\n4. 缺乏规律运动\n5. 睡前使用电子设备影响睡眠质量\n\n建议您记录一周的生活习惯，这样我们可以更准确地找出具体原因。';
    }
    
    if (input.includes('做什么') || input.includes('怎么办')) {
      return '针对您目前的健康状况，建议您采取以下措施：\n\n1. 作息调整：每晚22:00前入睡，保证7-8小时睡眠\n2. 饮食建议：减少盐分摄入，多吃新鲜蔬果，避免油腻食物\n3. 运动建议：每天散步30分钟，可选择早晨或傍晚\n4. 放松技巧：睡前可以听轻音乐、做深呼吸练习\n5. 定期监测：每天早晚各测量一次血压，记录在健康日记中\n\n这些都是安全且有效的方法，可以逐步改善您的健康状况。';
    }
    
    if (input.includes('医院') || input.includes('就医')) {
      return '根据您目前的情况，属于中等风险，暂时不需要立即就医。但如果出现以下情况，请及时就医：\n\n紧急情况（立即就医）：\n• 血压超过140/90 mmHg\n• 持续剧烈头痛或头晕\n• 胸闷、胸痛\n• 呼吸困难\n• 意识模糊\n\n建议就医：\n• 症状持续3天以上无好转\n• 睡眠问题严重影响日常生活\n• 出现新的不适症状\n\n定期体检：建议每3-6个月进行一次全面体检。';
    }

    return `我理解您的问题。基于您的健康数据，我建议您：\n\n1. 注意休息，保证充足睡眠\n2. 保持规律的作息时间\n3. 适当运动，但避免剧烈活动\n4. 饮食清淡，多喝水\n5. 继续监测您的生命体征\n\n如有任何不适加重的情况，请及时就医。您还有其他问题吗？`;
  };

  return (
    <div className="h-[calc(100vh-12rem)] grid grid-cols-4 gap-4">
      {/* 左侧：对话区域 (3/4宽度) */}
      <div className="col-span-3 flex flex-col gap-4">
        {/* 健康状态条 */}
        <Card className="bg-gradient-to-r from-orange-50 to-amber-50 border-orange-200">
          <div className="p-5 flex items-center justify-between">
            <div className="flex items-center gap-3 flex-1">
              <div className="w-12 h-12 rounded-full bg-orange-100 flex items-center justify-center flex-shrink-0">
                <AlertCircle className="h-6 w-6 text-orange-600" />
              </div>
              <div className="flex-1">
                <p className="text-xl font-medium text-orange-900 leading-relaxed">
                  {healthSummary}
                </p>
              </div>
            </div>
            <Button 
              variant="outline" 
              size="lg"
              className={`ml-4 flex-shrink-0 min-w-[140px] text-lg py-6 ${isSpeaking ? 'bg-blue-50 border-blue-300 text-blue-600' : 'bg-white'}`}
              onClick={handleSpeakSummary}
            >
              {isSpeaking ? (
                <>
                  <StopCircle className="mr-2 h-5 w-5" />
                  停止播报
                </>
              ) : (
                <>
                  <Volume2 className="mr-2 h-5 w-5" />
                  听你念一遍
                </>
              )}
            </Button>
          </div>
        </Card>

        {/* 对话区 */}
        <Card className="flex-1 flex flex-col min-h-0">
          <div className="p-5 border-b bg-slate-50/50">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-100 to-cyan-100 flex items-center justify-center">
                <Bot className="h-6 w-6 text-blue-600" />
              </div>
              <div>
                <h3 className="text-xl font-semibold">AI健康助手</h3>
                <p className="text-base text-muted-foreground">实时为您解答健康疑问</p>
              </div>
            </div>
          </div>
          
          <ScrollArea className="flex-1 p-6" ref={scrollAreaRef}>
            <div className="space-y-6">
              {messages.map((message) => (
                <div 
                  key={message.id} 
                  className={`flex gap-4 ${message.type === 'user' ? 'flex-row-reverse' : ''}`}
                >
                  <div className={`w-14 h-14 rounded-full flex items-center justify-center flex-shrink-0 ${
                    message.type === 'ai' 
                      ? 'bg-gradient-to-br from-blue-100 to-cyan-100' 
                      : 'bg-gradient-to-br from-slate-200 to-slate-300'
                  }`}>
                    {message.type === 'ai' ? (
                      <Bot className="h-7 w-7 text-blue-600" />
                    ) : (
                      <span className="text-lg font-semibold text-slate-700">我</span>
                    )}
                  </div>
                  
                  <div className={`max-w-[75%] ${message.type === 'user' ? 'items-end' : 'items-start'} flex flex-col gap-2`}>
                    <div className={`px-6 py-4 rounded-2xl text-lg leading-loose whitespace-pre-line ${
                      message.type === 'ai'
                        ? 'bg-gradient-to-br from-slate-50 to-slate-100 text-slate-900 rounded-tl-none border border-slate-200'
                        : 'bg-gradient-to-br from-blue-500 to-blue-600 text-white rounded-tr-none shadow-md'
                    }`}>
                      {message.content}
                    </div>
                    <span className="text-base text-muted-foreground px-2">
                      {message.timestamp.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </ScrollArea>

          {/* 快速问题 */}
          <div className="px-6 pt-4 pb-3 border-t bg-slate-50/50">
            <div className="grid grid-cols-3 gap-3">
              <Button 
                variant="outline" 
                size="lg"
                className="h-auto py-4 px-4 text-lg hover:bg-blue-50 hover:border-blue-300 hover:text-blue-600 transition-all"
                onClick={() => handleQuickQuestion('为什么会这样？')}
              >
                <span className="font-medium">为什么会这样？</span>
              </Button>
              <Button 
                variant="outline" 
                size="lg"
                className="h-auto py-4 px-4 text-lg hover:bg-green-50 hover:border-green-300 hover:text-green-600 transition-all"
                onClick={() => handleQuickQuestion('我可以做什么？')}
              >
                <span className="font-medium">我可以做什么？</span>
              </Button>
              <Button 
                variant="outline" 
                size="lg"
                className="h-auto py-4 px-4 text-lg hover:bg-orange-50 hover:border-orange-300 hover:text-orange-600 transition-all"
                onClick={() => handleQuickQuestion('需要去医院吗？')}
              >
                <span className="font-medium">需要去医院吗？</span>
              </Button>
            </div>
          </div>

          {/* 输入区 */}
          <div className="p-6 border-t bg-white">
            <div className="flex gap-3">
              <Button
                variant="outline"
                size="lg"
                className={`flex-shrink-0 h-16 w-16 ${isRecording ? 'bg-red-50 border-red-300 text-red-600 animate-pulse' : ''} ${isProcessing ? 'bg-blue-50 border-blue-300' : ''}`}
                onClick={handleVoiceInput}
                disabled={isProcessing}
              >
                {isProcessing ? (
                  <Loader2 className="h-7 w-7 animate-spin text-blue-600" />
                ) : isRecording ? (
                  <MicOff className="h-7 w-7" />
                ) : (
                  <Mic className="h-7 w-7" />
                )}
              </Button>
              
              <Input
                placeholder="比如：我最近老头晕，是不是血压太高？"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    handleSendMessage(inputValue);
                  }
                }}
                className="flex-1 h-16 text-lg px-6 border-slate-300 focus:border-blue-400 focus:ring-blue-400"
              />
              
              <Button
                size="lg"
                className="flex-shrink-0 h-16 px-10 bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 text-white shadow-md"
                onClick={() => handleSendMessage(inputValue)}
              >
                <Send className="mr-2 h-6 w-6" />
                <span className="text-lg font-medium">发送</span>
              </Button>
            </div>
            
            {/* 语音状态提示 */}
            {isRecording && (
              <div className="mt-3 flex items-center justify-center gap-3">
                <div className="text-base text-red-600 animate-pulse font-medium">
                  🎤 正在录音，请说话...
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  className="text-gray-500 hover:text-red-500"
                  onClick={handleCancelRecording}
                >
                  取消
                </Button>
              </div>
            )}
            {isProcessing && (
              <div className="mt-3 text-center text-base text-blue-600 font-medium">
                📝 正在识别语音...
              </div>
            )}
            {voiceError && (
              <div className="mt-3 text-center text-base text-orange-600 font-medium">
                ⚠️ {voiceError}
              </div>
            )}
            
            {/* 自动播报开关 */}
            <div className="mt-3 flex items-center justify-end gap-2">
              <span className="text-sm text-muted-foreground">AI回复自动播报</span>
              <Button
                variant="ghost"
                size="sm"
                className={`px-2 ${autoSpeak ? 'text-blue-600' : 'text-gray-400'}`}
                onClick={() => setAutoSpeak(!autoSpeak)}
              >
                {autoSpeak ? <Volume2 className="h-5 w-5" /> : <VolumeX className="h-5 w-5" />}
              </Button>
            </div>
          </div>
        </Card>
      </div>

      {/* 右侧：功能区域 (1/4宽度) */}
      <div className="col-span-1 flex flex-col gap-4 overflow-y-auto">
        {/* 今日健康提示 */}
        <Card className="bg-gradient-to-br from-green-50 to-emerald-50 border-green-200">
          <CardHeader className="pb-4">
            <div className="flex items-center gap-2">
              <Lightbulb className="h-6 w-6 text-green-600" />
              <CardTitle className="text-xl">今日健康提示</CardTitle>
            </div>
          </CardHeader>
          <CardContent>
            <ul className="space-y-3">
              {dailyTips.map((tip, idx) => (
                <li key={idx} className="flex items-start gap-3 text-base text-green-900">
                  <Star className="h-5 w-5 text-green-500 mt-0.5 flex-shrink-0" />
                  <span className="leading-relaxed">{tip}</span>
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>

        {/* 健康知识库 */}
        <Card>
          <CardHeader className="pb-4">
            <div className="flex items-center gap-2">
              <BookOpen className="h-6 w-6 text-blue-600" />
              <CardTitle className="text-xl">健康知识库</CardTitle>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {knowledgeBase.map((item, idx) => (
                <Button
                  key={idx}
                  variant="outline"
                  className="w-full h-auto py-4 px-4 flex items-start gap-3 hover:bg-blue-50 hover:border-blue-300 transition-all"
                >
                  <item.icon className={`h-6 w-6 ${item.color} mt-0.5 flex-shrink-0`} />
                  <div className="text-left flex-1">
                    <div className="text-lg font-medium">{item.title}</div>
                    <div className="text-base text-muted-foreground mt-1">{item.desc}</div>
                  </div>
                </Button>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* 历史会话 */}
        <Card>
          <CardHeader className="pb-4">
            <div className="flex items-center gap-2">
              <History className="h-6 w-6 text-purple-600" />
              <CardTitle className="text-xl">历史会话</CardTitle>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {historySessions.map((session) => (
                <Button
                  key={session.id}
                  variant="ghost"
                  className="w-full h-auto py-3 px-3 flex flex-col items-start gap-1 hover:bg-purple-50 transition-all"
                >
                  <div className="flex items-center gap-2 w-full">
                    <Clock className="h-4 w-4 text-muted-foreground flex-shrink-0" />
                    <span className="text-base font-medium truncate flex-1 text-left">{session.title}</span>
                  </div>
                  <div className="flex items-center justify-between w-full pl-6">
                    <span className="text-sm text-muted-foreground">{session.date}</span>
                  </div>
                </Button>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* 健康趋势 */}
        <Card className="bg-gradient-to-br from-blue-50 to-cyan-50 border-blue-200">
          <CardHeader className="pb-4">
            <div className="flex items-center gap-2">
              <TrendingUp className="h-6 w-6 text-blue-600" />
              <CardTitle className="text-xl">健康趋势</CardTitle>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-base text-muted-foreground">睡眠改善</span>
                <Badge variant="default" className="text-base px-3 py-1 bg-green-500">↑ 12%</Badge>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-base text-muted-foreground">运动频率</span>
                <Badge variant="default" className="text-base px-3 py-1 bg-blue-500">稳定</Badge>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-base text-muted-foreground">血压控制</span>
                <Badge variant="default" className="text-base px-3 py-1 bg-amber-500">待改善</Badge>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}