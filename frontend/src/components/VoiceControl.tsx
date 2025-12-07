/**
 * 语音控制组件
 * 支持唤醒词检测、语音命令、情感分析
 */
import React, { useState, useRef, useCallback, useEffect } from 'react';
import { Mic, MicOff, Volume2, Loader2, AlertCircle } from 'lucide-react';

// 支持的唤醒词
const WAKE_WORDS = ['糖豆糖豆', '糖豆', '你好糖豆'];

interface VoiceControlProps {
  onCommand?: (command: VoiceCommandResult) => void;
  onNavigate?: (route: string) => void;
  onEmergency?: () => void;
  className?: string;
}

interface VoiceCommandResult {
  text: string;
  response: string;
  audioUrl?: string;
  isControl: boolean;
  controlEvent?: string;
  controlData?: Record<string, any>;
  emotion?: string;
  agent?: string;
}

export const VoiceControl: React.FC<VoiceControlProps> = ({
  onCommand,
  onNavigate,
  onEmergency,
  className = '',
}) => {
  const [isListening, setIsListening] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [isAwake, setIsAwake] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [response, setResponse] = useState('');
  const [error, setError] = useState('');
  
  const recognitionRef = useRef<any>(null);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const awakeTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  // 初始化语音识别（使用浏览器Web Speech API）
  useEffect(() => {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = (window as any).webkitSpeechRecognition || (window as any).SpeechRecognition;
      recognitionRef.current = new SpeechRecognition();
      recognitionRef.current.continuous = true;
      recognitionRef.current.interimResults = true;
      recognitionRef.current.lang = 'zh-CN';

      recognitionRef.current.onresult = (event: any) => {
        let finalTranscript = '';
        for (let i = event.resultIndex; i < event.results.length; i++) {
          const transcript = event.results[i][0].transcript;
          if (event.results[i].isFinal) {
            finalTranscript += transcript;
          }
        }
        if (finalTranscript) {
          handleVoiceInput(finalTranscript);
        }
      };

      recognitionRef.current.onerror = (event: any) => {
        console.error('语音识别错误:', event.error);
        if (event.error !== 'no-speech') {
          setError('语音识别出错，请重试');
        }
      };

      recognitionRef.current.onend = () => {
        if (isListening) {
          // 自动重启
          try {
            recognitionRef.current?.start();
          } catch (e) {
            console.log('重启语音识别');
          }
        }
      };
    } else {
      setError('您的浏览器不支持语音识别');
    }

    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
      if (awakeTimeoutRef.current) {
        clearTimeout(awakeTimeoutRef.current);
      }
    };
  }, [isListening]);

  // 处理语音输入
  const handleVoiceInput = async (text: string) => {
    setTranscript(text);
    setError('');

    // 检测唤醒词
    const isWakeWord = WAKE_WORDS.some(w => text.includes(w));
    
    if (isWakeWord) {
      setIsAwake(true);
      // 移除唤醒词
      let cleanText = text;
      WAKE_WORDS.forEach(w => {
        cleanText = cleanText.replace(w, '').trim();
      });
      // 去除开头的标点
      cleanText = cleanText.replace(/^[,，。！？、]+/, '').trim();

      // 重置唤醒超时
      if (awakeTimeoutRef.current) {
        clearTimeout(awakeTimeoutRef.current);
      }
      awakeTimeoutRef.current = setTimeout(() => {
        setIsAwake(false);
      }, 30000); // 30秒后自动休眠

      if (!cleanText) {
        // 只有唤醒词，播放问候
        setResponse('我在呢，有什么可以帮您的吗？');
        speak('我在呢，有什么可以帮您的吗？');
        return;
      }

      // 处理实际命令
      await processCommand(cleanText);
    } else if (isAwake) {
      // 已唤醒状态，直接处理命令
      await processCommand(text);
      
      // 重置唤醒超时
      if (awakeTimeoutRef.current) {
        clearTimeout(awakeTimeoutRef.current);
      }
      awakeTimeoutRef.current = setTimeout(() => {
        setIsAwake(false);
      }, 30000);
    }
  };

  // 处理命令
  const processCommand = async (text: string) => {
    setIsProcessing(true);
    try {
      // 调用后端API进行意图识别和处理
      const formData = new FormData();
      // 由于使用浏览器语音识别，直接发送文本
      const response = await fetch('/api/v1/voice-agent/text-command', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          text, 
          user_role: 'elderly',
          voice_style: 'default'
        }),
      });

      if (!response.ok) {
        throw new Error('请求失败');
      }

      const result = await response.json();
      
      setResponse(result.response || '');
      
      // 播放语音回复
      if (result.audio_url) {
        playAudio(result.audio_url);
      } else if (result.response) {
        speak(result.response);
      }

      // 处理控制命令
      if (result.is_control) {
        handleControlEvent(result.control_event, result.control_data);
      }

      // 回调
      onCommand?.(result);

    } catch (err) {
      console.error('处理命令失败:', err);
      // 本地处理简单命令
      handleLocalCommand(text);
    } finally {
      setIsProcessing(false);
    }
  };

  // 本地命令处理（API失败时的fallback）
  const handleLocalCommand = (text: string) => {
    const lowerText = text.toLowerCase();
    
    // 紧急呼救
    if (['救命', '帮帮我', '呼救', '一键呼救'].some(w => lowerText.includes(w))) {
      setResponse('🚨 紧急呼救已触发！正在通知您的紧急联系人！');
      speak('紧急呼救已触发！正在通知您的紧急联系人！');
      onEmergency?.();
      return;
    }

    // 导航命令
    const navCommands: Record<string, string> = {
      '首页': '/home',
      '主页': '/home',
      '报告': '/report',
      '健康报告': '/report',
      '设置': '/settings',
      '返回': 'back',
    };

    for (const [keyword, route] of Object.entries(navCommands)) {
      if (lowerText.includes(keyword)) {
        setResponse(`好的，正在为您打开${keyword}`);
        speak(`好的，正在为您打开${keyword}`);
        onNavigate?.(route);
        return;
      }
    }

    // 无法识别
    setResponse('抱歉，我没有听清楚，请再说一遍');
    speak('抱歉，我没有听清楚，请再说一遍');
  };

  // 处理控制事件
  const handleControlEvent = (event: string, data: Record<string, any>) => {
    switch (event) {
      case 'navigate':
        onNavigate?.(data.route);
        break;
      case 'emergency_call':
        onEmergency?.();
        break;
      case 'query_data':
        // 可以触发数据查询
        console.log('查询数据:', data.type);
        break;
      case 'volume_control':
        // 音量控制
        console.log('音量控制:', data.action);
        break;
    }
  };

  // 播放音频
  const playAudio = (url: string) => {
    if (audioRef.current) {
      audioRef.current.src = url;
      audioRef.current.play().catch(console.error);
    }
  };

  // 使用浏览器TTS朗读
  const speak = (text: string) => {
    if ('speechSynthesis' in window) {
      // 停止当前播放
      window.speechSynthesis.cancel();
      
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.lang = 'zh-CN';
      utterance.rate = 0.9; // 稍慢语速
      utterance.pitch = 1;
      utterance.volume = 1;
      
      window.speechSynthesis.speak(utterance);
    }
  };

  // 开始/停止监听
  const toggleListening = useCallback(() => {
    if (isListening) {
      recognitionRef.current?.stop();
      setIsListening(false);
      setIsAwake(false);
    } else {
      try {
        recognitionRef.current?.start();
        setIsListening(true);
        setError('');
      } catch (e) {
        console.error('启动语音识别失败:', e);
      }
    }
  }, [isListening]);

  return (
    <div className={`voice-control ${className}`}>
      {/* 隐藏的音频播放器 */}
      <audio ref={audioRef} className="hidden" />
      
      {/* 语音控制按钮 */}
      <div className="flex flex-col items-center gap-3">
        <button
          onClick={toggleListening}
          disabled={isProcessing}
          className={`
            relative w-20 h-20 rounded-full flex items-center justify-center
            transition-all duration-300 shadow-lg
            ${isListening 
              ? isAwake 
                ? 'bg-green-500 hover:bg-green-600 animate-pulse' 
                : 'bg-blue-500 hover:bg-blue-600'
              : 'bg-gray-400 hover:bg-gray-500'
            }
            ${isProcessing ? 'opacity-70 cursor-wait' : 'cursor-pointer'}
          `}
        >
          {isProcessing ? (
            <Loader2 className="w-10 h-10 text-white animate-spin" />
          ) : isListening ? (
            <Mic className="w-10 h-10 text-white" />
          ) : (
            <MicOff className="w-10 h-10 text-white" />
          )}
          
          {/* 唤醒状态指示器 */}
          {isAwake && (
            <span className="absolute -top-1 -right-1 w-4 h-4 bg-yellow-400 rounded-full animate-ping" />
          )}
        </button>

        {/* 状态文字 */}
        <div className="text-center">
          <p className="text-sm font-medium text-gray-700">
            {isProcessing ? '处理中...' : 
             isAwake ? '🟢 已唤醒，请说话' : 
             isListening ? '🎤 说"糖豆糖豆"唤醒我' : 
             '点击开始语音'}
          </p>
          {transcript && (
            <p className="text-xs text-gray-500 mt-1 max-w-48 truncate">
              您说: {transcript}
            </p>
          )}
        </div>

        {/* 回复显示 */}
        {response && (
          <div className="mt-2 p-3 bg-blue-50 rounded-lg max-w-64">
            <div className="flex items-start gap-2">
              <Volume2 className="w-4 h-4 text-blue-500 mt-0.5 flex-shrink-0" />
              <p className="text-sm text-gray-700">{response}</p>
            </div>
          </div>
        )}

        {/* 错误提示 */}
        {error && (
          <div className="mt-2 p-2 bg-red-50 rounded-lg flex items-center gap-2">
            <AlertCircle className="w-4 h-4 text-red-500" />
            <p className="text-xs text-red-600">{error}</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default VoiceControl;
