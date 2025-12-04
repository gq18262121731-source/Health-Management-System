interface HeaderProps {
  currentTime: Date;
}

export function Header({ currentTime }: HeaderProps) {
  const formatDate = (date: Date) => {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    const seconds = String(date.getSeconds()).padStart(2, '0');
    const weekdays = ['星期日', '星期一', '星期二', '星期三', '星期四', '星期五', '星期六'];
    const weekday = weekdays[date.getDay()];
    
    return {
      date: `${year}-${month}-${day}`,
      time: `${hours}:${minutes}:${seconds}`,
      weekday
    };
  };

  const { date, time, weekday } = formatDate(currentTime);

  return (
    <div className="relative bg-gradient-to-r from-teal-800/40 via-emerald-800/40 to-teal-800/40 border-2 border-emerald-400/60 rounded-lg p-4 mb-6 shadow-2xl backdrop-blur-md overflow-hidden group"
         style={{
           boxShadow: '0 0 30px rgba(16, 185, 129, 0.4), inset 0 0 30px rgba(16, 185, 129, 0.1)'
         }}>
      
      {/* 流动光效边框 */}
      <div className="absolute inset-0 rounded-lg overflow-hidden">
        <div className="absolute top-0 left-0 right-0 h-[2px] bg-gradient-to-r from-transparent via-emerald-400 to-transparent animate-[slideRight_3s_ease-in-out_infinite]"></div>
        <div className="absolute bottom-0 left-0 right-0 h-[2px] bg-gradient-to-r from-transparent via-emerald-400 to-transparent animate-[slideLeft_3s_ease-in-out_infinite]"></div>
        <div className="absolute left-0 top-0 bottom-0 w-[2px] bg-gradient-to-b from-transparent via-emerald-400 to-transparent animate-[slideDown_3s_ease-in-out_infinite]" style={{ animationDelay: '0.5s' }}></div>
        <div className="absolute right-0 top-0 bottom-0 w-[2px] bg-gradient-to-b from-transparent via-emerald-400 to-transparent animate-[slideUp_3s_ease-in-out_infinite]" style={{ animationDelay: '0.5s' }}></div>
      </div>
      
      {/* 装饰线条 */}
      <div className="absolute top-0 left-0 w-32 h-1 bg-gradient-to-r from-transparent via-emerald-400 to-transparent"></div>
      <div className="absolute top-0 right-0 w-32 h-1 bg-gradient-to-r from-transparent via-emerald-400 to-transparent"></div>
      <div className="absolute bottom-0 left-0 w-32 h-1 bg-gradient-to-r from-transparent via-emerald-400 to-transparent"></div>
      <div className="absolute bottom-0 right-0 w-32 h-1 bg-gradient-to-r from-transparent via-emerald-400 to-transparent"></div>
      
      {/* 科技感光效 */}
      <div className="absolute top-0 left-1/4 w-32 h-32 bg-emerald-400/20 rounded-full blur-3xl pointer-events-none animate-pulse"></div>
      <div className="absolute bottom-0 right-1/4 w-32 h-32 bg-teal-400/20 rounded-full blur-3xl pointer-events-none animate-pulse" style={{ animationDelay: '1s' }}></div>
      
      <div className="relative flex items-center justify-between z-10">
        {/* 左侧：时间日期 */}
        <div className="text-left">
          <div className="text-3xl text-emerald-300 tracking-wider tabular-nums" style={{ textShadow: '0 0 12px rgba(16, 185, 129, 0.8)' }}>{time}</div>
          <div className="text-sm text-gray-300 mt-1">{date} {weekday}</div>
        </div>
        
        {/* 中间：标题 */}
        <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2">
          <h1 className="text-3xl tracking-wider text-emerald-300 whitespace-nowrap" style={{ textShadow: '0 0 15px rgba(16, 185, 129, 0.8)' }}>智慧健康管理大屏</h1>
        </div>
        
        {/* 右侧：退出按钮 */}
        <div className="flex items-center gap-2 px-4 py-2 border border-emerald-400/50 rounded-md bg-emerald-900/30 backdrop-blur-sm cursor-pointer hover:bg-emerald-900/50 transition-colors"
             style={{ boxShadow: '0 0 10px rgba(16, 185, 129, 0.3)' }}>
          <svg className="w-4 h-4 text-emerald-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
          </svg>
          <span className="text-sm text-emerald-300">退出</span>
        </div>
      </div>
      <style jsx>{`
        @keyframes slideRight {
          0% { transform: translateX(-100%); }
          100% { transform: translateX(200%); }
        }
        @keyframes slideLeft {
          0% { transform: translateX(100%); }
          100% { transform: translateX(-200%); }
        }
        @keyframes slideDown {
          0% { transform: translateY(-100%); }
          100% { transform: translateY(200%); }
        }
        @keyframes slideUp {
          0% { transform: translateY(100%); }
          100% { transform: translateY(-200%); }
        }
      `}</style>
    </div>
  );
}