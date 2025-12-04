// ============================================================================
// 语音交互服务
// 集成 ASR-LLM-TTS 功能
// ============================================================================

const API_BASE_URL = import.meta.env.VITE_HEALTH_API_URL || 'http://localhost:5000';

// 可用的 TTS 语音
export interface VoiceOption {
  id: string;
  name: string;
}

// TTS 响应
export interface TTSResponse {
  success: boolean;
  data?: {
    audio_url: string;
    filename: string;
    audio_base64?: string;
  };
  error?: string;
}

// ASR 响应
export interface ASRResponse {
  success: boolean;
  data?: {
    text: string;
  };
  error?: string;
}

// 语音对话响应
export interface VoiceChatResponse {
  success: boolean;
  data?: {
    input_text: string;
    response_text: string;
    audio_url?: string;
  };
  error?: string;
}

/**
 * 获取可用的语音列表
 */
export async function getAvailableVoices(): Promise<VoiceOption[]> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/voice/voices`);
    const result = await response.json();
    
    if (result.success && result.data?.voices) {
      return result.data.voices;
    }
    return [];
  } catch (error) {
    console.error('获取语音列表失败:', error);
    return [];
  }
}

/**
 * 文本转语音
 * @param text 要转换的文本
 * @param voice 语音ID（可选）
 * @param includeBase64 是否返回 base64 编码的音频
 */
export async function textToSpeech(
  text: string, 
  voice?: string,
  includeBase64: boolean = false
): Promise<TTSResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/voice/tts`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        text,
        voice: voice || 'zh-CN-XiaoyiNeural',
        include_base64: includeBase64
      })
    });
    
    return await response.json();
  } catch (error) {
    console.error('TTS 请求失败:', error);
    return { success: false, error: '网络错误' };
  }
}

/**
 * 语音转文本
 * @param audioBlob 音频 Blob 数据
 */
export async function speechToText(audioBlob: Blob): Promise<ASRResponse> {
  try {
    const formData = new FormData();
    formData.append('audio', audioBlob, 'recording.wav');
    
    const response = await fetch(`${API_BASE_URL}/api/voice/asr`, {
      method: 'POST',
      body: formData
    });
    
    return await response.json();
  } catch (error) {
    console.error('ASR 请求失败:', error);
    return { success: false, error: '网络错误' };
  }
}

/**
 * 语音对话（ASR + LLM + TTS 一体化）
 * @param audioBlob 音频 Blob 数据
 * @param voice TTS 语音ID（可选）
 */
export async function voiceChat(
  audioBlob: Blob, 
  voice?: string
): Promise<VoiceChatResponse> {
  try {
    const formData = new FormData();
    formData.append('audio', audioBlob, 'recording.wav');
    if (voice) {
      formData.append('voice', voice);
    }
    
    const response = await fetch(`${API_BASE_URL}/api/voice/chat`, {
      method: 'POST',
      body: formData
    });
    
    return await response.json();
  } catch (error) {
    console.error('语音对话请求失败:', error);
    return { success: false, error: '网络错误' };
  }
}

/**
 * 播放音频 URL
 * @param audioUrl 音频 URL
 */
export function playAudio(audioUrl: string): Promise<void> {
  return new Promise((resolve, reject) => {
    const audio = new Audio(`${API_BASE_URL}${audioUrl}`);
    audio.onended = () => resolve();
    audio.onerror = (e) => reject(e);
    audio.play().catch(reject);
  });
}

/**
 * 播放 base64 编码的音频
 * @param base64Audio base64 编码的音频数据
 */
export function playBase64Audio(base64Audio: string): Promise<void> {
  return new Promise((resolve, reject) => {
    const audio = new Audio(`data:audio/mpeg;base64,${base64Audio}`);
    audio.onended = () => resolve();
    audio.onerror = (e) => reject(e);
    audio.play().catch(reject);
  });
}

/**
 * 录音工具类
 */
export class AudioRecorder {
  private mediaRecorder: MediaRecorder | null = null;
  private audioChunks: Blob[] = [];
  private stream: MediaStream | null = null;

  /**
   * 开始录音
   */
  async start(): Promise<void> {
    try {
      this.stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      this.mediaRecorder = new MediaRecorder(this.stream);
      this.audioChunks = [];

      this.mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          this.audioChunks.push(event.data);
        }
      };

      this.mediaRecorder.start();
      console.log('🎤 开始录音');
    } catch (error) {
      console.error('无法访问麦克风:', error);
      throw new Error('无法访问麦克风，请检查权限设置');
    }
  }

  /**
   * 停止录音并返回音频 Blob
   */
  stop(): Promise<Blob> {
    return new Promise((resolve, reject) => {
      if (!this.mediaRecorder) {
        reject(new Error('录音器未初始化'));
        return;
      }

      this.mediaRecorder.onstop = () => {
        const audioBlob = new Blob(this.audioChunks, { type: 'audio/wav' });
        console.log('🎤 录音结束，大小:', audioBlob.size);
        
        // 停止所有音轨
        if (this.stream) {
          this.stream.getTracks().forEach(track => track.stop());
        }
        
        resolve(audioBlob);
      };

      this.mediaRecorder.stop();
    });
  }

  /**
   * 检查是否正在录音
   */
  isRecording(): boolean {
    return this.mediaRecorder?.state === 'recording';
  }
}

// 导出单例录音器
export const audioRecorder = new AudioRecorder();

/**
 * 使用 Web Speech API 进行语音合成（浏览器内置，无需后端）
 * @param text 要朗读的文本
 * @param lang 语言代码
 */
export function speakWithWebSpeech(text: string, lang: string = 'zh-CN'): Promise<void> {
  return new Promise((resolve, reject) => {
    if (!('speechSynthesis' in window)) {
      reject(new Error('浏览器不支持语音合成'));
      return;
    }

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = lang;
    utterance.rate = 1.0;
    utterance.pitch = 1.0;
    
    utterance.onend = () => resolve();
    utterance.onerror = (e) => reject(e);
    
    window.speechSynthesis.speak(utterance);
  });
}
