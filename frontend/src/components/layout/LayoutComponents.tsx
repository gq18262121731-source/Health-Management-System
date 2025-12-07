import React from 'react';
import { Activity, User, Brain, LogOut, MessageSquareText, FileText } from 'lucide-react';
import { Button } from "../ui/button";
import { Avatar, AvatarFallback, AvatarImage } from "../ui/avatar";
import { Sheet, SheetContent, SheetTrigger } from "../ui/sheet";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "../ui/tooltip";
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

  return (
    <div className="flex h-16 items-center px-6 pl-8"> 
      <div className="flex items-center text-muted-foreground">
        <span className="mr-2 text-[20px]">智慧健康管理系统</span>
        <span className="mr-2 text-[20px]">/</span>
        <span className="text-foreground font-medium text-[20px]">{getPageName()}</span>
      </div>
    </div>
  );
}