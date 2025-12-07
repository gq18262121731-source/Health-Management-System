/**
 * 语音服务 Hook
 * 
 * 封装 ASR（语音识别）和 TTS（语音合成）功能
 * 使用后端 SenseVoice + Edge-TTS
 */

import { useState, useRef, useCallback } from 'react';
import { 
  textToSpeech, 
  speechToText, 
  AudioRecorder,
  playAudio,
  VOICE_OPTIONS 
} from '../services/voiceService';

interface UseVoiceServiceReturn {
  // ASR 状态
  isRecording: boolean;
  isProcessing: boolean;
  transcript: string;
  
  // TTS 状态
  isSpeaking: boolean;
  
  // ASR 方法
  startRecording: () => Promise<void>;
  stopRecording: () => Promise<string>;
  cancelRecording: () => void;
  
  // TTS 方法
  speak: (text: string, voice?: string) => Promise<void>;
  stopSpeaking: () => void;
  
  // 工具
  resetTranscript: () => void;
  error: string | null;
  clearError: () => void;
}

export function useVoiceService(): UseVoiceServiceReturn {
  // ASR 状态
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [transcript, setTranscript] = useState('');
  
  // TTS 状态
  const [isSpeaking, setIsSpeaking] = useState(false);
  
  // 错误状态
  const [error, setError] = useState<string | null>(null);
  
  // Refs
  const recorderRef = useRef<AudioRecorder | null>(null);
  const audioRef = useRef<HTMLAudioElement | null>(null);

  /**
   * 开始录音
   */
  const startRecording = useCallback(async () => {
    try {
      setError(null);
      
      // 创建录音器
      recorderRef.current = new AudioRecorder();
      await recorderRef.current.start();
      
      setIsRecording(true);
    } catch (err: any) {
      setError(err.message || '无法启动录音');
      console.error('录音启动失败:', err);
    }
  }, []);

  /**
   * 停止录音并识别
   */
  const stopRecording = useCallback(async (): Promise<string> => {
    if (!recorderRef.current) {
      return '';
    }

    try {
      setIsRecording(false);
      setIsProcessing(true);
      setError(null);

      // 停止录音获取音频
      const audioBlob = await recorderRef.current.stop();
      
      // 调用后端 ASR
      const text = await speechToText(audioBlob);
      
      setTranscript(text);
      setIsProcessing(false);
      
      return text;
    } catch (err: any) {
      setIsProcessing(false);
      
      // 检查是否是后端未配置 ASR
      if (err.message?.includes('501') || err.message?.includes('未配置')) {
        setError('语音识别服务未配置，请使用文字输入');
      } else {
        setError(err.message || '语音识别失败');
      }
      
      console.error('语音识别失败:', err);
      return '';
    }
  }, []);

  /**
   * 取消录音
   */
  const cancelRecording = useCallback(() => {
    if (recorderRef.current) {
      recorderRef.current.cancel();
      recorderRef.current = null;
    }
    setIsRecording(false);
    setIsProcessing(false);
  }, []);

  /**
   * 语音播报
   */
  const speak = useCallback(async (text: string, voice?: string) => {
    try {
      setError(null);
      setIsSpeaking(true);

      // 调用后端 TTS
      const audioUrl = await textToSpeech({ 
        text, 
        voice: voice || 'xiaoxiao',
        rate: '+0%',   // 正常语速
        volume: '+10%' // 稍大音量
      });

      // 播放音频
      audioRef.current = playAudio(audioUrl);
      
      audioRef.current.onended = () => {
        setIsSpeaking(false);
      };
      
      audioRef.current.onerror = () => {
        setIsSpeaking(false);
        setError('音频播放失败');
      };
    } catch (err: any) {
      setIsSpeaking(false);
      setError(err.message || '语音合成失败');
      console.error('TTS 错误:', err);
    }
  }, []);

  /**
   * 停止播报
   */
  const stopSpeaking = useCallback(() => {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
      audioRef.current = null;
    }
    setIsSpeaking(false);
  }, []);

  /**
   * 清空识别结果
   */
  const resetTranscript = useCallback(() => {
    setTranscript('');
  }, []);

  /**
   * 清除错误
   */
  const clearError = useCallback(() => {
    setError(null);
  }, []);

  return {
    // ASR 状态
    isRecording,
    isProcessing,
    transcript,
    
    // TTS 状态
    isSpeaking,
    
    // ASR 方法
    startRecording,
    stopRecording,
    cancelRecording,
    
    // TTS 方法
    speak,
    stopSpeaking,
    
    // 工具
    resetTranscript,
    error,
    clearError,
  };
}

// 导出语音选项供组件使用
export { VOICE_OPTIONS };
