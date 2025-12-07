/**
 * 流式语音 Hook
 * 
 * 前端实时采集音频流 → WebSocket传输 → 后端faster-whisper实时识别
 */

import { useState, useRef, useCallback, useEffect } from 'react';

const WS_URL = 'ws://localhost:8000/api/v1/streaming/ws/stream';

interface UseStreamingVoiceReturn {
  // 连接状态
  isConnected: boolean;
  connect: () => void;
  disconnect: () => void;
  
  // ASR 状态
  isRecording: boolean;
  partialText: string;   // 实时识别文本
  finalText: string;     // 最终识别文本
  
  // TTS 状态
  isSpeaking: boolean;
  
  // 方法
  startRecording: () => Promise<void>;
  stopRecording: () => void;
  speak: (text: string) => void;
  stopSpeaking: () => void;
  
  // 回调
  onFinalText: (handler: (text: string) => void) => void;
  
  // 错误
  error: string | null;
  clearError: () => void;
}

export function useStreamingVoice(): UseStreamingVoiceReturn {
  const [isConnected, setIsConnected] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [partialText, setPartialText] = useState('');
  const [finalText, setFinalText] = useState('');
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const wsRef = useRef<WebSocket | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const processorRef = useRef<ScriptProcessorNode | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const audioQueueRef = useRef<Uint8Array[]>([]);
  const audioPlayerRef = useRef<AudioContext | null>(null);
  const finalTextHandlerRef = useRef<((text: string) => void) | null>(null);

  /**
   * 处理 WebSocket 消息
   */
  const handleMessage = useCallback((event: MessageEvent) => {
    try {
      const data = JSON.parse(event.data);
      console.log('📩 收到:', data.type);
      
      switch (data.type) {
        case 'partial':
          setPartialText(data.text || '');
          break;
          
        case 'final':
          setFinalText(data.text || '');
          setPartialText('');
          if (finalTextHandlerRef.current && data.text) {
            finalTextHandlerRef.current(data.text);
          }
          break;
          
        case 'tts_audio':
          // 播放TTS音频
          playAudioChunk(data.data);
          break;
          
        case 'tts_done':
          setIsSpeaking(false);
          break;
          
        case 'tts_stopped':
          setIsSpeaking(false);
          audioQueueRef.current = [];
          break;
          
        case 'status':
          if (data.recording !== undefined) {
            setIsRecording(data.recording);
          }
          if (!data.asr_available) {
            setError('语音识别服务未就绪');
          }
          break;
          
        case 'error':
          setError(data.message);
          break;
      }
    } catch (e) {
      console.error('解析消息失败:', e);
    }
  }, []);

  /**
   * 播放音频块
   */
  const playAudioChunk = useCallback(async (base64Data: string) => {
    try {
      const binaryData = atob(base64Data);
      const bytes = new Uint8Array(binaryData.length);
      for (let i = 0; i < binaryData.length; i++) {
        bytes[i] = binaryData.charCodeAt(i);
      }
      
      // 创建 Blob 并播放
      const blob = new Blob([bytes], { type: 'audio/mpeg' });
      const url = URL.createObjectURL(blob);
      const audio = new Audio(url);
      
      audio.onended = () => {
        URL.revokeObjectURL(url);
      };
      
      await audio.play();
    } catch (e) {
      console.error('播放音频失败:', e);
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
      console.log('🔌 连接 WebSocket...');
      const ws = new WebSocket(WS_URL);
      
      ws.onopen = () => {
        console.log('✅ WebSocket 已连接');
        setIsConnected(true);
        setError(null);
      };
      
      ws.onmessage = handleMessage;
      
      ws.onclose = () => {
        console.log('❌ WebSocket 断开');
        setIsConnected(false);
        setIsRecording(false);
      };
      
      ws.onerror = () => {
        setError('连接失败，请确保后端服务已启动');
      };
      
      wsRef.current = ws;
    } catch (e) {
      setError('无法创建连接');
    }
  }, [handleMessage]);

  /**
   * 断开连接
   */
  const disconnect = useCallback(() => {
    stopRecording();
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    setIsConnected(false);
  }, []);

  /**
   * 发送消息
   */
  const sendMessage = useCallback((data: object) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(data));
    }
  }, []);

  /**
   * 开始录音
   */
  const startRecording = useCallback(async () => {
    if (!isConnected) {
      connect();
      await new Promise(resolve => setTimeout(resolve, 500));
    }
    
    try {
      // 获取麦克风权限
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          sampleRate: 16000,
          channelCount: 1,
          echoCancellation: true,
          noiseSuppression: true,
        }
      });
      streamRef.current = stream;
      
      // 创建 AudioContext
      const audioContext = new AudioContext({ sampleRate: 16000 });
      audioContextRef.current = audioContext;
      
      const source = audioContext.createMediaStreamSource(stream);
      const processor = audioContext.createScriptProcessor(4096, 1, 1);
      processorRef.current = processor;
      
      // 处理音频数据
      processor.onaudioprocess = (e) => {
        if (!isRecording) return;
        
        const inputData = e.inputBuffer.getChannelData(0);
        
        // 转换为 16-bit PCM
        const pcmData = new Int16Array(inputData.length);
        for (let i = 0; i < inputData.length; i++) {
          pcmData[i] = Math.max(-32768, Math.min(32767, inputData[i] * 32768));
        }
        
        // 发送到后端
        const base64Data = btoa(String.fromCharCode(...new Uint8Array(pcmData.buffer)));
        sendMessage({ type: 'audio', data: base64Data });
      };
      
      source.connect(processor);
      processor.connect(audioContext.destination);
      
      // 通知后端开始
      sendMessage({ type: 'start' });
      setIsRecording(true);
      setPartialText('');
      setFinalText('');
      
      console.log('🎤 开始录音');
      
    } catch (e: any) {
      console.error('录音失败:', e);
      setError(e.message || '无法访问麦克风');
    }
  }, [isConnected, connect, sendMessage, isRecording]);

  /**
   * 停止录音
   */
  const stopRecording = useCallback(() => {
    // 停止音频处理
    if (processorRef.current) {
      processorRef.current.disconnect();
      processorRef.current = null;
    }
    
    if (audioContextRef.current) {
      audioContextRef.current.close();
      audioContextRef.current = null;
    }
    
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }
    
    // 通知后端停止
    sendMessage({ type: 'stop' });
    setIsRecording(false);
    
    console.log('🎤 停止录音');
  }, [sendMessage]);

  /**
   * TTS播放
   */
  const speak = useCallback((text: string) => {
    sendMessage({ type: 'speak', text });
    setIsSpeaking(true);
  }, [sendMessage]);

  /**
   * 停止TTS
   */
  const stopSpeaking = useCallback(() => {
    sendMessage({ type: 'stop_speak' });
    setIsSpeaking(false);
  }, [sendMessage]);

  /**
   * 设置最终文本回调
   */
  const onFinalText = useCallback((handler: (text: string) => void) => {
    finalTextHandlerRef.current = handler;
  }, []);

  /**
   * 清除错误
   */
  const clearError = useCallback(() => {
    setError(null);
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
    clearError,
  };
}
