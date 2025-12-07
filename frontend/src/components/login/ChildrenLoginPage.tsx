import React, { useState } from 'react';
import { Users, User, Lock, ArrowLeft } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from "../ui/card";
import { Button } from "../ui/button";

interface ChildrenLoginPageProps {
  onBack: () => void;
  onLogin: () => void;
}

export function ChildrenLoginPage({ onBack, onLogin }: ChildrenLoginPageProps) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');

  const handleLogin = () => {
    if (username && password) {
      onLogin();
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleLogin();
    }
  };

  return (
    <div className="min-h-screen w-full bg-gradient-to-br from-blue-50 via-indigo-50 to-cyan-50 flex items-center justify-center p-6">
      <div className="w-full max-w-xl">
        {/* 返回按钮 */}
        <Button
          variant="ghost"
          size="lg"
          onClick={onBack}
          className="mb-6 text-xl py-6 px-6 hover:bg-blue-100"
        >
          <ArrowLeft className="mr-2 h-6 w-6" />
          返回
        </Button>

        <Card className="border-2 border-blue-300 shadow-xl bg-white">
          <CardHeader className="pb-6 bg-gradient-to-r from-blue-100 to-indigo-100 border-b-2 border-blue-300">
            <div className="flex flex-col items-center gap-4">
              {/* Logo */}
              <div className="w-24 h-24 rounded-full bg-gradient-to-br from-blue-500 to-indigo-500 flex items-center justify-center shadow-lg">
                <Users className="h-14 w-14 text-white" />
              </div>
              
              {/* 标题 */}
              <div className="text-center space-y-2">
                <CardTitle className="text-4xl font-bold text-slate-800">
                  子女端登录
                </CardTitle>
                <p className="text-xl text-slate-600">
                  远程关爱父母健康
                </p>
              </div>
            </div>
          </CardHeader>

          <CardContent className="pt-8 pb-8 px-8 space-y-6">
            {/* 账号输入 */}
            <div className="space-y-3">
              <label className="flex items-center gap-2 text-lg font-semibold text-slate-700">
                <User className="h-5 w-5 text-blue-600" />
                账号
              </label>
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="请输入账号"
                className="w-full px-4 py-4 text-lg border-2 border-slate-300 rounded-lg 
                         focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-200
                         placeholder:text-slate-400 bg-slate-50 transition-all"
              />
            </div>

            {/* 密码输入 */}
            <div className="space-y-3">
              <label className="flex items-center gap-2 text-lg font-semibold text-slate-700">
                <Lock className="h-5 w-5 text-blue-600" />
                密码
              </label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="请输入密码"
                className="w-full px-4 py-4 text-lg border-2 border-slate-300 rounded-lg 
                         focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-200
                         placeholder:text-slate-400 bg-slate-50 transition-all"
              />
            </div>

            {/* 记住密码选项 */}
            <div className="flex items-center justify-between pt-2">
              <label className="flex items-center gap-2 cursor-pointer">
                <input type="checkbox" className="w-5 h-5 text-blue-500 rounded" />
                <span className="text-base text-slate-600">记住密码</span>
              </label>
              <a href="#" className="text-base text-blue-600 hover:text-blue-700 hover:underline">
                忘记密码？
              </a>
            </div>

            {/* 登录按钮 */}
            <Button
              size="lg"
              onClick={handleLogin}
              className="w-full text-2xl py-8 mt-4 bg-gradient-to-r from-blue-500 to-indigo-500 
                       hover:from-blue-600 hover:to-indigo-600 rounded-lg shadow-lg
                       hover:shadow-xl transition-all duration-300 font-semibold"
            >
              登录
            </Button>

            {/* 提示文字 */}
            <div className="text-center text-base text-slate-500 pt-4 space-y-2">
              <p>💡 演示账号：demo / 密码：123456</p>
              <p className="text-sm text-slate-400">登录后可查看多位长辈的健康数据</p>
            </div>

            {/* 注册入口 */}
            <div className="text-center text-base text-slate-600 pt-4 border-t">
              还没有账号？
              <a href="#" className="text-blue-600 hover:text-blue-700 hover:underline ml-2">
                立即注册
              </a>
            </div>
          </CardContent>
        </Card>

        {/* 安全提示 */}
        <div className="text-center text-sm text-slate-500 mt-6">
          🔒 您的数据经过加密传输，确保隐私安全
        </div>
      </div>
    </div>
  );
}
