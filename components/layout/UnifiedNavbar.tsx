import React from 'react';
import { Button } from '../ui/button';
import { LogOut, Volume2 } from 'lucide-react';
import { speechManager } from '../../services/speechManager';
import logoImage from 'figma:asset/5c227ba3fcc87ef2343e011cf298867b85205e30.png';

interface UnifiedNavbarProps {
  children: React.ReactNode;
  onLogout?: () => void;
  showVoice?: boolean; // 是否显示语音播报按钮（老人端显示）
  voiceText?: string; // 语音播报的文本内容
}

export function UnifiedNavbar({ children, onLogout, showVoice = false, voiceText }: UnifiedNavbarProps) {
  // 使用全局语音管理器播报
  const handleVoicePlay = () => {
    if (!voiceText) return;
    speechManager.speak(voiceText, { rate: 0.9 });
  };

  return (
    <nav className="sticky top-0 z-50 border-b bg-white/95 backdrop-blur supports-[backdrop-filter]:bg-white/60">
      <div className="flex h-20 items-center px-6 max-w-[1920px] mx-auto">
        {/* Logo */}
        <div className="flex items-center gap-3 mr-8">
          <img 
            src={logoImage} 
            alt="养生之道" 
            className="h-12 w-auto object-contain"
          />
        </div>

        {/* 导航菜单 */}
        <div className="flex gap-2 flex-1">
          {children}
        </div>

        {/* 右侧功能按钮 */}
        <div className="flex items-center gap-3">
          {/* 语音播报按钮（仅老人端显示） */}
          {showVoice && (
            <Button
              variant="outline"
              size="lg"
              onClick={handleVoicePlay}
              className="text-lg px-6 border-green-500 text-green-600 hover:bg-green-50"
            >
              <Volume2 className="mr-2 h-5 w-5" />
              语音播报
            </Button>
          )}

          {/* 退出登录 */}
          {onLogout && (
            <Button
              variant="outline"
              size="lg"
              onClick={onLogout}
              className="text-lg px-6 bg-teal-700 text-white border-2 border-teal-700 hover:bg-teal-800 hover:border-teal-800 shadow-md transition-all duration-200 hover:shadow-lg font-semibold"
            >
              <LogOut className="mr-2 h-5 w-5" />
              退出登录
            </Button>
          )}
        </div>
      </div>
    </nav>
  );
}