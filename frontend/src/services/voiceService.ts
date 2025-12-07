/**
 * 语音服务 - 封装后端 ASR/TTS API
 * 
 * ASR: SenseVoice (后端)
 * TTS: Edge-TTS (后端)
 */

const API_BASE = 'http://localhost:8000/api/v1';

// 获取 token
function getAuthToken(): string | null {
  return localStorage.getItem('token');
}

// 获取请求头
function getHeaders(): HeadersInit {
  const token = getAuthToken();
  return {
    'Authorization': token ? `Bearer ${token}` : '',
  };
}

/**
 * 可用的语音类型
 */
export const VOICE_OPTIONS = [
  { id: 'xiaoxiao', name: '晓晓', gender: '女', style: '温柔亲切（推荐）' },
  { id: 'xiaoyi', name: '晓伊', gender: '女', style: '活泼开朗' },
  { id: 'yunjian', name: '云健', gender: '男', style: '稳重大气' },
  { id: 'yunxi', name: '云希', gender: '男', style: '年轻活力' },
  { id: 'yunxia', name: '云夏', gender: '女', style: '童声可爱' },
  { id: 'yunyang', name: '云扬', gender: '男', style: '新闻播报' },
];

/**
 * TTS 请求参数
 */
export interface TTSRequest {
  text: string;
  voice?: string;   // 默认 xiaoxiao
  rate?: string;    // 语速 -50% ~ +50%，默认 -10%（适合老人）
  volume?: string;  // 音量 -50% ~ +50%，默认 +10%
}

/**
 * TTS 响应
 */
export interface TTSResponse {
  status: string;
  audio_id: string;
  audio_url: string;
  message: string;
}

/**
 * ASR 响应
 */
export interface ASRResponse {
  status: string;
  text: string;
  filename: string;
  language: string;
  message: string;
}

/**
 * 文本转语音 (TTS)
 * 
 * @param request TTS 请求参数
 * @returns 音频 URL
 */
export async function textToSpeech(request: TTSRequest): Promise<string> {
  try {
    const response = await fetch(`${API_BASE}/voice/tts`, {
      method: 'POST',
      headers: {
        ...getHeaders(),
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        text: request.text,
        voice: request.voice || 'xiaoxiao',
        rate: request.rate || '+0%',
        volume: request.volume || '+10%',
      }),
    });

    if (!response.ok) {
      throw new Error(`TTS 请求失败: ${response.status}`);
    }

    const data: TTSResponse = await response.json();
    
    // 返回完整的音频 URL
    return `${API_BASE}${data.audio_url}`;
  } catch (error) {
    console.error('TTS 错误:', error);
    throw error;
  }
}

/**
 * 语音转文本 (ASR)
 * 
 * @param audioBlob 音频数据
 * @param language 语言代码 (zh/en)
 * @returns 识别的文本
 */
export async function speechToText(audioBlob: Blob, language: string = 'zh'): Promise<string> {
  try {
    const formData = new FormData();
    formData.append('audio', audioBlob, 'recording.webm');
    formData.append('language', language);

    const response = await fetch(`${API_BASE}/voice/asr?language=${language}`, {
      method: 'POST',
      headers: getHeaders(),
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `ASR 请求失败: ${response.status}`);
    }

    const data: ASRResponse = await response.json();
    return data.text;
  } catch (error) {
    console.error('ASR 错误:', error);
    throw error;
  }
}

/**
 * 检查 ASR 服务状态
 */
export async function checkASRStatus(): Promise<boolean> {
  try {
    const response = await fetch(`${API_BASE}/voice/asr/status`);
    const data = await response.json();
    return data.asr_available;
  } catch {
    return false;
  }
}

/**
 * 播放音频
 * 
 * @param audioUrl 音频 URL
 * @returns Audio 元素
 */
export function playAudio(audioUrl: string): HTMLAudioElement {
  const audio = new Audio(audioUrl);
  audio.play();
  return audio;
}

/**
 * 录音类 - 使用 MediaRecorder API
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
      this.mediaRecorder = new MediaRecorder(this.stream, {
        mimeType: 'audio/webm;codecs=opus'
      });
      this.audioChunks = [];

      this.mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          this.audioChunks.push(event.data);
        }
      };

      this.mediaRecorder.start(100); // 每 100ms 收集一次数据
      console.log('🎤 开始录音');
    } catch (error) {
      console.error('录音启动失败:', error);
      throw new Error('无法访问麦克风，请检查权限设置');
    }
  }

  /**
   * 停止录音并返回音频数据
   */
  stop(): Promise<Blob> {
    return new Promise((resolve, reject) => {
      if (!this.mediaRecorder) {
        reject(new Error('录音器未初始化'));
        return;
      }

      this.mediaRecorder.onstop = () => {
        const audioBlob = new Blob(this.audioChunks, { type: 'audio/webm' });
        console.log('🎤 录音结束，大小:', audioBlob.size);
        
        // 停止所有音轨
        if (this.stream) {
          this.stream.getTracks().forEach(track => track.stop());
        }
        
        resolve(audioBlob);
      };

      this.mediaRecorder.onerror = (event) => {
        reject(new Error('录音错误'));
      };

      this.mediaRecorder.stop();
    });
  }

  /**
   * 取消录音
   */
  cancel(): void {
    if (this.mediaRecorder && this.mediaRecorder.state !== 'inactive') {
      this.mediaRecorder.stop();
    }
    if (this.stream) {
      this.stream.getTracks().forEach(track => track.stop());
    }
    this.audioChunks = [];
  }
}
