import React, { useState } from 'react';
import { ElderlyList } from './ElderlyList';
import { ElderlyDetail } from './ElderlyDetail';
import { SmartReminders } from './SmartReminders';
import { ChildrenAIAssistant } from './ChildrenAIAssistant';
import { Users, Bell, MessageSquare, LogOut } from 'lucide-react';
import { Button } from '../ui/button';
import { TechBackground } from '../ui/TechBackground';
import logoImage from 'figma:asset/5c227ba3fcc87ef2343e011cf298867b85205e30.png';

// ============================================================================
// 组件说明：子女端仪表板
// 
// 涉及API:
// - GET /api/v1/children/elders/list - 获取关联的老人列表
// - GET /api/v1/children/reminders/list - 获取提醒列表
// - POST /api/v1/children/ai/chat - AI助手对话
// 
// 功能模块：
// 1. 老人列表：查看所有关联的老人及其健康状况
// 2. 智能提醒：管理对老人的提醒（吃药、运动、复诊等）
// 3. AI助手：智能健康咨询和建议
// 4. 老人详情：查看单个老人的详细健康数据（点击列表项进入）
// 
// 数据流：
// - 登录后立即加载老人列表
// - 老人列表包含基础健康指标（体温、血压、心率等）
// - 点击老人卡片查看详细数据和实时监测
// ============================================================================

interface ChildrenDashboardProps {
  onLogout: () => void;
}

// 子女端侧边栏组件 - 与老人端布局一致，使用子女端蓝色主题
function ChildrenNavbar({ activeView, setActiveView, onLogout }: { 
  activeView: string; 
  setActiveView: (view: string) => void; 
  onLogout: () => void;
}) {
  const menuItems = [
    { id: 'list', icon: Users, label: '长辈列表' },
    { id: 'reminders', icon: Bell, label: '智能提醒' },
    { id: 'ai', icon: MessageSquare, label: 'AI健康助手' },
  ];

  return (
    <nav className="fixed left-0 top-0 z-50 h-full w-[590px] bg-gradient-to-b from-blue-500 to-indigo-600 shadow-xl flex flex-col">
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
                  ? 'bg-white text-blue-700 hover:bg-white shadow-md' 
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
          className="w-full text-[28px] px-6 py-6 h-18 bg-white/95 text-blue-700 border-2 border-white hover:bg-white hover:text-blue-800 hover:border-white shadow-md transition-all duration-200 hover:shadow-lg font-semibold rounded-xl"
        >
          <LogOut className="mr-4 h-8 w-8" />
          退出登录
        </Button>
      </div>
    </nav>
  );
}

// 子女端头部组件 - 与老人端样式一致
function ChildrenHeader({ activeView }: { activeView: string }) {
  const getPageName = () => {
    switch (activeView) {
      case 'list':
        return '老人列表';
      case 'detail':
        return '老人详情';
      case 'reminders':
        return '智能提醒';
      case 'ai':
        return 'AI健康助手';
      default:
        return '老人列表';
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

export function ChildrenDashboard({ onLogout }: ChildrenDashboardProps) {
  const [activeView, setActiveView] = useState('list');
  const [selectedElderly, setSelectedElderly] = useState<string | null>(null);

  // 处理查看老人详情
  const handleViewDetail = (elderlyId: string) => {
    setSelectedElderly(elderlyId);
    setActiveView('detail');
  };

  // 返回列表
  const handleBackToList = () => {
    setSelectedElderly(null);
    setActiveView('list');
  };

  return (
    <div className="min-h-screen w-full bg-slate-50 text-slate-900 dark:text-slate-50 font-sans relative">
      {/* 科技感背景 */}
      <TechBackground />
      
      {/* 左侧侧边栏导航 - 与老人端一致 */}
      <ChildrenNavbar activeView={activeView} setActiveView={setActiveView} onLogout={onLogout} />
      
      {/* 主内容区 - 左侧留出侧边栏空间 */}
      <div className="flex flex-col relative z-10 ml-[610px]">
        {/* 顶部面包屑 */}
        <ChildrenHeader activeView={activeView} />
        
        <main className="flex-1 p-6 pl-8">
          <div className="mx-auto max-w-7xl space-y-6">
            {activeView === 'list' && <ElderlyList onViewDetail={handleViewDetail} />}
            {activeView === 'detail' && selectedElderly && (
              <ElderlyDetail elderlyId={selectedElderly} onBack={handleBackToList} />
            )}
            {activeView === 'reminders' && <SmartReminders />}
            {activeView === 'ai' && <ChildrenAIAssistant />}
          </div>
        </main>
      </div>
    </div>
  );
}