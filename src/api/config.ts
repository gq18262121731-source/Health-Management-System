/**
 * ===========================================================================
 * API 配置文件
 * 
 * 功能：
 * 1. 环境配置（开发/生产）
 * 2. API 端点常量定义
 * 3. 统一管理所有 API 路径
 * ===========================================================================
 */

/**
 * API 基础配置
 */
export const API_CONFIG = {
  // 开发环境配置
  development: {
    baseURL: 'http://localhost:3000/api/v1',
    timeout: 10000,
  },
  // 生产环境配置
  production: {
    baseURL: 'https://api.smart-health.com/api/v1',
    timeout: 15000,
  },
  // 当前环境配置（自动选择）
  get baseURL() {
    return import.meta.env.PROD 
      ? this.production.baseURL 
      : this.development.baseURL;
  },
  get timeout() {
    return import.meta.env.PROD 
      ? this.production.timeout 
      : this.development.timeout;
  },
};

/**
 * API 端点常量
 * 
 * 组织方式：按角色和模块分类
 * 命名规范：大写下划线分隔
 */
export const API_ENDPOINTS = {
  // ============================================================================
  // 老人端 API
  // ============================================================================
  ELDERLY: {
    // 健康数据
    HEALTH_TODAY: '/elderly/health/today',
    HEALTH_CHARTS: '/elderly/health/charts',
    
    // 图表数据
    CHARTS_HEARTRATE: '/elderly/health/charts/heartrate',
    CHARTS_SLEEP: '/elderly/health/charts/sleep',
    CHARTS_BLOODPRESSURE: '/elderly/health/charts/bloodpressure',
    CHARTS_RADAR: '/elderly/health/charts/radar',
    
    // 报告
    REPORTS_CURRENT: '/elderly/reports/current',
    REPORTS_HISTORY: '/elderly/reports/history',
    REPORT_DETAIL: (id: string) => `/elderly/reports/${id}`,
    REPORT_PDF: (id: string) => `/elderly/reports/${id}/pdf`,
    
    // 心理健康
    PSYCHOLOGY_MOOD: '/elderly/psychology/mood',
    PSYCHOLOGY_MOOD_HISTORY: '/elderly/psychology/mood/history',
    PSYCHOLOGY_STRESS: '/elderly/psychology/stress',
    PSYCHOLOGY_RELAXATION_START: '/elderly/psychology/relaxation/start',
    PSYCHOLOGY_RELAXATION_COMPLETE: '/elderly/psychology/relaxation/complete',
    
    // AI 功能
    AI_CHAT: '/elderly/ai/chat',
    AI_ANALYZE: '/elderly/ai/analyze',
    AI_HISTORY: '/elderly/ai/history',
  },

  // ============================================================================
  // 子女端 API
  // ============================================================================
  CHILDREN: {
    // 老人管理
    ELDERS_LIST: '/children/elders/list',
    ELDER_DETAIL: (id: string) => `/children/elders/${id}/detail`,
    ELDER_HEALTH: (id: string) => `/children/elders/${id}/health`,
    
    // 实时监测
    MONITOR_REALTIME: (id: string) => `/children/monitor/${id}/realtime`,
    
    // 提醒管理
    REMINDERS_LIST: '/children/reminders/list',
    REMINDERS_CREATE: '/children/reminders/create',
    REMINDER_UPDATE: (id: string) => `/children/reminders/${id}/status`,
    REMINDER_DELETE: (id: string) => `/children/reminders/${id}`,
    
    // AI 助手
    AI_CHAT: '/children/ai/chat',
  },

  // ============================================================================
  // 社区端 API
  // ============================================================================
  COMMUNITY: {
    // 仪表板数据
    DASHBOARD_OVERVIEW: '/community/dashboard/overview',
    DASHBOARD_AGE_DISTRIBUTION: '/community/dashboard/age-distribution',
    DASHBOARD_HEALTH_TRENDS: '/community/dashboard/health-trends',
    DASHBOARD_DEVICES: '/community/dashboard/devices',
    DASHBOARD_SERVICES: '/community/dashboard/services',
    
    // 地图数据
    MAP_CONFIG: '/community/map/config',
    MAP_LOCATIONS: '/community/map/elders/locations',
    MAP_ALERTS: '/community/map/alerts',
    
    // 告警管理
    ALERTS_LIST: '/community/alerts/list',
    ALERTS_STATISTICS: '/community/alerts/statistics',
    ALERT_HANDLE: (id: string) => `/community/alerts/${id}/handle`,
    
    // 数据分析
    ANALYTICS_HEALTH: '/community/analytics/health',
    ANALYTICS_TRENDS: '/community/analytics/trends',
  },

  // ============================================================================
  // 认证 API
  // ============================================================================
  AUTH: {
    // 登录
    LOGIN: '/auth/login',
    LOGOUT: '/auth/logout',
    REFRESH_TOKEN: '/auth/refresh',
    
    // 个人信息
    PROFILE: (role: string) => `/${role}/profile`,
    PROFILE_UPDATE: (role: string) => `/${role}/profile`,
    AVATAR_UPLOAD: (role: string) => `/${role}/avatar/upload`,
    
    // 通知
    NOTIFICATIONS_UNREAD: (role: string) => `/${role}/notifications/unread`,
  },
};

/**
 * 查询参数类型定义
 */
export interface QueryParams {
  page?: number;
  pageSize?: number;
  period?: 'day' | 'week' | 'month' | 'year';
  type?: string;
  status?: string;
  sort?: string;
  order?: 'asc' | 'desc';
}

/**
 * 构建带查询参数的 URL
 * @param endpoint - API 端点
 * @param params - 查询参数
 * @returns 完整的 URL
 */
export function buildURL(endpoint: string, params?: QueryParams): string {
  if (!params) return endpoint;
  
  const queryString = Object.entries(params)
    .filter(([_, value]) => value !== undefined && value !== null)
    .map(([key, value]) => `${key}=${encodeURIComponent(value)}`)
    .join('&');
  
  return queryString ? `${endpoint}?${queryString}` : endpoint;
}
