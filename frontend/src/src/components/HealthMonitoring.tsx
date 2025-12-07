import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';

export function HealthMonitoring() {
  const data = [
    { name: '健康', value: 856, color: '#10b981' },
    { name: '亚健康', value: 298, color: '#fbbf24' },
    { name: '慢性病', value: 78, color: '#fb923c' },
    { name: '重点关注', value: 16, color: '#f87171' }
  ];

  const total = data.reduce((sum, item) => sum + item.value, 0);

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
      <div className="absolute top-0 right-0 w-24 h-24 bg-emerald-400/15 rounded-full blur-2xl"></div>
      
      <div className="flex items-center justify-between mb-2 relative z-10">
        <h3 className="text-lg text-emerald-300" style={{ textShadow: '0 0 10px rgba(16, 185, 129, 0.8)' }}>健康状况监测</h3>
        <span className="text-xs text-gray-400">Health Status</span>
      </div>
      
      <div className="flex-1 relative z-10">
        <ResponsiveContainer width="100%" height={210}>
          <BarChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="#134e4a" />
            <XAxis dataKey="name" stroke="#94a3b8" />
            <YAxis stroke="#94a3b8" />
            <Tooltip 
              contentStyle={{ 
                backgroundColor: '#134e4a', 
                border: '1px solid #10b981',
                borderRadius: '8px',
                color: '#d1fae5'
              }}
              content={({ active, payload }) => {
                if (active && payload && payload.length) {
                  const percent = ((payload[0].value as number / total) * 100).toFixed(1);
                  return (
                    <div className="bg-teal-900 border border-emerald-400 rounded-lg p-3">
                      <p className="text-emerald-300">{payload[0].payload.name}</p>
                      <p className="text-white">人数: {payload[0].value}</p>
                      <p className="text-gray-300">占比: {percent}%</p>
                    </div>
                  );
                }
                return null;
              }}
              cursor={{ fill: 'rgba(255, 255, 255, 0.1)' }}
            />
            <Bar dataKey="value" radius={[8, 8, 0, 0]}>
              {data.map((entry, index) => (
                <Bar key={`bar-${index}`} dataKey="value" fill={entry.color} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
      
      <div className="grid grid-cols-4 gap-2 mt-2 relative z-10">
        {data.map((item, index) => (
          <div key={index} className="text-center p-1.5 bg-slate-800/40 rounded border border-emerald-400/30">
            <div className="text-xs text-gray-400">{item.name}</div>
            <div className="text-lg text-emerald-300" style={{ color: item.color }}>{item.value}</div>
            <div className="text-xs text-gray-500">{((item.value / total) * 100).toFixed(1)}%</div>
          </div>
        ))}
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