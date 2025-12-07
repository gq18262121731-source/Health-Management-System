import { useState, useEffect } from 'react';
import { elderlyHealthApi, HeartRateChartResponse } from '@/api/elderly/health';
import { toast } from 'sonner@2.0.3';

/**
 * ===========================================================================
 * Hook: useHeartRateChart
 * 
 * 功能：
 * 1. 获取心率趋势图数据
 * 2. 支持切换时间段（周/月）
 * 3. 自动刷新数据
 * 
 * 使用场景：
 * - 老人端今日健康页面的心率趋势图
 * - 历史报告中的心率图表
 * 
 * API:
 * - GET /api/v1/elderly/health/charts/heartrate?period={period}
 * ===========================================================================
 */

interface UseHeartRateChartProps {
  /** 时间段 */
  period?: 'week' | 'month';
  /** 是否自动获取数据 */
  enabled?: boolean;
}

interface UseHeartRateChartReturn {
  /** 图表数据 */
  data: HeartRateChartResponse['data'] | null;
  /** 加载状态 */
  loading: boolean;
  /** 错误信息 */
  error: Error | null;
  /** 手动刷新 */
  refetch: () => Promise<void>;
}

export function useHeartRateChart({
  period = 'week',
  enabled = true,
}: UseHeartRateChartProps = {}): UseHeartRateChartReturn {
  const [data, setData] = useState<HeartRateChartResponse['data'] | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await elderlyHealthApi.getHeartRateChart(period);
      setData(response.data);
      
    } catch (err) {
      const error = err as Error;
      setError(error);
      toast.error('获取心率数据失败');
      console.error('获取心率数据失败:', error);
    } finally {
      setLoading(false);
    }
  };

  /**
   * 当 period 变化或 enabled 变化时重新获取数据
   */
  useEffect(() => {
    if (enabled) {
      fetchData();
    }
  }, [period, enabled]);

  return {
    data,
    loading,
    error,
    refetch: fetchData,
  };
}

/**
 * 使用示例：
 * 
 * ```typescript
 * function HeartRateChart() {
 *   const [period, setPeriod] = useState<'week' | 'month'>('week');
 *   const { data, loading } = useHeartRateChart({ period });
 * 
 *   if (loading) return <Skeleton />;
 * 
 *   return (
 *     <div>
 *       <ButtonGroup>
 *         <Button onClick={() => setPeriod('week')}>周</Button>
 *         <Button onClick={() => setPeriod('month')}>月</Button>
 *       </ButtonGroup>
 *       <LineChart data={data.dataPoints} />
 *     </div>
 *   );
 * }
 * ```
 */
