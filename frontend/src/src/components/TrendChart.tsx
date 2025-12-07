import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';

export function TrendChart() {
  const data = [
    { date: '11-20', 服务次数: 98, 预警次数: 12 },
    { date: '11-21', 服务次数: 112, 预警次数: 8 },
    { date: '11-22', 服务次数: 105, 预警次数: 15 },
    { date: '11-23', 服务次数: 128, 预警次数: 6 },
    { date: '11-24', 服务次数: 118, 预警次数: 11 },
    { date: '11-25', 服务次数: 136, 预警次数: 9 },
    { date: '11-26', 服务次数: 102, 预警次数: 8 }
  ];

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
      <div className="absolute -bottom-1 -left-1 w-8 h-8 border-b-2 border-l-2 border-emerald-400/70"></div>
      <div className="absolute -bottom-1 -right-1 w-8 h-8 border-b-2 border-r-2 border-emerald-400/70"></div>
      
      {/* 科技感光效 */}
      <div className="absolute bottom-0 left-0 w-24 h-24 bg-emerald-400/15 rounded-full blur-2xl"></div>
      
      <div className="flex items-center justify-between mb-4 relative z-10">
        <h3 className="text-lg text-emerald-300" style={{ textShadow: '0 0 10px rgba(16, 185, 129, 0.8)' }}>近7日趋势</h3>
        <span className="text-xs text-gray-400">Weekly Trend</span>
      </div>
      
      <div className="flex-1 relative z-10">
        <ResponsiveContainer width="100%" height={240}>
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="#134e4a" />
            <XAxis dataKey="date" stroke="#94a3b8" />
            <YAxis stroke="#94a3b8" />
            <Tooltip 
              contentStyle={{ 
                backgroundColor: '#134e4a', 
                border: '1px solid #10b981',
                borderRadius: '8px',
                color: '#d1fae5'
              }}
              content={({ active, payload, label }) => {
                if (active && payload && payload.length) {
                  return (
                    <div className="bg-teal-900 border border-emerald-400 rounded-lg p-3">
                      <p className="text-emerald-300 mb-2">{label}</p>
                      <p className="text-cyan-300">服务次数: {payload[0].value}</p>
                      <p className="text-orange-300">预警次数: {payload[1].value}</p>
                    </div>
                  );
                }
                return null;
              }}
            />
            <Legend />
            <Line 
              type="monotone" 
              dataKey="服务次数" 
              stroke="#10b981" 
              strokeWidth={2}
              dot={{ fill: '#10b981', r: 4 }}
              activeDot={{ r: 6 }}
            />
            <Line 
              type="monotone" 
              dataKey="预警次数" 
              stroke="#fb923c" 
              strokeWidth={2}
              dot={{ fill: '#fb923c', r: 4 }}
              activeDot={{ r: 6 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
      
      <div className="grid grid-cols-2 gap-3 mt-4 relative z-10">
        <div className="p-3 bg-emerald-900/30 rounded-lg border border-emerald-400/40"
             style={{ boxShadow: '0 0 12px rgba(16, 185, 129, 0.2)' }}>
          <div className="text-xs text-gray-300 mb-1">平均服务次数/日</div>
          <div className="text-lg text-emerald-300" style={{ textShadow: '0 0 8px rgba(16, 185, 129, 0.6)' }}>114 次</div>
        </div>
        <div className="p-3 bg-orange-900/30 rounded-lg border border-orange-400/40"
             style={{ boxShadow: '0 0 12px rgba(251, 146, 60, 0.2)' }}>
          <div className="text-xs text-gray-300 mb-1">平均预警次数/日</div>
          <div className="text-lg text-orange-300" style={{ textShadow: '0 0 8px rgba(251, 146, 60, 0.6)' }}>10 次</div>
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