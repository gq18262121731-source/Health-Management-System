import { AlertCircle, Heart, Activity, Thermometer } from 'lucide-react';

export function AlertList() {
  const alerts = [
    {
      id: 1,
      type: '血压异常',
      user: '张**',
      room: '3栋201',
      time: '10分钟前',
      level: 'high',
      icon: Heart
    },
    {
      id: 2,
      type: '心率偏高',
      user: '李**',
      room: '5栋108',
      time: '25分钟前',
      level: 'medium',
      icon: Activity
    },
    {
      id: 3,
      type: '体温异常',
      user: '王**',
      room: '2栋305',
      time: '1小时前',
      level: 'high',
      icon: Thermometer
    }
  ];

  const getLevelColor = (level: string) => {
    switch (level) {
      case 'high':
        return 'border-red-400/50 bg-red-900/30';
      case 'medium':
        return 'border-orange-400/50 bg-orange-900/30';
      default:
        return 'border-gray-400/50 bg-gray-900/30';
    }
  };

  const getLevelDot = (level: string) => {
    switch (level) {
      case 'high':
        return 'bg-red-400';
      case 'medium':
        return 'bg-orange-400';
      default:
        return 'bg-gray-400';
    }
  };

  return (
    <div className="bg-teal-900/50 backdrop-blur-md border-2 border-emerald-400/50 rounded-lg p-5 shadow-lg h-full flex flex-col relative overflow-hidden group"
         style={{ boxShadow: '0 0 20px rgba(16, 185, 129, 0.3), inset 0 0 20px rgba(16, 185, 129, 0.1)' }}>
      {/* 流光边框效果 */}
      <div className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-500">
        <div className="absolute inset-0 overflow-hidden rounded-lg">
          <div className="absolute top-0 left-0 w-full h-[2px] bg-gradient-to-r from-transparent via-emerald-400 to-transparent animate-[slideRight_2s_ease-in-out_infinite]"></div>
          <div className="absolute bottom-0 right-0 w-full h-[2px] bg-gradient-to-r from-transparent via-emerald-400 to-transparent animate-[slideLeft_2s_ease-in-out_infinite]"></div>
        </div>
      </div>
      
      {/* 装饰角 */}
      <div className="absolute -top-1 -left-1 w-8 h-8 border-t-2 border-l-2 border-emerald-400/70"></div>
      <div className="absolute -top-1 -right-1 w-8 h-8 border-t-2 border-r-2 border-emerald-400/70"></div>
      
      {/* 科技感光效 */}
      <div className="absolute top-0 right-0 w-24 h-24 bg-orange-400/15 rounded-full blur-2xl"></div>
      
      <div className="flex items-center justify-between mb-2 relative z-10">
        <h3 className="text-lg text-emerald-300" style={{ textShadow: '0 0 10px rgba(16, 185, 129, 0.8)' }}>实时预警</h3>
        <span className="text-xs text-gray-400">Real-time Alerts</span>
      </div>
      
      <div className="space-y-2.5 flex-1 overflow-y-auto pr-2 custom-scrollbar relative z-10">
        {alerts.map((alert) => (
          <div
            key={alert.id}
            className={`border-2 rounded-lg p-2.5 ${getLevelColor(alert.level)} hover:shadow-lg transition-all backdrop-blur-sm`}
          >
            <div className="flex items-start gap-2.5">
              <div className={`w-9 h-9 rounded-lg ${alert.level === 'high' ? 'bg-red-500/30 border border-red-400/50' : alert.level === 'medium' ? 'bg-orange-500/30 border border-orange-400/50' : 'bg-yellow-500/30 border border-yellow-400/50'} flex items-center justify-center flex-shrink-0`}>
                <alert.icon className={`w-5 h-5 ${alert.level === 'high' ? 'text-red-300' : alert.level === 'medium' ? 'text-orange-300' : 'text-yellow-300'}`} />
              </div>
              
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-0.5">
                  <div className={`w-2 h-2 rounded-full ${getLevelDot(alert.level)} animate-pulse`} style={{ boxShadow: `0 0 8px ${alert.level === 'high' ? '#f87171' : alert.level === 'medium' ? '#fb923c' : '#fbbf24'}` }}></div>
                  <span className="text-sm text-gray-100">{alert.type}</span>
                </div>
                <div className="flex items-center gap-3 text-xs text-gray-300">
                  <span>{alert.user}</span>
                  <span>•</span>
                  <span>{alert.room}</span>
                </div>
                <div className="text-xs text-gray-400 mt-0.5">{alert.time}</div>
              </div>
            </div>
          </div>
        ))}
      </div>
      
      <div className="mt-3 pt-3 border-t border-emerald-400/30 relative z-10">
        <div className="flex items-center justify-between text-sm">
          <span className="text-gray-300">今日预警统计</span>
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-1">
              <div className="w-2 h-2 rounded-full bg-red-400" style={{ boxShadow: '0 0 8px #f87171' }}></div>
              <span className="text-xs text-gray-300">紧急 3</span>
            </div>
            <div className="flex items-center gap-1">
              <div className="w-2 h-2 rounded-full bg-orange-400" style={{ boxShadow: '0 0 8px #fb923c' }}></div>
              <span className="text-xs text-gray-300">重要 2</span>
            </div>
            <div className="flex items-center gap-1">
              <div className="w-2 h-2 rounded-full bg-yellow-400" style={{ boxShadow: '0 0 8px #fbbf24' }}></div>
              <span className="text-xs text-gray-300">一般 3</span>
            </div>
          </div>
        </div>
      </div>
      <style jsx>{`
        @keyframes slideRight {
          0% { transform: translateX(-100%); }
          100% { transform: translateX(100%); }
        }
        @keyframes slideLeft {
          0% { transform: translateX(100%); }
          100% { transform: translateX(-100%); }
        }
      `}</style>
    </div>
  );
}