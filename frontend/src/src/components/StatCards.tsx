import { Users, Heart, AlertCircle, Activity } from 'lucide-react';
import { AnimatedNumber } from './AnimatedNumber';

export function StatCards() {
  const stats = [
    {
      icon: Users,
      label: '社区老人总数',
      value: 1248,
      unit: '人',
      change: '+12',
      changeLabel: '较上月',
      color: 'from-emerald-400 to-teal-400'
    },
    {
      icon: Heart,
      label: '健康监测人数',
      value: 1186,
      unit: '人',
      change: '95.0%',
      changeLabel: '覆盖率',
      color: 'from-teal-400 to-cyan-400'
    },
    {
      icon: AlertCircle,
      label: '今日预警',
      value: 8,
      unit: '条',
      change: '-3',
      changeLabel: '较昨日',
      color: 'from-orange-400 to-amber-400'
    },
    {
      icon: Activity,
      label: '服务完成率',
      value: 98.5,
      unit: '%',
      change: '+2.3%',
      changeLabel: '较上周',
      color: 'from-emerald-400 to-green-500'
    }
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 relative z-10">
      {stats.map((stat, index) => (
        <div
          key={index}
          className="bg-teal-900/50 backdrop-blur-md border-2 border-emerald-400/50 rounded-lg p-5 shadow-lg hover:shadow-emerald-400/60 hover:border-emerald-400/80 transition-all relative overflow-hidden group h-full"
          style={{ boxShadow: '0 0 20px rgba(16, 185, 129, 0.3), inset 0 0 20px rgba(16, 185, 129, 0.1)' }}
        >
          {/* 科技感光效 */}
          <div className="absolute top-0 right-0 w-20 h-20 bg-emerald-400/15 rounded-full blur-2xl group-hover:bg-emerald-400/25 transition-all pointer-events-none"></div>
          <div className="absolute -top-1 -right-1 w-8 h-8 border-t-2 border-r-2 border-emerald-400/70"></div>
          <div className="absolute -bottom-1 -left-1 w-8 h-8 border-b-2 border-l-2 border-emerald-400/70"></div>
          
          <div className="flex items-start justify-between relative z-10">
            <div className="flex-1">
              <p className="text-gray-300 text-sm mb-2">{stat.label}</p>
              <div className="flex items-baseline gap-1">
                <AnimatedNumber 
                  value={stat.value} 
                  className="text-3xl tabular-nums text-emerald-300"
                  suffix={stat.unit === '%' ? '' : ''}
                />
                <span className="text-lg text-gray-300">{stat.unit}</span>
              </div>
              <div className="mt-2 flex items-center gap-1 text-xs">
                <span className={stat.change.startsWith('+') || stat.change.includes('%') && !stat.change.startsWith('-') ? 'text-emerald-300' : 'text-orange-300'}>
                  {stat.change}
                </span>
                <span className="text-gray-400">{stat.changeLabel}</span>
              </div>
            </div>
            <div className={`w-12 h-12 rounded-lg bg-gradient-to-br ${stat.color} flex items-center justify-center shadow-lg relative`}
                 style={{ boxShadow: '0 0 15px rgba(16, 185, 129, 0.5)' }}>
              <div className="absolute inset-0 bg-emerald-400/30 rounded-lg blur-md opacity-0 group-hover:opacity-100 transition-all"></div>
              <stat.icon className="w-6 h-6 text-white relative z-10" />
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}