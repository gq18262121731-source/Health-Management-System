import { useState, useEffect } from 'react';
import { Header } from './components/Header';
import { StatCards } from './components/StatCards';
import { AgeDistribution } from './components/AgeDistribution';
import { HealthMonitoring } from './components/HealthMonitoring';
import { ServiceStats } from './components/ServiceStats';
import { AlertList } from './components/AlertList';
import { DeviceStatus } from './components/DeviceStatus';
import { TrendChart } from './components/TrendChart';
import { AnimatedBackground } from './components/AnimatedBackground';
import { CommunityMap2D } from './components/CommunityMap2D';

export default function App() {
  const [currentTime, setCurrentTime] = useState(new Date());

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  return (
    <div className="min-h-screen bg-slate-700 text-gray-100 p-4 overflow-auto relative">
      {/* 动态背景效果 */}
      <AnimatedBackground />
      
      {/* 背景图片层 */}
      <div className="fixed inset-0 z-0 pointer-events-none">
        <div className="absolute inset-0 bg-gradient-to-br from-emerald-900/80 via-teal-900/80 to-cyan-900/80"></div>
        <div 
          className="absolute inset-0 bg-cover bg-center opacity-30"
          style={{
            backgroundImage: `url('https://images.unsplash.com/photo-1480714378408-67cf0d13bc1b?w=1920&q=80')`,
            filter: 'blur(2px)'
          }}
        ></div>
        {/* 网格背景 */}
        <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDAiIGhlaWdodD0iNDAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PGRlZnM+PHBhdHRlcm4gaWQ9ImdyaWQiIHdpZHRoPSI0MCIgaGVpZ2h0PSI0MCIgcGF0dGVyblVuaXRzPSJ1c2VyU3BhY2VPblVzZSI+PHBhdGggZD0iTSA0MCAwIEwgMCAwIDAgNDAiIGZpbGw9Im5vbmUiIHN0cm9rZT0iIzEwYjk4MSIgc3Ryb2tlLXdpZHRoPSIwLjUiIG9wYWNpdHk9IjAuMyIvPjwvcGF0dGVybj48L2RlZnM+PHJlY3Qgd2lkdGg9IjEwMCUiIGhlaWdodD0iMTAwJSIgZmlsbD0idXJsKCNncmlkKSIvPjwvc3ZnPg==')] opacity-40"></div>
      </div>
      
      {/* 装饰光效 */}
      <div className="fixed top-0 left-0 w-full h-full pointer-events-none z-0">
        <div className="absolute top-20 left-20 w-96 h-96 bg-emerald-500/20 rounded-full blur-3xl"></div>
        <div className="absolute bottom-20 right-20 w-96 h-96 bg-teal-500/20 rounded-full blur-3xl"></div>
      </div>
      
      <div className="max-w-[1920px] mx-auto relative z-20">
        <Header currentTime={currentTime} />
        
        <StatCards />
        
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 mt-4">
          {/* 左侧列 */}
          <div className="space-y-4 flex flex-col">
            <AgeDistribution />
            <ServiceStats />
          </div>
          
          {/* 中间列 */}
          <div className="space-y-4 flex flex-col">
            <HealthMonitoring />
            <TrendChart />
          </div>
          
          {/* 右侧列 */}
          <div className="space-y-4 flex flex-col">
            <AlertList />
            <DeviceStatus />
          </div>
        </div>
        
        {/* 底部社区平面图 */}
        <div className="mt-4 h-[900px]">
          <CommunityMap2D />
        </div>
      </div>
    </div>
  );
}