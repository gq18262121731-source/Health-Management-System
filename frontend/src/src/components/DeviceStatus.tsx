import { Wifi, WifiOff, Power } from 'lucide-react';

export function DeviceStatus() {
  const devices = [
    { name: '智能手环', online: 1186, offline: 62, total: 1248 },
    { name: '智能床垫', online: 856, offline: 124, total: 980 },
    { name: '紧急呼叫器', online: 1205, offline: 43, total: 1248 },
    { name: '健康一体机', online: 28, offline: 4, total: 32 }
  ];

  return (
    <div className="bg-teal-900/50 backdrop-blur-md border-2 border-emerald-400/50 rounded-lg p-5 shadow-lg h-full flex flex-col relative group"
         style={{ boxShadow: '0 0 20px rgba(16, 185, 129, 0.3), inset 0 0 20px rgba(16, 185, 129, 0.1)' }}>
      {/* 流光边框效果 */}
      <div className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-500">
        <div className="absolute inset-0 overflow-hidden rounded-lg">
          <div className="absolute top-0 left-0 w-full h-[2px] bg-gradient-to-r from-transparent via-emerald-400 to-transparent animate-[slideRight_2s_ease-in-out_infinite]"></div>
          <div className="absolute bottom-0 right-0 w-full h-[2px] bg-gradient-to-r from-transparent via-emerald-400 to-transparent animate-[slideLeft_2s_ease-in-out_infinite]"></div>
        </div>
      </div>
      
      {/* 科技感光效 */}
      <div className="absolute bottom-0 right-0 w-24 h-24 bg-emerald-400/15 rounded-full blur-2xl"></div>
      
      <div className="flex items-center justify-between mb-4 relative z-10">
        <h3 className="text-lg text-emerald-300" style={{ textShadow: '0 0 10px rgba(16, 185, 129, 0.8)' }}>设备在线状态</h3>
        <span className="text-xs text-gray-400">Device Status</span>
      </div>
      
      <div className="space-y-4 flex-1 relative z-10 min-h-0 overflow-auto">
        {devices.map((device, index) => {
          const onlineRate = ((device.online / device.total) * 100).toFixed(1);
          
          return (
            <div key={index} className="space-y-2">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Power className="w-4 h-4 text-emerald-400" />
                  <span className="text-sm text-gray-200">{device.name}</span>
                </div>
                <span className="text-sm text-emerald-300" style={{ textShadow: '0 0 8px rgba(16, 185, 129, 0.6)' }}>{onlineRate}%</span>
              </div>
              
              <div className="h-2 bg-slate-800/50 rounded-full overflow-hidden border border-emerald-400/30">
                <div
                  className="h-full bg-gradient-to-r from-emerald-400 to-teal-500 rounded-full transition-all relative"
                  style={{ 
                    width: `${onlineRate}%`,
                    boxShadow: '0 0 10px rgba(16, 185, 129, 0.6)'
                  }}
                >
                  <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/30 to-transparent animate-pulse"></div>
                </div>
              </div>
              
              <div className="flex items-center justify-between text-xs text-gray-300">
                <div className="flex items-center gap-3">
                  <div className="flex items-center gap-1">
                    <Wifi className="w-3 h-3 text-emerald-400" />
                    <span>在线 {device.online}</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <WifiOff className="w-3 h-3 text-red-400" />
                    <span>离线 {device.offline}</span>
                  </div>
                </div>
                <span>总数 {device.total}</span>
              </div>
            </div>
          );
        })}
      </div>
      
      <div className="mt-4 p-4 bg-emerald-900/30 rounded-lg border border-emerald-400/40 relative z-10 min-h-[70px] flex-shrink-0"
           style={{ boxShadow: '0 0 15px rgba(16, 185, 129, 0.3)' }}>
        <div className="flex items-center justify-between">
          <span className="text-sm text-gray-300">设备总在线率</span>
          <span className="text-xl text-emerald-300" style={{ textShadow: '0 0 10px rgba(16, 185, 129, 0.8)' }}>94.8%</span>
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