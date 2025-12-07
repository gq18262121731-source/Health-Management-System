/**
 * 健康数据 API 服务
 * 
 * 从后端获取实时健康数据，替代前端静态数据
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

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
    if (!response.ok) throw new Error('API不可用');
    const result = await response.json();
    return result;
  } catch (error) {
    console.log('使用模拟健康数据');
    return { success: true, data: getMockTodayHealthData() };
  }
}

/**
 * 获取图表数据（心率、睡眠、血压、雷达图）
 */
export async function getChartData(userId: string, days: number = 7): Promise<{ success: boolean; data?: ChartDataResponse; error?: string }> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/health/charts?user_id=${userId}&days=${days}`);
    if (!response.ok) throw new Error('API不可用');
    const result = await response.json();
    return result;
  } catch (error) {
    console.log('使用模拟图表数据');
    return { success: true, data: getMockChartData() };
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
    if (!response.ok) throw new Error('API不可用');
    const result = await response.json();
    return result;
  } catch (error) {
    console.log('使用模拟雷达图数据');
    return { success: true, data: getMockChartData().healthRadar };
  }
}

// ============================================================================
// 模拟数据（API不可用时的fallback）
// ============================================================================

function getMockTodayHealthData(): TodayHealthData {
  return {
    userId: 'elderly_001',
    userName: '张三',
    vitalSigns: {
      temperature: { value: 36.5, unit: '°C', change: 0, status: '正常' },
      bloodSugar: { value: 5.2, unit: 'mmol/L', status: '正常', testType: '空腹' },
      bloodPressure: { systolic: 118, diastolic: 75, unit: 'mmHg', status: '正常' },
      heartRate: { value: 72, unit: 'bpm', change: -2, status: '正常' },
      spo2: { value: 98, unit: '%', status: '正常' },
    },
    activity: {
      steps: 6500,
      goal: 10000,
      percentage: 65,
      distance: 4.2,
      calories: 280,
    },
    weight: {
      value: 65,
      unit: 'kg',
      bmi: 22.5,
      bmiStatus: '正常',
    },
  };
}

function getMockChartData(): ChartDataResponse {
  const now = new Date();
  const heartRate = Array.from({ length: 24 }, (_, i) => ({
    time: `${String(i).padStart(2, '0')}:00`,
    value: 65 + Math.floor(Math.random() * 20)
  }));
  
  const sleep = Array.from({ length: 7 }, (_, i) => {
    const date = new Date(now);
    date.setDate(date.getDate() - (6 - i));
    return {
      date: date.toISOString().split('T')[0],
      duration: 6 + Math.random() * 2,
      quality: Math.random() > 0.3 ? 'good' : 'fair'
    };
  });
  
  const bloodPressure = Array.from({ length: 7 }, (_, i) => {
    const date = new Date(now);
    date.setDate(date.getDate() - (6 - i));
    return {
      date: date.toISOString().split('T')[0],
      systolic: 110 + Math.floor(Math.random() * 20),
      diastolic: 70 + Math.floor(Math.random() * 10)
    };
  });
  
  const healthRadar = [
    { subject: '心血管', value: 85 },
    { subject: '睡眠', value: 75 },
    { subject: '运动', value: 70 },
    { subject: '营养', value: 80 },
    { subject: '心理', value: 88 },
    { subject: '免疫', value: 82 }
  ];
  
  return { heartRate, sleep, bloodPressure, healthRadar };
}
