import React, { useState, useEffect } from 'react';
import { Heart, User, Lock, ArrowLeft, Volume2 } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from "../ui/card";
import { Button } from "../ui/button";
import { speechManager } from '../../services/speechManager';

interface ElderlyLoginPageProps {
  onBack: () => void;
  onLogin: () => void;
}

export function ElderlyLoginPage({ onBack, onLogin }: ElderlyLoginPageProps) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [rememberMe, setRememberMe] = useState(false);

  // 页面加载时读取保存的账号密码
  useEffect(() => {
    const savedUsername = localStorage.getItem('elderly_username');
    const savedPassword = localStorage.getItem('elderly_password');
    const savedRememberMe = localStorage.getItem('elderly_rememberMe');
    
    if (savedRememberMe === 'true' && savedUsername && savedPassword) {
      setUsername(savedUsername);
      setPassword(savedPassword);
      setRememberMe(true);
    }
  }, []);

  // 使用全局语音管理器播报
  const speak = (text: string) => {
    setIsSpeaking(true);
    speechManager.speak(text, {
      rate: 0.8,
      onEnd: () => setIsSpeaking(false),
      onError: () => setIsSpeaking(false)
    });
  };

  // 监听全局语音状态
  useEffect(() => {
    const handleSpeakingChange = (speaking: boolean) => {
      setIsSpeaking(speaking);
    };
    speechManager.addListener(handleSpeakingChange);
    return () => {
      speechManager.removeListener(handleSpeakingChange);
    };
  }, []);

  // 进入页面自动播报
  useEffect(() => {
    const timer = setTimeout(() => {
      speak('欢迎使用智慧健康管理系统老人端，请输入您的账号和密码');
    }, 500);
    
    return () => {
      clearTimeout(timer);
      speechManager.stop();
    };
  }, []);

  const handleLogin = () => {
    if (username && password) {
      // 保存账号密码到本地存储
      if (rememberMe) {
        localStorage.setItem('elderly_username', username);
        localStorage.setItem('elderly_password', password);
        localStorage.setItem('elderly_rememberMe', 'true');
      } else {
        // 如果取消记住密码，清除保存的信息
        localStorage.removeItem('elderly_username');
        localStorage.removeItem('elderly_password');
        localStorage.removeItem('elderly_rememberMe');
      }
      
      speak('登录成功，正在进入系统');
      setTimeout(() => {
        onLogin();
      }, 1000);
    } else {
      speak('请输入账号和密码');
    }
  };

  return (
    <div className="min-h-screen w-full bg-gradient-to-br from-teal-50 via-emerald-50 to-green-50 flex items-center justify-center p-8">
      <div className="w-full max-w-3xl">
        {/* 返回按钮 - 超大 */}
        <Button
          variant="ghost"
          size="lg"
          onClick={() => {
            speak('返回选择界面');
            setTimeout(onBack, 500);
          }}
          className="mb-8 text-[32px] py-10 px-8 hover:bg-teal-100"
        >
          <ArrowLeft className="mr-4 h-12 w-12" />
          返回
        </Button>

        <Card className="border-4 border-teal-300 shadow-2xl bg-white">
          <CardHeader className="pb-8 bg-gradient-to-r from-teal-100 to-emerald-100 border-b-4 border-teal-300">
            <div className="flex flex-col items-center gap-6">
              {/* Logo - 超大 */}
              <div className="w-32 h-32 rounded-full bg-gradient-to-br from-[#0d9488] to-[#14b8a6] flex items-center justify-center shadow-xl">
                <Heart className="h-20 w-20 text-white" />
              </div>
              
              {/* 标题 - 特大字体 */}
              <div className="text-center space-y-4">
                <CardTitle className="text-[64px] font-bold text-slate-800 leading-tight">
                  老人端登录
                </CardTitle>
                <p className="text-[36px] text-slate-600">
                  个人健康监测与管理
                </p>
              </div>

              {/* 语音播报按钮 */}
              <Button
                variant="outline"
                size="lg"
                onClick={() => speak('欢迎使用智慧健康管理系统老人端，请输入您的账号和密码')}
                className={`text-[28px] py-8 px-10 border-3 ${isSpeaking ? 'bg-teal-100 border-teal-500' : 'border-teal-300'}`}
              >
                <Volume2 className={`mr-3 h-10 w-10 ${isSpeaking ? 'animate-pulse text-teal-600' : 'text-teal-500'}`} />
                {isSpeaking ? '播报中...' : '语音播报'}
              </Button>
            </div>
          </CardHeader>

          <CardContent className="pt-12 pb-12 px-12 space-y-10">
            {/* 账号输入 */}
            <div className="space-y-6">
              <label className="flex items-center gap-4 text-[40px] font-semibold text-slate-700">
                <User className="h-12 w-12 text-teal-600" />
                账号
              </label>
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                onFocus={() => speak('请输入账号')}
                placeholder="请输入您的账号"
                className="w-full px-10 py-10 text-[40px] border-4 border-slate-300 rounded-2xl 
                         focus:outline-none focus:border-teal-500 focus:ring-4 focus:ring-teal-200
                         placeholder:text-slate-400 bg-slate-50"
              />
            </div>

            {/* 密码输入 */}
            <div className="space-y-6">
              <label className="flex items-center gap-4 text-[40px] font-semibold text-slate-700">
                <Lock className="h-12 w-12 text-teal-600" />
                密码
              </label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                onFocus={() => speak('请输入密码')}
                placeholder="请输入您的密码"
                className="w-full px-10 py-10 text-[40px] border-4 border-slate-300 rounded-2xl 
                         focus:outline-none focus:border-teal-500 focus:ring-4 focus:ring-teal-200
                         placeholder:text-slate-400 bg-slate-50"
              />
            </div>

            {/* 记住我 - 适老化设计 */}
            <div className="flex items-center gap-6 bg-teal-50 p-6 rounded-xl border-2 border-teal-200">
              <input
                type="checkbox"
                id="rememberMe"
                checked={rememberMe}
                onChange={(e) => {
                  setRememberMe(e.target.checked);
                  speak(e.target.checked ? '已开启记住密码' : '已关闭记住密码');
                }}
                onFocus={() => speak('记住密码选项')}
                className="h-10 w-10 text-teal-600 focus:ring-teal-500 focus:ring-4 border-4 border-gray-300 rounded-lg cursor-pointer"
              />
              <label 
                htmlFor="rememberMe" 
                className="text-[36px] font-semibold text-slate-700 cursor-pointer flex-1"
              >
                记住我的账号和密码
              </label>
            </div>

            {/* 登录按钮 - 超大 */}
            <Button
              size="lg"
              onClick={handleLogin}
              className="w-full text-[48px] py-16 mt-10 bg-gradient-to-r from-teal-500 to-emerald-500 
                       hover:from-teal-600 hover:to-emerald-600 rounded-2xl shadow-xl
                       hover:shadow-2xl transition-all duration-300 font-bold"
            >
              登录系统
            </Button>

            {/* 提示文字 - 大字体 */}
            <div className="text-center text-[28px] text-slate-500 pt-6 space-y-3">
              <p>💡 首次使用？账号：demo 密码：123456</p>
              <p className="text-[24px] text-slate-400">如有问题，请联系社区工作人员</p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}