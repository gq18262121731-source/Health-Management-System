/**
 * 全局语音播报 Context
 * 
 * 为老年端提供统一的语音播报功能
 * - 优先使用浏览器内置 TTS（零延迟）
 * - 降级到后端 TTS
 * - 支持打断当前播放
 */

import React, { createContext, useContext, useState, useRef, useCallback, ReactNode, useEffect } from 'react';

// 使用相对路径，通过vite代理转发到后端
const API_BASE = '';

// TTS 模式
type TTSMode = 'browser' | 'backend';

interface VoiceContextType {
  // 状态
  isSpeaking: boolean;
  isEnabled: boolean;
  
  // 方法
  speak: (text: string) => Promise<void>;
  stop: () => void;
  toggle: () => void;  // 开关语音功能
  
  // 朗读页面元素
  speakElement: (element: HTMLElement | null) => Promise<void>;
}

const VoiceContext = createContext<VoiceContextType | null>(null);

interface VoiceProviderProps {
  children: ReactNode;
}

export function VoiceProvider({ children }: VoiceProviderProps) {
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [isEnabled, setIsEnabled] = useState(true);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const queueRef = useRef<string[]>([]);
  const isPlayingRef = useRef(false);

  /**
   * 快速TTS - 直接获取音频流（不保存文件，更快）
   */
  const fetchAudioFast = async (text: string): Promise<Blob | null> => {
    try {
      const response = await fetch(`${API_BASE}/api/v1/voice/tts/fast`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          text,
          voice: 'xiaoxiao',
          rate: '+15%',  // 加快语速
          volume: '+10%',
        }),
      });

      if (!response.ok) return null;
      return await response.blob();
    } catch (error) {
      console.error('TTS 请求失败:', error);
      return null;
    }
  };

  /**
   * 播放音频Blob
   */
  const playAudioBlob = (blob: Blob): Promise<void> => {
    return new Promise((resolve, reject) => {
      if (audioRef.current) {
        audioRef.current.pause();
        URL.revokeObjectURL(audioRef.current.src); // 释放之前的URL
      }

      const url = URL.createObjectURL(blob);
      const audio = new Audio(url);
      audioRef.current = audio;

      audio.onended = () => {
        setIsSpeaking(false);
        URL.revokeObjectURL(url); // 释放URL
        resolve();
      };

      audio.onerror = () => {
        setIsSpeaking(false);
        URL.revokeObjectURL(url);
        reject(new Error('音频播放失败'));
      };

      setIsSpeaking(true);
      audio.play().catch(reject);
    });
  };

  /**
   * 处理播放队列 - 分句快速播放
   */
  const processQueue = useCallback(async () => {
    if (isPlayingRef.current || queueRef.current.length === 0) return;

    isPlayingRef.current = true;

    while (queueRef.current.length > 0) {
      const text = queueRef.current.shift();
      if (!text) continue;

      const audioBlob = await fetchAudioFast(text);
      if (audioBlob) {
        try {
          await playAudioBlob(audioBlob);
        } catch (error) {
          console.error('播放失败:', error);
        }
      }
    }

    isPlayingRef.current = false;
  }, []);

  /**
   * 按句子分割文本（用于快速播放）
   */
  const splitSentences = (text: string): string[] => {
    // 按中文标点分割
    const parts = text.split(/([。！？；])/);
    const result: string[] = [];
    let current = "";
    
    for (const part of parts) {
      current += part;
      // 遇到句末标点就分割
      if (/[。！？；]/.test(part) && current.trim()) {
        result.push(current.trim());
        current = "";
      }
    }
    
    if (current.trim()) {
      result.push(current.trim());
    }
    
    return result.length > 0 ? result : [text];
  };

  /**
   * 语音播报 - 按句子分割，首句更快播放
   */
  const speak = useCallback(async (text: string) => {
    if (!isEnabled || !text.trim()) return;

    // 清空队列，打断当前播放
    queueRef.current = [];
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current = null;
    }
    setIsSpeaking(false);
    isPlayingRef.current = false;

    // 按句子分割，每句单独播放（首句延迟更低）
    const sentences = splitSentences(text);
    queueRef.current.push(...sentences);

    await processQueue();
  }, [isEnabled, processQueue]);

  /**
   * 停止播放
   */
  const stop = useCallback(() => {
    queueRef.current = [];
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current = null;
    }
    setIsSpeaking(false);
    isPlayingRef.current = false;
  }, []);

  /**
   * 开关语音功能
   */
  const toggle = useCallback(() => {
    setIsEnabled(prev => !prev);
    if (isEnabled) {
      stop();
    }
  }, [isEnabled, stop]);

  /**
   * 朗读 HTML 元素内容
   */
  const speakElement = useCallback(async (element: HTMLElement | null) => {
    if (!element) return;

    // 提取元素的文本内容
    const text = element.innerText || element.textContent || '';
    if (text.trim()) {
      await speak(text.trim());
    }
  }, [speak]);

  return (
    <VoiceContext.Provider
      value={{
        isSpeaking,
        isEnabled,
        speak,
        stop,
        toggle,
        speakElement,
      }}
    >
      {children}
    </VoiceContext.Provider>
  );
}

/**
 * 使用全局语音播报
 */
export function useVoice() {
  const context = useContext(VoiceContext);
  if (!context) {
    throw new Error('useVoice must be used within VoiceProvider');
  }
  return context;
}

/**
 * 语音播报按钮组件
 */
export function SpeakButton({ 
  text, 
  className = '',
  children 
}: { 
  text: string; 
  className?: string;
  children?: ReactNode;
}) {
  const { speak, isSpeaking, stop, isEnabled } = useVoice();

  const handleClick = () => {
    if (isSpeaking) {
      stop();
    } else {
      speak(text);
    }
  };

  if (!isEnabled) return null;

  return (
    <button
      onClick={handleClick}
      className={`inline-flex items-center gap-1 text-blue-600 hover:text-blue-800 ${className}`}
      title={isSpeaking ? '停止播放' : '语音播报'}
    >
      {isSpeaking ? (
        <span className="animate-pulse">🔊</span>
      ) : (
        <span>🔈</span>
      )}
      {children}
    </button>
  );
}
