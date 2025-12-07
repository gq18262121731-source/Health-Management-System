import React from 'react';
import { Sparkles } from 'lucide-react';
import { Button } from '../ui/button';

interface AIAnalysisButtonProps {
  dataType: string;
  dataValue: string | number;
  onAnalyze: (prompt: string) => void;
  className?: string;
  size?: 'sm' | 'md' | 'lg';
}

export function AIAnalysisButton({ 
  dataType, 
  dataValue, 
  onAnalyze, 
  className = '',
  size = 'md'
}: AIAnalysisButtonProps) {
  
  const handleClick = () => {
    // 语音播报
    if ('speechSynthesis' in window) {
      const utterance = new SpeechSynthesisUtterance(`正在为您分析${dataType}数据`);
      utterance.lang = 'zh-CN';
      utterance.rate = 0.8;
      window.speechSynthesis.speak(utterance);
    }

    // 根据数据类型生成分析提示词
    const prompt = generateAnalysisPrompt(dataType, dataValue);
    onAnalyze(prompt);
  };

  const sizeClasses = {
    sm: 'h-8 px-3 text-sm',
    md: 'h-10 px-4 text-base',
    lg: 'h-12 px-6 text-lg',
  };

  const iconSizes = {
    sm: 'h-4 w-4',
    md: 'h-5 w-5',
    lg: 'h-6 w-6',
  };

  return (
    <Button
      variant="outline"
      onClick={handleClick}
      className={`${sizeClasses[size]} bg-gradient-to-r from-purple-50 to-blue-50 
                 border-2 border-purple-300 hover:border-purple-400
                 text-purple-700 hover:text-purple-800
                 hover:shadow-lg transition-all duration-200
                 font-semibold ${className}`}
      title={`AI分析${dataType}`}
    >
      <Sparkles className={`${iconSizes[size]} mr-2`} />
      AI分析
    </Button>
  );
}

// 生成AI分析提示词
function generateAnalysisPrompt(dataType: string, dataValue: string | number): string {
  const prompts: Record<string, string> = {
    '体温': `我的当前体温是${dataValue}°C，请帮我分析一下这个体温是否正常，有什么需要注意的吗？`,
    '步数': `我今天走了${dataValue}步，请帮我分析一下这个运动量是否合适，给我一些运动建议。`,
    '体重': `我的当前体重是${dataValue}kg，请帮我分析一下这个体重是否健康，有什么饮食和运动建议吗？`,
    '血糖': `我的当前血糖是${dataValue}mmol/L，请帮我分析一下这个血糖水平是否正常，需要注意什么？`,
    '血压': `我的当前血压是${dataValue}mmHg，请帮我分析一下这个血压是否正常，给我一些建议。`,
    '心率': `我的当前心率是${dataValue}次/分，请帮我分析一下这个心率是否正常，有什么需要注意的吗？`,
    '睡眠': `我昨晚的睡眠情况是${dataValue}，请帮我分析一下睡眠质量如何，给我一些改善建议。`,
    '心率趋势': `请帮我分析一下我最近的心率变化趋势，给我一些健康建议。`,
    '睡眠分析': `请帮我分析一下我最近的睡眠质量，包括深睡、浅睡、快速眼动等阶段，给我一些改善睡眠的建议。`,
    '血压趋势': `请帮我分析一下我最近的血压变化趋势，给我一些控制血压的建议。`,
    '综合健康': `请根据我最近的所有健康数据，给我一个综合的健康分析和建议。`,
  };

  return prompts[dataType] || `请帮我分析一下${dataType}的数据：${dataValue}`;
}
