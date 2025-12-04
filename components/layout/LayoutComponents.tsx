import React, { useState, useEffect } from 'react';
import { Activity, BarChart2, Calendar, Sprout, Home, Settings, User, Brain, LogOut, Menu, MessageSquareText, FileText, Volume2, StopCircle } from 'lucide-react';
import { Button } from "../ui/button";
import { Avatar, AvatarFallback, AvatarImage } from "../ui/avatar";
import { Sheet, SheetContent, SheetTrigger } from "../ui/sheet";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "../ui/tooltip";
import { speechManager } from '../../services/speechManager';
import logoImage from 'figma:asset/5c227ba3fcc87ef2343e011cf298867b85205e30.png';

interface NavbarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  onLogout?: () => void;
}

export function Navbar({ activeTab, setActiveTab, onLogout }: NavbarProps) {
  const menuItems = [
    { id: 'analysis', icon: Activity, label: '今日健康' },
    { id: 'reports', icon: FileText, label: '我的报告' },
    { id: 'consultation', icon: MessageSquareText, label: 'AI健康助手' },
    { id: 'psychology', icon: Brain, label: '心理健康' },
    { id: 'myinfo', icon: User, label: '我的信息' },
  ];

  return (
    <nav className="fixed left-0 top-0 z-50 h-full w-[590px] bg-gradient-to-b from-[#0d9488] to-[#0f766e] shadow-xl flex flex-col">
      {/* Logo Section */}
      <div className="flex items-center justify-center py-6 border-b border-white/20">
        <img src={logoImage} alt="养生之道" className="h-14 w-auto object-contain" />
      </div>

      {/* Navigation Menu */}
      <div className="flex-1 flex flex-col py-4 px-3 space-y-2">
        {menuItems.map((item) => {
          const isActive = activeTab === item.id;
          
          return (
            <Button
              key={item.id}
              variant={isActive ? "secondary" : "ghost"}
              className={`justify-start h-20 px-6 text-[32px] w-full rounded-xl transition-all duration-200
                ${isActive 
                  ? 'bg-white text-teal-700 hover:bg-white shadow-md' 
                  : 'text-white/90 hover:text-white hover:bg-white/20'
                }`}
              onClick={() => setActiveTab(item.id)}
            >
              <item.icon className="mr-4 h-9 w-9 flex-shrink-0" />
              <span className="truncate font-semibold">{item.label}</span>
            </Button>
          );
        })}
      </div>

      {/* Bottom Actions - 退出登录按钮 */}
      <div className="p-3 border-t border-white/20">
        {onLogout && (
          <Button 
            variant="outline" 
            size="lg" 
            onClick={onLogout}
            className="w-full text-[28px] px-6 py-6 h-18 bg-white/95 text-teal-700 border-2 border-white hover:bg-white hover:text-teal-800 hover:border-white shadow-md transition-all duration-200 hover:shadow-lg font-semibold rounded-xl"
          >
            <LogOut className="mr-4 h-8 w-8" />
            退出登录
          </Button>
        )}
      </div>
    </nav>
  );
}

export function Header({ activeTab }: { activeTab: string }) {
  const [zoomLevel, setZoomLevel] = useState(1);
  const [isSpeaking, setIsSpeaking] = useState(false);

  // 根据activeTab获取当前页面名称
  const getPageName = () => {
    switch (activeTab) {
      case 'analysis':
        return '今日健康';
      case 'reports':
        return '我的报告';
      case 'consultation':
        return 'AI健康助手';
      case 'psychology':
        return '心理健康';
      case 'myinfo':
        return '我的信息';
      default:
        return '今日健康';
    }
  };

  const handleZoom = () => {
    const nextLevel = zoomLevel >= 1.2 ? 1 : zoomLevel + 0.1;
    setZoomLevel(nextLevel);
    document.documentElement.style.fontSize = `${nextLevel * 100}%`;
  };

  const handleSpeak = () => {
    if (isSpeaking) {
      speechManager.stop();
      setIsSpeaking(false);
    } else {
      const summary = "下午好，张三。这是你今天的健康监测概览。平均心率72，血压118/75，血氧98%，体温36.5度。";
      setIsSpeaking(true);
      speechManager.speak(summary, {
        rate: 1,
        onEnd: () => setIsSpeaking(false),
        onError: () => setIsSpeaking(false)
      });
    }
  };

  // 监听全局语音状态
  useEffect(() => {
    const handleSpeakingChange = (speaking: boolean) => {
      setIsSpeaking(speaking);
    };
    speechManager.addListener(handleSpeakingChange);
    return () => {
      speechManager.removeListener(handleSpeakingChange);
      speechManager.stop();
    };
  }, []);

  return (
    <div className="flex h-12 items-center justify-between px-6 pl-8 border-b"> 
      <div className="flex items-center text-sm text-muted-foreground">
        <span className="mr-2">智慧健康管理系统</span>
        <span className="mr-2">/</span>
        <span className="text-foreground font-medium">{getPageName()}</span>
      </div>
      
      <div className="flex items-center gap-3 border-l pl-4">
        <Button 
          variant="ghost" 
          size="lg"
          className={`h-12 px-4 gap-2 text-[20px] ${isSpeaking ? 'text-blue-500 animate-pulse' : 'text-slate-700 hover:text-foreground hover:bg-slate-100'}`}
          onClick={handleSpeak}
        >
          {isSpeaking ? <StopCircle className="h-6 w-6" /> : <Volume2 className="h-6 w-6" />}
          <span className="text-[32px] font-bold">{isSpeaking ? '停止播报' : '语音播报'}</span>
        </Button>
      </div>
    </div>
  );
}