import React, { useState } from 'react';
import { Smile, Frown, Meh, Heart, ArrowRight, Brain } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from "../ui/card";
import { Button } from "../ui/button";

// ============================================================================
// 组件说明：快速心情记录卡片
// 
// 涉及API:
// - POST /api/v1/elderly/psychology/mood - 提交心情记录（点击"详细记录"后跳转到心理健康页面）
// 
// 功能：
// 1. 快速选择今日心情（很好/愉快/一般/低落）
// 2. 显示当前选中的心情状态
// 3. 点击"详细记录"跳转到心理健康页面进行详细记录
// 
// 注意：
// - 实际提交在 PsychologyPage 组件中完成
// - 此组件只负责快速选择和跳转
// ============================================================================

interface MoodQuickCardProps {
  onNavigateToMood: (mood: string) => void;
}

export function MoodQuickCard({ onNavigateToMood }: MoodQuickCardProps) {
  const moodOptions = [
    { value: 'excellent', label: '很好', icon: Heart, color: 'text-rose-500', bg: 'bg-rose-50' },
    { value: 'good', label: '愉快', icon: Smile, color: 'text-green-500', bg: 'bg-green-50' },
    { value: 'normal', label: '一般', icon: Meh, color: 'text-amber-500', bg: 'bg-amber-50' },
    { value: 'bad', label: '低落', icon: Frown, color: 'text-slate-500', bg: 'bg-slate-50' },
  ];

  // 使用状态管理当前心情，默认为"愉快"
  const [selectedMood, setSelectedMood] = useState('good');
  
  // 获取当前选中的心情数据
  const currentMood = moodOptions.find(m => m.value === selectedMood) || moodOptions[1];

  return (
    <Card className="bg-gradient-to-br from-purple-50 to-pink-50 border-purple-200">
      <CardHeader className="pb-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-purple-100 flex items-center justify-center">
              <Brain className="h-6 w-6 text-purple-600" />
            </div>
            <CardTitle className="text-2xl">今日心情</CardTitle>
          </div>
          <span className="text-base text-muted-foreground">今天 09:30</span>
        </div>
      </CardHeader>
      <CardContent>
        <div className="flex items-center justify-between">
          {/* 左侧：当前心情显示 */}
          <div className="flex items-center gap-6">
            <div className={`w-20 h-20 rounded-full ${currentMood.bg} flex items-center justify-center transition-all`}>
              <currentMood.icon className={`h-12 w-12 ${currentMood.color}`} />
            </div>
            <div>
              <div className="text-3xl font-bold mb-1">{currentMood.label}</div>
              <div className="text-lg text-muted-foreground">
                {selectedMood === 'excellent' && '心情非常棒！'}
                {selectedMood === 'good' && '心情状态良好'}
                {selectedMood === 'normal' && '心情还算平稳'}
                {selectedMood === 'bad' && '需要关注情绪'}
              </div>
            </div>
          </div>

          {/* 右侧：其他心情选项预览 + 操作按钮 */}
          <div className="flex items-center gap-6">
            {/* 心情图标预览 - 可点击切换 */}
            <div className="flex items-center gap-2">
              {moodOptions.map((mood) => (
                <button
                  key={mood.value}
                  onClick={() => setSelectedMood(mood.value)}
                  className={`w-12 h-12 rounded-full flex items-center justify-center transition-all ${
                    selectedMood === mood.value 
                      ? `${mood.bg} ring-2 ring-purple-400 shadow-md scale-110` 
                      : 'bg-white/60 hover:bg-white hover:scale-105 hover:shadow-sm'
                  }`}
                >
                  <mood.icon className={`h-6 w-6 ${mood.color} ${selectedMood === mood.value ? '' : 'opacity-60'}`} />
                </button>
              ))}
            </div>

            {/* 操作按钮 */}
            <Button 
              size="lg"
              className="text-lg px-8 py-6 bg-purple-500 hover:bg-purple-600 shadow-md"
              onClick={() => onNavigateToMood(selectedMood)}
            >
              详细记录
              <ArrowRight className="ml-2 h-5 w-5" />
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}