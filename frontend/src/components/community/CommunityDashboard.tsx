import React, { useState } from 'react';
import { DataVisualization } from './DataVisualization';
import { BigScreenDashboard } from './BigScreenDashboard';
import { GroupHealthAnalysis } from './GroupHealthAnalysis';
import { AlertManagement } from './AlertManagement';
import { BarChart3, Users, AlertTriangle, LogOut, Monitor } from 'lucide-react';
import { Button } from '../ui/button';
import { TechBackground } from '../ui/TechBackground';
import logoImage from 'figma:asset/5c227ba3fcc87ef2343e011cf298867b85205e30.png';

interface CommunityDashboardProps {
  onLogout: () => void;
}

// 社区端侧边栏组件 - 橙色/琥珀色主题
function CommunityNavbar({ activeView, setActiveView, onLogout }: { 
  activeView: string; 
  setActiveView: (view: string) => void; 
  onLogout: () => void;
}) {
  const menuItems = [
    { id: 'bigscreen', icon: Monitor, label: '数据大屏' },
    { id: 'visualization', icon: BarChart3, label: '数据可视化' },
    { id: 'analysis', icon: Users, label: '群体分析' },
    { id: 'alerts', icon: AlertTriangle, label: '预警管理' },
  ];

  return (
    <nav className="fixed left-0 top-0 z-50 h-full w-[590px] bg-gradient-to-b from-amber-500 to-orange-600 shadow-xl flex flex-col">
      {/* Logo Section */}
      <div className="flex items-center justify-center py-6 border-b border-white/20">
        <img src={logoImage} alt="养生之道" className="h-14 w-auto object-contain" />
      </div>

      {/* Navigation Menu */}
      <div className="flex-1 flex flex-col py-4 px-3 space-y-2">
        {menuItems.map((item) => {
          const isActive = activeView === item.id;
          
          return (
            <Button
              key={item.id}
              variant={isActive ? "secondary" : "ghost"}
              className={`justify-start h-20 px-6 text-[32px] w-full rounded-xl transition-all duration-200
                ${isActive 
                  ? 'bg-white text-amber-700 hover:bg-white shadow-md' 
                  : 'text-white/90 hover:text-white hover:bg-white/20'
                }`}
              onClick={() => setActiveView(item.id)}
            >
              <item.icon className="mr-4 h-9 w-9 flex-shrink-0" />
              <span className="truncate font-semibold">{item.label}</span>
            </Button>
          );
        })}
      </div>

      {/* Bottom Actions - 退出登录按钮 */}
      <div className="p-3 border-t border-white/20">
        <Button 
          variant="outline" 
          size="lg" 
          onClick={onLogout}
          className="w-full text-[28px] px-6 py-6 h-18 bg-white/95 text-amber-700 border-2 border-white hover:bg-white hover:text-amber-800 hover:border-white shadow-md transition-all duration-200 hover:shadow-lg font-semibold rounded-xl"
        >
          <LogOut className="mr-4 h-8 w-8" />
          退出登录
        </Button>
      </div>
    </nav>
  );
}

// 社区端头部组件
function CommunityHeader({ activeView }: { activeView: string }) {
  const getPageName = () => {
    switch (activeView) {
      case 'bigscreen':
        return '数据大屏';
      case 'visualization':
        return '数据可视化';
      case 'analysis':
        return '群体健康分析';
      case 'alerts':
        return '预警与干预管理';
      default:
        return '数据可视化';
    }
  };

  return (
    <div className="flex h-12 items-center justify-between px-6 pl-8 border-b"> 
      <div className="flex items-center text-sm text-muted-foreground">
        <span className="mr-2">智慧健康管理系统</span>
        <span className="mr-2">/</span>
        <span className="text-foreground font-medium">{getPageName()}</span>
      </div>
      
      <div className="flex items-center gap-3 border-l pl-4">
        <span className="text-lg text-muted-foreground">
          {new Date().toLocaleDateString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric', weekday: 'long' })}
        </span>
      </div>
    </div>
  );
}

export function CommunityDashboard({ onLogout }: CommunityDashboardProps) {
  const [activeView, setActiveView] = useState('visualization');

  // 大屏模式 - 全屏显示，不显示侧边栏
  if (activeView === 'bigscreen') {
    return (
      <div className="min-h-screen bg-slate-900">
        <BigScreenDashboard onBack={() => setActiveView('visualization')} />
      </div>
    );
  }

  return (
    <div className="min-h-screen w-full bg-slate-50 text-slate-900 dark:text-slate-50 font-sans relative">
      {/* 科技感背景 */}
      <TechBackground />
      
      {/* 左侧侧边栏导航 - 橙色主题 */}
      <CommunityNavbar activeView={activeView} setActiveView={setActiveView} onLogout={onLogout} />
      
      {/* 主内容区 - 左侧留出侧边栏空间 */}
      <div className="flex flex-col relative z-10 ml-[610px]">
        {/* 顶部面包屑 */}
        <CommunityHeader activeView={activeView} />
        
        <main className="flex-1 p-6 pl-8">
          <div className="mx-auto max-w-7xl space-y-6">
            {activeView === 'visualization' && <DataVisualization />}
            {activeView === 'analysis' && <GroupHealthAnalysis />}
            {activeView === 'alerts' && <AlertManagement />}
          </div>
        </main>
      </div>
    </div>
  );
}