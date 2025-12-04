import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "../ui/card";
import { Footprints, Flame, Timer } from 'lucide-react';

const CustomProgress = ({ value, colorClass, bgClass }: { value: number, colorClass: string, bgClass: string }) => (
  <div className={`h-2 w-full overflow-hidden rounded-full ${bgClass}`}>
    <div
      className={`h-full flex-1 transition-all ${colorClass}`}
      style={{ width: `${value}%` }}
    />
  </div>
);

export function DailyActivity() {
  return (
    <Card className="h-full">
      <CardHeader>
        <CardTitle>今日活动目标</CardTitle>
      </CardHeader>
      <CardContent className="space-y-8">
        <div className="space-y-2">
          <div className="flex items-center justify-between text-sm">
            <div className="flex items-center gap-2">
              <div className="p-1.5 bg-orange-100 rounded-md text-orange-600">
                <Footprints className="h-4 w-4" />
              </div>
              <span className="font-medium">步数</span>
            </div>
            <span className="text-muted-foreground">8,542 / 10,000 步</span>
          </div>
          <CustomProgress value={85} bgClass="bg-orange-100" colorClass="bg-orange-500" />
        </div>

        <div className="space-y-2">
          <div className="flex items-center justify-between text-sm">
             <div className="flex items-center gap-2">
              <div className="p-1.5 bg-red-100 rounded-md text-red-600">
                <Flame className="h-4 w-4" />
              </div>
              <span className="font-medium">卡路里</span>
            </div>
            <span className="text-muted-foreground">450 / 600 kcal</span>
          </div>
          <CustomProgress value={75} bgClass="bg-red-100" colorClass="bg-red-500" />
        </div>

        <div className="space-y-2">
          <div className="flex items-center justify-between text-sm">
             <div className="flex items-center gap-2">
              <div className="p-1.5 bg-blue-100 rounded-md text-blue-600">
                <Timer className="h-4 w-4" />
              </div>
              <span className="font-medium">活跃时间</span>
            </div>
            <span className="text-muted-foreground">45 / 60 分钟</span>
          </div>
          <CustomProgress value={65} bgClass="bg-blue-100" colorClass="bg-blue-500" />
        </div>
      </CardContent>
    </Card>
  );
}
