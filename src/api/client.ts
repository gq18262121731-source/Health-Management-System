import axios, { AxiosInstance, AxiosRequestConfig } from 'axios';
import { setupInterceptors } from './interceptors';
import { API_CONFIG } from './config';

/**
 * ===========================================================================
 * Axios 客户端实例
 * 
 * 功能：
 * 1. 创建配置好的 Axios 实例
 * 2. 统一的请求/响应处理
 * 3. 类型安全的 API 调用方法
 * 4. 自动添加认证 token
 * 5. 统一错误处理
 * ===========================================================================
 */

// 创建 Axios 实例
const apiClient: AxiosInstance = axios.create({
  baseURL: API_CONFIG.baseURL,
  timeout: API_CONFIG.timeout,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 设置拦截器（请求/响应拦截）
setupInterceptors(apiClient);

/**
 * 统一的 API 调用方法
 * 
 * 特点：
 * - 类型安全：泛型 <T> 确保返回类型正确
 * - 自动解包：直接返回 response.data
 * - 错误处理：拦截器统一处理错误
 */
export const api = {
  /**
   * GET 请求
   * @param url - API 端点
   * @param config - Axios 配置
   * @returns Promise<T> - 响应数据
   */
  get: <T>(url: string, config?: AxiosRequestConfig): Promise<T> => 
    apiClient.get(url, config).then(res => res.data),
  
  /**
   * POST 请求
   * @param url - API 端点
   * @param data - 请求数据
   * @param config - Axios 配置
   * @returns Promise<T> - 响应数据
   */
  post: <T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> => 
    apiClient.post(url, data, config).then(res => res.data),
  
  /**
   * PUT 请求
   * @param url - API 端点
   * @param data - 请求数据
   * @param config - Axios 配置
   * @returns Promise<T> - 响应数据
   */
  put: <T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> => 
    apiClient.put(url, data, config).then(res => res.data),
  
  /**
   * DELETE 请求
   * @param url - API 端点
   * @param config - Axios 配置
   * @returns Promise<T> - 响应数据
   */
  delete: <T>(url: string, config?: AxiosRequestConfig): Promise<T> => 
    apiClient.delete(url, config).then(res => res.data),
  
  /**
   * PATCH 请求
   * @param url - API 端点
   * @param data - 请求数据
   * @param config - Axios 配置
   * @returns Promise<T> - 响应数据
   */
  patch: <T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> => 
    apiClient.patch(url, data, config).then(res => res.data),
};

// 导出 Axios 实例（高级用法）
export default apiClient;
