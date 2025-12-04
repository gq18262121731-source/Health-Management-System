/**
 * 健康评估系统 API 服务
 * 
 * 封装与 health_assessment_system 后端的通信
 * 包含健康评估、报告生成、多智能体对话等功能
 */

// API 基础配置
const API_BASE_URL = import.meta.env.VITE_HEALTH_API_URL || 'http://localhost:5000';

// ============================================================================
// 类型定义
// ============================================================================

/** 健康等级 */
export type HealthLevel = 'excellent' | 'good' | 'suboptimal' | 'attention' | 'high_risk';

/** 风险因素 */
export interface RiskFactor {
  name: string;
  score: number;
  priority: 'high' | 'medium' | 'low';
  category: 'disease' | 'lifestyle' | 'trend';
}

/** 维度评分 */
export interface DimensionScores {
  disease: number;
  lifestyle: number;
  trend: number;
}

/** 评估结果 */
export interface AssessmentResult {
  assessment_id: string;
  user_id: string;
  assessment_date: string;
  overall_score: number;
  health_level: HealthLevel;
  dimension_scores: DimensionScores;
  top_risk_factors: RiskFactor[];
  recommendations: string[];
}

/** 可视化数据 */
export interface VisualizationData {
  overview: {
    overall_score: number;
    health_level: HealthLevel;
    assessment_date: string;
  };
  dimension_scores: DimensionScores;
  risk_factors: RiskFactor[];
  trend_indicators: Array<{
    metric: string;
    direction: 'improving' | 'stable' | 'worsening';
    deviation: number;
  }>;
  risk_distribution: {
    high: number;
    medium: number;
    low: number;
  };
}

/** 评估历史记录 */
export interface AssessmentRecord {
  assessment_id: string;
  assessment_date: string;
  overall_score: number;
  health_level: HealthLevel;
}

/** 报告类型 */
export type ReportType = 'elderly' | 'family' | 'community';

/** 报告格式 */
export type ReportFormat = 'text' | 'json' | 'html';

/** 智能体对话响应 */
export interface AgentChatResponse {
  response: string;
  agent: string;
  emotion: string;
  suggestions: string[];
}

/** API 响应包装 */
interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
}

// ============================================================================
// API 请求封装
// ============================================================================

async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<ApiResponse<T>> {
  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    });

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('API请求失败:', error);
    return {
      success: false,
      error: error instanceof Error ? error.message : '网络请求失败',
    };
  }
}

// ============================================================================
// 健康评估 API
// ============================================================================

/**
 * 运行健康评估
 * @param userId 用户ID
 * @param options 评估选项
 */
export async function runAssessment(
  userId: string,
  options: {
    assessmentType?: 'scheduled' | 'on_demand';
    triggeredBy?: 'family' | 'community' | 'self';
    customDays?: number;
  } = {}
): Promise<ApiResponse<AssessmentResult>> {
  return apiRequest<AssessmentResult>('/api/health/assess', {
    method: 'POST',
    body: JSON.stringify({
      user_id: userId,
      assessment_type: options.assessmentType || 'on_demand',
      triggered_by: options.triggeredBy || 'self',
      custom_days: options.customDays || 30,
    }),
  });
}

/**
 * 生成健康报告
 * @param userId 用户ID
 * @param options 报告选项
 */
export async function generateReport(
  userId: string,
  options: {
    assessmentId?: string;
    reportType?: ReportType;
    reportFormat?: ReportFormat;
  } = {}
): Promise<ApiResponse<{ report_type: string; content: string; generated_at: string }>> {
  return apiRequest('/api/health/report', {
    method: 'POST',
    body: JSON.stringify({
      user_id: userId,
      assessment_id: options.assessmentId,
      report_type: options.reportType || 'elderly',
      report_format: options.reportFormat || 'json',
    }),
  });
}

/**
 * 获取可视化数据
 * @param userId 用户ID
 * @param assessmentId 评估ID（可选）
 */
export async function getVisualizationData(
  userId: string,
  assessmentId?: string
): Promise<ApiResponse<VisualizationData>> {
  const params = new URLSearchParams({ user_id: userId });
  if (assessmentId) {
    params.append('assessment_id', assessmentId);
  }
  return apiRequest<VisualizationData>(`/api/health/visualization?${params}`);
}

/**
 * 获取评估历史
 * @param userId 用户ID
 * @param limit 返回数量限制
 */
export async function getAssessmentHistory(
  userId: string,
  limit: number = 10
): Promise<ApiResponse<{ records: AssessmentRecord[] }>> {
  const params = new URLSearchParams({
    user_id: userId,
    limit: limit.toString(),
  });
  return apiRequest(`/api/health/history?${params}`);
}

// ============================================================================
// 多智能体对话 API
// ============================================================================

/**
 * 与智能体对话
 * @param userId 用户ID
 * @param message 消息内容
 * @param userName 用户姓名（可选）
 */
export async function chatWithAgent(
  userId: string,
  message: string,
  userName?: string
): Promise<ApiResponse<AgentChatResponse>> {
  return apiRequest<AgentChatResponse>('/api/agent/chat', {
    method: 'POST',
    body: JSON.stringify({
      user_id: userId,
      user_name: userName || '',
      message,
    }),
  });
}

/**
 * 获取智能体问候语
 * @param userId 用户ID
 * @param userName 用户姓名
 */
export async function getAgentGreeting(
  userId: string,
  userName?: string
): Promise<ApiResponse<{ greeting: string }>> {
  const params = new URLSearchParams({ user_id: userId });
  if (userName) {
    params.append('user_name', userName);
  }
  return apiRequest(`/api/agent/greeting?${params}`);
}

/**
 * 获取会话信息
 * @param userId 用户ID
 */
export async function getSessionInfo(
  userId: string
): Promise<ApiResponse<{
  session_start: string;
  message_count: number;
  current_agent: string;
  user_profile: Record<string, unknown>;
}>> {
  return apiRequest(`/api/agent/session?user_id=${userId}`);
}

/**
 * 清空对话历史
 * @param userId 用户ID
 */
export async function clearConversation(userId: string): Promise<ApiResponse<{ message: string }>> {
  return apiRequest('/api/agent/clear', {
    method: 'POST',
    body: JSON.stringify({ user_id: userId }),
  });
}

// ============================================================================
// 健康等级工具函数
// ============================================================================

/** 健康等级中文映射 */
export const healthLevelLabels: Record<HealthLevel, string> = {
  excellent: '优秀',
  good: '良好',
  suboptimal: '亚健康',
  attention: '需关注',
  high_risk: '高风险',
};

/** 健康等级颜色映射 */
export const healthLevelColors: Record<HealthLevel, string> = {
  excellent: 'text-green-600 bg-green-50 border-green-200',
  good: 'text-blue-600 bg-blue-50 border-blue-200',
  suboptimal: 'text-yellow-600 bg-yellow-50 border-yellow-200',
  attention: 'text-orange-600 bg-orange-50 border-orange-200',
  high_risk: 'text-red-600 bg-red-50 border-red-200',
};

/** 获取健康等级标签 */
export function getHealthLevelLabel(level: HealthLevel): string {
  return healthLevelLabels[level] || level;
}

/** 获取健康等级颜色类名 */
export function getHealthLevelColor(level: HealthLevel): string {
  return healthLevelColors[level] || '';
}

/** 根据分数获取健康等级 */
export function getHealthLevelFromScore(score: number): HealthLevel {
  if (score >= 85) return 'excellent';
  if (score >= 70) return 'good';
  if (score >= 55) return 'suboptimal';
  if (score >= 40) return 'attention';
  return 'high_risk';
}
