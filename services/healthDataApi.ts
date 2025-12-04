/**
 * 健康数据 API 服务
 * 
 * 从后端获取实时健康数据，替代前端静态数据
 */

const API_BASE_URL = import.meta.env.VITE_HEALTH_API_URL || 'http://localhost:5000';

// ============================================================================
// 类型定义
// ============================================================================

/** 心率数据点 */
export interface HeartRateDataPoint {
  time: string;
  value: number;
}

/** 睡眠数据点 */
export interface SleepDataPoint {
  day: string;
  deepSleep: number;
  lightSleep: number;
  quality: number;
}

/** 血压数据点 */
export interface BloodPressureDataPoint {
  day: string;
  systolic: number;
  diastolic: number;
  normalHigh: number;
  normalLow: number;
}

/** 健康雷达数据 */
export interface HealthRadarDataPoint {
  subject: string;
  score: number;
  lastMonth: number;
  fullMark: number;
}

/** 今日健康数据 */
export interface TodayHealthData {
  userId: string;
  userName: string;
  vitalSigns: {
    temperature: { value: number; unit: string; change: number; status: string };
    bloodSugar: { value: number; unit: string; status: string; testType: string };
    bloodPressure: { systolic: number; diastolic: number; unit: string; status: string };
    heartRate: { value: number; unit: string; change: number; status: string };
    spo2: { value: number; unit: string; status: string };
  };
  activity: {
    steps: number;
    goal: number;
    percentage: number;
    distance: number;
    calories: number;
  };
  weight: {
    value: number;
    unit: string;
    bmi: number;
    bmiStatus: string;
  };
}

/** 图表数据响应 */
export interface ChartDataResponse {
  heartRate: HeartRateDataPoint[];
  sleep: SleepDataPoint[];
  bloodPressure: BloodPressureDataPoint[];
  healthRadar: HealthRadarDataPoint[];
}

// ============================================================================
// API 函数
// ============================================================================

/**
 * 获取今日健康数据
 */
export async function getTodayHealthData(userId: string): Promise<{ success: boolean; data?: TodayHealthData; error?: string }> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/health/today?user_id=${userId}`);
    const result = await response.json();
    return result;
  } catch (error) {
    console.error('获取今日健康数据失败:', error);
    return { success: false, error: '网络错误' };
  }
}

/**
 * 获取图表数据（心率、睡眠、血压、雷达图）
 */
export async function getChartData(userId: string, days: number = 7): Promise<{ success: boolean; data?: ChartDataResponse; error?: string }> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/health/charts?user_id=${userId}&days=${days}`);
    const result = await response.json();
    return result;
  } catch (error) {
    console.error('获取图表数据失败:', error);
    return { success: false, error: '网络错误' };
  }
}

/**
 * 获取心率历史数据
 */
export async function getHeartRateHistory(userId: string, hours: number = 24): Promise<{ success: boolean; data?: HeartRateDataPoint[]; error?: string }> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/health/heart-rate?user_id=${userId}&hours=${hours}`);
    const result = await response.json();
    return result;
  } catch (error) {
    console.error('获取心率数据失败:', error);
    return { success: false, error: '网络错误' };
  }
}

/**
 * 获取睡眠历史数据
 */
export async function getSleepHistory(userId: string, days: number = 7): Promise<{ success: boolean; data?: SleepDataPoint[]; error?: string }> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/health/sleep?user_id=${userId}&days=${days}`);
    const result = await response.json();
    return result;
  } catch (error) {
    console.error('获取睡眠数据失败:', error);
    return { success: false, error: '网络错误' };
  }
}

/**
 * 获取血压历史数据
 */
export async function getBloodPressureHistory(userId: string, days: number = 7): Promise<{ success: boolean; data?: BloodPressureDataPoint[]; error?: string }> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/health/blood-pressure?user_id=${userId}&days=${days}`);
    const result = await response.json();
    return result;
  } catch (error) {
    console.error('获取血压数据失败:', error);
    return { success: false, error: '网络错误' };
  }
}

/**
 * 获取健康雷达图数据
 */
export async function getHealthRadarData(userId: string): Promise<{ success: boolean; data?: HealthRadarDataPoint[]; error?: string }> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/health/radar?user_id=${userId}`);
    const result = await response.json();
    return result;
  } catch (error) {
    console.error('获取雷达图数据失败:', error);
    return { success: false, error: '网络错误' };
  }
}
