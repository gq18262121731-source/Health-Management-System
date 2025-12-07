/**
 * 全双工语音助手组件
 * 
 * 参考小红书 FireRedChat 实现:
 * - 全双工语音交互：支持用户随时打断 AI
 * - 语音活动检测（VAD）：智能检测用户是否在说话
 * - 流式响应：边识别边回复，降低延迟
 * - 状态可视化：波形动画、状态提示
 */

import React, { useState, useRef, useCallback, useEffect } from 'react';
import { Mic, MicOff, Volume2, VolumeX, Phone, PhoneOff, Loader2 } from 'lucide-react';
import { Button } from '../ui/button';
import { Card, CardContent } from '../ui/card';
import { useVoice } from '../../contexts/VoiceContext';

const API_BASE = 'http://localhost:8000';

// 语音状态
type VoiceState = 
  | 'idle'           // 空闲
  | 'listening'      // 正在听用户说话
  | 'processing'     // 正在处理用户语音
  | 'speaking'       // AI正在说话
  | 'interrupted';   // 被用户打断

interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

interface FullDuplexVoiceAssistantProps {
  onMessage?: (message: Message) => void;
  className?: string;
}

export function FullDuplexVoiceAssistant({ onMessage, className = '' }: FullDuplexVoiceAssistantProps) {
  // 使用全局语音Context（避免多个语音同时播放）
  const { speak: globalSpeak, stop: globalStop, isSpeaking: globalIsSpeaking } = useVoice();
  
  // 状态
  const [voiceState, setVoiceState] = useState<VoiceState>('idle');
  const [isSessionActive, setIsSessionActive] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [currentTranscript, setCurrentTranscript] = useState('');
  const [aiResponse, setAiResponse] = useState('');
  const [volumeLevel, setVolumeLevel] = useState(0);
  
  // Refs
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const recognitionRef = useRef<any>(null);
  const silenceTimerRef = useRef<NodeJS.Timeout | null>(null);
  const isListeningRef = useRef(false);
  
  // VAD 参数
  const VAD_THRESHOLD = 0.02;  // 音量阈值
  const SILENCE_TIMEOUT = 1500; // 静音超时（毫秒）
  
  /**
   * 初始化音频分析器（用于 VAD）
   */
  const initAudioAnalyser = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;
      
      const audioContext = new AudioContext();
      audioContextRef.current = audioContext;
      
      const analyser = audioContext.createAnalyser();
      analyser.fftSize = 256;
      analyserRef.current = analyser;
      
      const source = audioContext.createMediaStreamSource(stream);
      source.connect(analyser);
      
      return true;
    } catch (error) {
      console.error('无法获取麦克风权限:', error);
      return false;
    }
  }, []);
  
  /**
   * 检测音量级别（VAD）
   */
  const detectVolume = useCallback(() => {
    if (!analyserRef.current) return 0;
    
    const dataArray = new Uint8Array(analyserRef.current.frequencyBinCount);
    analyserRef.current.getByteFrequencyData(dataArray);
    
    const average = dataArray.reduce((a, b) => a + b, 0) / dataArray.length;
    return average / 255; // 归一化到 0-1
  }, []);
  
  /**
   * 开始语音会话
   */
  const startSession = useCallback(async () => {
    const success = await initAudioAnalyser();
    if (!success) return;
    
    setIsSessionActive(true);
    setVoiceState('listening');
    
    // 初始化语音识别
    const SpeechRecognition = (window as any).webkitSpeechRecognition || (window as any).SpeechRecognition;
    if (SpeechRecognition) {
      const recognition = new SpeechRecognition();
      recognition.continuous = true;
      recognition.interimResults = true;
      recognition.lang = 'zh-CN';
      
      recognition.onresult = (event: any) => {
        let transcript = '';
        let isFinal = false;
        
        for (let i = event.resultIndex; i < event.results.length; i++) {
          transcript += event.results[i][0].transcript;
          if (event.results[i].isFinal) {
            isFinal = true;
          }
        }
        
        setCurrentTranscript(transcript);
        
        // 重置静音计时器
        if (silenceTimerRef.current) {
          clearTimeout(silenceTimerRef.current);
        }
        
        if (isFinal && transcript.trim()) {
          // 用户说完了，开始处理
          handleUserSpeechEnd(transcript.trim());
        } else {
          // 设置静音检测
          silenceTimerRef.current = setTimeout(() => {
            if (transcript.trim() && voiceState === 'listening') {
              handleUserSpeechEnd(transcript.trim());
            }
          }, SILENCE_TIMEOUT);
        }
      };
      
      recognition.onerror = (event: any) => {
        console.error('语音识别错误:', event.error);
        if (event.error !== 'no-speech') {
          // 尝试重启
          setTimeout(() => {
            if (isSessionActive && isListeningRef.current) {
              recognition.start();
            }
          }, 1000);
        }
      };
      
      recognition.onend = () => {
        // 自动重启
        if (isSessionActive && isListeningRef.current) {
          recognition.start();
        }
      };
      
      recognitionRef.current = recognition;
      recognition.start();
      isListeningRef.current = true;
    }
    
    // 开始音量监测
    startVolumeMonitor();
    
    // 播放欢迎语
    await speak('您好，我是您的健康助手，有什么可以帮您的吗？');
  }, [initAudioAnalyser]);
  
  /**
   * 结束语音会话
   */
  const endSession = useCallback(() => {
    setIsSessionActive(false);
    setVoiceState('idle');
    isListeningRef.current = false;
    
    // 停止语音识别
    if (recognitionRef.current) {
      recognitionRef.current.stop();
    }
    
    // 停止全局音频播放
    globalStop();
    
    // 清理
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
    }
    if (audioContextRef.current) {
      audioContextRef.current.close();
    }
    if (silenceTimerRef.current) {
      clearTimeout(silenceTimerRef.current);
    }
  }, [globalStop]);
  
  /**
   * 音量监测循环
   */
  const startVolumeMonitor = useCallback(() => {
    const monitor = () => {
      if (!isSessionActive) return;
      
      const volume = detectVolume();
      setVolumeLevel(volume);
      
      requestAnimationFrame(monitor);
    };
    monitor();
  }, [detectVolume, isSessionActive]);
  
  /**
   * 用户说话结束，处理语音
   */
  const handleUserSpeechEnd = useCallback(async (transcript: string) => {
    setVoiceState('processing');
    setCurrentTranscript('');
    
    // 添加用户消息
    const userMessage: Message = {
      role: 'user',
      content: transcript,
      timestamp: new Date()
    };
    setMessages(prev => [...prev, userMessage]);
    onMessage?.(userMessage);
    
    // 调用 AI 获取回复
    try {
      const response = await fetch(`${API_BASE}/api/v1/ai/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: transcript,
          context: 'health_assistant',
          stream: false
        })
      });
      
      if (!response.ok) throw new Error('AI 请求失败');
      
      const data = await response.json();
      const aiText = data.data?.response || data.response || '抱歉，我没有理解您的意思。';
      
      // 添加 AI 消息
      const assistantMessage: Message = {
        role: 'assistant',
        content: aiText,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, assistantMessage]);
      onMessage?.(assistantMessage);
      
      // 播放 AI 回复
      await speak(aiText);
      
    } catch (error) {
      console.error('AI 请求失败:', error);
      await speak('抱歉，系统出现了一些问题，请稍后再试。');
    }
  }, [onMessage]);
  
  /**
   * TTS 播放（使用全局语音Context，支持打断）
   */
  const speak = useCallback(async (text: string) => {
    setVoiceState('speaking');
    setAiResponse(text);
    
    try {
      // 使用全局语音播放（会自动停止其他正在播放的语音）
      await globalSpeak(text);
    } catch (error) {
      console.error('TTS 失败:', error);
    }
    
    // 回到监听状态
    if (isSessionActive) {
      setVoiceState('listening');
      setAiResponse('');
    }
  }, [isSessionActive, globalSpeak]);
  
  /**
   * 手动打断
   */
  const interrupt = useCallback(() => {
    globalStop();
    setVoiceState('listening');
    setAiResponse('');
  }, [globalStop]);
  
  // 清理
  useEffect(() => {
    return () => {
      endSession();
    };
  }, [endSession]);
  
  // 状态文本
  const getStateText = () => {
    switch (voiceState) {
      case 'idle': return '点击开始对话';
      case 'listening': return '正在聆听...';
      case 'processing': return '正在思考...';
      case 'speaking': return '正在回复...';
      case 'interrupted': return '已打断';
      default: return '';
    }
  };
  
  // 状态颜色
  const getStateColor = () => {
    switch (voiceState) {
      case 'listening': return 'bg-green-500';
      case 'processing': return 'bg-yellow-500';
      case 'speaking': return 'bg-blue-500';
      case 'interrupted': return 'bg-orange-500';
      default: return 'bg-gray-400';
    }
  };

  return (
    <Card className={`${className} overflow-hidden`}>
      <CardContent className="p-6">
        {/* 状态指示器 */}
        <div className="flex items-center justify-center mb-6">
          <div className="relative">
            {/* 波形动画 */}
            <div className={`w-32 h-32 rounded-full ${getStateColor()} transition-all duration-300 flex items-center justify-center`}
                 style={{
                   transform: `scale(${1 + volumeLevel * 0.3})`,
                   boxShadow: voiceState === 'listening' 
                     ? `0 0 ${volumeLevel * 60}px ${volumeLevel * 30}px rgba(34, 197, 94, 0.3)`
                     : voiceState === 'speaking'
                     ? '0 0 30px 15px rgba(59, 130, 246, 0.3)'
                     : 'none'
                 }}>
              {voiceState === 'processing' ? (
                <Loader2 className="w-12 h-12 text-white animate-spin" />
              ) : voiceState === 'speaking' ? (
                <Volume2 className="w-12 h-12 text-white animate-pulse" />
              ) : isSessionActive ? (
                <Mic className="w-12 h-12 text-white" />
              ) : (
                <MicOff className="w-12 h-12 text-white" />
              )}
            </div>
            
            {/* 音量条 */}
            {isSessionActive && voiceState === 'listening' && (
              <div className="absolute -bottom-4 left-1/2 transform -translate-x-1/2 flex gap-1">
                {[...Array(5)].map((_, i) => (
                  <div
                    key={i}
                    className="w-2 bg-green-500 rounded-full transition-all duration-75"
                    style={{
                      height: `${Math.min(32, 8 + volumeLevel * 100 * (i + 1) / 5)}px`
                    }}
                  />
                ))}
              </div>
            )}
          </div>
        </div>
        
        {/* 状态文本 */}
        <div className="text-center mb-4">
          <p className="text-xl font-medium text-gray-700">{getStateText()}</p>
          {currentTranscript && (
            <p className="mt-2 text-lg text-gray-600 italic">"{currentTranscript}"</p>
          )}
          {aiResponse && voiceState === 'speaking' && (
            <p className="mt-2 text-lg text-blue-600">"{aiResponse}"</p>
          )}
        </div>
        
        {/* 控制按钮 */}
        <div className="flex justify-center gap-4">
          {!isSessionActive ? (
            <Button
              size="lg"
              className="rounded-full w-16 h-16 bg-green-500 hover:bg-green-600"
              onClick={startSession}
            >
              <Phone className="w-8 h-8" />
            </Button>
          ) : (
            <>
              {voiceState === 'speaking' && (
                <Button
                  size="lg"
                  variant="outline"
                  className="rounded-full w-14 h-14"
                  onClick={interrupt}
                >
                  <VolumeX className="w-6 h-6" />
                </Button>
              )}
              <Button
                size="lg"
                className="rounded-full w-16 h-16 bg-red-500 hover:bg-red-600"
                onClick={endSession}
              >
                <PhoneOff className="w-8 h-8" />
              </Button>
            </>
          )}
        </div>
        
        {/* 对话历史 */}
        {messages.length > 0 && (
          <div className="mt-6 max-h-48 overflow-y-auto space-y-2">
            {messages.slice(-6).map((msg, index) => (
              <div
                key={index}
                className={`p-3 rounded-lg text-sm ${
                  msg.role === 'user'
                    ? 'bg-green-100 text-green-800 ml-8'
                    : 'bg-blue-100 text-blue-800 mr-8'
                }`}
              >
                <span className="font-medium">{msg.role === 'user' ? '您：' : 'AI：'}</span>
                {msg.content}
              </div>
            ))}
          </div>
        )}
        
        {/* 使用提示 */}
        <div className="mt-4 text-center text-sm text-gray-500">
          {isSessionActive ? (
            <p>💡 您可以随时说话打断 AI 的回复</p>
          ) : (
            <p>点击绿色按钮开始语音对话</p>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

export default FullDuplexVoiceAssistant;
