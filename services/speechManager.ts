// ============================================================================
// 全局语音管理器 - 确保任何时候只有一个语音在播放
// ============================================================================

class SpeechManager {
  private static instance: SpeechManager;
  private isSpeaking: boolean = false;
  private currentUtterance: SpeechSynthesisUtterance | null = null;
  private listeners: Set<(speaking: boolean) => void> = new Set();

  private constructor() {
    // 私有构造函数，确保单例
  }

  public static getInstance(): SpeechManager {
    if (!SpeechManager.instance) {
      SpeechManager.instance = new SpeechManager();
    }
    return SpeechManager.instance;
  }

  // 停止所有语音
  public stop(): void {
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
    }
    this.isSpeaking = false;
    this.currentUtterance = null;
    this.notifyListeners();
  }

  // 播放语音（会先停止之前的语音）
  public speak(text: string, options?: {
    rate?: number;
    pitch?: number;
    volume?: number;
    lang?: string;
    onEnd?: () => void;
    onError?: () => void;
  }): Promise<void> {
    return new Promise((resolve, reject) => {
      // 先停止之前的语音
      this.stop();

      if (!('speechSynthesis' in window)) {
        resolve();
        return;
      }

      // 等待一下确保之前的语音完全停止
      setTimeout(() => {
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = options?.lang || 'zh-CN';
        utterance.rate = options?.rate || 0.9;
        utterance.pitch = options?.pitch || 1;
        utterance.volume = options?.volume || 1;

        utterance.onstart = () => {
          this.isSpeaking = true;
          this.notifyListeners();
        };

        utterance.onend = () => {
          this.isSpeaking = false;
          this.currentUtterance = null;
          this.notifyListeners();
          options?.onEnd?.();
          resolve();
        };

        utterance.onerror = () => {
          this.isSpeaking = false;
          this.currentUtterance = null;
          this.notifyListeners();
          options?.onError?.();
          resolve(); // 不reject，避免未处理的错误
        };

        this.currentUtterance = utterance;
        this.isSpeaking = true;
        this.notifyListeners();
        window.speechSynthesis.speak(utterance);
      }, 100);
    });
  }

  // 获取当前是否正在播放
  public getIsSpeaking(): boolean {
    return this.isSpeaking;
  }

  // 添加状态监听器
  public addListener(callback: (speaking: boolean) => void): void {
    this.listeners.add(callback);
  }

  // 移除状态监听器
  public removeListener(callback: (speaking: boolean) => void): void {
    this.listeners.delete(callback);
  }

  // 通知所有监听器
  private notifyListeners(): void {
    this.listeners.forEach(callback => callback(this.isSpeaking));
  }
}

// 导出单例实例
export const speechManager = SpeechManager.getInstance();

// 便捷函数
export const stopAllSpeech = () => speechManager.stop();
export const speak = (text: string, options?: Parameters<typeof speechManager.speak>[1]) => 
  speechManager.speak(text, options);
export const isSpeaking = () => speechManager.getIsSpeaking();
