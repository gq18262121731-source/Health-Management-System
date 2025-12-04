import { AxiosInstance, AxiosError, InternalAxiosRequestConfig } from 'axios';
import { toast } from 'sonner@2.0.3';

/**
 * ===========================================================================
 * Axios 拦截器配置
 * 
 * 功能：
 * 1. 请求拦截：添加 token、用户角色等
 * 2. 响应拦截：统一错误处理、日志记录
 * 3. 错误分类处理：401、403、404、500等
 * ===========================================================================
 */

export function setupInterceptors(instance: AxiosInstance) {
  // ============================================================================
  // 请求拦截器
  // ============================================================================
  instance.interceptors.request.use(
    (config: InternalAxiosRequestConfig) => {
      // 1. 添加认证 token
      const token = localStorage.getItem('authToken');
      if (token && config.headers) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      
      // 2. 添加用户角色
      const role = localStorage.getItem('userRole');
      if (role && config.headers) {
        config.headers['X-User-Role'] = role;
      }
      
      // 3. 添加用户 ID（如果存在）
      const userId = localStorage.getItem('userId');
      if (userId && config.headers) {
        config.headers['X-User-ID'] = userId;
      }
      
      // 4. 日志记录（开发环境）
      if (import.meta.env.DEV) {
        console.log('🚀 API Request:', {
          method: config.method?.toUpperCase(),
          url: config.url,
          data: config.data,
          params: config.params,
        });
      }
      
      return config;
    },
    (error: AxiosError) => {
      console.error('❌ Request Error:', error);
      return Promise.reject(error);
    }
  );

  // ============================================================================
  // 响应拦截器
  // ============================================================================
  instance.interceptors.response.use(
    (response) => {
      // 1. 日志记录（开发环境）
      if (import.meta.env.DEV) {
        console.log('✅ API Response:', {
          url: response.config.url,
          status: response.status,
          data: response.data,
        });
      }
      
      // 2. 检查业务状态码
      if (response.data && response.data.success === false) {
        const errorMessage = response.data.error?.message || '操作失败';
        toast.error(errorMessage);
        return Promise.reject(new Error(errorMessage));
      }
      
      return response;
    },
    (error: AxiosError) => {
      console.error('❌ Response Error:', error);
      
      // 统一错误处理
      if (error.response) {
        const status = error.response.status;
        const message = (error.response.data as any)?.message || '请求失败';
        
        switch (status) {
          case 400:
            // 请求参数错误
            toast.error(message || '请求参数错误');
            break;
            
          case 401:
            // 未授权，需要重新登录
            toast.error('登录已过期，请重新登录');
            // 清除认证信息
            localStorage.removeItem('authToken');
            localStorage.removeItem('userId');
            localStorage.removeItem('userRole');
            // 跳转到登录页
            setTimeout(() => {
              window.location.href = '/';
            }, 1500);
            break;
            
          case 403:
            // 无权限
            toast.error('您没有权限执行此操作');
            break;
            
          case 404:
            // 资源不存在
            toast.error('请求的资源不存在');
            break;
            
          case 409:
            // 冲突（如数据已存在）
            toast.error(message || '数据冲突');
            break;
            
          case 422:
            // 验证失败
            toast.error(message || '数据验证失败');
            break;
            
          case 429:
            // 请求过于频繁
            toast.error('请求过于频繁，请稍后再试');
            break;
            
          case 500:
            // 服务器错误
            toast.error('服务器错误，请稍后重试');
            break;
            
          case 502:
            // 网关错误
            toast.error('网关错误，请检查网络连接');
            break;
            
          case 503:
            // 服务不可用
            toast.error('服务暂时不可用，请稍后重试');
            break;
            
          default:
            // 其他错误
            toast.error(message || `请求失败 (${status})`);
        }
      } else if (error.request) {
        // 请求已发出但没有收到响应
        toast.error('网络错误，请检查网络连接');
      } else {
        // 请求配置错误
        toast.error('请求配置错误');
      }
      
      return Promise.reject(error);
    }
  );
}

/**
 * 检查是否为网络错误
 */
export function isNetworkError(error: any): boolean {
  return error.code === 'ECONNABORTED' || 
         error.message === 'Network Error' ||
         !error.response;
}

/**
 * 检查是否为认证错误
 */
export function isAuthError(error: any): boolean {
  return error.response?.status === 401;
}

/**
 * 检查是否为权限错误
 */
export function isPermissionError(error: any): boolean {
  return error.response?.status === 403;
}

/**
 * 提取错误消息
 */
export function getErrorMessage(error: any): string {
  if (error.response?.data?.message) {
    return error.response.data.message;
  }
  if (error.message) {
    return error.message;
  }
  return '未知错误';
}
