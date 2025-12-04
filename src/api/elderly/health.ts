import { api } from '../client';
import { API_ENDPOINTS, buildURL, QueryParams } from '../config';

/**
 * ===========================================================================
 * 老人端 - 健康数据 API
 * 
 * 涉及端点：
 * - GET /elderly/health/today - 获取今日健康数据
 * - GET /elderly/health/charts/heartrate - 获取心率趋势图
 * - GET /elderly/health/charts/sleep - 获取睡眠分析
 * - GET /elderly/health/charts/bloodpressure - 获取血压趋势
 * - GET /elderly/health/charts/radar - 获取健康雷达图
 * ===========================================================================
 */

/**
 * 今日健康数据响应（类型定义见 types/api/health.types.ts）
 */
export interface HealthTodayResponse {
  success: boolean;
  data: {
    userId: string;
    userName: string;
    vitalSigns: {
      temperature: {
        value: number;
        unit: string;
        change: number;
        status: 'normal' | 'low' | 'high';
      };
      bloodSugar: {
        value: number;
        unit: string;
        status: string;
        testType: 'fasting' | 'postprandial';
      };
      bloodPressure: {
        systolic: number;
        diastolic: number;
        unit: string;
        status: string;
      };
      heartRate: {
        value: number;
        unit: string;
        change: number;
        status: string;
        variability: string;
      };
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
  };
  timestamp: string;
}

/**
 * 心率图表数据响应
 */
export interface HeartRateChartResponse {
  success: boolean;
  data: {
    period: 'week' | 'month';
    dataPoints: Array<{
      time: string;
      value: number;
      timestamp: string;
    }>;
    statistics: {
      average: number;
      min: number;
      max: number;
    };
  };
}

/**
 * 睡眠分析数据响应
 */
export interface SleepAnalysisResponse {
  success: boolean;
  data: {
    period: 'week' | 'month';
    dataPoints: Array<{
      day: string;
      deepSleep: number;
      lightSleep: number;
      total: number;
    }>;
    statistics: {
      averageDeepSleep: number;
      averageTotalSleep: number;
      sleepQuality: 'good' | 'fair' | 'poor';
    };
  };
}

/**
 * 血压趋势数据响应
 */
export interface BloodPressureChartResponse {
  success: boolean;
  data: {
    period: 'week' | 'month';
    dataPoints: Array<{
      time: string;
      systolic: number;
      diastolic: number;
      timestamp: string;
    }>;
    statistics: {
      averageSystolic: number;
      averageDiastolic: number;
    };
  };
}

/**
 * 健康雷达图数据响应
 */
export interface HealthRadarResponse {
  success: boolean;
  data: {
    categories: Array<{
      category: string;
      score: number;
      maxScore: number;
    }>;
    overallScore: number;
  };
}

/**
 * 老人端健康数据 API
 */
export const elderlyHealthApi = {
  /**
   * 获取今日健康数据
   * 
   * @returns Promise<HealthTodayResponse>
   * 
   * @example
   * const data = await elderlyHealthApi.getTodayHealth();
   * console.log(data.data.vitalSigns.heartRate.value); // 72
   */
  getTodayHealth: () => 
    api.get<HealthTodayResponse>(API_ENDPOINTS.ELDERLY.HEALTH_TODAY),

  /**
   * 获取心率趋势图数据
   * 
   * @param period - 时间段 ('week' | 'month')
   * @returns Promise<HeartRateChartResponse>
   * 
   * @example
   * const chartData = await elderlyHealthApi.getHeartRateChart('week');
   * console.log(chartData.data.dataPoints); // [{ time: '周一', value: 72 }, ...]
   */
  getHeartRateChart: (period: 'week' | 'month' = 'week') => 
    api.get<HeartRateChartResponse>(
      buildURL(API_ENDPOINTS.ELDERLY.CHARTS_HEARTRATE, { period })
    ),

  /**
   * 获取睡眠分析数据
   * 
   * @param period - 时间段 ('week' | 'month')
   * @returns Promise<SleepAnalysisResponse>
   * 
   * @example
   * const sleepData = await elderlyHealthApi.getSleepAnalysis('week');
   * console.log(sleepData.data.statistics.averageTotalSleep); // 7.5
   */
  getSleepAnalysis: (period: 'week' | 'month' = 'week') => 
    api.get<SleepAnalysisResponse>(
      buildURL(API_ENDPOINTS.ELDERLY.CHARTS_SLEEP, { period })
    ),

  /**
   * 获取血压趋势数据
   * 
   * @param period - 时间段 ('week' | 'month')
   * @returns Promise<BloodPressureChartResponse>
   * 
   * @example
   * const bpData = await elderlyHealthApi.getBloodPressureChart('month');
   */
  getBloodPressureChart: (period: 'week' | 'month' = 'week') => 
    api.get<BloodPressureChartResponse>(
      buildURL(API_ENDPOINTS.ELDERLY.CHARTS_BLOODPRESSURE, { period })
    ),

  /**
   * 获取健康雷达图数据
   * 
   * @returns Promise<HealthRadarResponse>
   * 
   * @example
   * const radarData = await elderlyHealthApi.getHealthRadar();
   * console.log(radarData.data.overallScore); // 85
   */
  getHealthRadar: () => 
    api.get<HealthRadarResponse>(API_ENDPOINTS.ELDERLY.CHARTS_RADAR),
};
