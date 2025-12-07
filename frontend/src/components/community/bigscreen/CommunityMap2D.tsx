import { useState } from 'react';
import communityImageLabeled from 'figma:asset/a6a8584d81114e37a33568db3546c0c6d4e54027.png';

interface Building {
  id: number;
  name: string;
  // 使用百分比定位，适配不同屏幕尺寸
  x: string; // 百分比
  y: string; // 百分比
  width: string; // 百分比
  height: string; // 百分比
  elderCount: number;
  alertCount: number;
  healthyRate: number;
  type: 'residential' | 'activity' | 'medical' | 'service';
}

export function CommunityMap2D() {
  const [selectedBuilding, setSelectedBuilding] = useState<Building | null>(null);
  const [hoveredBuilding, setHoveredBuilding] = useState<number | null>(null);

  // 📐 精确坐标数据（来自BUILDING_COORDINATES.md文档）
  const buildings: Building[] = [
    // 顶部一排（从左到右4栋）
    { id: 1, name: '1号楼', x: '8%', y: '13%', width: '20%', height: '20%', elderCount: 87, alertCount: 0, healthyRate: 100, type: 'residential' },
    { id: 2, name: '2号楼', x: '33%', y: '13%', width: '20%', height: '20%', elderCount: 92, alertCount: 1, healthyRate: 99, type: 'residential' },
    { id: 3, name: '3号楼', x: '58%', y: '13%', width: '20%', height: '20%', elderCount: 105, alertCount: 0, healthyRate: 100, type: 'residential' },
    { id: 4, name: '4号楼', x: '85%', y: '13%', width: '12%', height: '20%', elderCount: 98, alertCount: 2, healthyRate: 98, type: 'residential' },
    
    // 中间一排（从左到右3栋）
    { id: 5, name: '5号楼', x: '14%', y: '38%', width: '24%', height: '27%', elderCount: 112, alertCount: 0, healthyRate: 100, type: 'residential' },
    { id: 6, name: '6号楼', x: '56%', y: '38%', width: '28%', height: '27%', elderCount: 88, alertCount: 0, healthyRate: 100, type: 'residential' },
    { id: 7, name: '7号楼', x: '89%', y: '38%', width: '8.5%', height: '28%', elderCount: 96, alertCount: 0, healthyRate: 100, type: 'residential' },
    
    // 底部一排（从左到右3栋）
    { id: 8, name: '8号楼', x: '3%', y: '70%', width: '11%', height: '26%', elderCount: 89, alertCount: 0, healthyRate: 100, type: 'residential' },
    { id: 9, name: '9号楼', x: '17%', y: '70%', width: '20%', height: '26%', elderCount: 94, alertCount: 0, healthyRate: 100, type: 'residential' },
    { id: 10, name: '10号楼', x: '56%', y: '70%', width: '21%', height: '26%', elderCount: 78, alertCount: 0, healthyRate: 100, type: 'residential' },
  ];

  const getColor = (building: Building) => {
    if (building.alertCount > 2) return 'rgba(245, 158, 11, 0.7)'; // 橙色
    if (building.alertCount > 0) return 'rgba(251, 191, 36, 0.7)'; // 黄色
    
    switch (building.type) {
      case 'residential':
        return 'rgba(16, 185, 129, 0.6)'; // 绿色
      case 'activity':
        return 'rgba(20, 184, 166, 0.6)'; // 青绿色
      case 'medical':
        return 'rgba(6, 182, 212, 0.6)'; // 青色
      default:
        return 'rgba(16, 185, 129, 0.6)';
    }
  };

  const getBorderColor = (building: Building) => {
    if (building.alertCount > 0) return '#fbbf24';
    
    switch (building.type) {
      case 'residential':
        return '#10b981';
      case 'activity':
        return '#14b8a6';
      case 'medical':
        return '#06b6d4';
      default:
        return '#10b981';
    }
  };

  const totalElders = buildings.reduce((sum, b) => sum + b.elderCount, 0);
  const totalAlerts = buildings.reduce((sum, b) => sum + b.alertCount, 0);

  return (
    <div className="bg-teal-900/40 backdrop-blur-md border-2 border-emerald-400/50 rounded-lg shadow-lg relative overflow-hidden h-full flex flex-col"
         style={{ boxShadow: '0 0 30px rgba(16, 185, 129, 0.3), inset 0 0 30px rgba(16, 185, 129, 0.05)' }}>
      
      {/* 装饰角 */}
      <div className="absolute -top-1 -left-1 w-12 h-12 border-t-2 border-l-2 border-emerald-400/70 z-10"></div>
      <div className="absolute -top-1 -right-1 w-12 h-12 border-t-2 border-r-2 border-emerald-400/70 z-10"></div>
      <div className="absolute -bottom-1 -left-1 w-12 h-12 border-b-2 border-l-2 border-emerald-400/70 z-10"></div>
      <div className="absolute -bottom-1 -right-1 w-12 h-12 border-b-2 border-r-2 border-emerald-400/70 z-10"></div>
      
      {/* 标题栏 */}
      <div className="bg-gradient-to-r from-teal-900/80 to-emerald-900/80 px-6 py-3 border-b-2 border-emerald-400/30 flex-shrink-0">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-emerald-300 flex items-center gap-2">
              <span className="w-2 h-2 bg-emerald-400 rounded-full animate-pulse"></span>
              社区平面图
            </h3>
            <p className="text-xs text-gray-400 mt-1">Community Map · 点击建筑查看详情</p>
          </div>
          
          {/* 统计信息 */}
          <div className="flex gap-6 text-xs">
            <div className="text-center">
              <div className="text-gray-400">总建筑</div>
              <div className="text-emerald-300">{buildings.length}栋</div>
            </div>
            <div className="text-center">
              <div className="text-gray-400">总人数</div>
              <div className="text-emerald-300">{totalElders}人</div>
            </div>
            <div className="text-center">
              <div className="text-gray-400">预警数</div>
              <div className={totalAlerts > 0 ? 'text-yellow-300' : 'text-emerald-300'}>{totalAlerts}个</div>
            </div>
          </div>
        </div>
      </div>

      <div className="p-4 flex-1 flex flex-col min-h-0">
        {/* 航拍图容器 */}
        <div className="flex-1 relative bg-slate-800/50 rounded-lg border border-emerald-400/20 overflow-hidden min-h-[500px]">
          {/* 航拍图背景 - 填满容器宽度 */}
          <img 
            src={communityImageLabeled} 
            alt="社区航拍图" 
            className="w-full h-full object-cover"
            style={{ objectPosition: 'center center' }}
          />
          
          {/* 交互层 - 建筑热区 */}
          <div className="absolute inset-0">
            {buildings.map((building) => {
              const isSelected = selectedBuilding?.id === building.id;
              const isHovered = hoveredBuilding === building.id;
              const color = getColor(building);
              const borderColor = getBorderColor(building);
              
              return (
                <div
                  key={building.id}
                  className="absolute cursor-pointer transition-all duration-300"
                  style={{
                    left: building.x,
                    top: building.y,
                    width: building.width,
                    height: building.height,
                  }}
                  onClick={() => setSelectedBuilding(building)}
                  onMouseEnter={() => setHoveredBuilding(building.id)}
                  onMouseLeave={() => setHoveredBuilding(null)}
                >
                  {/* 建筑覆盖层 */}
                  <div
                    className="absolute inset-0 rounded-md transition-all duration-300"
                    style={{
                      backgroundColor: isHovered || isSelected ? color : 'transparent',
                      border: `2px solid ${borderColor}`,
                      borderStyle: isSelected ? 'solid' : 'dashed',
                      boxShadow: isSelected 
                        ? `0 0 20px ${borderColor}, inset 0 0 20px ${borderColor}40`
                        : isHovered 
                        ? `0 0 15px ${borderColor}`
                        : 'none',
                    }}
                  >
                    {/* 脉冲动画边框 */}
                    {(isSelected || isHovered) && (
                      <div
                        className="absolute inset-0 rounded-md animate-pulse"
                        style={{
                          border: `1px solid ${borderColor}`,
                          opacity: 0.6,
                        }}
                      ></div>
                    )}
                  </div>
                  
                  {/* 建筑信息标签 */}
                  {(isHovered || isSelected) && (
                    <div 
                      className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 
                                 bg-teal-900/95 backdrop-blur-sm px-3 py-2 rounded-lg border border-emerald-400/50
                                 shadow-lg pointer-events-none z-10 min-w-[120px]"
                      style={{ boxShadow: `0 0 20px ${borderColor}80` }}
                    >
                      <div className="text-center">
                        <div className="text-emerald-300 text-sm mb-1">{building.name}</div>
                        <div className="text-xs text-gray-300">{building.elderCount}人入住</div>
                        {building.alertCount > 0 && (
                          <div className="text-xs text-yellow-300 mt-1">
                            ⚠️ {building.alertCount}个预警
                          </div>
                        )}
                      </div>
                    </div>
                  )}
                  
                  {/* 预警标记 */}
                  {building.alertCount > 0 && (
                    <div className="absolute -top-2 -right-2 z-20">
                      <div className="relative">
                        <div 
                          className="w-8 h-8 bg-yellow-500 rounded-full flex items-center justify-center
                                     shadow-lg animate-pulse"
                          style={{ boxShadow: '0 0 15px rgba(251, 191, 36, 0.8)' }}
                        >
                          <span className="text-white text-xs">{building.alertCount}</span>
                        </div>
                        {/* 脉冲光圈 */}
                        <div 
                          className="absolute inset-0 bg-yellow-500 rounded-full animate-ping opacity-75"
                        ></div>
                      </div>
                    </div>
                  )}
                  
                  {/* 楼号标签（常驻显示） */}
                  {!isHovered && !isSelected && (
                    <div 
                      className="absolute top-2 left-2 bg-emerald-900/80 backdrop-blur-sm 
                                 px-2 py-1 rounded text-xs text-emerald-300 border border-emerald-400/50
                                 pointer-events-none shadow-md"
                    >
                      {building.name}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>

        {/* 底部信息栏 */}
        <div className="mt-3 flex items-start justify-between gap-4 flex-shrink-0">
          {/* 图例 */}
          <div className="flex-1 bg-teal-950/40 rounded-lg px-3 py-2 border border-emerald-400/20">
            <div className="flex items-center gap-3 flex-wrap text-xs">
              <div className="flex items-center gap-1.5">
                <div className="w-3 h-3 bg-emerald-500 rounded border border-emerald-400"></div>
                <span className="text-gray-300">住宅楼</span>
              </div>
              <div className="flex items-center gap-1.5">
                <div className="w-6 h-6 bg-yellow-400 rounded-full flex items-center justify-center text-white text-xs">!</div>
                <span className="text-gray-300">预警</span>
              </div>
            </div>
          </div>

          {/* 选中建筑详情 */}
          {selectedBuilding && (
            <div className="flex-1 bg-emerald-900/60 rounded-lg px-4 py-2 border-2 border-emerald-400/50 shadow-lg"
                 style={{ boxShadow: '0 0 20px rgba(16, 185, 129, 0.4)' }}>
              <div className="grid grid-cols-4 gap-3 text-xs">
                <div>
                  <div className="text-gray-400">建筑</div>
                  <div className="text-emerald-300">{selectedBuilding.name}</div>
                </div>
                <div>
                  <div className="text-gray-400">类型</div>
                  <div className="text-emerald-300">
                    {selectedBuilding.type === 'residential' && '住宅楼'}
                    {selectedBuilding.type === 'activity' && '活动中心'}
                    {selectedBuilding.type === 'medical' && '医疗楼'}
                  </div>
                </div>
                <div>
                  <div className="text-gray-400">入住</div>
                  <div className="text-emerald-300">{selectedBuilding.elderCount}人</div>
                </div>
                <div>
                  <div className="text-gray-400">健康率</div>
                  <div className="text-emerald-300">{selectedBuilding.healthyRate}%</div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
