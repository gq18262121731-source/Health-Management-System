import React from 'react';
import { Card, CardContent } from '../ui/card';
import { AIAnalysisButton } from './AIAnalysisButton';
import { LucideIcon } from 'lucide-react';

// ============================================================================
// 组件说明：老人端健康卡片（带AI分析按钮）
// 
// 数据来源：
// - GET /api/v1/elderly/health/today 的 vitalSigns 对象
//   - bloodSugar: { value, unit, status, testType }
//   - bloodPressure: { systolic, diastolic, unit, status }
//   - heartRate: { value, unit, change, status }
// 
// 功能：
// 1. 显示单个健康指标的卡片（血糖、血压、心率等）
// 2. 右上角有AI分析按钮，点击后调用悬浮AI助手
// 3. 适老化设计：超大字体，清晰的颜色对比
// ============================================================================

interface HealthCardWithAIProps {
  icon: LucideIcon;
  iconColor: string;
  value: string | number;
  unit: string;
  title: string;
  status: string;
  statusColor?: string;
  bgGradient: string;
  borderColor: string;
  dataType: string;
  onAnalyze: (prompt: string) => void;
}

export function HealthCardWithAI({
  icon: Icon,
  iconColor,
  value,
  unit,
  title,
  status,
  statusColor = 'text-muted-foreground',
  bgGradient,
  borderColor,
  dataType,
  onAnalyze
}: HealthCardWithAIProps) {
  return (
    <Card className={`${bgGradient} ${borderColor} relative`}>
      <CardContent className="pt-6 pb-4">
        {/* AI分析按钮 - 右上角 */}
        <div className="absolute top-4 right-4">
          <AIAnalysisButton
            dataType={dataType}
            dataValue={value}
            onAnalyze={onAnalyze}
            size="md"
          />
        </div>

        <div className="space-y-4">
          <div className="flex items-center gap-8 pr-32">
            {/* Icon */}
            <Icon className={`h-8 w-8 ${iconColor} flex-shrink-0`} />
            
            {/* Value & Unit */}
            <div className="flex items-baseline gap-2 w-64">
              <span className="text-6xl font-bold">{value}</span>
              <span className="text-xl text-muted-foreground">{unit}</span>
            </div>
            
            {/* Title */}
            <div className="font-semibold leading-tight ml-auto pr-6 text-[64px] whitespace-nowrap">{title}</div>
          </div>
          
          {/* Status - Bottom Center */}
          <div className={`text-xl ${statusColor} text-center pt-2 border-t`}>
            {status}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}