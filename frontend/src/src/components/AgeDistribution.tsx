import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';

export function AgeDistribution() {
  const data = [
    { name: '60-70岁', value: 420, color: '#10b981', percentage: 33.7 },
    { name: '70-80岁', value: 518, color: '#14b8a6', percentage: 41.5 },
    { name: '80-90岁', value: 256, color: '#06b6d4', percentage: 20.5 },
    { name: '90岁以上', value: 54, color: '#0891b2', percentage: 4.3 }
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
      <div className="absolute -top-1 -left-1 w-8 h-8 border-t-2 border-l-2 border-emerald-400/70"></div>
      <div className="absolute -top-1 -right-1 w-8 h-8 border-t-2 border-r-2 border-emerald-400/70"></div>
      
      {/* 科技感光效 */}
      <div className="absolute top-0 left-0 w-24 h-24 bg-emerald-400/15 rounded-full blur-2xl"></div>
      
      <div className="flex items-center justify-between mb-2 relative z-10">
        <h3 className="text-lg text-emerald-300" style={{ textShadow: '0 0 10px rgba(16, 185, 129, 0.8)' }}>年龄分布</h3>
        <span className="text-xs text-gray-400">Age Distribution</span>
      </div>
      
      <div className="flex gap-4 flex-1 relative z-10">
        {/* 饼图 */}
        <div className="flex-1">
          <ResponsiveContainer width="100%" height={210}>
            <PieChart>
              <Pie
                data={data}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {data.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: '#134e4a', 
                  border: '1px solid #10b981',
                  borderRadius: '8px',
                  color: '#ffffff'
                }}
                itemStyle={{ color: '#ffffff' }}
                labelStyle={{ color: '#ffffff' }}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>
        
        {/* 文字说明 */}
        <div className="w-32 flex flex-col justify-center space-y-2">
          <div className="text-center p-1.5 bg-emerald-900/30 rounded-lg border border-emerald-400/30">
            <div className="text-xs text-gray-400">总人数</div>
            <div className="text-xl text-emerald-300" style={{ textShadow: '0 0 8px rgba(16, 185, 129, 0.6)' }}>1,248</div>
          </div>
          <div className="text-center p-1.5 bg-teal-900/30 rounded-lg border border-teal-400/30">
            <div className="text-xs text-gray-400">平均年龄</div>
            <div className="text-xl text-teal-300" style={{ textShadow: '0 0 8px rgba(20, 184, 166, 0.6)' }}>74岁</div>
          </div>
          <div className="text-center p-1.5 bg-cyan-900/30 rounded-lg border border-cyan-400/30">
            <div className="text-xs text-gray-400">最大年龄</div>
            <div className="text-xl text-cyan-300" style={{ textShadow: '0 0 8px rgba(6, 182, 212, 0.6)' }}>96岁</div>
          </div>
        </div>
      </div>
      
      <div className="grid grid-cols-2 gap-3 mt-2 relative z-10">
        {data.map((item, index) => (
          <div key={index} className="flex items-center gap-2 bg-slate-800/30 p-2 rounded">
            <div className="w-3 h-3 rounded-full" style={{ backgroundColor: item.color, boxShadow: `0 0 8px ${item.color}` }}></div>
            <span className="text-sm text-white">{item.name}</span>
            <span className="text-sm ml-auto text-white">{item.value}人</span>
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