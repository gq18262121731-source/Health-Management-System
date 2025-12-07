// 讯飞星火 API 服务
// 文档: https://www.xfyun.cn/doc/spark/Web.html
// 
// ============================================================================
// 核心技术：上下文注入（Context Injection）
// ============================================================================
// 将用户实时生理指标、健康评估结果动态融入 LLM 系统提示，
// 实现个性化问诊建议，随用户数据变化实时调整。
// ============================================================================

import CryptoJS from 'crypto-js';
import { getTodayHealthData, TodayHealthData } from './healthDataApi';

const SPARK_CONFIG = {
  APPID: '136dab64',
  API_SECRET: 'NDFlZjcyMTRhMjUzMjk3ZDQwM2I5ZGE3',
  API_KEY: '0c1dc672ab3c5cdad820eae1aa22841c',
  // 星火大模型版本 (可选: v1.5, v2.0, v3.0, v3.5, v4.0)
  VERSION: 'v3.5',
};

// 根据版本获取对应的 URL 和 domain
function getSparkUrl(version: string) {
  const versionMap: Record<string, { url: string; domain: string }> = {
    'v1.5': { url: 'wss://spark-api.xf-yun.com/v1.1/chat', domain: 'general' },
    'v2.0': { url: 'wss://spark-api.xf-yun.com/v2.1/chat', domain: 'generalv2' },
    'v3.0': { url: 'wss://spark-api.xf-yun.com/v3.1/chat', domain: 'generalv3' },
    'v3.5': { url: 'wss://spark-api.xf-yun.com/v3.5/chat', domain: 'generalv3.5' },
    'v4.0': { url: 'wss://spark-api.xf-yun.com/v4.0/chat', domain: '4.0Ultra' },
  };
  return versionMap[version] || versionMap['v3.5'];
}

// 生成鉴权 URL
function getAuthUrl(): string {
  const { url } = getSparkUrl(SPARK_CONFIG.VERSION);
  const host = new URL(url).host;
  const path = new URL(url).pathname;
  const date = new Date().toUTCString();

  const signatureOrigin = `host: ${host}\ndate: ${date}\nGET ${path} HTTP/1.1`;
  const signatureSha = CryptoJS.HmacSHA256(signatureOrigin, SPARK_CONFIG.API_SECRET);
  const signature = CryptoJS.enc.Base64.stringify(signatureSha);

  const authorizationOrigin = `api_key="${SPARK_CONFIG.API_KEY}", algorithm="hmac-sha256", headers="host date request-line", signature="${signature}"`;
  const authorization = btoa(authorizationOrigin);

  return `${url}?authorization=${authorization}&date=${encodeURIComponent(date)}&host=${host}`;
}

// ============================================================================
// 上下文注入：用户健康数据缓存
// ============================================================================
let cachedHealthData: TodayHealthData | null = null;
let lastFetchTime = 0;
const CACHE_DURATION = 60000; // 1分钟缓存

// 获取用户健康数据（带缓存）
async function fetchUserHealthData(userId: string): Promise<TodayHealthData | null> {
  const now = Date.now();
  if (cachedHealthData && now - lastFetchTime < CACHE_DURATION) {
    return cachedHealthData;
  }
  
  try {
    const result = await getTodayHealthData(userId);
    if (result.success && result.data) {
      cachedHealthData = result.data;
      lastFetchTime = now;
      return cachedHealthData;
    }
  } catch (error) {
    console.error('获取健康数据失败:', error);
  }
  return null;
}

// ============================================================================
// RAG 知识检索（从后端获取相关医学知识）
// ============================================================================
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface RAGResult {
  context: string;
  results: Array<{
    id: string;
    title: string;
    content: string;
    category: string;
    score: number;
  }>;
}

// RAG 知识检索缓存
let ragCache: Map<string, { data: RAGResult; timestamp: number }> = new Map();
const RAG_CACHE_DURATION = 300000; // 5分钟缓存

async function fetchRAGContext(query: string): Promise<RAGResult | null> {
  // 检查缓存
  const cached = ragCache.get(query);
  if (cached && Date.now() - cached.timestamp < RAG_CACHE_DURATION) {
    console.log('✅ RAG 缓存命中');
    return cached.data;
  }

  try {
    const response = await fetch(`${API_BASE_URL}/api/rag/search`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query, top_k: 3 })
    });
    
    const result = await response.json();
    if (result.success && result.data) {
      // 存入缓存
      ragCache.set(query, { data: result.data, timestamp: Date.now() });
      console.log(`✅ RAG 检索成功: ${result.data.results?.length || 0} 条相关知识`);
      return result.data;
    }
  } catch (error) {
    console.error('RAG 检索失败:', error);
  }
  return null;
}

// ============================================================================
// 动态系统提示词生成（核心：上下文注入 + RAG 增强）
// ============================================================================
function generateDynamicSystemPrompt(
  healthData: TodayHealthData | null,
  ragContext?: string
): string {
  // 基础系统提示词
  let prompt = `你是一个专业的AI健康助手，专门为老年人提供健康咨询服务。

你的职责：
1. 根据用户描述的症状，提供专业但易懂的健康建议
2. 分析用户的健康数据（血压、心率、血糖、睡眠等），给出个性化建议
3. 判断症状的紧急程度，必要时建议就医
4. 提供日常保健、饮食、运动等方面的指导
5. 用温和、关怀的语气与老年用户交流

注意事项：
- 使用简单易懂的语言，避免专业术语
- 回答要有条理，使用数字列表
- 对于严重症状，务必建议及时就医
- 不要做出明确的诊断，只提供参考建议
- 回答要简洁，控制在200字以内`;

  // ============================================================================
  // 上下文注入：将用户实时健康数据融入系统提示
  // ============================================================================
  if (healthData) {
    const vs = healthData.vitalSigns;
    const activity = healthData.activity;
    const weight = healthData.weight;
    
    // 判断各项指标状态
    const bpStatus = vs.bloodPressure.systolic > 140 || vs.bloodPressure.diastolic > 90 
      ? '偏高' : vs.bloodPressure.systolic < 90 ? '偏低' : '正常';
    const hrStatus = vs.heartRate.value > 100 ? '偏快' : vs.heartRate.value < 60 ? '偏慢' : '正常';
    const bsStatus = vs.bloodSugar.value > 7.0 ? '偏高' : vs.bloodSugar.value < 3.9 ? '偏低' : '正常';
    const activityStatus = activity.steps < 3000 ? '运动不足' : activity.steps > 8000 ? '运动充足' : '运动适中';
    
    prompt += `

============================================================================
【用户实时健康数据 - 上下文注入】
============================================================================
当前用户：${healthData.userName || '用户'}
数据更新时间：${new Date().toLocaleString('zh-CN')}

【生命体征】
- 血压：${vs.bloodPressure.systolic}/${vs.bloodPressure.diastolic} mmHg（${bpStatus}）
- 心率：${vs.heartRate.value} bpm（${hrStatus}）
- 血糖：${vs.bloodSugar.value} mmol/L（${bsStatus}）
- 体温：${vs.temperature.value}°C
- 血氧：${vs.spo2?.value || 98}%

【活动数据】
- 今日步数：${activity.steps.toLocaleString()} 步（${activityStatus}）
- 目标完成：${activity.percentage.toFixed(1)}%
- 消耗热量：约 ${activity.calories} 千卡

【体重管理】
- 体重：${weight.value} kg
- BMI：${weight.bmi}（${weight.bmiStatus}）

【健康提醒】
${bpStatus !== '正常' ? '⚠️ 血压' + bpStatus + '，需要关注\n' : ''}${hrStatus !== '正常' ? '⚠️ 心率' + hrStatus + '，建议观察\n' : ''}${bsStatus !== '正常' ? '⚠️ 血糖' + bsStatus + '，注意饮食\n' : ''}${activityStatus === '运动不足' ? '⚠️ 今日运动量不足，建议适当活动\n' : ''}
请根据以上用户健康数据，提供更加个性化、精准的健康建议。
============================================================================`;
  }

  // ============================================================================
  // RAG 增强：注入检索到的医学知识
  // ============================================================================
  if (ragContext) {
    prompt += `

============================================================================
【RAG 医学知识检索结果】
============================================================================
${ragContext}

请参考以上医学知识，结合用户的具体情况，提供专业、准确的健康建议。
回答时可以引用相关知识来源，增强回答的权威性。
============================================================================`;
  }

  return prompt;
}

// 静态系统提示词（备用，无健康数据时使用）
const HEALTH_SYSTEM_PROMPT = `你是一个专业的AI健康助手，专门为老年人提供健康咨询服务。

你的职责：
1. 根据用户描述的症状，提供专业但易懂的健康建议
2. 分析用户的健康数据（血压、心率、血糖、睡眠等），给出个性化建议
3. 判断症状的紧急程度，必要时建议就医
4. 提供日常保健、饮食、运动等方面的指导
5. 用温和、关怀的语气与老年用户交流

注意事项：
- 使用简单易懂的语言，避免专业术语
- 回答要有条理，使用数字列表
- 对于严重症状，务必建议及时就医
- 不要做出明确的诊断，只提供参考建议
- 回答要简洁，控制在200字以内`;

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

// 用户ID（用于获取健康数据）
let currentUserId = 'elderly_001';

// 设置当前用户ID
export function setCurrentUserId(userId: string) {
  currentUserId = userId;
  // 清除缓存，下次会重新获取
  cachedHealthData = null;
  lastFetchTime = 0;
}

// ============================================================================
// 发送消息到讯飞星火（带上下文注入 + RAG 增强）
// ============================================================================
export function sendToSpark(
  messages: ChatMessage[],
  onMessage: (text: string) => void,
  onComplete: () => void,
  onError: (error: string) => void
): () => void {
  const authUrl = getAuthUrl();
  const { domain } = getSparkUrl(SPARK_CONFIG.VERSION);
  
  let ws: WebSocket | null = null;
  let fullResponse = '';

  // 获取用户最后一条消息用于 RAG 检索
  const lastUserMessage = messages.filter(m => m.role === 'user').pop()?.content || '';

  // 并行获取健康数据和 RAG 知识
  Promise.all([
    fetchUserHealthData(currentUserId),
    fetchRAGContext(lastUserMessage)
  ]).then(([healthData, ragResult]) => {
    // 生成动态系统提示词（核心：上下文注入 + RAG 增强）
    const ragContext = ragResult?.context || '';
    const dynamicPrompt = generateDynamicSystemPrompt(healthData, ragContext);
    
    // 日志输出
    if (healthData) {
      console.log('✅ 上下文注入成功：已将用户健康数据融入系统提示');
    }
    if (ragResult && ragResult.results?.length > 0) {
      console.log(`✅ RAG 增强成功：检索到 ${ragResult.results.length} 条相关医学知识`);
      ragResult.results.forEach((r, i) => {
        console.log(`   ${i + 1}. [${r.category}] ${r.title} (相似度: ${r.score.toFixed(3)})`);
      });
    } else {
      console.log('⚠️ RAG 增强：未找到相关知识');
    }

    try {
      ws = new WebSocket(authUrl);

      ws.onopen = () => {
        const requestData = {
          header: {
            app_id: SPARK_CONFIG.APPID,
            uid: currentUserId,
          },
          parameter: {
            chat: {
              domain: domain,
              temperature: 0.7,
              max_tokens: 1024,
              top_k: 4,
            },
          },
          payload: {
            message: {
              text: [
                // 使用动态生成的系统提示词（包含用户健康数据 + RAG 知识）
                { role: 'system', content: dynamicPrompt },
                ...messages.map(m => ({ role: m.role, content: m.content })),
              ],
            },
          },
        };
        ws?.send(JSON.stringify(requestData));
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          
          if (data.header.code !== 0) {
            onError(`API错误: ${data.header.message}`);
            ws?.close();
            return;
          }

          const content = data.payload?.choices?.text?.[0]?.content || '';
          fullResponse += content;
          onMessage(fullResponse);

          // status: 0-首次, 1-中间, 2-最后
          if (data.header.status === 2) {
            onComplete();
            ws?.close();
          }
        } catch (e) {
          onError('解析响应失败');
        }
      };

      ws.onerror = () => {
        onError('WebSocket连接失败，请检查网络');
      };

      ws.onclose = () => {
        // 连接关闭
      };
    } catch (error) {
      onError('创建连接失败');
    }
  }).catch((error) => {
    console.error('初始化失败:', error);
    // 即使获取健康数据失败，也尝试继续对话（使用默认提示词）
    try {
      const authUrlFallback = getAuthUrl();
      const { domain: domainFallback } = getSparkUrl(SPARK_CONFIG.VERSION);
      
      ws = new WebSocket(authUrlFallback);
      
      ws.onopen = () => {
        const requestData = {
          header: {
            app_id: SPARK_CONFIG.APPID,
            uid: currentUserId,
          },
          parameter: {
            chat: {
              domain: domainFallback,
              temperature: 0.7,
              max_tokens: 1024,
              top_k: 4,
            },
          },
          payload: {
            message: {
              text: [
                { role: 'system', content: HEALTH_SYSTEM_PROMPT },
                ...messages.map(m => ({ role: m.role, content: m.content })),
              ],
            },
          },
        };
        ws?.send(JSON.stringify(requestData));
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          
          if (data.header.code !== 0) {
            onError(`API错误: ${data.header.message}`);
            ws?.close();
            return;
          }

          const content = data.payload?.choices?.text?.[0]?.content || '';
          fullResponse += content;
          onMessage(fullResponse);

          if (data.header.status === 2) {
            onComplete();
            ws?.close();
          }
        } catch (e) {
          onError('解析响应失败');
        }
      };

      ws.onerror = () => {
        onError('WebSocket连接失败，请检查网络');
      };
    } catch (fallbackError) {
      onError('连接失败，请稍后重试');
    }
  });

  // 返回取消函数
  return () => {
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.close();
    }
  };
}

// ============================================================================
// 带上下文注入的增强版发送函数（支持自定义健康数据）
// ============================================================================
export function sendToSparkWithContext(
  messages: ChatMessage[],
  healthData: TodayHealthData | null,
  onMessage: (text: string) => void,
  onComplete: () => void,
  onError: (error: string) => void
): () => void {
  const authUrl = getAuthUrl();
  const { domain } = getSparkUrl(SPARK_CONFIG.VERSION);
  
  // 生成动态系统提示词
  const dynamicPrompt = generateDynamicSystemPrompt(healthData);
  
  let ws: WebSocket | null = null;
  let fullResponse = '';

  try {
    ws = new WebSocket(authUrl);

    ws.onopen = () => {
      const requestData = {
        header: {
          app_id: SPARK_CONFIG.APPID,
          uid: currentUserId,
        },
        parameter: {
          chat: {
            domain: domain,
            temperature: 0.7,
            max_tokens: 1024,
            top_k: 4,
          },
        },
        payload: {
          message: {
            text: [
              { role: 'system', content: dynamicPrompt },
              ...messages.map(m => ({ role: m.role, content: m.content })),
            ],
          },
        },
      };
      ws?.send(JSON.stringify(requestData));
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        
        if (data.header.code !== 0) {
          onError(`API错误: ${data.header.message}`);
          ws?.close();
          return;
        }

        const content = data.payload?.choices?.text?.[0]?.content || '';
        fullResponse += content;
        onMessage(fullResponse);

        if (data.header.status === 2) {
          onComplete();
          ws?.close();
        }
      } catch (e) {
        onError('解析响应失败');
      }
    };

    ws.onerror = () => {
      onError('WebSocket连接失败，请检查网络');
    };

    ws.onclose = () => {};
  } catch (error) {
    onError('创建连接失败');
  }

  return () => {
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.close();
    }
  };
}
