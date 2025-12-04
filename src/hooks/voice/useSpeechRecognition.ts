import { useState, useRef, useCallback } from 'react';

/**
 * ===========================================================================
 * Hook: useSpeechRecognition
 * 
 * 功能：
 * 1. 浏览器语音识别（Web Speech API）
 * 2. 将语音转换为文本
 * 3. 适老化设计，简化使用
 * 
 * 使用场景：
 * - 老人端所有输入框的语音输入
 * - AI 对话的语音输入
 * - 心情记录的语音备注
 * 
 * 浏览器支持：
 * - Chrome、Edge、Safari（部分）
 * - 需要 HTTPS 或 localhost
 * ===========================================================================
 */

interface UseSpeechRecognitionReturn {
  /** 是否正在监听 */
  isListening: boolean;
  /** 识别的文本 */
  transcript: string;
  /** 开始监听 */
  startListening: () => void;
  /** 停止监听 */
  stopListening: () => void;
  /** 清空识别结果 */
  resetTranscript: () => void;
  /** 是否支持语音识别 */
  isSupported: boolean;
}

export function useSpeechRecognition(): UseSpeechRecognitionReturn {
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const recognitionRef = useRef<any>(null);

  /**
   * 检查浏览器是否支持语音识别
   */
  const isSupported = 
    'webkitSpeechRecognition' in window || 
    'SpeechRecognition' in window;

  /**
   * 开始语音识别
   */
  const startListening = useCallback(() => {
    // 检查浏览器支持
    if (!isSupported) {
      alert('您的浏览器不支持语音识别功能，请使用 Chrome 或 Edge 浏览器');
      return;
    }

    // 如果已经在监听，先停止
    if (isListening) {
      recognitionRef.current?.stop();
      setIsListening(false);
      return;
    }

    // 创建语音识别实例
    const SpeechRecognition = 
      (window as any).SpeechRecognition || 
      (window as any).webkitSpeechRecognition;
    
    const recognition = new SpeechRecognition();
    
    // 配置
    recognition.lang = 'zh-CN';              // 中文
    recognition.continuous = false;          // 不持续监听
    recognition.interimResults = false;      // 不返回中间结果
    recognition.maxAlternatives = 1;         // 只返回最佳结果

    // 事件监听 - 开始
    recognition.onstart = () => {
      console.log('🎤 开始语音识别');
      setIsListening(true);
    };

    // 事件监听 - 结果
    recognition.onresult = (event: any) => {
      const result = event.results[0][0].transcript;
      console.log('✅ 识别结果:', result);
      setTranscript(result);
      setIsListening(false);
    };

    // 事件监听 - 错误
    recognition.onerror = (event: any) => {
      console.error('❌ 语音识别错误:', event.error);
      
      let errorMessage = '语音识别失败';
      switch (event.error) {
        case 'no-speech':
          errorMessage = '没有检测到语音，请再试一次';
          break;
        case 'audio-capture':
          errorMessage = '无法访问麦克风，请检查权限';
          break;
        case 'not-allowed':
          errorMessage = '麦克风权限被拒绝，请在浏览器设置中允许';
          break;
        case 'network':
          errorMessage = '网络错误，请检查网络连接';
          break;
      }
      
      alert(errorMessage);
      setIsListening(false);
    };

    // 事件监听 - 结束
    recognition.onend = () => {
      console.log('🎤 语音识别结束');
      setIsListening(false);
    };

    // 保存实例并开始识别
    recognitionRef.current = recognition;
    recognition.start();
  }, [isListening, isSupported]);

  /**
   * 停止语音识别
   */
  const stopListening = useCallback(() => {
    if (recognitionRef.current) {
      recognitionRef.current.stop();
      setIsListening(false);
    }
  }, []);

  /**
   * 清空识别结果
   */
  const resetTranscript = useCallback(() => {
    setTranscript('');
  }, []);

  return {
    isListening,
    transcript,
    startListening,
    stopListening,
    resetTranscript,
    isSupported,
  };
}

/**
 * 使用示例：
 * 
 * ```typescript
 * function VoiceInput() {
 *   const [text, setText] = useState('');
 *   const { 
 *     isListening, 
 *     transcript, 
 *     startListening,
 *     resetTranscript,
 *     isSupported 
 *   } = useSpeechRecognition();
 * 
 *   // 当识别结果变化时，更新输入框
 *   useEffect(() => {
 *     if (transcript) {
 *       setText(transcript);
 *       resetTranscript();
 *     }
 *   }, [transcript]);
 * 
 *   if (!isSupported) {
 *     return <p>您的浏览器不支持语音输入</p>;
 *   }
 * 
 *   return (
 *     <div>
 *       <Input value={text} onChange={(e) => setText(e.target.value)} />
 *       <Button onClick={startListening}>
 *         {isListening ? (
 *           <>
 *             <Mic className="animate-pulse" />
 *             正在聆听...
 *           </>
 *         ) : (
 *           <>
 *             <Mic />
 *             语音输入
 *           </>
 *         )}
 *       </Button>
 *     </div>
 *   );
 * }
 * ```
 */
