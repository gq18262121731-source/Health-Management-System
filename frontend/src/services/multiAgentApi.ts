/**
 * 多智能体 API 服务
 * 
 * 调用后端多智能体系统，支持：
 * - 健康管家：日常健康问答、数据解读
 * - 慢病专家：高血压/糖尿病/血脂风险评估
 * - 生活教练：运动处方、饮食营养、睡眠改善
 * - 心理关怀师：情绪识别、心理疏导
 * 
 * 后端 API: POST /api/ai/consult
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface ConsultRequest {
  user_input: string;
  elderly_id?: string;
  use_knowledge_base?: boolean;
  save_history?: boolean;
}

export interface ConsultResponse {
  status: string;
  data: {
    query: string;
    response: string;
    user_role: string;
    health_data_used: boolean;
    knowledge_base_used: boolean;
  };
  message: string;
}

export interface AgentInfo {
  name: string;
  role: string;
  description: string;
  capabilities: string[];
}

/**
 * 调用后端多智能体 AI 咨询（公开接口，无需认证）
 * 
 * @param userInput 用户输入
 * @param userRole 用户角色 (elderly/children/community)
 * @returns AI 回复
 */
export async function consultMultiAgent(
  userInput: string,
  userRole: string = 'elderly'
): Promise<{ success: boolean; response: string; error?: string }> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/ai/consult/public`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        user_input: userInput,
        user_role: userRole,
      }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      return {
        success: false,
        response: '',
        error: errorData.detail || `请求失败: ${response.status}`,
      };
    }

    const data: ConsultResponse = await response.json();
    
    return {
      success: true,
      response: data.data.response,
    };
  } catch (error) {
    console.error('多智能体 API 调用失败:', error);
    return {
      success: false,
      response: '',
      error: error instanceof Error ? error.message : '网络错误',
    };
  }
}

/**
 * 流式调用多智能体 API（模拟流式，实际后端暂不支持流式）
 * 
 * @param userInput 用户输入
 * @param onMessage 消息回调（逐字显示）
 * @param onComplete 完成回调
 * @param onError 错误回调
 * @param userRole 用户角色
 */
export function consultMultiAgentStream(
  userInput: string,
  onMessage: (text: string) => void,
  onComplete: () => void,
  onError: (error: string) => void,
  userRole: string = 'elderly'
): () => void {
  let cancelled = false;

  consultMultiAgent(userInput, userRole)
    .then((result) => {
      if (cancelled) return;

      if (!result.success) {
        onError(result.error || '请求失败');
        return;
      }

      // 模拟流式输出（逐字显示）
      const text = result.response;
      let index = 0;
      const chunkSize = 3; // 每次显示3个字符

      const streamInterval = setInterval(() => {
        if (cancelled) {
          clearInterval(streamInterval);
          return;
        }

        index += chunkSize;
        if (index >= text.length) {
          onMessage(text);
          clearInterval(streamInterval);
          onComplete();
        } else {
          onMessage(text.substring(0, index));
        }
      }, 30); // 30ms 间隔
    })
    .catch((error) => {
      if (!cancelled) {
        onError(error.message || '请求失败');
      }
    });

  // 返回取消函数
  return () => {
    cancelled = true;
  };
}

/**
 * 获取多智能体系统信息
 */
export async function getAgentsInfo(): Promise<{
  success: boolean;
  agents: AgentInfo[];
  error?: string;
}> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/ai/agents`);
    
    if (!response.ok) {
      return { success: false, agents: [], error: `请求失败: ${response.status}` };
    }

    const data = await response.json();
    
    return {
      success: true,
      agents: data.data?.agents || [],
    };
  } catch (error) {
    console.error('获取智能体信息失败:', error);
    return {
      success: false,
      agents: [],
      error: error instanceof Error ? error.message : '网络错误',
    };
  }
}

/**
 * 检查 AI 服务健康状态
 */
export async function checkAIHealth(): Promise<{
  available: boolean;
  provider?: string;
  mode: 'real' | 'mock';
}> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/ai/health`);
    
    if (!response.ok) {
      return { available: false, mode: 'mock' };
    }

    const data = await response.json();
    
    return {
      available: data.data?.ai_service_available || false,
      provider: data.data?.provider,
      mode: data.data?.mode || 'mock',
    };
  } catch (error) {
    return { available: false, mode: 'mock' };
  }
}
