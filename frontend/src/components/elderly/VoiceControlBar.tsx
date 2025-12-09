/**
 * 语音控制栏 - 重写版本
 * 
 * 修复问题：
 * 1. useEffect 依赖导致 SpeechRecognition 重复创建
 * 2. 回调函数引用过时状态
 * 3. 重复启动导致 aborted 错误
 */

import React, { useRef, useState, useEffect, useCallback } from 'react';
import { Volume2, Square, Mic, MicOff, Loader2 } from 'lucide-react';
import { Button } from '../ui/button';
import { useVoice } from '../../contexts/VoiceContext';

// 智能打断配置
const BARGE_IN_CONFIG = {
  minSpeechDuration: 300,
  immediateBargeInWords: ['停', '等等', '等一下', '停止', '别说了', '打断', '暂停', '好了'],
  noiseWords: ['嗯', '啊', '哦', '呃', '额'],
};

interface VoiceControlBarProps {
  className?: string;
  healthData?: any;
  userName?: string;
  onNavigate?: (route: string) => void;
  onEmergency?: () => void;
  onGenerateReport?: () => void;
  onSetReminder?: (data: { time?: string; type?: string }) => void;
  onQueryData?: (type: string) => string | null;  // 返回要播报的文本
}

export function VoiceControlBar({ 
  className = '', 
  healthData, 
  userName = '您', 
  onNavigate, 
  onEmergency,
  onGenerateReport,
  onSetReminder,
  onQueryData,
}: VoiceControlBarProps) {
  const { isSpeaking, speak, stop } = useVoice();
  
  // UI 状态
  const [isListening, setIsListening] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [interimText, setInterimText] = useState('');
  const [bargeInStatus, setBargeInStatus] = useState<'idle' | 'detecting' | 'confirmed'>('idle');
  
  // Refs - 用于在回调中访问最新状态
  const recognitionRef = useRef<any>(null);
  const isListeningRef = useRef(false);
  const isProcessingRef = useRef(false);
  const isSpeakingRef = useRef(false);
  const speechStartTimeRef = useRef<number | null>(null);
  const bargeInTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  
  // 同步 isSpeaking 到 ref
  useEffect(() => {
    isSpeakingRef.current = isSpeaking;
  }, [isSpeaking]);

  // 安全启动识别 - 使用 useCallback 保持引用稳定
  const safeStart = useCallback(() => {
    const recognition = recognitionRef.current;
    if (!recognition) {
      console.error('❌ 语音识别未初始化');
      return false;
    }
    
    // 检查是否已在运行 - 通过尝试启动来判断
    try {
      recognition.start();
      console.log('✅ 语音识别已启动');
      return true;
    } catch (e: any) {
      if (e.message?.includes('already started')) {
        console.log('ℹ️ 识别已在运行中，无需重启');
        return true; // 已经在运行，也算成功
      }
      console.error('❌ 启动失败:', e.message);
      return false;
    }
  }, []);

  // 安全停止识别
  const safeStop = useCallback(() => {
    const recognition = recognitionRef.current;
    if (recognition) {
      try {
        recognition.stop();
      } catch (e) {
        // 忽略停止错误
      }
    }
  }, []);

  // 初始化语音识别 - 只执行一次
  useEffect(() => {
    if (!('webkitSpeechRecognition' in window || 'SpeechRecognition' in window)) {
      console.error('浏览器不支持语音识别');
      return;
    }

    const SpeechRecognition = (window as any).webkitSpeechRecognition || (window as any).SpeechRecognition;
    const recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = true;
    recognition.lang = 'zh-CN';
    recognition.maxAlternatives = 1;

    recognition.onstart = () => {
      console.log('🎤 开始监听...');
      setInterimText('');
    };

    recognition.onresult = (event: any) => {
      let interim = '';
      let final = '';
      
      for (let i = event.resultIndex; i < event.results.length; i++) {
        const text = event.results[i][0].transcript;
        if (event.results[i].isFinal) {
          final += text;
        } else {
          interim += text;
        }
      }
      
      if (interim) {
        setInterimText(interim);
        
        // 智能打断检测 - 使用 ref 检查 isSpeaking
        if (isSpeakingRef.current) {
          handleSmartBargeIn(interim);
        }
      }
      
      if (final) {
        console.log('📝 识别结果:', final);
        setTranscript(final);
        setInterimText('');
        speechStartTimeRef.current = null;
        setBargeInStatus('idle');
        processCommand(final);
      }
    };

    recognition.onerror = (event: any) => {
      console.log('语音识别事件:', event.error);
      
      switch (event.error) {
        case 'no-speech':
          // 没有检测到语音，如果还在监听就重启
          if (isListeningRef.current && !isProcessingRef.current) {
            setTimeout(() => {
              if (isListeningRef.current) safeStart();
            }, 300);
          }
          break;
        case 'aborted':
          // 被中断，这是正常的，忽略
          break;
        case 'not-allowed':
        case 'permission-denied':
          alert('请允许麦克风权限才能使用语音功能');
          isListeningRef.current = false;
          setIsListening(false);
          break;
        case 'network':
          if (isListeningRef.current && !isProcessingRef.current) {
            setTimeout(() => {
              if (isListeningRef.current) safeStart();
            }, 500);
          }
          break;
      }
    };

    recognition.onend = () => {
      console.log('🎤 监听结束');
      // 如果还想监听，重新启动
      if (isListeningRef.current && !isProcessingRef.current) {
        setTimeout(() => {
          if (isListeningRef.current) {
            safeStart();
          }
        }, 300);
      }
    };

    recognitionRef.current = recognition;
    console.log('✅ 语音识别初始化完成');

    return () => {
      recognition.stop();
      if (bargeInTimeoutRef.current) clearTimeout(bargeInTimeoutRef.current);
    };
  }, []); // 空依赖，只初始化一次

  // 智能打断检测
  const handleSmartBargeIn = (text: string) => {
    const now = Date.now();
    
    if (!speechStartTimeRef.current) {
      speechStartTimeRef.current = now;
      setBargeInStatus('detecting');
      console.log('🎯 检测到用户说话...');
    }
    
    // 噪音词检测
    if (BARGE_IN_CONFIG.noiseWords.some(w => text.trim() === w)) {
      return;
    }
    
    // 立即打断词检测
    if (BARGE_IN_CONFIG.immediateBargeInWords.some(w => text.includes(w))) {
      console.log('⚡ 检测到打断关键词');
      confirmBargeIn();
      return;
    }
    
    // 时长检测
    const duration = now - speechStartTimeRef.current;
    if (duration >= BARGE_IN_CONFIG.minSpeechDuration) {
      console.log(`⏱️ 说话时长 ${duration}ms，确认打断`);
      confirmBargeIn();
    }
  };

  // 确认打断
  const confirmBargeIn = () => {
    console.log('🔇 确认打断，停止播报');
    setBargeInStatus('confirmed');
    stop();
    speechStartTimeRef.current = null;
    if (bargeInTimeoutRef.current) {
      clearTimeout(bargeInTimeoutRef.current);
      bargeInTimeoutRef.current = null;
    }
  };

  // 处理前端事件
  const handleFrontendEvent = async (event: string, data: any) => {
    console.log('🎯 处理前端事件:', event, data);
    
    switch (event) {
      case 'navigate':
        // 页面导航
        if (onNavigate && data.route) {
          onNavigate(data.route);
        }
        break;
        
      case 'query_data':
        // 健康数据查询播报
        const queryText = getHealthDataText(data.type);
        if (queryText) {
          speak(queryText);
          await new Promise(r => setTimeout(r, queryText.length * 120 + 500));
        }
        break;
        
      case 'generate_report':
        // 生成报告
        if (onGenerateReport) {
          onGenerateReport();
        }
        break;
        
      case 'set_reminder':
        // 设置提醒
        if (onSetReminder) {
          onSetReminder(data);
        }
        // 显示提醒设置成功的提示
        if (data.time) {
          speak(`好的，已为您设置${data.time}的${data.type === 'medication' ? '吃药' : ''}提醒`);
        }
        break;
        
      case 'emergency_call':
        // 紧急呼救
        if (onEmergency) {
          onEmergency();
        }
        break;
        
      case 'stop_speaking':
        // 停止语音
        stop();
        break;
        
      case 'cancel_action':
        // 取消操作
        stop();
        break;
        
      default:
        console.log('未知事件类型:', event);
    }
  };

  // 根据类型获取健康数据播报文本
  const getHealthDataText = (type: string): string | null => {
    // 如果有外部查询回调，优先使用
    if (onQueryData) {
      const result = onQueryData(type);
      if (result) return result;
    }
    
    // 使用本地健康数据
    if (!healthData?.vitalSigns) {
      return '正在加载健康数据，请稍候。';
    }
    
    const vs = healthData.vitalSigns;
    const name = healthData.userName || userName;
    
    switch (type) {
      case 'blood_pressure':
        if (vs.bloodPressure?.systolic) {
          return `${name}，您的血压是${vs.bloodPressure.systolic}/${vs.bloodPressure.diastolic}毫米汞柱，${vs.bloodPressure.status || '正常'}。`;
        }
        return '暂无血压数据。';
        
      case 'blood_sugar':
        if (vs.bloodSugar?.value) {
          return `${name}，您的血糖是${vs.bloodSugar.value}毫摩尔每升，${vs.bloodSugar.status || '正常'}。`;
        }
        return '暂无血糖数据。';
        
      case 'heart_rate':
        if (vs.heartRate?.value) {
          return `${name}，您的心率是每分钟${vs.heartRate.value}次，${vs.heartRate.status || '正常'}。`;
        }
        return '暂无心率数据。';
        
      case 'sleep':
        // TODO: 从后端获取睡眠数据
        return `${name}，昨晚您睡了约7小时30分钟，睡眠质量良好。`;
        
      case 'all':
      case 'today':
      case 'health_summary':
        return generateHealthReport();
        
      default:
        return generateHealthReport();
    }
  };

  // 处理命令
  const processCommand = async (text: string) => {
    isProcessingRef.current = true;
    setIsProcessing(true);
    
    try {
      const response = await fetch('/api/v1/voice-agent/text-command', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text, user_role: 'elderly', voice_style: 'default' }),
      });
      
      if (response.ok) {
        const result = await response.json();
        
        if (result.response) {
          speak(result.response);
          const duration = Math.max(result.response.length * 120, 1500);
          await new Promise(resolve => setTimeout(resolve, duration));
        }
        
        // 处理前端事件
        if (result.is_control && result.control_event) {
          handleFrontendEvent(result.control_event, result.control_data || {});
        }
        
        // 处理自动化场景事件
        if (result.is_automation && result.frontend_events) {
          for (const evt of result.frontend_events) {
            await handleFrontendEvent(evt.event, evt.data || {});
            // 事件间稍作延迟
            await new Promise(r => setTimeout(r, 500));
          }
        }
      } else {
        speak('抱歉，请求失败了，请再试一次');
      }
    } catch (err) {
      console.error('请求失败:', err);
      if (['救命', '帮帮我', '呼救'].some(w => text.includes(w))) {
        speak('紧急呼救已触发！正在通知您的紧急联系人！');
        onEmergency?.();
      } else {
        speak('抱歉，请求失败了，请再试一次');
      }
    } finally {
      isProcessingRef.current = false;
      setIsProcessing(false);
      setBargeInStatus('idle');
    }
  };

  // 切换语音输入
  const toggleListening = useCallback(() => {
    console.log('🔘 toggleListening, 当前状态:', isListening);
    
    if (isListening) {
      // 停止
      console.log('⏹️ 停止');
      isListeningRef.current = false;
      setIsListening(false);
      setTranscript('');
      setInterimText('');
      safeStop();
      stop();
    } else {
      // 开始
      if (!recognitionRef.current) {
        alert('您的浏览器不支持语音识别，请使用Chrome或Edge浏览器');
        return;
      }
      
      console.log('▶️ 开始');
      isListeningRef.current = true;
      setIsListening(true);
      
      // 启动识别
      safeStart();
    }
  }, [isListening, safeStart, safeStop, stop]);

  // 生成健康数据播报文本
  const generateHealthReport = (): string => {
    if (!healthData?.vitalSigns) {
      return '您好，正在加载健康数据，请稍候。';
    }

    const vs = healthData.vitalSigns;
    const act = healthData.activity;
    const wt = healthData.weight;
    const name = healthData.userName || userName;
    
    let text = `${name}好，以下是您今天的健康数据。`;
    
    if (vs.temperature?.value) {
      text += `体温${vs.temperature.value}摄氏度，${vs.temperature.status || '正常'}。`;
    }
    if (vs.heartRate?.value) {
      text += `心率每分钟${vs.heartRate.value}次，${vs.heartRate.status || '正常'}。`;
    }
    if (vs.bloodPressure?.systolic) {
      text += `血压${vs.bloodPressure.systolic}/${vs.bloodPressure.diastolic}毫米汞柱，${vs.bloodPressure.status || '正常'}。`;
    }
    if (vs.bloodSugar?.value) {
      text += `血糖${vs.bloodSugar.value}毫摩尔每升，${vs.bloodSugar.status || '正常'}。`;
    }
    if (act?.steps !== undefined) {
      const percentage = Math.round((act.steps / (act.goal || 10000)) * 100);
      text += `今日步数${act.steps}步，完成目标的${percentage}%。`;
    }
    if (wt?.value) {
      text += `体重${wt.value}公斤。`;
    }
    
    text += '总体健康状况良好，请继续保持！';
    return text;
  };

  // 朗读页面
  const handleReadPage = () => {
    const text = generateHealthReport();
    speak(text);
  };

  return (
    <div className={`flex items-center gap-3 ${className}`}>
      {/* 语音输入按钮 */}
      <Button 
        variant="ghost" 
        size="lg"
        disabled={isProcessing}
        className={`h-12 px-5 gap-2 rounded-lg transition-all ${
          isListening
            ? 'bg-green-500 text-white animate-pulse'
            : 'bg-white/20 text-white hover:bg-white/30 border border-white/30'
        }`}
        onClick={toggleListening}
      >
        {isProcessing ? (
          <>
            <Loader2 className="h-6 w-6 animate-spin" />
            <span className="text-[20px] font-bold">处理中</span>
          </>
        ) : isListening ? (
          <>
            <Mic className="h-6 w-6" />
            <span className="text-[20px] font-bold">🎤 聆听中</span>
          </>
        ) : (
          <>
            <MicOff className="h-6 w-6" />
            <span className="text-[20px] font-bold">语音助手</span>
          </>
        )}
      </Button>

      {/* 语音播报按钮 */}
      <Button 
        variant="ghost" 
        size="lg"
        className={`h-12 px-5 gap-2 rounded-lg transition-all ${
          isSpeaking 
            ? 'bg-white/90 text-red-500 animate-pulse' 
            : 'bg-white/20 text-white hover:bg-white/30 border border-white/30'
        }`}
        onClick={isSpeaking ? stop : handleReadPage}
      >
        {isSpeaking ? (
          <>
            <Square className="h-6 w-6" />
            <span className="text-[20px] font-bold">停止</span>
          </>
        ) : (
          <>
            <Volume2 className="h-6 w-6" />
            <span className="text-[20px] font-bold">播报</span>
          </>
        )}
      </Button>

      {/* 实时识别文字提示 */}
      {isListening && (interimText || transcript) && (
        <div className="flex flex-col text-white/90 text-sm max-w-48">
          {interimText && (
            <span className={`truncate ${
              bargeInStatus === 'confirmed' 
                ? 'text-red-300' 
                : bargeInStatus === 'detecting' 
                  ? 'text-orange-300 animate-pulse' 
                  : 'text-yellow-300 animate-pulse'
            }`}>
              {bargeInStatus === 'confirmed' ? '⏹️' : '🎤'} {interimText}...
            </span>
          )}
          {transcript && !interimText && (
            <span className="truncate">
              ✓ {transcript}
            </span>
          )}
        </div>
      )}
    </div>
  );
}
