import React, { useState, useRef, useEffect, forwardRef, useImperativeHandle } from 'react';
import { Bot, Send, Mic, MicOff, Volume2, VolumeX, StopCircle, AlertCircle, History, BookOpen, TrendingUp, Lightbulb, Clock, Star, Loader2, Radio, Cpu, Sparkles } from 'lucide-react';
import { sendToSpark, ChatMessage } from '../../services/sparkApi';
import { consultMultiAgentStream } from '../../services/multiAgentApi';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../ui/card";
import { Button } from "../ui/button";
import { Input } from "../ui/input";
import { ScrollArea } from "../ui/scroll-area";
import { Badge } from "../ui/badge";
import { textToSpeech, playAudio } from '../../services/voiceApi';
import { useVoice } from '../../contexts/VoiceContext';

// ============================================================================
// 组件说明：AI健康咨询组件
// 
// 涉及API:
// - POST /api/v1/elderly/ai/chat - 发送消息给AI助手
// - POST /api/v1/elderly/ai/analyze - 触发AI分析（从健康卡片点击"AI分析"按钮）
// - GET /api/v1/elderly/ai/history - 获取对话历史
// 
// Request (chat):
// {
//   message: string,
//   context?: {
//     healthData?: object,  // 当前健康数据
//     recentReports?: array // 最近的健康报告
//   }
// }
// 
// Response:
// {
//   success: true,
//   data: {
//     messageId: "msg_001",
//     aiResponse: "根据您的血压数据...",
//     suggestions: ["减少盐分摄入", "保持心情平和"],
//     timestamp: "2024-11-26T14:30:00Z"
//   }
// }
// 
// 功能：
// 1. AI对话：用户输入问题，AI回答健康建议
// 2. 自动分析：从健康卡片触发，自动生成分析prompt
// 3. 语音输入：点击麦克风按钮进行语音输入
// 4. 语音播报：AI回复自动语音播报
// 5. 对话历史：显示历史对话记录
// 6. 快捷问题：常见健康问题快速提问
// 
// 适老化设计：
// - 超大字体
// - 语音输入/播报
// - 简洁的对话界面
// ============================================================================

interface Message {
  id: string;
  type: 'user' | 'ai';
  content: string;
  timestamp: Date;
}

interface AIConsultationProps {
  isFloating?: boolean;
  autoPrompt?: string | null;
}

export const AIConsultation = forwardRef<any, AIConsultationProps>(({ isFloating = false, autoPrompt = null }, ref) => {
  // 使用全局语音Context（避免多个语音同时播放）
  const { speak: globalSpeak, stop: globalStop, isSpeaking: globalIsSpeaking } = useVoice();
  
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      type: 'ai',
      content: '您好，我是您的AI健康助手。我注意到您最近的健康数据显示血压略高（118/75 mmHg），且深睡时间较短。请问您有什么不舒服的地方吗？',
      timestamp: new Date()
    }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isListening, setIsListening] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [autoVoiceMode, setAutoVoiceMode] = useState(true); // 自动语音交互模式（默认开启）
  const [autoSpeakEnabled, setAutoSpeakEnabled] = useState(true); // AI回复自动朗读
  const [voiceInitialized, setVoiceInitialized] = useState(false); // 语音是否已初始化
  const [useMultiAgent, setUseMultiAgent] = useState(true); // 使用后端多智能体系统（默认开启）
  const scrollAreaRef = useRef<HTMLDivElement>(null);
  const recognitionRef = useRef<any>(null);
  const cancelRequestRef = useRef<(() => void) | null>(null);
  const lastAiResponseRef = useRef<string>(''); // 记录最后一次AI回复，用于语音播报
  const autoPromptProcessedRef = useRef<string | null>(null); // 记录已处理的autoPrompt，避免重复发送
  const isSendingRef = useRef(false); // 防止重复发送

  // 健康状态摘要
  const healthSummary = "您目前的总体状态：中等风险，血压略高、睡眠不足。";

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

  // 停止所有语音播放（使用全局方法）
  const stopAllSpeech = () => {
    globalStop();
    window.speechSynthesis?.cancel(); // 同时停止浏览器内置TTS
    setIsSpeaking(false);
  };

  // 语音播报健康摘要（使用全局语音）
  const handleSpeakSummary = () => {
    if (isSpeaking || globalIsSpeaking) {
      stopAllSpeech();
    } else {
      // 先停止之前的语音
      stopAllSpeech();
      setIsSpeaking(true);
      globalSpeak(healthSummary).finally(() => setIsSpeaking(false));
    }
  };

  // 发送消息
  const handleSendMessage = (content: string) => {
    if (!content.trim() || isLoading || isSendingRef.current) return;
    
    // 防止重复发送
    isSendingRef.current = true;
    setTimeout(() => { isSendingRef.current = false; }, 500);

    // 取消之前的请求
    if (cancelRequestRef.current) {
      cancelRequestRef.current();
    }

    // 添加用户消息
    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: content,
      timestamp: new Date()
    };
    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    // 创建AI消息占位
    const aiMessageId = (Date.now() + 1).toString();
    const aiMessage: Message = {
      id: aiMessageId,
      type: 'ai',
      content: '',
      timestamp: new Date()
    };
    setMessages(prev => [...prev, aiMessage]);

    // 根据模式选择 API
    if (useMultiAgent) {
      // 使用后端多智能体系统
      console.log('🤖 使用后端多智能体系统');
      cancelRequestRef.current = consultMultiAgentStream(
        content,
        // onMessage - 流式更新
        (text) => {
          setMessages(prev => prev.map(m => 
            m.id === aiMessageId ? { ...m, content: text } : m
          ));
          lastAiResponseRef.current = text;
        },
        // onComplete
        async () => {
          setIsLoading(false);
          cancelRequestRef.current = null;
          
          // 自动语音播报AI回复
          if (autoSpeakEnabled && lastAiResponseRef.current) {
            await speakText(lastAiResponseRef.current);
          }
          
          // 自动语音模式下，播报完成后继续监听
          if (autoVoiceMode) {
            setTimeout(() => startVoiceRecognition(), 500);
          }
        },
        // onError
        (error) => {
          // 多智能体失败时，回退到讯飞星火
          console.log('⚠️ 多智能体失败，回退到讯飞星火:', error);
          fallbackToSpark(content, aiMessageId);
        }
      );
    } else {
      // 使用讯飞星火 API
      console.log('✨ 使用讯飞星火 API');
      callSparkApi(content, aiMessageId);
    }
  };

  // 调用讯飞星火 API
  const callSparkApi = (content: string, aiMessageId: string) => {
    // 构建对话历史
    const chatHistory: ChatMessage[] = messages
      .filter(m => m.content.trim())
      .map(m => ({
        role: m.type === 'user' ? 'user' : 'assistant',
        content: m.content
      })) as ChatMessage[];
    
    chatHistory.push({ role: 'user', content: content });

    cancelRequestRef.current = sendToSpark(
      chatHistory,
      // onMessage - 流式更新
      (text) => {
        setMessages(prev => prev.map(m => 
          m.id === aiMessageId ? { ...m, content: text } : m
        ));
        lastAiResponseRef.current = text;
      },
      // onComplete
      async () => {
        setIsLoading(false);
        cancelRequestRef.current = null;
        
        // 自动语音播报AI回复
        if (autoSpeakEnabled && lastAiResponseRef.current) {
          await speakText(lastAiResponseRef.current);
        }
        
        // 自动语音模式下，播报完成后继续监听
        if (autoVoiceMode) {
          setTimeout(() => startVoiceRecognition(), 500);
        }
      },
      // onError
      (error) => {
        setMessages(prev => prev.map(m => 
          m.id === aiMessageId 
            ? { ...m, content: `抱歉，出现了一些问题：${error}\n\n请稍后再试，或者您可以换个方式描述您的问题。` } 
            : m
        ));
        setIsLoading(false);
        cancelRequestRef.current = null;
        
        // 自动语音模式下继续监听
        if (autoVoiceMode) {
          setTimeout(() => startVoiceRecognition(), 1000);
        }
      }
    );
  };

  // 回退到讯飞星火（多智能体失败时）
  const fallbackToSpark = (content: string, aiMessageId: string) => {
    setMessages(prev => prev.map(m => 
      m.id === aiMessageId ? { ...m, content: '正在切换到备用服务...' } : m
    ));
    callSparkApi(content, aiMessageId);
  };

  // 使用全局语音Context播报文本（避免多个语音同时播放）
  const speakText = async (text: string): Promise<void> => {
    // 先停止所有正在播放的语音
    stopAllSpeech();
    
    // 等待一下确保语音完全停止
    await new Promise(r => setTimeout(r, 100));
    
    setIsSpeaking(true);
    
    try {
      // 使用全局语音播放
      await globalSpeak(text);
    } catch (error) {
      console.error('语音播放失败:', error);
    } finally {
      setIsSpeaking(false);
    }
  };
  
  // 开始语音识别
  const startVoiceRecognition = () => {
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
      console.log('浏览器不支持语音识别');
      return;
    }
    
    // 防止重复启动，且确保语音播放已停止
    if (isListening || isSpeaking || isLoading) return;
    
    // 确保停止任何正在播放的语音
    stopAllSpeech();
    
    // 先停止之前的识别
    if (recognitionRef.current) {
      try {
        recognitionRef.current.stop();
      } catch (e) {
        // 忽略停止错误
      }
    }
    
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    const recognition = new SpeechRecognition();
    
    recognition.lang = 'zh-CN';
    recognition.continuous = true;  // 持续监听，不会因为短暂停顿而停止
    recognition.interimResults = true;  // 显示中间结果，让用户知道在识别
    recognition.maxAlternatives = 1;

    let finalTranscript = '';  // 最终识别结果
    let silenceTimer: NodeJS.Timeout | null = null;  // 静音计时器
    const SILENCE_TIMEOUT = 2000;  // 2秒无声音则停止

    // 重置静音计时器
    const resetSilenceTimer = () => {
      if (silenceTimer) {
        clearTimeout(silenceTimer);
      }
      silenceTimer = setTimeout(() => {
        // 超时停止识别
        recognition.stop();
      }, SILENCE_TIMEOUT);
    };

    recognition.onstart = () => {
      setIsListening(true);
      finalTranscript = '';
      resetSilenceTimer();
    };

    recognition.onresult = (event: any) => {
      // 重置静音计时器，因为检测到了声音
      resetSilenceTimer();
      
      let interimTranscript = '';
      
      for (let i = event.resultIndex; i < event.results.length; i++) {
        const transcript = event.results[i][0].transcript;
        if (event.results[i].isFinal) {
          finalTranscript += transcript;
        } else {
          interimTranscript += transcript;
        }
      }
      
      // 实时显示识别内容（包括中间结果）
      const displayText = finalTranscript + interimTranscript;
      if (displayText) {
        setInputValue(displayText);
      }
    };

    recognition.onerror = (event: any) => {
      if (silenceTimer) clearTimeout(silenceTimer);
      
      // no-speech 错误表示没有检测到声音，可以忽略并重试
      if (event.error === 'no-speech') {
        setIsListening(false);
        if (autoVoiceMode) {
          setTimeout(() => startVoiceRecognition(), 500);
        }
        return;
      }
      
      setIsListening(false);
      if (autoVoiceMode) {
        setTimeout(() => startVoiceRecognition(), 1000);
      }
    };

    recognition.onend = () => {
      if (silenceTimer) clearTimeout(silenceTimer);
      setIsListening(false);
      
      // 如果有识别结果，发送消息
      if (finalTranscript.trim()) {
        if (autoVoiceMode) {
          handleSendMessage(finalTranscript);
        }
        // 手动模式下保留在输入框中
      } else if (autoVoiceMode) {
        // 没有识别到内容，继续监听
        setTimeout(() => startVoiceRecognition(), 500);
      }
    };

    recognitionRef.current = recognition;
    recognition.start();
  };
  
  // 切换自动语音交互模式
  const toggleAutoVoiceMode = () => {
    if (autoVoiceMode) {
      // 关闭自动模式
      setAutoVoiceMode(false);
      recognitionRef.current?.stop();
      stopAllSpeech();
      setIsListening(false);
    } else {
      // 开启自动模式
      setAutoVoiceMode(true);
      // 先停止所有语音，再播报提示并开始监听
      stopAllSpeech();
      setTimeout(() => {
        speakText('语音交互模式已开启，请说话').then(() => {
          startVoiceRecognition();
        });
      }, 200);
    }
  };

  // 快速问题处理
  const handleQuickQuestion = (question: string) => {
    handleSendMessage(question);
  };

  // 语音输入（手动模式）
  const handleVoiceInput = () => {
    if (isListening) {
      recognitionRef.current?.stop();
      setIsListening(false);
      return;
    }
    startVoiceRecognition();
  };

  // 自动提示处理 - 避免重复发送
  useEffect(() => {
    if (autoPrompt && autoPrompt !== autoPromptProcessedRef.current) {
      autoPromptProcessedRef.current = autoPrompt;
      // 延迟一下确保组件已完全加载
      setTimeout(() => {
        handleSendMessage(autoPrompt);
      }, 100);
    }
  }, [autoPrompt]);

  // 页面加载后自动开启语音交互
  useEffect(() => {
    if (voiceInitialized) return;
    
    // 延迟启动，等待组件完全加载
    const timer = setTimeout(() => {
      if (autoVoiceMode && !voiceInitialized) {
        setVoiceInitialized(true);
        
        // 先播报欢迎语，然后开始监听
        const welcomeText = '您好，我是您的AI健康助手，请问有什么可以帮您的？';
        speakText(welcomeText).then(() => {
          // 播报完成后开始监听
          setTimeout(() => startVoiceRecognition(), 500);
        });
      }
    }, 1500);
    
    return () => clearTimeout(timer);
  }, [autoVoiceMode, voiceInitialized]);

  // 暴露方法给父组件
  useImperativeHandle(ref, () => ({
    sendMessage: handleSendMessage
  }));

  return (
    <div className="h-full flex flex-col gap-4 p-4 overflow-y-auto">
      {/* 顶部健康状态条 */}
      <Card className="bg-gradient-to-r from-orange-50 to-amber-50 border-orange-200">
        <div className="p-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-orange-100 flex items-center justify-center flex-shrink-0">
              <AlertCircle className="h-5 w-5 text-orange-600" />
            </div>
            <div className="flex-1">
              <p className="text-lg font-medium text-orange-900 leading-relaxed">
                {healthSummary}
              </p>
            </div>
          </div>
          <Button 
            variant="outline" 
            size="lg"
            className={`ml-4 flex-shrink-0 min-w-[120px] ${isSpeaking ? 'bg-blue-50 border-blue-300 text-blue-600' : 'bg-white'}`}
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

      {/* 自动语音交互模式提示 */}
      {autoVoiceMode && (
        <Card className={`border-2 ${isListening ? 'border-green-400 bg-green-50' : isSpeaking ? 'border-blue-400 bg-blue-50' : 'border-purple-400 bg-purple-50'}`}>
          <div className="p-4 flex items-center justify-center gap-4">
            <div className={`w-4 h-4 rounded-full animate-pulse ${isListening ? 'bg-green-500' : isSpeaking ? 'bg-blue-500' : 'bg-purple-500'}`} />
            <span className="text-lg font-medium">
              {isListening ? '🎤 正在聆听您说话...' : isSpeaking ? '🔊 AI正在回复...' : isLoading ? '🤔 AI正在思考...' : '⏳ 等待中...'}
            </span>
            <Button 
              variant="outline" 
              size="sm"
              onClick={toggleAutoVoiceMode}
              className="ml-4"
            >
              <MicOff className="mr-2 h-4 w-4" />
              关闭语音模式
            </Button>
          </div>
        </Card>
      )}

      {/* 中部对话区 */}
      <Card className="flex-1 flex flex-col min-h-0">
        <div className="p-4 border-b bg-slate-50/50">
          <div className="flex items-center gap-2">
            <Bot className="h-5 w-5 text-blue-500" />
            <h3 className="font-semibold">AI健康助手</h3>
            {/* AI引擎指示器 */}
            <Badge 
              variant={useMultiAgent ? "default" : "secondary"}
              className={`ml-2 ${useMultiAgent ? 'bg-emerald-500' : 'bg-blue-500'}`}
            >
              {useMultiAgent ? '🤖 多智能体' : '✨ 讯飞星火'}
            </Badge>
            <div className="flex items-center gap-2 ml-auto">
              {/* AI引擎切换按钮 */}
              <Button
                variant={useMultiAgent ? "default" : "outline"}
                size="sm"
                onClick={() => setUseMultiAgent(!useMultiAgent)}
                className={useMultiAgent ? 'bg-emerald-500 hover:bg-emerald-600' : ''}
                title={useMultiAgent ? '当前：后端多智能体系统（健康管家+慢病专家+生活教练+心理关怀师）' : '当前：讯飞星火大模型'}
              >
                {useMultiAgent ? <Cpu className="mr-1 h-4 w-4" /> : <Sparkles className="mr-1 h-4 w-4" />}
                {useMultiAgent ? '多智能体' : '星火'}
              </Button>
              {/* 自动语音交互按钮 */}
              <Button
                variant={autoVoiceMode ? "default" : "outline"}
                size="sm"
                onClick={toggleAutoVoiceMode}
                className={autoVoiceMode ? 'bg-purple-500 hover:bg-purple-600' : ''}
              >
                <Radio className={`mr-1 h-4 w-4 ${autoVoiceMode ? 'animate-pulse' : ''}`} />
                {autoVoiceMode ? '语音对话中' : '开启语音对话'}
              </Button>
              {/* 自动朗读开关 */}
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setAutoSpeakEnabled(!autoSpeakEnabled)}
                title={autoSpeakEnabled ? '关闭自动朗读' : '开启自动朗读'}
              >
                {autoSpeakEnabled ? <Volume2 className="h-4 w-4 text-blue-500" /> : <VolumeX className="h-4 w-4 text-gray-400" />}
              </Button>
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
                {/* 头像 */}
                <div className={`w-12 h-12 rounded-full flex items-center justify-center flex-shrink-0 ${
                  message.type === 'ai' 
                    ? 'bg-gradient-to-br from-blue-100 to-cyan-100' 
                    : 'bg-gradient-to-br from-slate-200 to-slate-300'
                }`}>
                  {message.type === 'ai' ? (
                    <Bot className="h-6 w-6 text-blue-600" />
                  ) : (
                    <span className="text-base font-semibold text-slate-700">我</span>
                  )}
                </div>
                
                {/* 消息气泡 */}
                <div className={`max-w-[75%] ${message.type === 'user' ? 'items-end' : 'items-start'} flex flex-col gap-1`}>
                  <div className={`px-5 py-4 rounded-2xl text-base leading-loose whitespace-pre-line ${
                    message.type === 'ai'
                      ? 'bg-gradient-to-br from-slate-50 to-slate-100 text-slate-900 rounded-tl-none border border-slate-200'
                      : 'bg-gradient-to-br from-blue-500 to-blue-600 text-white rounded-tr-none shadow-md'
                  }`}>
                    {message.content}
                  </div>
                  <span className="text-xs text-muted-foreground px-2">
                    {message.timestamp.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </ScrollArea>

        {/* 快速问题按钮区 */}
        <div className="px-6 pt-4 pb-3 border-t bg-slate-50/50">
          <div className="grid grid-cols-3 gap-3">
            <Button 
              variant="outline" 
              size="lg"
              className="h-auto py-3 px-4 text-base hover:bg-blue-50 hover:border-blue-300 hover:text-blue-600 transition-all"
              onClick={() => handleQuickQuestion('为什么会这样？')}
            >
              <span className="font-medium">为什么会这样？</span>
            </Button>
            <Button 
              variant="outline" 
              size="lg"
              className="h-auto py-3 px-4 text-base hover:bg-green-50 hover:border-green-300 hover:text-green-600 transition-all"
              onClick={() => handleQuickQuestion('我可做什么？')}
            >
              <span className="font-medium">我可以做什么？</span>
            </Button>
            <Button 
              variant="outline" 
              size="lg"
              className="h-auto py-3 px-4 text-base hover:bg-orange-50 hover:border-orange-300 hover:text-orange-600 transition-all"
              onClick={() => handleQuickQuestion('需要去医院吗？')}
            >
              <span className="font-medium">需要去医院吗？</span>
            </Button>
          </div>
        </div>

        {/* 底部输入区 */}
        <div className="p-6 border-t bg-white">
          <div className="flex gap-3">
            <Button
              variant="outline"
              size="lg"
              className={`flex-shrink-0 h-14 w-14 ${isListening ? 'bg-red-50 border-red-300 text-red-600 animate-pulse' : ''}`}
              onClick={handleVoiceInput}
            >
              <Mic className="h-6 w-6" />
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
              className="flex-1 h-14 text-base px-5 border-slate-300 focus:border-blue-400 focus:ring-blue-400"
            />
            
            <Button
              size="lg"
              className="flex-shrink-0 h-14 px-8 bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 text-white shadow-md disabled:opacity-50"
              onClick={() => handleSendMessage(inputValue)}
              disabled={isLoading}
            >
              {isLoading ? (
                <>
                  <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                  <span className="text-base font-medium">思考中</span>
                </>
              ) : (
                <>
                  <Send className="mr-2 h-5 w-5" />
                  <span className="text-base font-medium">发送</span>
                </>
              )}
            </Button>
          </div>
          
          {isListening && (
            <div className="mt-3 text-center text-sm text-red-600 animate-pulse">
              正在聆听您的声音...
            </div>
          )}
        </div>
      </Card>
    </div>
  );
});

AIConsultation.displayName = 'AIConsultation';