/**
 * 实时语音对话组件
 * 
 * 功能：
 * 1. 实时转写 - 说话时文字实时出现
 * 2. 自动语音检测 - 不用手动点击开始/结束
 * 3. 流式TTS播放 - AI回复边生成边播放
 * 4. 打断功能 - 随时打断AI说话
 */

import React, { useState, useRef, useEffect } from 'react';
import { 
  Bot, Send, Mic, MicOff, Volume2, VolumeX, StopCircle, 
  Wifi, WifiOff, AlertCircle, Loader2, Radio
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from "../ui/card";
import { Button } from "../ui/button";
import { Input } from "../ui/input";
import { ScrollArea } from "../ui/scroll-area";
import { Badge } from "../ui/badge";
import { useStreamingVoice } from '../../hooks/useStreamingVoice';

interface Message {
  id: string;
  type: 'user' | 'ai' | 'system';
  content: string;
  timestamp: Date;
}

export function RealtimeConsultation() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      type: 'ai',
      content: '您好，我是AI健康助手。点击下方"开始对话"按钮，然后直接说话即可，我会实时听取并回复您。',
      timestamp: new Date()
    }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [autoSpeak, setAutoSpeak] = useState(true);
  const scrollAreaRef = useRef<HTMLDivElement>(null);
  
  // 使用流式语音 Hook
  const {
    isConnected,
    connect,
    disconnect,
    isRecording,
    partialText,
    finalText,
    isSpeaking,
    startRecording,
    stopRecording,
    speak,
    stopSpeaking,
    onFinalText,
    error,
    clearError
  } = useStreamingVoice();

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
  }, [messages, partialText]);

  // 设置最终文本回调
  useEffect(() => {
    onFinalText((text) => {
      if (text.trim()) {
        handleSendMessage(text);
      }
    });
  }, [onFinalText]);

  // 发送消息
  const handleSendMessage = (content: string) => {
    if (!content.trim()) return;

    // 添加用户消息
    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: content,
      timestamp: new Date()
    };
    setMessages(prev => [...prev, userMessage]);
    setInputValue('');

    // 模拟AI回复
    setTimeout(() => {
      const aiResponse = generateAIResponse(content);
      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'ai',
        content: aiResponse,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, aiMessage]);
      
      // 自动语音播报
      if (autoSpeak && isConnected) {
        speak(aiResponse);
      }
    }, 800);
  };

  // 生成AI回复
  const generateAIResponse = (userInput: string): string => {
    const input = userInput.toLowerCase();
    
    if (input.includes('头晕') || input.includes('晕')) {
      return '头晕可能与睡眠不足或血压波动有关。建议您保证充足睡眠，避免突然起身。如果症状持续，请及时就医。';
    }
    
    if (input.includes('血压')) {
      return '根据您的数据，血压略高。建议减少盐分摄入，保持规律运动，每天早晚测量血压并记录。';
    }
    
    if (input.includes('睡眠') || input.includes('睡不着')) {
      return '改善睡眠建议：晚上10点前入睡，睡前避免看手机，可以听轻音乐或做深呼吸放松。';
    }
    
    if (input.includes('你好') || input.includes('在吗')) {
      return '我在的！有什么可以帮您的吗？您可以问我关于健康的任何问题。';
    }

    return `我听到您说：${userInput}。请问您具体想了解什么健康问题呢？比如血压、睡眠、饮食等方面。`;
  };

  // 切换录音模式
  const toggleRecording = async () => {
    if (isRecording) {
      stopRecording();
    } else {
      if (!isConnected) {
        connect();
        // 等待连接后开始录音
        await new Promise(resolve => setTimeout(resolve, 500));
      }
      await startRecording();
    }
  };

  return (
    <div className="h-[calc(100vh-8rem)] flex flex-col gap-4">
      {/* 状态栏 */}
      <Card className="flex-shrink-0">
        <div className="p-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            {/* 连接状态 */}
            <div className="flex items-center gap-2">
              {isConnected ? (
                <Badge variant="default" className="bg-green-500">
                  <Wifi className="w-3 h-3 mr-1" />
                  已连接
                </Badge>
              ) : (
                <Badge variant="secondary" className="bg-gray-400">
                  <WifiOff className="w-3 h-3 mr-1" />
                  未连接
                </Badge>
              )}
            </div>
            
            {/* 录音状态 */}
            {isRecording && (
              <Badge variant="destructive" className="animate-pulse">
                <Radio className="w-3 h-3 mr-1" />
                正在录音...
              </Badge>
            )}
            
            {/* TTS状态 */}
            {isSpeaking && (
              <Badge variant="default" className="bg-blue-500">
                <Volume2 className="w-3 h-3 mr-1" />
                正在播放
              </Badge>
            )}
          </div>
          
          {/* 控制按钮 */}
          <div className="flex items-center gap-2">
            {/* 自动播报开关 */}
            <Button
              variant="ghost"
              size="sm"
              className={autoSpeak ? 'text-blue-600' : 'text-gray-400'}
              onClick={() => setAutoSpeak(!autoSpeak)}
            >
              {autoSpeak ? <Volume2 className="w-4 h-4" /> : <VolumeX className="w-4 h-4" />}
              <span className="ml-1 text-sm">自动播报</span>
            </Button>
            
            {/* 打断按钮 */}
            {isSpeaking && (
              <Button
                variant="outline"
                size="sm"
                className="text-red-600 border-red-300"
                onClick={stopSpeaking}
              >
                <StopCircle className="w-4 h-4 mr-1" />
                打断
              </Button>
            )}
          </div>
        </div>
      </Card>

      {/* 对话区域 */}
      <Card className="flex-1 flex flex-col min-h-0">
        <CardHeader className="pb-3 border-b">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-100 to-cyan-100 flex items-center justify-center">
              <Bot className="h-6 w-6 text-blue-600" />
            </div>
            <div>
              <CardTitle className="text-lg">AI健康助手 - 实时对话</CardTitle>
              <p className="text-sm text-muted-foreground">支持实时语音识别和自动播报</p>
            </div>
          </div>
        </CardHeader>
        
        <ScrollArea className="flex-1 p-4" ref={scrollAreaRef}>
          <div className="space-y-4">
            {messages.map((message) => (
              <div 
                key={message.id} 
                className={`flex gap-3 ${message.type === 'user' ? 'flex-row-reverse' : ''}`}
              >
                <div className={`w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0 ${
                  message.type === 'ai' 
                    ? 'bg-gradient-to-br from-blue-100 to-cyan-100' 
                    : 'bg-gradient-to-br from-slate-200 to-slate-300'
                }`}>
                  {message.type === 'ai' ? (
                    <Bot className="h-5 w-5 text-blue-600" />
                  ) : (
                    <span className="text-sm font-semibold text-slate-700">我</span>
                  )}
                </div>
                
                <div className={`max-w-[75%] ${message.type === 'user' ? 'items-end' : 'items-start'} flex flex-col gap-1`}>
                  <div className={`px-4 py-3 rounded-2xl text-base leading-relaxed ${
                    message.type === 'ai'
                      ? 'bg-slate-100 text-slate-900 rounded-tl-none'
                      : 'bg-blue-500 text-white rounded-tr-none'
                  }`}>
                    {message.content}
                  </div>
                  <span className="text-xs text-muted-foreground px-1">
                    {message.timestamp.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })}
                  </span>
                </div>
              </div>
            ))}
            
            {/* 实时转写显示 */}
            {partialText && (
              <div className="flex gap-3 flex-row-reverse">
                <div className="w-10 h-10 rounded-full bg-gradient-to-br from-slate-200 to-slate-300 flex items-center justify-center flex-shrink-0">
                  <span className="text-sm font-semibold text-slate-700">我</span>
                </div>
                <div className="max-w-[75%] px-4 py-3 rounded-2xl rounded-tr-none bg-blue-200 text-blue-900 border-2 border-dashed border-blue-400">
                  <span className="animate-pulse">🎤 </span>
                  {partialText}
                  <span className="animate-pulse">|</span>
                </div>
              </div>
            )}
          </div>
        </ScrollArea>

        {/* 输入区 */}
        <div className="p-4 border-t bg-slate-50">
          {/* 错误提示 */}
          {error && (
            <div className="mb-3 p-3 rounded-lg bg-orange-50 border border-orange-200 flex items-center gap-2 text-orange-700">
              <AlertCircle className="w-4 h-4" />
              <span className="text-sm">{error}</span>
            </div>
          )}
          
          <div className="flex gap-3">
            {/* 语音按钮 */}
            <Button
              variant={isRecording ? "destructive" : "default"}
              size="lg"
              className={`flex-shrink-0 h-14 px-6 ${isRecording ? 'animate-pulse' : ''}`}
              onClick={toggleRecording}
            >
              {isRecording ? (
                <>
                  <MicOff className="h-5 w-5 mr-2" />
                  停止录音
                </>
              ) : (
                <>
                  <Mic className="h-5 w-5 mr-2" />
                  开始录音
                </>
              )}
            </Button>
            
            {/* 文字输入 */}
            <Input
              placeholder="或者在这里输入文字..."
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSendMessage(inputValue);
                }
              }}
              className="flex-1 h-14 text-base px-4"
            />
            
            <Button
              size="lg"
              className="flex-shrink-0 h-14 px-6"
              onClick={() => handleSendMessage(inputValue)}
              disabled={!inputValue.trim()}
            >
              <Send className="h-5 w-5 mr-2" />
              发送
            </Button>
          </div>
          
          {/* 使用提示 */}
          <p className="mt-3 text-center text-sm text-muted-foreground">
            💡 点击"开始录音"后说话，系统会实时识别。停止录音后AI会自动回复。
          </p>
        </div>
      </Card>
    </div>
  );
}
