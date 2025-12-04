// ============================================================================
// 唤醒词监听服务 - 通过特定唤醒词激活语音交互
// 唤醒词: "糖豆"
// ============================================================================

type WakeCallback = () => void;

class WakeWordService {
  private static instance: WakeWordService;
  private recognition: any = null;
  private isListening: boolean = false;
  private wakeCallback: WakeCallback | null = null;
  private wakeWord: string = '糖豆';
  private listeners: Set<(listening: boolean) => void> = new Set();

  private constructor() {}

  public static getInstance(): WakeWordService {
    if (!WakeWordService.instance) {
      WakeWordService.instance = new WakeWordService();
    }
    return WakeWordService.instance;
  }

  // 设置唤醒词
  public setWakeWord(word: string): void {
    this.wakeWord = word;
  }

  // 获取当前唤醒词
  public getWakeWord(): string {
    return this.wakeWord;
  }

  // 设置唤醒回调
  public onWake(callback: WakeCallback): void {
    this.wakeCallback = callback;
  }

  // 开始监听唤醒词
  public startListening(): boolean {
    if (this.isListening) return true;

    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (!SpeechRecognition) {
      console.error('浏览器不支持语音识别');
      return false;
    }

    this.recognition = new SpeechRecognition();
    this.recognition.lang = 'zh-CN';
    this.recognition.continuous = true;
    this.recognition.interimResults = true;
    this.recognition.maxAlternatives = 3; // 多个候选结果提高识别率

    this.recognition.onstart = () => {
      this.isListening = true;
      this.notifyListeners();
      console.log('🎤 唤醒词监听已启动，说"糖豆"唤醒我');
    };

    this.recognition.onresult = (event: any) => {
      for (let i = event.resultIndex; i < event.results.length; i++) {
        // 检查所有候选结果
        for (let j = 0; j < event.results[i].length; j++) {
          const transcript = event.results[i][j].transcript.toLowerCase();
          
          // 检测唤醒词（支持多种变体）
          if (this.containsWakeWord(transcript)) {
            console.log('🎉 检测到唤醒词:', transcript);
            
            // 暂停唤醒词监听
            this.pauseListening();
            
            // 触发唤醒回调
            if (this.wakeCallback) {
              this.wakeCallback();
            }
            return;
          }
        }
      }
    };

    this.recognition.onerror = (event: any) => {
      if (event.error === 'no-speech' || event.error === 'aborted') {
        // 静默重启
        if (this.isListening) {
          setTimeout(() => this.restartListening(), 100);
        }
        return;
      }
      console.error('唤醒词识别错误:', event.error);
    };

    this.recognition.onend = () => {
      // 如果还在监听状态，自动重启
      if (this.isListening) {
        setTimeout(() => this.restartListening(), 100);
      }
    };

    try {
      this.recognition.start();
      return true;
    } catch (e) {
      console.error('启动唤醒词监听失败:', e);
      return false;
    }
  }

  // 检测是否包含唤醒词
  private containsWakeWord(text: string): boolean {
    const variations = [
      this.wakeWord,
      '糖豆',
      '唐豆',
      '糖斗',
      '汤豆',
      '堂豆',
      '糖宝',
      '唐宝',
      '汤宝',
      'tangdou',
      'tangbao',
    ];
    
    return variations.some(word => text.includes(word.toLowerCase()));
  }

  // 暂停监听（被唤醒后暂停，等待对话结束）
  public pauseListening(): void {
    if (this.recognition) {
      try {
        this.recognition.stop();
      } catch (e) {}
    }
    this.isListening = false;
    this.notifyListeners();
  }

  // 重新开始监听
  private restartListening(): void {
    if (!this.isListening) return;
    
    try {
      this.recognition?.start();
    } catch (e) {
      // 可能已经在运行，忽略错误
    }
  }

  // 恢复监听（对话结束后恢复）
  public resumeListening(): void {
    if (this.isListening) return;
    this.startListening();
  }

  // 停止监听
  public stopListening(): void {
    this.isListening = false;
    if (this.recognition) {
      try {
        this.recognition.stop();
      } catch (e) {}
      this.recognition = null;
    }
    this.notifyListeners();
    console.log('🔇 唤醒词监听已停止');
  }

  // 获取监听状态
  public getIsListening(): boolean {
    return this.isListening;
  }

  // 添加状态监听器
  public addListener(callback: (listening: boolean) => void): void {
    this.listeners.add(callback);
  }

  // 移除状态监听器
  public removeListener(callback: (listening: boolean) => void): void {
    this.listeners.delete(callback);
  }

  // 通知所有监听器
  private notifyListeners(): void {
    this.listeners.forEach(callback => callback(this.isListening));
  }
}

// 导出单例
export const wakeWordService = WakeWordService.getInstance();
