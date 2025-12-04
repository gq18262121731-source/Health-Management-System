import React from 'react';
import { Users, Heart, Shield, BarChart3 } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../ui/card";
import { Button } from "../ui/button";

interface LoginPageProps {
  onSelectRole: (role: 'elderly' | 'children' | 'community') => void;
}

export function LoginPage({ onSelectRole }: LoginPageProps) {
  return (
    <div className="min-h-screen w-full bg-gradient-to-br from-green-50 via-emerald-50 to-teal-50 flex items-center justify-center p-6">
      <div className="w-full max-w-5xl space-y-8">
        {/* Logo and Title */}
        <div className="text-center space-y-4">
          <div className="flex justify-center">
            <div className="w-20 h-20 rounded-full bg-gradient-to-br from-[#0d9488] to-[#14b8a6] flex items-center justify-center shadow-lg">
              <Heart className="h-12 w-12 text-white" />
            </div>
          </div>
          <h1 className="text-5xl font-bold text-slate-800">智慧健康管理系统</h1>
          <p className="text-2xl text-muted-foreground">关爱健康，智慧生活</p>
        </div>

        {/* Role Selection Cards */}
        <div className="grid grid-cols-3 gap-6 mt-12">
          {/* 老人端 */}
          <Card 
            className="hover:shadow-2xl transition-all cursor-pointer border-2 hover:border-teal-400 bg-white group"
            onClick={() => onSelectRole('elderly')}
          >
            <CardHeader className="pb-4">
              <div className="flex justify-center mb-4">
                <div className="w-24 h-24 rounded-full bg-gradient-to-br from-teal-100 to-teal-50 flex items-center justify-center group-hover:scale-110 transition-transform">
                  <Heart className="h-14 w-14 text-teal-600" />
                </div>
              </div>
              <CardTitle className="text-4xl text-center">老人端</CardTitle>
              <CardDescription className="text-xl text-center mt-3">
                个人健康监测与管理
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <ul className="space-y-3 text-lg text-muted-foreground">
                <li className="flex items-center gap-3">
                  <span className="text-teal-500 text-2xl">✓</span>
                  <span>实时健康数据监测</span>
                </li>
                <li className="flex items-center gap-3">
                  <span className="text-teal-500 text-2xl">✓</span>
                  <span>心理健康记录</span>
                </li>
                <li className="flex items-center gap-3">
                  <span className="text-teal-500 text-2xl">✓</span>
                  <span>AI健康小助手</span>
                </li>
                <li className="flex items-center gap-3">
                  <span className="text-teal-500 text-2xl">✓</span>
                  <span>健康报告生成</span>
                </li>
              </ul>
              <Button 
                size="lg" 
                className="w-full text-xl py-8 mt-6 bg-teal-500 hover:bg-teal-600"
              >
                进入老人端
              </Button>
            </CardContent>
          </Card>

          {/* 子女端 */}
          <Card 
            className="hover:shadow-2xl transition-all cursor-pointer border-2 hover:border-blue-400 bg-white group"
            onClick={() => onSelectRole('children')}
          >
            <CardHeader className="pb-4">
              <div className="flex justify-center mb-4">
                <div className="w-24 h-24 rounded-full bg-gradient-to-br from-blue-100 to-blue-50 flex items-center justify-center group-hover:scale-110 transition-transform">
                  <Users className="h-14 w-14 text-blue-600" />
                </div>
              </div>
              <CardTitle className="text-4xl text-center">子女端</CardTitle>
              <CardDescription className="text-xl text-center mt-3">
                远程关爱父母健康
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <ul className="space-y-3 text-lg text-muted-foreground">
                <li className="flex items-center gap-3">
                  <span className="text-blue-500 text-2xl">✓</span>
                  <span>查看多位老人健康状况</span>
                </li>
                <li className="flex items-center gap-3">
                  <span className="text-blue-500 text-2xl">✓</span>
                  <span>智能健康提醒</span>
                </li>
                <li className="flex items-center gap-3">
                  <span className="text-blue-500 text-2xl">✓</span>
                  <span>AI健康小助手</span>
                </li>
                <li className="flex items-center gap-3">
                  <span className="text-blue-500 text-2xl">✓</span>
                  <span>异常情况通知</span>
                </li>
              </ul>
              <Button 
                size="lg" 
                className="w-full text-xl py-8 mt-6 bg-blue-500 hover:bg-blue-600"
              >
                进入子女端
              </Button>
            </CardContent>
          </Card>

          {/* 社区端 */}
          <Card 
            className="hover:shadow-2xl transition-all cursor-pointer border-2 hover:border-green-400 bg-white group"
            onClick={() => onSelectRole('community')}
          >
            <CardHeader className="pb-4">
              <div className="flex justify-center mb-4">
                <div className="w-24 h-24 rounded-full bg-gradient-to-br from-green-100 to-green-50 flex items-center justify-center group-hover:scale-110 transition-transform">
                  <BarChart3 className="h-14 w-14 text-green-600" />
                </div>
              </div>
              <CardTitle className="text-4xl text-center">社区端</CardTitle>
              <CardDescription className="text-xl text-center mt-3">
                社区健康数据分析
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <ul className="space-y-3 text-lg text-muted-foreground">
                <li className="flex items-center gap-3">
                  <span className="text-green-500 text-2xl">✓</span>
                  <span>社区健康数据统计</span>
                </li>
                <li className="flex items-center gap-3">
                  <span className="text-green-500 text-2xl">✓</span>
                  <span>健康趋势分析</span>
                </li>
                <li className="flex items-center gap-3">
                  <span className="text-green-500 text-2xl">✓</span>
                  <span>AI健康小助手</span>
                </li>
                <li className="flex items-center gap-3">
                  <span className="text-green-500 text-2xl">✓</span>
                  <span>健康报告生成</span>
                </li>
              </ul>
              <Button 
                size="lg" 
                className="w-full text-xl py-8 mt-6 bg-green-500 hover:bg-green-600"
              >
                进入社区端
              </Button>
            </CardContent>
          </Card>
        </div>

        {/* Footer */}
        <div className="text-center text-lg text-muted-foreground pt-8">
          <div className="flex items-center justify-center gap-2">
            <Shield className="h-5 w-5" />
            <span>您的健康数据安全加密存储</span>
          </div>
        </div>
      </div>
    </div>
  );
}