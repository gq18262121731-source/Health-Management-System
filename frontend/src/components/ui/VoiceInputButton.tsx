import React, { useState } from 'react';
import { Mic } from 'lucide-react';

interface VoiceInputButtonProps {
  onVoiceResult: (text: string) => void;
  className?: string;
  size?: 'sm' | 'md' | 'lg';
}

export function VoiceInputButton({ onVoiceResult, className = '', size = 'md' }: VoiceInputButtonProps) {
  const [isListening, setIsListening] = useState(false);

  const sizeClasses = {
    sm: 'w-10 h-10',
    md: 'w-14 h-14',
    lg: 'w-16 h-16',
  };

  const iconSizes = {
    sm: 'h-5 w-5',
    md: 'h-7 w-7',
    lg: 'h-8 w-8',
  };

  const handleVoiceInput = () => {
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
      alert('您的浏览器不支持语音识别功能');
      return;
    }

    const SpeechRecognition = (window as any).webkitSpeechRecognition || (window as any).SpeechRecognition;
    const recognition = new SpeechRecognition();
    
    recognition.lang = 'zh-CN';
    recognition.continuous = false;
    recognition.interimResults = false;

    setIsListening(true);
    
    // 语音播报提示
    if ('speechSynthesis' in window) {
      const utterance = new SpeechSynthesisUtterance('请开始说话');
      utterance.lang = 'zh-CN';
      utterance.rate = 0.9;
      window.speechSynthesis.speak(utterance);
    }

    recognition.onresult = (event: any) => {
      const transcript = event.results[0][0].transcript;
      onVoiceResult(transcript);
      setIsListening(false);
      
      // 播报识别结果
      if ('speechSynthesis' in window) {
        const utterance = new SpeechSynthesisUtterance(`已识别：${transcript}`);
        utterance.lang = 'zh-CN';
        utterance.rate = 0.9;
        window.speechSynthesis.speak(utterance);
      }
    };

    recognition.onerror = () => {
      setIsListening(false);
      alert('语音识别出错，请重试');
    };

    recognition.onend = () => {
      setIsListening(false);
    };

    recognition.start();
  };

  return (
    <button
      type="button"
      onClick={handleVoiceInput}
      className={`flex-shrink-0 ${sizeClasses[size]} rounded-lg flex items-center justify-center
                 transition-all duration-200 border-2
                 ${isListening 
                   ? 'bg-red-500 border-red-600 text-white animate-pulse shadow-lg' 
                   : 'bg-teal-500 hover:bg-teal-600 border-teal-600 text-white shadow-md hover:shadow-lg'
                 } ${className}`}
      title="语音输入"
    >
      <Mic className={iconSizes[size]} />
    </button>
  );
}
