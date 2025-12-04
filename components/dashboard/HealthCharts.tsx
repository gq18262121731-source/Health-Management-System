import React, { useState, useEffect, useRef } from 'react';
import { Line, LineChart, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Area, AreaChart, RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Legend, ReferenceLine, ReferenceArea } from 'recharts';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "../ui/card";
import { Loader2, Heart, BedDouble, Activity as ActivityIcon } from 'lucide-react';
import { getChartData, HeartRateDataPoint, SleepDataPoint, BloodPressureDataPoint, HealthRadarDataPoint } from '../../services/healthDataApi';

// ============================================================================
// 健康图表组件 - 从后端API获取动态数据
// ============================================================================

// 默认数据（API失败时使用）
const defaultHeartRateData: HeartRateDataPoint[] = [
  { time: '00:00', value: 68 },
  { time: '02:00', value: 62 },
  { time: '04:00', value: 58 },
  { time: '06:00', value: 65 },
  { time: '08:00', value: 78 },
  { time: '10:00', value: 82 },
  { time: '12:00', value: 75 },
  { time: '14:00', value: 80 },
  { time: '16:00', value: 85 },
  { time: '18:00', value: 88 },
  { time: '20:00', value: 76 },
  { time: '22:00', value: 70 },
];

const defaultSleepData: SleepDataPoint[] = [
  { day: '周一', deepSleep: 2.8, lightSleep: 4.4, quality: 85 },
  { day: '周二', deepSleep: 2.2, lightSleep: 4.3, quality: 70 },
  { day: '周三', deepSleep: 3.2, lightSleep: 4.8, quality: 90 },
  { day: '周四', deepSleep: 2.9, lightSleep: 4.6, quality: 82 },
  { day: '周五', deepSleep: 1.8, lightSleep: 3.7, quality: 50 },
  { day: '周六', deepSleep: 3.6, lightSleep: 5.4, quality: 95 },
  { day: '周日', deepSleep: 3.3, lightSleep: 4.9, quality: 88 },
];

const defaultBloodPressureData: BloodPressureDataPoint[] = [
  { day: '周一', systolic: 120, diastolic: 80, normalHigh: 120, normalLow: 80 },
  { day: '周二', systolic: 118, diastolic: 76, normalHigh: 120, normalLow: 80 },
  { day: '周三', systolic: 122, diastolic: 82, normalHigh: 120, normalLow: 80 },
  { day: '周四', systolic: 115, diastolic: 75, normalHigh: 120, normalLow: 80 },
  { day: '周五', systolic: 119, diastolic: 78, normalHigh: 120, normalLow: 80 },
  { day: '周六', systolic: 118, diastolic: 75, normalHigh: 120, normalLow: 80 },
  { day: '周日', systolic: 121, diastolic: 79, normalHigh: 120, normalLow: 80 },
];

const defaultHealthRadarData: HealthRadarDataPoint[] = [
  { subject: '心血管', score: 85, lastMonth: 82, fullMark: 100 },
  { subject: '睡眠质量', score: 78, lastMonth: 72, fullMark: 100 },
  { subject: '运动量', score: 72, lastMonth: 68, fullMark: 100 },
  { subject: '营养均衡', score: 88, lastMonth: 85, fullMark: 100 },
  { subject: '心理健康', score: 90, lastMonth: 88, fullMark: 100 },
  { subject: '体重管理', score: 82, lastMonth: 80, fullMark: 100 },
];

// 全局数据状态（共享给所有图表组件）
let chartDataCache: {
  heartRate: HeartRateDataPoint[];
  sleep: SleepDataPoint[];
  bloodPressure: BloodPressureDataPoint[];
  healthRadar: HealthRadarDataPoint[];
  lastFetch: number;
} | null = null;

// 数据刷新间隔（毫秒）
const DATA_REFRESH_INTERVAL = 60000; // 1分钟

// 获取图表数据的Hook
function useChartData(userId: string = 'elderly_001') {
  const [data, setData] = useState(chartDataCache);
  const [loading, setLoading] = useState(!chartDataCache);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      // 如果缓存有效，使用缓存
      if (chartDataCache && Date.now() - chartDataCache.lastFetch < DATA_REFRESH_INTERVAL) {
        setData(chartDataCache);
        setLoading(false);
        return;
      }

      try {
        const result = await getChartData(userId, 7);
        if (result.success && result.data) {
          chartDataCache = {
            ...result.data,
            lastFetch: Date.now()
          };
          setData(chartDataCache);
        } else {
          // 使用默认数据
          chartDataCache = {
            heartRate: defaultHeartRateData,
            sleep: defaultSleepData,
            bloodPressure: defaultBloodPressureData,
            healthRadar: defaultHealthRadarData,
            lastFetch: Date.now()
          };
          setData(chartDataCache);
        }
      } catch (err) {
        setError('数据加载失败');
        // 使用默认数据
        chartDataCache = {
          heartRate: defaultHeartRateData,
          sleep: defaultSleepData,
          bloodPressure: defaultBloodPressureData,
          healthRadar: defaultHealthRadarData,
          lastFetch: Date.now()
        };
        setData(chartDataCache);
      } finally {
        setLoading(false);
      }
    };

    fetchData();

    // 定时刷新
    const interval = setInterval(fetchData, DATA_REFRESH_INTERVAL);
    return () => clearInterval(interval);
  }, [userId]);

  return { data, loading, error };
}

// Helper component to safely render chart only when dimensions are known
function ChartContainer({ children, height = 300 }: { children: (width: number, height: number) => React.ReactNode, height?: number }) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [dimensions, setDimensions] = useState<{ width: number; height: number } | null>(null);

  useEffect(() => {
    const observer = new ResizeObserver((entries) => {
      if (!entries || entries.length === 0) return;
      const { width, height } = entries[0].contentRect;
      if (width > 0 && height > 0) {
        setDimensions({ width, height });
      }
    });

    if (containerRef.current) {
      observer.observe(containerRef.current);
    }

    return () => observer.disconnect();
  }, []);

  return (
    <div ref={containerRef} style={{ width: '100%', height }} className="w-full">
      {dimensions ? (
        children(dimensions.width, dimensions.height)
      ) : (
        <div className="w-full h-full bg-slate-50/50 animate-pulse rounded-md flex items-center justify-center text-xs text-muted-foreground">
          Loading Chart...
        </div>
      )}
    </div>
  );
}

export function HeartRateChart() {
  const { data, loading } = useChartData();
  const heartRateData = data?.heartRate || defaultHeartRateData;
  
  const maxRate = Math.max(...heartRateData.map(d => d.value));
  const minRate = Math.min(...heartRateData.map(d => d.value));
  const avgRate = Math.round(heartRateData.reduce((sum, d) => sum + d.value, 0) / heartRateData.length);
  
  if (loading) {
    return (
      <Card className="col-span-4 lg:col-span-2 bg-gradient-to-br from-rose-100 to-rose-50 border-rose-200">
        <CardContent className="flex items-center justify-center h-[380px]">
          <Loader2 className="h-8 w-8 animate-spin text-rose-500" />
          <span className="ml-2 text-muted-foreground">加载心率数据...</span>
        </CardContent>
      </Card>
    );
  }
  
  return (
    <Card className="col-span-4 lg:col-span-2 bg-gradient-to-br from-rose-100 to-rose-50 border-rose-200 shadow-lg">
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-red-500 to-rose-500 flex items-center justify-center shadow-md">
              <Heart className="h-6 w-6 text-white" />
            </div>
            <div>
              <CardTitle className="text-xl font-bold text-rose-900">心率趋势 (24h)</CardTitle>
              <CardDescription className="text-base text-rose-700">
                平均心率: <span className="font-bold text-rose-900">{avgRate}</span> BPM
              </CardDescription>
            </div>
          </div>
          <div className="flex gap-4">
            <div className="text-center px-4 py-2 bg-white/60 rounded-xl">
              <div className="text-xs text-rose-600 font-medium">最高</div>
              <div className="text-lg font-bold text-red-600">{maxRate}</div>
            </div>
            <div className="text-center px-4 py-2 bg-white/60 rounded-xl">
              <div className="text-xs text-blue-600 font-medium">最低</div>
              <div className="text-lg font-bold text-blue-600">{minRate}</div>
            </div>
          </div>
        </div>
      </CardHeader>
      <CardContent className="pt-2">
        <ChartContainer height={280}>
          {(width, height) => (
            <AreaChart width={width} height={height} data={heartRateData} margin={{ top: 20, right: 30, left: 10, bottom: 10 }}>
              <defs>
                <linearGradient id="colorHeart" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#f43f5e" stopOpacity={0.6}/>
                  <stop offset="50%" stopColor="#fb7185" stopOpacity={0.3}/>
                  <stop offset="100%" stopColor="#fecdd3" stopOpacity={0.1}/>
                </linearGradient>
                <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">
                  <feDropShadow dx="0" dy="2" stdDeviation="3" floodColor="#f43f5e" floodOpacity="0.3"/>
                </filter>
              </defs>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#fecdd3" />
              <XAxis 
                dataKey="time" 
                tickLine={false} 
                axisLine={false} 
                tick={{ fontSize: 12, fill: '#9f1239', fontWeight: 500 }} 
                interval={3}
              />
              <YAxis 
                tickLine={false} 
                axisLine={false} 
                tick={{ fontSize: 12, fill: '#9f1239', fontWeight: 500 }} 
                domain={[50, 110]}
                width={40}
              />
              {/* 正常心率范围参考区域 */}
              <ReferenceArea y1={60} y2={100} fill="#22c55e" fillOpacity={0.15} />
              <ReferenceLine y={60} stroke="#22c55e" strokeDasharray="5 5" strokeWidth={1.5} />
              <ReferenceLine y={100} stroke="#22c55e" strokeDasharray="5 5" strokeWidth={1.5} />
              <Tooltip 
                contentStyle={{ 
                  borderRadius: '12px', 
                  border: 'none', 
                  boxShadow: '0 10px 25px -5px rgb(244 63 94 / 0.3)', 
                  fontSize: '14px',
                  background: 'linear-gradient(135deg, #fff 0%, #fff1f2 100%)',
                  padding: '12px 16px'
                }}
                cursor={{ stroke: '#f43f5e', strokeWidth: 2, strokeDasharray: '5 5' }}
                formatter={(value: number, name: string, props: any) => {
                  return [`${value} BPM`, '心率'];
                }}
                labelFormatter={(label) => `时间: ${label}`}
              />
              <Area 
                type="monotone" 
                dataKey="value" 
                stroke="#f43f5e" 
                strokeWidth={3} 
                fillOpacity={1} 
                fill="url(#colorHeart)"
                dot={{ fill: '#fff', stroke: '#f43f5e', strokeWidth: 2, r: 4 }}
                activeDot={{ fill: '#f43f5e', stroke: '#fff', strokeWidth: 3, r: 7, filter: 'url(#shadow)' }}
              />
            </AreaChart>
          )}
        </ChartContainer>
        {/* 图例 */}
        <div className="flex justify-center gap-6 mt-2 text-sm">
          <div className="flex items-center gap-2">
            <div className="w-4 h-1 bg-gradient-to-r from-rose-500 to-rose-400 rounded-full"></div>
            <span className="text-rose-700 font-medium">实时心率</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 bg-green-500/20 border border-green-500 rounded"></div>
            <span className="text-green-700 font-medium">正常范围 (60-100)</span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

export function SleepAnalysisChart() {
  const { data, loading } = useChartData();
  const sleepData = data?.sleep || defaultSleepData;
  
  const avgDeepSleep = (sleepData.reduce((acc, d) => acc + d.deepSleep, 0) / sleepData.length).toFixed(1);
  const avgLightSleep = (sleepData.reduce((acc, d) => acc + d.lightSleep, 0) / sleepData.length).toFixed(1);
  const avgTotal = (parseFloat(avgDeepSleep) + parseFloat(avgLightSleep)).toFixed(1);
  const avgQuality = (sleepData.reduce((acc, d) => acc + d.quality, 0) / sleepData.length).toFixed(0);
  
  if (loading) {
    return (
      <Card className="col-span-4 lg:col-span-2 bg-gradient-to-br from-indigo-200 to-indigo-100 border-indigo-300">
        <CardContent className="flex items-center justify-center h-[430px]">
          <Loader2 className="h-8 w-8 animate-spin text-indigo-500" />
          <span className="ml-2 text-muted-foreground">加载睡眠数据...</span>
        </CardContent>
      </Card>
    );
  }
  
  return (
    <Card className="col-span-4 lg:col-span-2 bg-gradient-to-br from-indigo-200 to-indigo-100 border-indigo-300 shadow-lg">
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-indigo-600 to-purple-600 flex items-center justify-center shadow-md">
              <BedDouble className="h-6 w-6 text-gray-100" />
            </div>
            <div>
              <CardTitle className="text-xl font-bold text-indigo-900">睡眠质量分析</CardTitle>
              <CardDescription className="text-base text-indigo-700">
                平均睡眠: <span className="font-bold text-indigo-900">{avgTotal}</span> 小时
              </CardDescription>
            </div>
          </div>
          <div className="flex gap-3">
            <div className="text-center px-4 py-2 bg-white/60 rounded-xl">
              <div className="text-xs text-indigo-600 font-medium">深睡</div>
              <div className="text-lg font-bold text-indigo-700">{avgDeepSleep}h</div>
            </div>
            <div className="text-center px-4 py-2 bg-white/60 rounded-xl">
              <div className="text-xs text-purple-600 font-medium">质量</div>
              <div className="text-lg font-bold text-purple-700">{avgQuality}分</div>
            </div>
          </div>
        </div>
      </CardHeader>
      <CardContent className="pt-2">
        <ChartContainer height={320}>
          {(width, height) => (
            <BarChart width={width} height={height} data={sleepData} margin={{ top: 20, right: 40, left: 10, bottom: 10 }}>
              <defs>
                <linearGradient id="colorDeepSleep" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#6366f1" stopOpacity={1}/>
                  <stop offset="100%" stopColor="#818cf8" stopOpacity={0.8}/>
                </linearGradient>
                <linearGradient id="colorLightSleep" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#a5b4fc" stopOpacity={0.9}/>
                  <stop offset="100%" stopColor="#c7d2fe" stopOpacity={0.7}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#c7d2fe" />
              <XAxis 
                dataKey="day" 
                tickLine={false} 
                axisLine={false} 
                tick={{ fontSize: 12, fill: '#4338ca', fontWeight: 500 }} 
              />
              <YAxis 
                tickLine={false} 
                axisLine={false} 
                tick={{ fontSize: 12, fill: '#4338ca', fontWeight: 500 }}
                width={35}
              />
              <ReferenceLine y={8} stroke="#22c55e" strokeDasharray="5 5" strokeWidth={2} />
              <Tooltip 
                cursor={{ fill: 'rgba(99, 102, 241, 0.1)' }}
                contentStyle={{ 
                  borderRadius: '12px', 
                  border: 'none', 
                  boxShadow: '0 10px 25px -5px rgb(99 102 241 / 0.3)', 
                  fontSize: '14px',
                  background: 'linear-gradient(135deg, #fff 0%, #eef2ff 100%)',
                  padding: '12px 16px'
                }}
                formatter={(value: number, name: string) => {
                  if (name === 'deepSleep') return [`${value} 小时`, '深度睡眠'];
                  if (name === 'lightSleep') return [`${value} 小时`, '浅度睡眠'];
                  if (name === 'quality') return [`${value} 分`, '质量分数'];
                  return [value, name];
                }}
              />
              <Bar dataKey="deepSleep" stackId="sleep" fill="url(#colorDeepSleep)" radius={[0, 0, 0, 0]} barSize={35} />
              <Bar dataKey="lightSleep" stackId="sleep" fill="url(#colorLightSleep)" radius={[6, 6, 0, 0]} barSize={35} />
              <Line 
                type="monotone" 
                dataKey="quality" 
                stroke="#a855f7" 
                strokeWidth={3} 
                dot={{ r: 5, fill: '#fff', stroke: '#a855f7', strokeWidth: 2 }}
                activeDot={{ r: 7, fill: '#a855f7', stroke: '#fff', strokeWidth: 2 }}
                yAxisId="right"
              />
              <YAxis 
                yAxisId="right"
                orientation="right"
                tickLine={false} 
                axisLine={false} 
                tick={{ fontSize: 12, fill: '#9333ea', fontWeight: 500 }}
                domain={[0, 100]}
                width={35}
              />
            </BarChart>
          )}
        </ChartContainer>
        <div className="flex justify-center gap-6 mt-2 text-sm">
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 bg-gradient-to-b from-indigo-500 to-indigo-400 rounded"></div>
            <span className="text-indigo-700 font-medium">深度睡眠</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 bg-gradient-to-b from-indigo-300 to-indigo-200 rounded"></div>
            <span className="text-indigo-600 font-medium">浅度睡眠</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-1 bg-purple-500 rounded-full"></div>
            <span className="text-purple-700 font-medium">质量分数</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-0.5 bg-green-500 rounded-full" style={{borderStyle: 'dashed'}}></div>
            <span className="text-green-700 font-medium">推荐8h</span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

export function BloodPressureChart() {
  const { data, loading } = useChartData();
  const bloodPressureData = data?.bloodPressure || defaultBloodPressureData;
  
  const avgSystolic = (bloodPressureData.reduce((acc, d) => acc + d.systolic, 0) / bloodPressureData.length).toFixed(0);
  const avgDiastolic = (bloodPressureData.reduce((acc, d) => acc + d.diastolic, 0) / bloodPressureData.length).toFixed(0);
  
  // 判断血压状态
  const systolicNum = parseInt(avgSystolic);
  const diastolicNum = parseInt(avgDiastolic);
  const isNormal = systolicNum >= 90 && systolicNum <= 120 && diastolicNum >= 60 && diastolicNum <= 80;
  
  if (loading) {
    return (
      <Card className="col-span-4 lg:col-span-2 bg-gradient-to-br from-blue-100 to-blue-50 border-blue-200">
        <CardContent className="flex items-center justify-center h-[430px]">
          <Loader2 className="h-8 w-8 animate-spin text-blue-500" />
          <span className="ml-2 text-muted-foreground">加载血压数据...</span>
        </CardContent>
      </Card>
    );
  }
  
  return (
    <Card className="col-span-4 lg:col-span-2 bg-gradient-to-br from-blue-100 to-blue-50 border-blue-200 shadow-lg">
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-blue-500 to-cyan-500 flex items-center justify-center shadow-md">
              <ActivityIcon className="h-6 w-6 text-white" />
            </div>
            <div>
              <CardTitle className="text-xl font-bold text-blue-900">血压趋势 (7天)</CardTitle>
              <CardDescription className="text-base text-blue-700">
                收缩压 <span className="font-bold text-red-600">{avgSystolic}</span> / 舒张压 <span className="font-bold text-blue-600">{avgDiastolic}</span> mmHg
              </CardDescription>
            </div>
          </div>
          <div className={`px-4 py-2 rounded-xl ${isNormal ? 'bg-green-100' : 'bg-orange-100'}`}>
            <div className={`text-sm font-bold ${isNormal ? 'text-green-700' : 'text-orange-700'}`}>
              {isNormal ? '✓ 血压稳定' : '⚠ 需关注'}
            </div>
            <div className={`text-xs ${isNormal ? 'text-green-600' : 'text-orange-600'}`}>
              {isNormal ? '波动范围正常' : '建议咨询医生'}
            </div>
          </div>
        </div>
      </CardHeader>
      <CardContent className="pt-2">
        <ChartContainer height={320}>
          {(width, height) => (
            <LineChart width={width} height={height} data={bloodPressureData} margin={{ top: 20, right: 30, left: 10, bottom: 10 }}>
              <defs>
                <linearGradient id="colorSystolic" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#ef4444" stopOpacity={0.3}/>
                  <stop offset="100%" stopColor="#ef4444" stopOpacity={0}/>
                </linearGradient>
                <linearGradient id="colorDiastolic" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#3b82f6" stopOpacity={0.3}/>
                  <stop offset="100%" stopColor="#3b82f6" stopOpacity={0}/>
                </linearGradient>
                <filter id="shadowBP" x="-20%" y="-20%" width="140%" height="140%">
                  <feDropShadow dx="0" dy="2" stdDeviation="3" floodColor="#3b82f6" floodOpacity="0.3"/>
                </filter>
              </defs>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#bfdbfe" />
              <XAxis 
                dataKey="day" 
                tickLine={false} 
                axisLine={false} 
                tick={{ fontSize: 12, fill: '#1e40af', fontWeight: 500 }} 
              />
              <YAxis 
                tickLine={false} 
                axisLine={false} 
                tick={{ fontSize: 12, fill: '#1e40af', fontWeight: 500 }} 
                domain={[50, 140]}
                width={40}
              />
              <ReferenceArea y1={90} y2={120} fill="#22c55e" fillOpacity={0.15} label={{ value: '收缩压正常范围 90-120', position: 'insideTopRight', fontSize: 11, fill: '#16a34a', fontWeight: 500 }} />
              <ReferenceArea y1={60} y2={80} fill="#3b82f6" fillOpacity={0.1} label={{ value: '舒张压正常范围 60-80', position: 'insideBottomRight', fontSize: 11, fill: '#2563eb', fontWeight: 500 }} />
              <ReferenceLine y={120} stroke="#22c55e" strokeDasharray="5 5" strokeWidth={1.5} label={{ value: '120', position: 'left', fontSize: 10, fill: '#16a34a' }} />
              <ReferenceLine y={90} stroke="#22c55e" strokeDasharray="5 5" strokeWidth={1.5} label={{ value: '90', position: 'left', fontSize: 10, fill: '#16a34a' }} />
              <ReferenceLine y={80} stroke="#3b82f6" strokeDasharray="5 5" strokeWidth={1.5} label={{ value: '80', position: 'left', fontSize: 10, fill: '#2563eb' }} />
              <ReferenceLine y={60} stroke="#3b82f6" strokeDasharray="5 5" strokeWidth={1.5} label={{ value: '60', position: 'left', fontSize: 10, fill: '#2563eb' }} />
              <Tooltip 
                contentStyle={{ 
                  borderRadius: '12px', 
                  border: 'none', 
                  boxShadow: '0 10px 25px -5px rgb(59 130 246 / 0.3)', 
                  fontSize: '14px',
                  background: 'linear-gradient(135deg, #fff 0%, #eff6ff 100%)',
                  padding: '12px 16px'
                }}
                cursor={{ stroke: '#3b82f6', strokeWidth: 2, strokeDasharray: '5 5' }}
                formatter={(value: number, name: string) => {
                  if (name === '收缩压') return [`${value} mmHg`, '收缩压 (高压)'];
                  if (name === '舒张压') return [`${value} mmHg`, '舒张压 (低压)'];
                  return [value, name];
                }}
              />
              <Area 
                type="monotone" 
                dataKey="systolic" 
                stroke="transparent"
                fill="url(#colorSystolic)"
              />
              <Area 
                type="monotone" 
                dataKey="diastolic" 
                stroke="transparent"
                fill="url(#colorDiastolic)"
              />
              <Line 
                type="monotone" 
                dataKey="systolic" 
                stroke="#ef4444" 
                strokeWidth={3} 
                dot={{ r: 5, strokeWidth: 2, fill: '#fff', stroke: '#ef4444' }}
                activeDot={{ r: 8, fill: '#ef4444', stroke: '#fff', strokeWidth: 3 }}
                name="收缩压"
              />
              <Line 
                type="monotone" 
                dataKey="diastolic" 
                stroke="#3b82f6" 
                strokeWidth={3} 
                dot={{ r: 5, strokeWidth: 2, fill: '#fff', stroke: '#3b82f6' }}
                activeDot={{ r: 8, fill: '#3b82f6', stroke: '#fff', strokeWidth: 3, filter: 'url(#shadowBP)' }}
                name="舒张压"
              />
            </LineChart>
          )}
        </ChartContainer>
        <div className="flex justify-center gap-6 mt-2 text-sm">
          <div className="flex items-center gap-2">
            <div className="w-4 h-1 bg-red-500 rounded-full"></div>
            <span className="text-red-700 font-medium">收缩压 (高压)</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-1 bg-blue-500 rounded-full"></div>
            <span className="text-blue-700 font-medium">舒张压 (低压)</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 bg-green-500/20 border border-green-500 rounded"></div>
            <span className="text-green-700 font-medium">正常范围 (收缩压: 90-120 / 舒张压: 60-80)</span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

export function HealthRadarChart() {
  const { data, loading } = useChartData();
  const healthRadarData = data?.healthRadar || defaultHealthRadarData;
  
  const avgCurrentScore = (healthRadarData.reduce((acc, d) => acc + d.score, 0) / healthRadarData.length).toFixed(0);
  const avgLastMonthScore = (healthRadarData.reduce((acc, d) => acc + d.lastMonth, 0) / healthRadarData.length).toFixed(0);
  const improvement = Number(avgCurrentScore) - Number(avgLastMonthScore);
  
  if (loading) {
    return (
      <Card className="col-span-4 lg:col-span-2 bg-gradient-to-br from-green-100 to-green-50 border-green-200">
        <CardContent className="flex items-center justify-center h-[580px]">
          <Loader2 className="h-8 w-8 animate-spin text-green-500" />
          <span className="ml-2 text-muted-foreground">加载健康数据...</span>
        </CardContent>
      </Card>
    );
  }
  
  return (
    <Card className="col-span-4 lg:col-span-2 bg-gradient-to-br from-green-100 to-green-50 border-green-200 shadow-lg">
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-14 h-14 rounded-xl bg-gradient-to-br from-green-500 to-emerald-500 flex items-center justify-center shadow-md">
              <ActivityIcon className="h-7 w-7 text-white" />
            </div>
            <div>
              <CardTitle className="text-xl font-bold text-green-900">健康雷达图</CardTitle>
              <CardDescription className="text-base text-green-700">综合健康状况评估</CardDescription>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <div className="text-center px-5 py-3 bg-white/70 rounded-xl shadow-sm">
              <div className="text-xs text-green-600 font-medium">综合评分</div>
              <div className="text-3xl font-bold text-green-700">{avgCurrentScore}</div>
            </div>
            <div className={`text-center px-4 py-3 rounded-xl ${improvement >= 0 ? 'bg-green-200/50' : 'bg-red-200/50'}`}>
              <div className="text-xs text-gray-600 font-medium">较上月</div>
              <div className={`text-xl font-bold ${improvement >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                {improvement >= 0 ? '+' : ''}{improvement}
              </div>
            </div>
          </div>
        </div>
      </CardHeader>
      <CardContent className="flex gap-6 min-h-[480px] pt-2">
        {/* 左侧：雷达图 */}
        <div className="flex-[3] min-w-0">
          <ChartContainer height={420}>
            {(width, height) => (
              <RadarChart width={width} height={height} data={healthRadarData} margin={{ top: 30, right: 50, left: 50, bottom: 30 }}>
                <defs>
                  <linearGradient id="colorRadarCurrent" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#10b981" stopOpacity={0.6}/>
                    <stop offset="100%" stopColor="#34d399" stopOpacity={0.2}/>
                  </linearGradient>
                  <linearGradient id="colorRadarLast" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#60a5fa" stopOpacity={0.3}/>
                    <stop offset="100%" stopColor="#93c5fd" stopOpacity={0.1}/>
                  </linearGradient>
                  <filter id="shadowRadar" x="-20%" y="-20%" width="140%" height="140%">
                    <feDropShadow dx="0" dy="2" stdDeviation="4" floodColor="#10b981" floodOpacity="0.4"/>
                  </filter>
                </defs>
                <PolarGrid stroke="#86efac" strokeWidth={1} />
                <PolarAngleAxis 
                  dataKey="subject" 
                  tick={{ fontSize: 13, fill: '#166534', fontWeight: 600 }}
                />
                <PolarRadiusAxis 
                  angle={30} 
                  domain={[0, 100]} 
                  tick={{ fontSize: 11, fill: '#22c55e', fontWeight: 500 }}
                  tickCount={5}
                />
                <Tooltip 
                  contentStyle={{ 
                    borderRadius: '12px', 
                    border: 'none', 
                    boxShadow: '0 10px 25px -5px rgb(16 185 129 / 0.3)', 
                    fontSize: '14px',
                    background: 'linear-gradient(135deg, #fff 0%, #ecfdf5 100%)',
                    padding: '12px 16px'
                  }}
                  formatter={(value: number, name: string) => {
                    if (name === '本月') return [`${value} 分`, '本月得分'];
                    if (name === '上月') return [`${value} 分`, '上月得分'];
                    return [value, name];
                  }}
                />
                {/* 上月数据对比 */}
                <Radar 
                  name="上月" 
                  dataKey="lastMonth" 
                  stroke="#60a5fa" 
                  fill="url(#colorRadarLast)" 
                  strokeWidth={2}
                  strokeDasharray="6 4"
                />
                {/* 本月数据 */}
                <Radar 
                  name="本月" 
                  dataKey="score" 
                  stroke="#10b981" 
                  fill="url(#colorRadarCurrent)" 
                  strokeWidth={3}
                  filter="url(#shadowRadar)"
                />
              </RadarChart>
            )}
          </ChartContainer>
          <div className="flex justify-center gap-8 text-sm">
            <div className="flex items-center gap-2">
              <div className="w-5 h-3 bg-gradient-to-r from-green-500 to-emerald-400 rounded"></div>
              <span className="text-green-700 font-medium">本月健康状况</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-5 h-0.5 bg-blue-400 rounded-full" style={{borderStyle: 'dashed'}}></div>
              <span className="text-blue-600 font-medium">上月对比</span>
            </div>
          </div>
        </div>

        {/* 右侧：指标卡片两列布局 */}
        <div className="flex-[2] grid grid-cols-2 gap-3 content-center min-w-[340px]">
          {/* 心血管 */}
          <div className="bg-white/95 backdrop-blur-sm px-3 py-3 rounded-lg shadow-md border-l-4 border-green-500">
            <div className="space-y-1">
              <div className="text-xs text-gray-600">心血管</div>
              <div className="flex items-baseline gap-1">
                <div className="text-2xl font-bold text-green-700">{healthRadarData[0].score}</div>
                <div className="text-xs text-green-600/70">分</div>
              </div>
              {healthRadarData[0].score !== healthRadarData[0].lastMonth && (
                <div className={`text-xs flex items-center gap-0.5 ${healthRadarData[0].score > healthRadarData[0].lastMonth ? 'text-green-600' : 'text-red-600'}`}>
                  <span>{healthRadarData[0].score > healthRadarData[0].lastMonth ? '↑' : '↓'}</span>
                  <span>{Math.abs(healthRadarData[0].score - healthRadarData[0].lastMonth)}</span>
                </div>
              )}
            </div>
          </div>
          
          {/* 睡眠质量 */}
          <div className="bg-white/95 backdrop-blur-sm px-3 py-3 rounded-lg shadow-md border-l-4 border-indigo-500">
            <div className="space-y-1">
              <div className="text-xs text-gray-600">睡眠质量</div>
              <div className="flex items-baseline gap-1">
                <div className="text-2xl font-bold text-indigo-700">{healthRadarData[1].score}</div>
                <div className="text-xs text-indigo-600/70">分</div>
              </div>
              {healthRadarData[1].score !== healthRadarData[1].lastMonth && (
                <div className={`text-xs flex items-center gap-0.5 ${healthRadarData[1].score > healthRadarData[1].lastMonth ? 'text-green-600' : 'text-red-600'}`}>
                  <span>{healthRadarData[1].score > healthRadarData[1].lastMonth ? '↑' : '↓'}</span>
                  <span>{Math.abs(healthRadarData[1].score - healthRadarData[1].lastMonth)}</span>
                </div>
              )}
            </div>
          </div>
          
          {/* 运动量 */}
          <div className="bg-white/95 backdrop-blur-sm px-3 py-3 rounded-lg shadow-md border-l-4 border-blue-500">
            <div className="space-y-1">
              <div className="text-xs text-gray-600">运动量</div>
              <div className="flex items-baseline gap-1">
                <div className="text-2xl font-bold text-blue-700">{healthRadarData[2].score}</div>
                <div className="text-xs text-blue-600/70">分</div>
              </div>
              {healthRadarData[2].score !== healthRadarData[2].lastMonth && (
                <div className={`text-xs flex items-center gap-0.5 ${healthRadarData[2].score > healthRadarData[2].lastMonth ? 'text-green-600' : 'text-red-600'}`}>
                  <span>{healthRadarData[2].score > healthRadarData[2].lastMonth ? '↑' : '↓'}</span>
                  <span>{Math.abs(healthRadarData[2].score - healthRadarData[2].lastMonth)}</span>
                </div>
              )}
            </div>
          </div>
          
          {/* 营养均衡 */}
          <div className="bg-white/95 backdrop-blur-sm px-3 py-3 rounded-lg shadow-md border-l-4 border-amber-500">
            <div className="space-y-1">
              <div className="text-xs text-gray-600">营养均衡</div>
              <div className="flex items-baseline gap-1">
                <div className="text-2xl font-bold text-amber-700">{healthRadarData[3].score}</div>
                <div className="text-xs text-amber-600/70">分</div>
              </div>
              {healthRadarData[3].score !== healthRadarData[3].lastMonth && (
                <div className={`text-xs flex items-center gap-0.5 ${healthRadarData[3].score > healthRadarData[3].lastMonth ? 'text-green-600' : 'text-red-600'}`}>
                  <span>{healthRadarData[3].score > healthRadarData[3].lastMonth ? '↑' : '↓'}</span>
                  <span>{Math.abs(healthRadarData[3].score - healthRadarData[3].lastMonth)}</span>
                </div>
              )}
            </div>
          </div>
          
          {/* 心理健康 */}
          <div className="bg-white/95 backdrop-blur-sm px-3 py-3 rounded-lg shadow-md border-l-4 border-purple-500">
            <div className="space-y-1">
              <div className="text-xs text-gray-600">心理健康</div>
              <div className="flex items-baseline gap-1">
                <div className="text-2xl font-bold text-purple-700">{healthRadarData[4].score}</div>
                <div className="text-xs text-purple-600/70">分</div>
              </div>
              {healthRadarData[4].score !== healthRadarData[4].lastMonth && (
                <div className={`text-xs flex items-center gap-0.5 ${healthRadarData[4].score > healthRadarData[4].lastMonth ? 'text-green-600' : 'text-red-600'}`}>
                  <span>{healthRadarData[4].score > healthRadarData[4].lastMonth ? '↑' : '↓'}</span>
                  <span>{Math.abs(healthRadarData[4].score - healthRadarData[4].lastMonth)}</span>
                </div>
              )}
            </div>
          </div>
          
          {/* 体重管理 */}
          <div className="bg-white/95 backdrop-blur-sm px-3 py-3 rounded-lg shadow-md border-l-4 border-teal-500">
            <div className="space-y-1">
              <div className="text-xs text-gray-600">体重管理</div>
              <div className="flex items-baseline gap-1">
                <div className="text-2xl font-bold text-teal-700">{healthRadarData[5].score}</div>
                <div className="text-xs text-teal-600/70">分</div>
              </div>
              {healthRadarData[5].score !== healthRadarData[5].lastMonth && (
                <div className={`text-xs flex items-center gap-0.5 ${healthRadarData[5].score > healthRadarData[5].lastMonth ? 'text-green-600' : 'text-red-600'}`}>
                  <span>{healthRadarData[5].score > healthRadarData[5].lastMonth ? '↑' : '↓'}</span>
                  <span>{Math.abs(healthRadarData[5].score - healthRadarData[5].lastMonth)}</span>
                </div>
              )}
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}