/**
 * 实时语音 Hook
 * 
 * 功能：
 * 1. 实时转写 - 说话时文字实时出现
 * 2. 自动语音检测 - 不用手动点击开始/结束
 * 3. 流式TTS播放 - AI回复边生成边播放
 * 4. 打断功能 - 随时打断AI说话
 */

import { useState, useRef, useCallback, useEffect } from 'react';

const WS_URL = 'ws://localhost:8000/api/v1/realtime-voice/ws/voice';

type MessageHandler = (message: RealtimeMessage) => void;

interface RealtimeMessage {
  type: string;
  text?: string;
  message?: string;
  success?: boolean;
  is_recording?: boolean;
  is_speaking?: boolean;
}

interface UseRealtimeVoiceReturn {
  // 连接状态
  isConnected: boolean;
  connect: () => void;
  disconnect: () => void;
  
  // ASR 状态
  isListening: boolean;
  isRecording: boolean;  // VAD 检测到语音
  realtimeText: string;  // 实时转写文本
  finalText: string;     // 最终识别文本
  
  // TTS 状态
  isSpeaking: boolean;
  
  // 方法
  startListening: () => void;
  stopListening: () => void;
  speak: (text: string) => void;
  stopSpeaking: () => void;  // 打断
  
  // 回调设置
  onFinalText: (handler: (text: string) => void) => void;
  
  // 错误
  error: string | null;
}

export function useRealtimeVoice(): UseRealtimeVoiceReturn {
  const [isConnected, setIsConnected] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [realtimeText, setRealtimeText] = useState('');
  const [finalText, setFinalText] = useState('');
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const wsRef = useRef<WebSocket | null>(null);
  const finalTextHandlerRef = useRef<((text: string) => void) | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  /**
   * 处理 WebSocket 消息
   */
  const handleMessage = useCallback((event: MessageEvent) => {
    try {
      const message: RealtimeMessage = JSON.parse(event.data);
      console.log('📩 收到消息:', message);
      
      switch (message.type) {
        case 'realtime_text':
          // 实时转写文本
          setRealtimeText(message.text || '');
          break;
          
        case 'final_text':
          // 最终识别文本
          setFinalText(message.text || '');
          setRealtimeText('');  // 清空实时文本
          if (finalTextHandlerRef.current && message.text) {
            finalTextHandlerRef.current(message.text);
          }
          break;
          
        case 'recording_start':
          setIsRecording(true);
          break;
          
        case 'recording_stop':
          setIsRecording(false);
          break;
          
        case 'vad_start':
          // 检测到语音开始
          setIsRecording(true);
          console.log('🎤 检测到语音');
          break;
          
        case 'vad_stop':
          // 检测到语音结束
          console.log('🎤 语音结束');
          break;
          
        case 'tts_start':
          setIsSpeaking(true);
          break;
          
        case 'tts_end':
          setIsSpeaking(false);
          break;
          
        case 'tts_interrupted':
          setIsSpeaking(false);
          console.log('🔇 语音被打断');
          break;
          
        case 'status':
          if (message.is_recording !== undefined) {
            setIsRecording(message.is_recording);
          }
          if (message.is_speaking !== undefined) {
            setIsSpeaking(message.is_speaking);
          }
          break;
          
        case 'error':
          setError(message.message || '未知错误');
          break;
      }
    } catch (e) {
      console.error('解析消息失败:', e);
    }
  }, []);

  /**
   * 连接 WebSocket
   */
  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      return;
    }
    
    try {
      console.log('🔌 连接 WebSocket:', WS_URL);
      const ws = new WebSocket(WS_URL);
      
      ws.onopen = () => {
        console.log('✅ WebSocket 已连接');
        setIsConnected(true);
        setError(null);
      };
      
      ws.onmessage = handleMessage;
      
      ws.onclose = (event) => {
        console.log('❌ WebSocket 断开:', event.code);
        setIsConnected(false);
        setIsListening(false);
        setIsRecording(false);
        
        // 自动重连
        if (event.code !== 1000) {
          reconnectTimeoutRef.current = setTimeout(() => {
            console.log('🔄 尝试重连...');
            connect();
          }, 3000);
        }
      };
      
      ws.onerror = (error) => {
        console.error('WebSocket 错误:', error);
        setError('连接失败，请确保后端服务已启动');
      };
      
      wsRef.current = ws;
    } catch (e) {
      console.error('创建 WebSocket 失败:', e);
      setError('无法创建连接');
    }
  }, [handleMessage]);

  /**
   * 断开 WebSocket
   */
  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }
    if (wsRef.current) {
      wsRef.current.close(1000);
      wsRef.current = null;
    }
    setIsConnected(false);
  }, []);

  /**
   * 发送消息
   */
  const sendMessage = useCallback((action: string, data?: object) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ action, ...data }));
    } else {
      setError('未连接到服务器');
    }
  }, []);

  /**
   * 开始监听（自动VAD）
   */
  const startListening = useCallback(() => {
    sendMessage('start_listening');
    setIsListening(true);
    setRealtimeText('');
    setFinalText('');
  }, [sendMessage]);

  /**
   * 停止监听
   */
  const stopListening = useCallback(() => {
    sendMessage('stop_listening');
    setIsListening(false);
  }, [sendMessage]);

  /**
   * 播放语音（流式TTS）
   */
  const speak = useCallback((text: string) => {
    sendMessage('speak', { text });
  }, [sendMessage]);

  /**
   * 停止播放（打断）
   */
  const stopSpeaking = useCallback(() => {
    sendMessage('stop_speaking');
  }, [sendMessage]);

  /**
   * 设置最终文本回调
   */
  const onFinalText = useCallback((handler: (text: string) => void) => {
    finalTextHandlerRef.current = handler;
  }, []);

  /**
   * 清理
   */
  useEffect(() => {
    return () => {
      disconnect();
    };
  }, [disconnect]);

  return {
    isConnected,
    connect,
    disconnect,
    isListening,
    isRecording,
    realtimeText,
    finalText,
    isSpeaking,
    startListening,
    stopListening,
    speak,
    stopSpeaking,
    onFinalText,
    error,
  };
}
