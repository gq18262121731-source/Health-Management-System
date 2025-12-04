import { useState, useEffect } from 'react';
import { elderlyHealthApi, HealthTodayResponse } from '@/api/elderly/health';
import { toast } from 'sonner@2.0.3';

/**
 * ===========================================================================
 * Hook: useHealthData
 * 
 * 功能：
 * 1. 获取老人端今日健康数据
 * 2. 管理 loading 和 error 状态
 * 3. 提供 refetch 方法手动刷新
 * 
 * 使用场景：
 * - 老人端今日健康页面
 * - 健康卡片组件
 * 
 * API:
 * - GET /api/v1/elderly/health/today
 * ===========================================================================
 */

interface UseHealthDataReturn {
  /** 健康数据 */
  data: HealthTodayResponse['data'] | null;
  /** 加载状态 */
  loading: boolean;
  /** 错误信息 */
  error: Error | null;
  /** 手动刷新数据 */
  refetch: () => Promise<void>;
}

export function useHealthData(): UseHealthDataReturn {
  const [data, setData] = useState<HealthTodayResponse['data'] | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  /**
   * 获取数据的函数
   */
  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // 调用 API
      const response = await elderlyHealthApi.getTodayHealth();
      
      // 设置数据
      setData(response.data);
      
    } catch (err) {
      const error = err as Error;
      setError(error);
      
      // 错误提示
      toast.error('获取健康数据失败，请稍后重试');
      
      console.error('获取健康数据失败:', error);
    } finally {
      setLoading(false);
    }
  };

  /**
   * 组件挂载时自动获取数据
   */
  useEffect(() => {
    fetchData();
  }, []);

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
 * function DashboardPage() {
 *   const { data, loading, error, refetch } = useHealthData();
 * 
 *   if (loading) return <Loading />;
 *   if (error) return <Error message={error.message} />;
 * 
 *   return (
 *     <div>
 *       <h1>{data.userName}</h1>
 *       <HealthCard data={data.vitalSigns.heartRate} />
 *       <Button onClick={refetch}>刷新</Button>
 *     </div>
 *   );
 * }
 * ```
 */
