import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "../ui/card";
import { CalendarDays, Clock, MapPin } from 'lucide-react';
import { Badge } from "../ui/badge";

export function ScheduleList() {
  const appointments = [
    {
      id: 1,
      title: '全科体检复查',
      doctor: '李医生',
      date: '今天',
      time: '14:00 - 15:00',
      location: '门诊大楼 302室',
      type: '检查',
      status: 'upcoming'
    },
    {
      id: 2,
      title: '牙科护理',
      doctor: '王医生',
      date: '明天',
      time: '09:30 - 10:30',
      location: '口腔科 2楼',
      type: '治疗',
      status: 'scheduled'
    },
    {
      id: 3,
      title: '营养咨询',
      doctor: '赵医师',
      date: '11月28日',
      time: '16:00 - 17:00',
      location: '线上视频会议',
      type: '咨询',
      status: 'scheduled'
    }
  ];

  return (
    <Card className="h-full">
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <span>即将到来的日程</span>
          <Badge variant="outline" className="font-normal">3 个待办</Badge>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-6">
          {appointments.map((apt) => (
            <div key={apt.id} className="flex items-start space-x-4 border-b last:border-0 pb-4 last:pb-0">
              <div className="mt-1 bg-blue-50 text-blue-600 p-2 rounded-lg">
                <CalendarDays className="h-5 w-5" />
              </div>
              <div className="space-y-1 flex-1">
                <h4 className="font-semibold text-sm leading-none">{apt.title}</h4>
                <p className="text-sm text-muted-foreground">主治医师: {apt.doctor}</p>
                <div className="flex items-center pt-1 space-x-4 text-xs text-muted-foreground">
                  <div className="flex items-center">
                    <Clock className="mr-1 h-3 w-3" />
                    {apt.date} {apt.time}
                  </div>
                </div>
                <div className="flex items-center pt-1 text-xs text-muted-foreground">
                   <MapPin className="mr-1 h-3 w-3" />
                   {apt.location}
                </div>
              </div>
              <Badge variant={apt.status === 'upcoming' ? 'default' : 'secondary'}>
                {apt.type}
              </Badge>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
