import { useState, useEffect } from 'react';
import { Users, Heart, AlertCircle, Activity, ArrowLeft } from 'lucide-react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, LineChart, Line, XAxis, YAxis, CartesianGrid, Legend, BarChart, Bar } from 'recharts';
import { CommunityMap2D } from './bigscreen/CommunityMap2D';

// ============================================================================
// 组件说明：社区端大屏数据展示
// 
// 涉及API:
// - GET /api/v1/community/dashboard/overview - 获取总览数据（总人数、健康监测人数、告警数、设备数）
// - GET /api/v1/community/dashboard/age-distribution - 获取年龄分布数据（饼图）
// - GET /api/v1/community/dashboard/health-trends?period=week - 获取健康趋势数据（折线图）
// - GET /api/v1/community/dashboard/devices - 获取设备状态分布
// - GET /api/v1/community/dashboard/services - 获取服务项目统计（柱状图）
// 
// 功能：
// 1. 四个主要统计卡片（总人数、监测人数、告警数、设备数）- 带数字动画
// 2. 年龄分布饼图
// 3. 健康趋势折线图（7天数据）
// 4. 设备状态饼图
// 5. 服务项目柱状图
// 6. 2D数字孪生地图（显示老人位置和告警）
// 7. 实时时钟显示
// 
// 数据刷新：
// - 使用轮询每30秒刷新一次数据
// - 地图组件独立刷新（每10秒）
// ============================================================================

// 动画数字组件
function AnimatedNumber({ value, duration = 2000, className = '', suffix = '' }: { value: number; duration?: number; className?: string; suffix?: string }) {
  const [displayValue, setDisplayValue] = useState(0);

  useEffect(() => {
    let startTime: number | null = null;
    let animationFrame: number;

    const animate = (currentTime: number) => {
      if (!startTime) startTime = currentTime;
      const progress = Math.min((currentTime - startTime) / duration, 1);
      
      const easeOutQuart = 1 - Math.pow(1 - progress, 4);
      setDisplayValue(Math.floor(easeOutQuart * value));

      if (progress < 1) {
        animationFrame = requestAnimationFrame(animate);
      }
    };

    animationFrame = requestAnimationFrame(animate);

    return () => {
      if (animationFrame) {
        cancelAnimationFrame(animationFrame);
      }
    };
  }, [value, duration]);

  return (
    <span className={className}>
      {displayValue.toLocaleString()}{suffix}
    </span>
  );
}

// 动画背景组件
function AnimatedBackground() {
  return (
    <div className="fixed inset-0 pointer-events-none overflow-hidden z-0">
      <div 
        className="absolute inset-0 opacity-20"
        style={{
          backgroundImage: `
            linear-gradient(to right, rgba(16, 185, 129, 0.1) 1px, transparent 1px),
            linear-gradient(to bottom, rgba(16, 185, 129, 0.1) 1px, transparent 1px)
          `,
          backgroundSize: '50px 50px'
        }}
      />
      <div className="absolute inset-0">
        {[...Array(20)].map((_, i) => (
          <div
            key={i}
            className="absolute w-1 h-1 bg-emerald-400 rounded-full animate-pulse"
            style={{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
              opacity: 0.3 + Math.random() * 0.4
            }}
          />
        ))}
      </div>
    </div>
  );
}

interface BigScreenDashboardProps {
  onBack?: () => void;
}

export function BigScreenDashboard({ onBack }: BigScreenDashboardProps) {
  const [currentTime, setCurrentTime] = useState(new Date());

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  const formatDate = (date: Date) => {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    const seconds = String(date.getSeconds()).padStart(2, '0');
    const weekdays = ['星期日', '星期一', '星期二', '星期三', '星期四', '星期五', '星期六'];
    const weekday = weekdays[date.getDay()];
    
    return {
      date: `${year}-${month}-${day}`,
      time: `${hours}:${minutes}:${seconds}`,
      weekday
    };
  };

  const { date, time, weekday } = formatDate(currentTime);

  // 统计卡片数据
  const stats = [
    {
      icon: Users,
      label: '社区老人总数',
      value: 1248,
      unit: '人',
      change: '+12',
      changeLabel: '较上月',
      color: 'from-emerald-400 to-teal-400'
    },
    {
      icon: Heart,
      label: '健康监测人数',
      value: 1186,
      unit: '人',
      change: '95.0%',
      changeLabel: '覆盖率',
      color: 'from-teal-400 to-cyan-400'
    },
    {
      icon: AlertCircle,
      label: '今日预警',
      value: 8,
      unit: '条',
      change: '-3',
      changeLabel: '较昨日',
      color: 'from-orange-400 to-amber-400'
    },
    {
      icon: Activity,
      label: '服务完成率',
      value: 98.5,
      unit: '%',
      change: '+2.3%',
      changeLabel: '较上周',
      color: 'from-emerald-400 to-green-500'
    }
  ];

  // 年龄分布数据
  const ageData = [
    { name: '60-70岁', value: 420, color: '#10b981', percentage: 33.7 },
    { name: '70-80岁', value: 518, color: '#14b8a6', percentage: 41.5 },
    { name: '80-90岁', value: 256, color: '#06b6d4', percentage: 20.5 },
    { name: '90岁以上', value: 54, color: '#0891b2', percentage: 4.3 }
  ];

  // 近7日趋势数据
  const weeklyTrendData = [
    { date: '11-20', 服务次数: 98, 预警次数: 12 },
    { date: '11-21', 服务次数: 105, 预警次数: 8 },
    { date: '11-22', 服务次数: 112, 预警次数: 15 },
    { date: '11-23', 服务次数: 95, 预警次数: 10 },
    { date: '11-24', 服务次数: 118, 预警次数: 7 },
    { date: '11-25', 服务次数: 125, 预警次数: 11 },
    { date: '11-26', 服务次数: 114, 预警次数: 9 }
  ];
  const avgServicePerDay = Math.round(weeklyTrendData.reduce((sum, d) => sum + d.服务次数, 0) / 7);
  const avgAlertPerDay = Math.round(weeklyTrendData.reduce((sum, d) => sum + d.预警次数, 0) / 7);

  // 健康监测数据
  const healthData = [
    { name: '血压', normal: 856, abnormal: 82, color: '#10b981' },
    { name: '血糖', normal: 902, abnormal: 56, color: '#14b8a6' },
    { name: '心率', normal: 920, abnormal: 38, color: '#06b6d4' },
    { name: '血氧', normal: 945, abnormal: 13, color: '#0891b2' }
  ];

  // 实时告警数据
  const alerts = [
    { time: '14:25', name: '张三', type: '血压异常', level: 'high', status: '处理中' },
    { time: '14:18', name: '李四', type: '心率过快', level: 'medium', status: '已通知' },
    { time: '14:05', name: '王五', type: '血糖偏高', level: 'medium', status: '已通知' },
    { time: '13:52', name: '赵六', type: '体温异常', level: 'high', status: '处理中' },
    { time: '13:30', name: '孙七', type: '血氧偏低', level: 'low', status: '已处理' },
  ];

  // 今日预警统计数据
  const alertStatsData = [
    { name: '紧急', count: 3, color: '#ef4444', icon: '🔴' },
    { name: '警告', count: 5, color: '#f59e0b', icon: '🟡' },
    { name: '一般', count: 8, color: '#3b82f6', icon: '🔵' }
  ];
  const totalAlerts = alertStatsData.reduce((sum, item) => sum + item.count, 0);

  // 运动活跃度数据
  const activityData = [
    { name: '活跃', value: 486, percentage: 39, color: '#22c55e' },
    { name: '正常', value: 512, percentage: 41, color: '#3b82f6' },
    { name: '偏少', value: 186, percentage: 15, color: '#f59e0b' },
    { name: '不足', value: 64, percentage: 5, color: '#ef4444' }
  ];
  const avgSteps = 5862;
  const avgActiveMinutes = 42;

  // 本月服务统计数据
  const serviceData = [
    { name: '医疗服务', value: 186, color: '#10b981' },
    { name: '生活照料', value: 158, color: '#14b8a6' },
    { name: '健康咨询', value: 142, color: '#06b6d4' },
    { name: '紧急救助', value: 98, color: '#f59e0b' },
    { name: '心理关怀', value: 125, color: '#8b5cf6' },
    { name: '康复训练', value: 90, color: '#ec4899' },
  ];
  const totalServices = serviceData.reduce((sum, item) => sum + item.value, 0);

  return (
    <div className="min-h-screen bg-slate-700 text-gray-100 p-4 overflow-auto relative">
      {/* 动态背景效果 */}
      <AnimatedBackground />
      
      {/* 背景图片层 */}
      <div className="fixed inset-0 z-0 pointer-events-none">
        <div className="absolute inset-0 bg-gradient-to-br from-emerald-900/80 via-teal-900/80 to-cyan-900/80"></div>
        <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDAiIGhlaWdodD0iNDAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PGRlZnM+PHBhdHRlcm4gaWQ9ImdyaWQiIHdpZHRoPSI0MCIgaGVpZ2h0PSI0MCIgcGF0dGVyblVuaXRzPSJ1c2VyU3BhY2VPblVzZSI+PHBhdGggZD0iTSA0MCAwIEwgMCAwIDAgNDAiIGZpbGw9Im5vbmUiIHN0cm9rZT0iIzEwYjk4MSIgc3Ryb2tlLXdpZHRoPSIwLjUiIG9wYWNpdHk9IjAuMyIvPjwvcGF0dGVybj48L2RlZnM+PHJlY3Qgd2lkdGg9IjEwMCUiIGhlaWdodD0iMTAwJSIgZmlsbD0idXJsKCNncmlkKSIvPjwvc3ZnPg==')] opacity-40"></div>
      </div>
      
      {/* 装饰光效 */}
      <div className="fixed top-0 left-0 w-full h-full pointer-events-none z-0">
        <div className="absolute top-20 left-20 w-96 h-96 bg-emerald-500/20 rounded-full blur-3xl"></div>
        <div className="absolute bottom-20 right-20 w-96 h-96 bg-teal-500/20 rounded-full blur-3xl"></div>
      </div>
      
      <div className="max-w-[1920px] mx-auto relative z-20">
        {/* 页面头部 */}
        <div className="relative bg-gradient-to-r from-teal-800/40 via-emerald-800/40 to-teal-800/40 border-2 border-emerald-400/60 rounded-lg p-4 mb-6 shadow-2xl backdrop-blur-md overflow-hidden group"
             style={{
               boxShadow: '0 0 30px rgba(16, 185, 129, 0.4), inset 0 0 30px rgba(16, 185, 129, 0.1)'
             }}>
          
          <div className="absolute -top-1 -right-1 w-8 h-8 border-t-2 border-r-2 border-emerald-400/70"></div>
          <div className="absolute -bottom-1 -left-1 w-8 h-8 border-b-2 border-l-2 border-emerald-400/70"></div>
          
          <div className="relative flex items-center justify-between z-10">
            <div className="text-left">
              <div className="text-3xl text-emerald-300 tracking-wider tabular-nums" style={{ textShadow: '0 0 12px rgba(16, 185, 129, 0.8)' }}>{time}</div>
              <div className="text-sm text-gray-300 mt-1">{date} {weekday}</div>
            </div>
            
            <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2">
              <h1 className="text-3xl tracking-wider text-emerald-300 whitespace-nowrap" style={{ textShadow: '0 0 15px rgba(16, 185, 129, 0.8)' }}>智慧健康管理大屏</h1>
            </div>
            
            {onBack && (
              <button
                onClick={onBack}
                className="flex items-center gap-2 px-4 py-2 border border-emerald-400/50 rounded-md bg-emerald-900/30 backdrop-blur-sm hover:bg-emerald-800/50 transition-all cursor-pointer"
              >
                <ArrowLeft className="w-4 h-4 text-emerald-300" />
                <span className="text-sm text-emerald-300">返回</span>
              </button>
            )}
          </div>
        </div>
        
        {/* 统计卡片 */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 relative z-10 mb-4">
          {stats.map((stat, index) => (
            <div
              key={index}
              className="bg-teal-900/50 backdrop-blur-md border-2 border-emerald-400/50 rounded-lg p-5 shadow-lg hover:shadow-emerald-400/60 hover:border-emerald-400/80 transition-all relative overflow-hidden group h-full"
              style={{ boxShadow: '0 0 20px rgba(16, 185, 129, 0.3), inset 0 0 20px rgba(16, 185, 129, 0.1)' }}
            >
              <div className="absolute top-0 right-0 w-20 h-20 bg-emerald-400/15 rounded-full blur-2xl group-hover:bg-emerald-400/25 transition-all pointer-events-none"></div>
              <div className="absolute -top-1 -right-1 w-8 h-8 border-t-2 border-r-2 border-emerald-400/70"></div>
              <div className="absolute -bottom-1 -left-1 w-8 h-8 border-b-2 border-l-2 border-emerald-400/70"></div>
              
              <div className="flex items-start justify-between relative z-10">
                <div className="flex-1">
                  <p className="text-gray-300 text-sm mb-2">{stat.label}</p>
                  <div className="flex items-baseline gap-1">
                    <AnimatedNumber 
                      value={stat.value} 
                      className="text-3xl tabular-nums text-emerald-300"
                    />
                    <span className="text-lg text-gray-300">{stat.unit}</span>
                  </div>
                  <div className="mt-2 flex items-center gap-1 text-xs">
                    <span className={stat.change.startsWith('+') || (stat.change.includes('%') && !stat.change.startsWith('-')) ? 'text-emerald-300' : 'text-orange-300'}>
                      {stat.change}
                    </span>
                    <span className="text-gray-400">{stat.changeLabel}</span>
                  </div>
                </div>
                <div className={`w-12 h-12 rounded-lg bg-gradient-to-br ${stat.color} flex items-center justify-center shadow-lg relative`}
                     style={{ boxShadow: '0 0 15px rgba(16, 185, 129, 0.5)' }}>
                  <stat.icon className="w-6 h-6 text-white relative z-10" />
                </div>
              </div>
            </div>
          ))}
        </div>
        
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 mt-4">
          {/* 左侧列 - 年龄分布 */}
          <div className="space-y-4 flex flex-col">
            <div className="bg-teal-900/50 backdrop-blur-md border-2 border-emerald-400/50 rounded-lg p-5 shadow-lg h-full flex flex-col relative overflow-hidden"
                 style={{ boxShadow: '0 0 20px rgba(16, 185, 129, 0.3), inset 0 0 20px rgba(16, 185, 129, 0.1)' }}>
              <div className="absolute -top-1 -left-1 w-8 h-8 border-t-2 border-l-2 border-emerald-400/70"></div>
              <div className="absolute -top-1 -right-1 w-8 h-8 border-t-2 border-r-2 border-emerald-400/70"></div>
              
              <div className="flex items-center justify-between mb-2 relative z-10">
                <h3 className="text-lg text-emerald-300" style={{ textShadow: '0 0 10px rgba(16, 185, 129, 0.8)' }}>年龄分布</h3>
                <span className="text-xs text-gray-400">Age Distribution</span>
              </div>
              
              <div className="flex gap-4 flex-1 relative z-10">
                <div className="flex-1">
                  <ResponsiveContainer width="100%" height={210}>
                    <PieChart>
                      <Pie
                        data={ageData}
                        cx="50%"
                        cy="50%"
                        labelLine={false}
                        label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                        outerRadius={80}
                        fill="#8884d8"
                        dataKey="value"
                      >
                        {ageData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Pie>
                      <Tooltip 
                        contentStyle={{ 
                          backgroundColor: '#134e4a', 
                          border: '1px solid #10b981',
                          borderRadius: '8px',
                          color: '#ffffff'
                        }}
                      />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
                
                <div className="w-32 flex flex-col justify-center space-y-2">
                  <div className="text-center p-1.5 bg-emerald-900/30 rounded-lg border border-emerald-400/30">
                    <div className="text-xs text-gray-400">总人数</div>
                    <div className="text-xl text-emerald-300">1,248</div>
                  </div>
                  <div className="text-center p-1.5 bg-teal-900/30 rounded-lg border border-teal-400/30">
                    <div className="text-xs text-gray-400">平均年龄</div>
                    <div className="text-xl text-teal-300">74岁</div>
                  </div>
                  <div className="text-center p-1.5 bg-cyan-900/30 rounded-lg border border-cyan-400/30">
                    <div className="text-xs text-gray-400">最大年龄</div>
                    <div className="text-xl text-cyan-300">96岁</div>
                  </div>
                </div>
              </div>
              
              <div className="grid grid-cols-2 gap-3 mt-2 relative z-10">
                {ageData.map((item, index) => (
                  <div key={index} className="flex items-center gap-2 bg-slate-800/30 p-2 rounded">
                    <div className="w-3 h-3 rounded-full" style={{ backgroundColor: item.color, boxShadow: `0 0 8px ${item.color}` }}></div>
                    <span className="text-sm text-white">{item.name}</span>
                    <span className="text-sm ml-auto text-white">{item.value}人</span>
                  </div>
                ))}
              </div>
            </div>
            
            {/* 健康监测 */}
            <div className="bg-teal-900/50 backdrop-blur-md border-2 border-emerald-400/50 rounded-lg p-5 shadow-lg relative"
                 style={{ boxShadow: '0 0 20px rgba(16, 185, 129, 0.3)' }}>
              <div className="absolute -top-1 -left-1 w-8 h-8 border-t-2 border-l-2 border-emerald-400/70"></div>
              <h3 className="text-lg text-emerald-300 mb-4" style={{ textShadow: '0 0 10px rgba(16, 185, 129, 0.8)' }}>健康监测</h3>
              <ResponsiveContainer width="100%" height={200}>
                <BarChart data={healthData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                  <XAxis dataKey="name" stroke="#94a3b8" />
                  <YAxis stroke="#94a3b8" />
                  <Tooltip 
                    contentStyle={{ 
                      backgroundColor: '#134e4a', 
                      border: '1px solid #10b981',
                      borderRadius: '8px'
                    }}
                  />
                  <Legend />
                  <Bar dataKey="normal" fill="#10b981" name="正常" radius={[8, 8, 0, 0]} />
                  <Bar dataKey="abnormal" fill="#f59e0b" name="异常" radius={[8, 8, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
            
            {/* 本月服务统计 */}
            <div className="bg-teal-900/50 backdrop-blur-md border-2 border-emerald-400/50 rounded-lg p-5 shadow-lg flex-1 relative"
                 style={{ boxShadow: '0 0 20px rgba(16, 185, 129, 0.3)' }}>
              <div className="absolute -bottom-1 -left-1 w-8 h-8 border-b-2 border-l-2 border-emerald-400/70"></div>
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg text-emerald-300" style={{ textShadow: '0 0 10px rgba(16, 185, 129, 0.8)' }}>本月服务统计</h3>
                <span className="text-xs text-gray-400">Service Statistics</span>
              </div>
              
              <div className="space-y-3">
                {serviceData.map((item, index) => (
                  <div key={index} className="space-y-1">
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-gray-300">{item.name}</span>
                      <span className="text-white font-medium">{item.value}次</span>
                    </div>
                    <div className="h-2 bg-slate-700/50 rounded-full overflow-hidden">
                      <div 
                        className="h-full rounded-full transition-all duration-1000"
                        style={{ 
                          width: `${(item.value / 200) * 100}%`,
                          backgroundColor: item.color,
                          boxShadow: `0 0 8px ${item.color}`
                        }}
                      />
                    </div>
                  </div>
                ))}
              </div>
              
              <div className="mt-4 pt-4 border-t border-emerald-400/30 flex items-center justify-between">
                <span className="text-gray-400">服务总次数</span>
                <div className="flex items-baseline gap-1">
                  <AnimatedNumber value={totalServices} className="text-2xl text-emerald-300" />
                  <span className="text-lg text-gray-300">次</span>
                </div>
              </div>
            </div>
          </div>
          
          {/* 中间列 - 近7日趋势 + 运动活跃度 */}
          <div className="space-y-4 flex flex-col">
            {/* 近7日趋势 */}
            <div className="bg-teal-900/50 backdrop-blur-md border-2 border-emerald-400/50 rounded-lg p-5 shadow-lg relative"
                 style={{ boxShadow: '0 0 20px rgba(16, 185, 129, 0.3)' }}>
              <div className="absolute -top-1 -right-1 w-8 h-8 border-t-2 border-r-2 border-emerald-400/70"></div>
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg text-emerald-300" style={{ textShadow: '0 0 10px rgba(16, 185, 129, 0.8)' }}>近7日趋势</h3>
                <span className="text-xs text-gray-400">Weekly Trend</span>
              </div>
              <ResponsiveContainer width="100%" height={200}>
                <LineChart data={weeklyTrendData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                  <XAxis dataKey="date" stroke="#94a3b8" fontSize={12} />
                  <YAxis stroke="#94a3b8" fontSize={12} />
                  <Tooltip 
                    contentStyle={{ 
                      backgroundColor: '#134e4a', 
                      border: '1px solid #10b981',
                      borderRadius: '8px'
                    }}
                  />
                  <Legend />
                  <Line type="monotone" dataKey="服务次数" stroke="#10b981" strokeWidth={2} dot={{ r: 4, fill: '#10b981' }} />
                  <Line type="monotone" dataKey="预警次数" stroke="#f59e0b" strokeWidth={2} dot={{ r: 4, fill: '#f59e0b' }} />
                </LineChart>
              </ResponsiveContainer>
              <div className="grid grid-cols-2 gap-4 mt-4 pt-4 border-t border-emerald-400/30">
                <div className="text-center">
                  <div className="text-xs text-gray-400">平均服务次数/日</div>
                  <div className="text-xl text-emerald-300 font-bold">{avgServicePerDay} <span className="text-sm text-gray-400">次</span></div>
                </div>
                <div className="text-center">
                  <div className="text-xs text-gray-400">平均预警次数/日</div>
                  <div className="text-xl text-orange-300 font-bold">{avgAlertPerDay} <span className="text-sm text-gray-400">次</span></div>
                </div>
              </div>
            </div>
            
            {/* 运动活跃度 */}
            <div className="bg-teal-900/50 backdrop-blur-md border-2 border-emerald-400/50 rounded-lg p-5 shadow-lg flex-1 relative flex flex-col"
                 style={{ boxShadow: '0 0 20px rgba(16, 185, 129, 0.3)' }}>
              <div className="absolute -bottom-1 -right-1 w-8 h-8 border-b-2 border-r-2 border-emerald-400/70"></div>
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-lg text-emerald-300" style={{ textShadow: '0 0 10px rgba(16, 185, 129, 0.8)' }}>运动活跃度</h3>
                <span className="text-xs text-gray-400">Activity Level</span>
              </div>
              
              {/* 大号环形图居中 + 中心数据 */}
              <div className="flex-1 flex items-center justify-center relative min-h-0">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={activityData}
                      cx="50%"
                      cy="50%"
                      innerRadius="55%"
                      outerRadius="85%"
                      paddingAngle={3}
                      dataKey="value"
                    >
                      {activityData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} stroke="transparent" />
                      ))}
                    </Pie>
                    <Tooltip 
                      contentStyle={{ 
                        backgroundColor: '#134e4a', 
                        border: '1px solid #10b981',
                        borderRadius: '8px'
                      }}
                      formatter={(value: number, name: string) => [`${value}人`, name]}
                    />
                  </PieChart>
                </ResponsiveContainer>
                {/* 中心文字 */}
                <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                  <div className="text-center">
                    <div className="text-3xl font-bold text-white" style={{ textShadow: '0 0 20px rgba(16, 185, 129, 0.8)' }}>
                      80%
                    </div>
                    <div className="text-xs text-gray-400">活跃率</div>
                  </div>
                </div>
              </div>
              
              {/* 图例横向分布 */}
              <div className="flex justify-center gap-4 py-3">
                {activityData.map((item, index) => (
                  <div key={index} className="flex items-center gap-1.5">
                    <div className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: item.color, boxShadow: `0 0 6px ${item.color}` }}></div>
                    <span className="text-xs text-gray-300">{item.name}</span>
                    <span className="text-xs text-white font-medium">{item.percentage}%</span>
                  </div>
                ))}
              </div>
              
              {/* 底部数据卡片 */}
              <div className="grid grid-cols-2 gap-3">
                <div className="text-center p-3 rounded-lg relative overflow-hidden" 
                     style={{ background: 'linear-gradient(135deg, rgba(16,185,129,0.3) 0%, rgba(6,182,212,0.2) 100%)' }}>
                  <div className="absolute inset-0 bg-gradient-to-r from-emerald-500/10 to-transparent"></div>
                  <div className="relative">
                    <div className="text-xs text-gray-400 mb-1">日均步数</div>
                    <div className="flex items-baseline justify-center gap-1">
                      <AnimatedNumber value={avgSteps} className="text-2xl font-bold text-emerald-300" style={{ textShadow: '0 0 10px rgba(16, 185, 129, 0.6)' }} />
                      <span className="text-sm text-gray-400">步</span>
                    </div>
                  </div>
                </div>
                <div className="text-center p-3 rounded-lg relative overflow-hidden"
                     style={{ background: 'linear-gradient(135deg, rgba(6,182,212,0.3) 0%, rgba(59,130,246,0.2) 100%)' }}>
                  <div className="absolute inset-0 bg-gradient-to-r from-cyan-500/10 to-transparent"></div>
                  <div className="relative">
                    <div className="text-xs text-gray-400 mb-1">日均活动时长</div>
                    <div className="flex items-baseline justify-center gap-1">
                      <AnimatedNumber value={avgActiveMinutes} className="text-2xl font-bold text-cyan-300" style={{ textShadow: '0 0 10px rgba(6, 182, 212, 0.6)' }} />
                      <span className="text-sm text-gray-400">分钟</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          {/* 右侧列 - 告警和设备状态 */}
          <div className="space-y-4 flex flex-col">
            {/* 实时告警 */}
            <div className="bg-teal-900/50 backdrop-blur-md border-2 border-emerald-400/50 rounded-lg p-5 shadow-lg relative"
                 style={{ boxShadow: '0 0 20px rgba(16, 185, 129, 0.3)', maxHeight: '400px' }}>
              <div className="absolute -top-1 -right-1 w-8 h-8 border-t-2 border-r-2 border-emerald-400/70"></div>
              <h3 className="text-lg text-emerald-300 mb-4" style={{ textShadow: '0 0 10px rgba(16, 185, 129, 0.8)' }}>实时告警</h3>
              <div className="space-y-3 overflow-y-auto" style={{ maxHeight: '320px' }}>
                {alerts.map((alert, index) => (
                  <div 
                    key={index}
                    className={`p-3 rounded-lg border-l-4 ${
                      alert.level === 'high' 
                        ? 'bg-red-900/30 border-red-500' 
                        : alert.level === 'medium'
                        ? 'bg-yellow-900/30 border-yellow-500'
                        : 'bg-blue-900/30 border-blue-500'
                    }`}
                  >
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-white">{alert.name}</span>
                      <span className="text-xs text-gray-400">{alert.time}</span>
                    </div>
                    <div className="text-sm text-gray-300">{alert.type}</div>
                    <div className="text-xs text-gray-400 mt-1">{alert.status}</div>
                  </div>
                ))}
              </div>
            </div>
            
            {/* 今日预警统计 */}
            <div className="bg-teal-900/50 backdrop-blur-md border-2 border-emerald-400/50 rounded-lg p-5 shadow-lg flex-1 relative flex flex-col"
                 style={{ boxShadow: '0 0 20px rgba(16, 185, 129, 0.3)' }}>
              <div className="absolute -bottom-1 -right-1 w-8 h-8 border-b-2 border-r-2 border-emerald-400/70"></div>
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-lg text-emerald-300" style={{ textShadow: '0 0 10px rgba(16, 185, 129, 0.8)' }}>今日预警统计</h3>
              </div>
              
              {/* 顶部大数字 */}
              <div className="text-center py-4 mb-2 rounded-xl" style={{ background: 'linear-gradient(135deg, rgba(16,185,129,0.2) 0%, rgba(6,182,212,0.1) 100%)' }}>
                <div className="text-xs text-gray-400 mb-1">今日预警总数</div>
                <div className="text-5xl font-bold text-emerald-300" style={{ textShadow: '0 0 30px rgba(16, 185, 129, 0.8)' }}>
                  {totalAlerts}
                </div>
                <div className="text-sm text-gray-400 mt-1">较昨日 <span className="text-red-400">+2</span></div>
              </div>
              
              {/* 三个预警类型卡片 */}
              <div className="flex-1 flex flex-col justify-center space-y-3">
                {alertStatsData.map((item, index) => {
                  const percentage = (item.count / totalAlerts) * 100;
                  return (
                    <div key={index} className="p-3 rounded-xl flex items-center gap-4" 
                         style={{ background: `linear-gradient(90deg, ${item.color}15 0%, transparent 100%)`, borderLeft: `3px solid ${item.color}` }}>
                      {/* 圆环 */}
                      <div className="relative w-14 h-14 flex-shrink-0">
                        <svg className="w-full h-full transform -rotate-90">
                          <circle cx="28" cy="28" r="22" fill="transparent" stroke="rgba(255,255,255,0.1)" strokeWidth="5" />
                          <circle cx="28" cy="28" r="22" fill="transparent" stroke={item.color} strokeWidth="5" strokeLinecap="round"
                            strokeDasharray={2 * Math.PI * 22} strokeDashoffset={2 * Math.PI * 22 * (1 - percentage / 100)}
                            style={{ filter: `drop-shadow(0 0 4px ${item.color})` }} />
                        </svg>
                        <div className="absolute inset-0 flex items-center justify-center">
                          <span className="text-lg font-bold" style={{ color: item.color }}>{item.count}</span>
                        </div>
                      </div>
                      {/* 信息 */}
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <span className="text-lg">{item.icon}</span>
                          <span className="text-white font-medium">{item.name}预警</span>
                        </div>
                        <div className="h-2 bg-slate-700/50 rounded-full overflow-hidden">
                          <div className="h-full rounded-full" style={{ width: `${percentage}%`, background: `linear-gradient(90deg, ${item.color}, ${item.color}80)`, boxShadow: `0 0 8px ${item.color}` }} />
                        </div>
                      </div>
                      {/* 百分比 */}
                      <div className="text-right">
                        <div className="text-2xl font-bold" style={{ color: item.color }}>{percentage.toFixed(0)}%</div>
                      </div>
                    </div>
                  );
                })}
              </div>
              
              {/* 底部提示 */}
              <div className="mt-3 pt-3 border-t border-emerald-400/30 flex items-center justify-between text-xs text-gray-400">
                <span>🕐 最近更新: 14:25</span>
                <span>📊 处理率: 87%</span>
              </div>
            </div>
          </div>
        </div>
        
        {/* 底部社区2D数字孪生地图 */}
        <div className="mt-4 h-[800px]">
          <CommunityMap2D />
        </div>
      </div>
    </div>
  );
}