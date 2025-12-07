import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "../ui/card";
import { ArrowDown, ArrowUp, Minus } from 'lucide-react';

interface StatCardProps {
  title: string;
  value: string | number;
  unit: string;
  icon: React.ReactNode;
  trend?: 'up' | 'down' | 'neutral';
  trendValue?: string;
  description?: string;
  color?: string;
  className?: string;
}

export function StatCard({ title, value, unit, icon, trend, trendValue, description, color = "text-slate-900", className }: StatCardProps) {
  return (
    <Card className={className}>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium text-muted-foreground">
          {title}
        </CardTitle>
        <div className={`${color}`}>
          {icon}
        </div>
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">
          {value} <span className="text-sm font-normal text-muted-foreground">{unit}</span>
        </div>
        <p className="text-xs text-muted-foreground mt-1 flex items-center">
          {trend === 'up' && <ArrowUp className="mr-1 h-3 w-3 text-emerald-500" />}
          {trend === 'down' && <ArrowDown className="mr-1 h-3 w-3 text-rose-500" />}
          {trend === 'neutral' && <Minus className="mr-1 h-3 w-3 text-slate-500" />}
          <span className={trend === 'up' ? 'text-emerald-500' : trend === 'down' ? 'text-rose-500' : 'text-slate-500'}>
            {trendValue}
          </span>
          <span className="ml-1">{description}</span>
        </p>
      </CardContent>
    </Card>
  );
}
