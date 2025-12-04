import React, { useState, useRef, useEffect, forwardRef, useImperativeHandle } from 'react';
import { X, MessageCircle, Minimize2, Maximize2, Move } from 'lucide-react';
import { AIConsultation } from '../consultation/AIConsultation';
import { speechManager } from '../../services/speechManager';
import { wakeWordService } from '../../services/wakeWordService';
import aiRobotImage from 'figma:asset/e4f865575775d810eb6a9ea7ef6d8574b96945a4.png';

// ============================================================================
// 组件说明：老人端悬浮AI助手
// 
// 涉及API:
// - POST /api/v1/elderly/ai/chat - AI对话
// - POST /api/v1/elderly/ai/analyze - AI数据分析
// 
// 功能：
// 1. 可拖动的悬浮球
// 2. 展开为可自由移动和缩放的聊天窗口
// 3. 接收外部触发的分析请求（通过 openWithPrompt）
// 4. 语音播报功能
// ============================================================================

export interface FloatingAIAssistantRef {
  openWithPrompt: (prompt: string) => void;
}

export const FloatingAIAssistant = forwardRef<FloatingAIAssistantRef>((props, ref) => {
  const [isOpen, setIsOpen] = useState(false);
  const [position, setPosition] = useState({ x: window.innerWidth - 140, y: window.innerHeight / 2 - 60 });
  const [isDragging, setIsDragging] = useState(false);
  const [dragOffset, setDragOffset] = useState({ x: 0, y: 0 });
  const [isMinimized, setIsMinimized] = useState(false);
  const [autoPrompt, setAutoPrompt] = useState<string | null>(null);
  const floatingBtnRef = useRef<HTMLDivElement>(null);
  const aiConsultationRef = useRef<any>(null);
  
  // 窗口位置和大小状态 - 适中大小，刚好展示所有内容
  const [windowPos, setWindowPos] = useState({ x: window.innerWidth - 720, y: 50 });
  const [windowSize, setWindowSize] = useState({ width: 700, height: 750 });
  const [isWindowDragging, setIsWindowDragging] = useState(false);
  const [isResizing, setIsResizing] = useState(false);
  const [resizeDirection, setResizeDirection] = useState('');
  const [windowDragOffset, setWindowDragOffset] = useState({ x: 0, y: 0 });
  const [isMaximized, setIsMaximized] = useState(false);
  const [prevWindowState, setPrevWindowState] = useState({ pos: { x: window.innerWidth - 720, y: 50 }, size: { width: 700, height: 750 } });
  const windowRef = useRef<HTMLDivElement>(null);

  // 暴露给父组件的方法
  useImperativeHandle(ref, () => ({
    openWithPrompt: (prompt: string) => {
      // 使用全局语音管理器停止所有语音
      speechManager.stop();
      
      setAutoPrompt(prompt);
      setIsOpen(true);
      setIsMinimized(false);
      
      // 使用全局语音管理器播报
      speechManager.speak('AI健康小助手正在为您分析', { rate: 0.8 });
    }
  }));

  // 页面加载时启动唤醒词监听
  useEffect(() => {
    console.log('🎤 FloatingAIAssistant: 启动唤醒词监听');
    
    // 设置唤醒回调 - 唤醒后打开对话窗口
    wakeWordService.onWake(() => {
      console.log('🎉 糖豆被唤醒了！自动打开对话窗口');
      speechManager.stop();
      setIsOpen(true);
      setIsMinimized(false);
      // 播报后由 AIConsultation 组件处理语音识别
      speechManager.speak('我在，您有什么事吗', { rate: 0.9 });
    });

    // 启动唤醒词监听
    wakeWordService.startListening();
    
    return () => {
      wakeWordService.stopListening();
    };
  }, []);

  // 处理拖动开始
  const handleMouseDown = (e: React.MouseEvent) => {
    if (isOpen) return; // 展开时不允许拖动
    
    setIsDragging(true);
    const rect = floatingBtnRef.current?.getBoundingClientRect();
    if (rect) {
      setDragOffset({
        x: e.clientX - rect.left,
        y: e.clientY - rect.top,
      });
    }
  };

  // 处理拖动中
  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (!isDragging) return;

      const newX = e.clientX - dragOffset.x;
      const newY = e.clientY - dragOffset.y;

      // 限制在窗口范围内
      const maxX = window.innerWidth - 120;
      const maxY = window.innerHeight - 120;

      setPosition({
        x: Math.max(0, Math.min(newX, maxX)),
        y: Math.max(0, Math.min(newY, maxY)),
      });
    };

    const handleMouseUp = () => {
      setIsDragging(false);
    };

    if (isDragging) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
    }

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };
  }, [isDragging, dragOffset]);

  // 点击悬浮球
  const handleClick = () => {
    if (!isDragging) {
      // 使用全局语音管理器
      speechManager.stop();
      
      setIsOpen(true);
      setIsMinimized(false);
      
      // 使用全局语音管理器播报
      speechManager.speak('AI健康小助手为您服务', { rate: 0.8 });
    }
  };

  // 关闭聊天框
  const handleClose = () => {
    // 使用全局语音管理器停止所有语音
    speechManager.stop();
    setIsOpen(false);
    setIsMinimized(false);
  };

  // 最小化聊天框
  const handleMinimize = () => {
    setIsMinimized(true);
  };

  // 从最小化恢复
  const handleRestore = () => {
    setIsMinimized(false);
  };

  // 窗口拖动开始
  const handleWindowDragStart = (e: React.MouseEvent) => {
    if (isMaximized) return;
    e.preventDefault();
    setIsWindowDragging(true);
    setWindowDragOffset({
      x: e.clientX - windowPos.x,
      y: e.clientY - windowPos.y,
    });
  };

  // 窗口缩放开始
  const handleResizeStart = (e: React.MouseEvent, direction: string) => {
    if (isMaximized) return;
    e.preventDefault();
    e.stopPropagation();
    setIsResizing(true);
    setResizeDirection(direction);
  };

  // 最大化/还原
  const handleMaximize = () => {
    if (isMaximized) {
      // 还原
      setWindowPos(prevWindowState.pos);
      setWindowSize(prevWindowState.size);
      setIsMaximized(false);
    } else {
      // 最大化前保存状态
      setPrevWindowState({ pos: windowPos, size: windowSize });
      setWindowPos({ x: 0, y: 0 });
      setWindowSize({ width: window.innerWidth, height: window.innerHeight });
      setIsMaximized(true);
    }
  };

  // 处理窗口拖动和缩放
  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (isWindowDragging) {
        const newX = e.clientX - windowDragOffset.x;
        const newY = e.clientY - windowDragOffset.y;
        
        // 限制在屏幕范围内
        const maxX = window.innerWidth - windowSize.width;
        const maxY = window.innerHeight - windowSize.height;
        
        setWindowPos({
          x: Math.max(0, Math.min(newX, maxX)),
          y: Math.max(0, Math.min(newY, maxY)),
        });
      }
      
      if (isResizing && windowRef.current) {
        const minWidth = 400;
        const minHeight = 500;
        
        let newWidth = windowSize.width;
        let newHeight = windowSize.height;
        let newX = windowPos.x;
        let newY = windowPos.y;
        
        if (resizeDirection.includes('e')) {
          newWidth = Math.max(minWidth, e.clientX - windowPos.x);
        }
        if (resizeDirection.includes('w')) {
          const deltaX = windowPos.x - e.clientX;
          const potentialWidth = windowSize.width + deltaX;
          if (potentialWidth >= minWidth) {
            newWidth = potentialWidth;
            newX = e.clientX;
          }
        }
        if (resizeDirection.includes('s')) {
          newHeight = Math.max(minHeight, e.clientY - windowPos.y);
        }
        if (resizeDirection.includes('n')) {
          const deltaY = windowPos.y - e.clientY;
          const potentialHeight = windowSize.height + deltaY;
          if (potentialHeight >= minHeight) {
            newHeight = potentialHeight;
            newY = e.clientY;
          }
        }
        
        setWindowSize({ width: newWidth, height: newHeight });
        setWindowPos({ x: newX, y: newY });
      }
    };

    const handleMouseUp = () => {
      setIsWindowDragging(false);
      setIsResizing(false);
      setResizeDirection('');
    };

    if (isWindowDragging || isResizing) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
    }

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };
  }, [isWindowDragging, isResizing, windowDragOffset, windowPos, windowSize, resizeDirection]);

  return (
    <>
      {/* 悬浮球按钮 */}
      {!isOpen && (
        <div
          ref={floatingBtnRef}
          className={`fixed z-50 cursor-grab active:cursor-grabbing transition-transform
                     ${isDragging ? 'scale-110' : 'hover:scale-105'}`}
          style={{
            left: `${position.x}px`,
            top: `${position.y}px`,
            width: '120px',
            height: '120px',
          }}
          onMouseDown={handleMouseDown}
          onClick={handleClick}
        >
          {/* 脉冲光环 */}
          <div className="absolute inset-0 bg-teal-400 rounded-full animate-ping opacity-30"></div>
          
          {/* 主体 */}
          <div className="relative w-full h-full bg-gradient-to-br from-teal-400 to-emerald-500 
                        rounded-full shadow-2xl flex items-center justify-center
                        border-4 border-white overflow-hidden group">
            {/* AI机器人图片 */}
            <img 
              src={aiRobotImage} 
              alt="AI助手" 
              className="w-full h-full object-cover"
            />
            
            {/* 悬浮提示 */}
            <div className="absolute -top-16 left-1/2 transform -translate-x-1/2 
                          bg-slate-800 text-white px-4 py-2 rounded-lg text-lg
                          opacity-0 group-hover:opacity-100 transition-opacity
                          whitespace-nowrap pointer-events-none shadow-xl">
              点击打开AI助手
              <div className="absolute top-full left-1/2 transform -translate-x-1/2 
                            border-8 border-transparent border-t-slate-800"></div>
            </div>
          </div>

          {/* 小红点提示 */}
          <div className="absolute -top-2 -right-2 w-8 h-8 bg-[rgb(44,154,251)] rounded-full flex items-center justify-center text-white font-bold text-sm shadow-lg animate-bounce border-2 border-white">
            AI
          </div>
        </div>
      )}

      {/* 可自由移动和缩放的聊天窗口 */}
      {isOpen && (
        <div
          ref={windowRef}
          className={`fixed z-50 bg-white shadow-2xl rounded-xl overflow-hidden
                      ${isWindowDragging ? 'cursor-grabbing' : ''}
                      ${isMaximized ? '' : 'border-2 border-teal-400'}`}
          style={{
            left: `${windowPos.x}px`,
            top: `${windowPos.y}px`,
            width: `${windowSize.width}px`,
            height: `${windowSize.height}px`,
          }}
        >
          {isMinimized ? (
            /* 最小化状态 */
            <div className="h-full flex flex-col items-center justify-start pt-6 bg-gradient-to-b from-teal-50 to-white">
              {/* AI机器人图片 - 小尺寸 */}
              <div 
                className="w-16 h-16 rounded-full overflow-hidden cursor-pointer 
                         hover:scale-110 transition-transform shadow-lg mb-4"
                onClick={handleRestore}
              >
                <img 
                  src={aiRobotImage} 
                  alt="AI助手" 
                  className="w-full h-full object-cover"
                />
              </div>
              
              {/* 竖向文字 */}
              <div className="writing-mode-vertical text-lg font-semibold text-teal-600 mb-6"
                   style={{ writingMode: 'vertical-rl' }}>
                AI助手
              </div>

              {/* 按钮组 */}
              <div className="space-y-4">
                <button
                  onClick={handleRestore}
                  className="w-12 h-12 bg-teal-500 hover:bg-teal-600 text-white rounded-lg
                           flex items-center justify-center transition-colors shadow-md"
                  title="展开"
                >
                  <MessageCircle className="h-6 w-6" />
                </button>
                
                <button
                  onClick={handleClose}
                  className="w-12 h-12 bg-red-500 hover:bg-red-600 text-white rounded-lg
                           flex items-center justify-center transition-colors shadow-md"
                  title="关闭"
                >
                  <X className="h-6 w-6" />
                </button>
              </div>
            </div>
          ) : (
            /* 完整展开状态 */
            <div className="h-full flex flex-col">
              {/* 头部 - 可拖动区域 */}
              <div 
                className={`bg-gradient-to-r from-teal-500 to-emerald-500 p-3 flex items-center justify-between border-b-2 border-teal-600
                           ${isMaximized ? '' : 'cursor-grab active:cursor-grabbing'}`}
                onMouseDown={handleWindowDragStart}
              >
                <div className="flex items-center gap-3">
                  {/* 拖动提示图标 */}
                  {!isMaximized && (
                    <Move className="h-5 w-5 text-white/60" />
                  )}
                  
                  {/* AI机器人头像 */}
                  <div className="w-12 h-12 rounded-full overflow-hidden border-2 border-white shadow-lg">
                    <img 
                      src={aiRobotImage} 
                      alt="AI助手" 
                      className="w-full h-full object-cover"
                    />
                  </div>
                  
                  <div>
                    <h2 className="text-white text-xl font-bold">AI健康小助手</h2>
                    <p className="text-teal-100 text-sm">智能健康咨询</p>
                  </div>
                </div>

                {/* 操作按钮 */}
                <div className="flex items-center gap-2">
                  <button
                    onClick={handleMinimize}
                    className="w-10 h-10 bg-white/20 hover:bg-white/30 text-white rounded-lg
                             flex items-center justify-center transition-colors"
                    title="最小化"
                  >
                    <Minimize2 className="h-5 w-5" />
                  </button>
                  
                  <button
                    onClick={handleMaximize}
                    className="w-10 h-10 bg-white/20 hover:bg-white/30 text-white rounded-lg
                             flex items-center justify-center transition-colors"
                    title={isMaximized ? "还原" : "最大化"}
                  >
                    <Maximize2 className="h-5 w-5" />
                  </button>
                  
                  <button
                    onClick={handleClose}
                    className="w-10 h-10 bg-red-500/80 hover:bg-red-500 text-white rounded-lg
                             flex items-center justify-center transition-colors"
                    title="关闭"
                  >
                    <X className="h-5 w-5" />
                  </button>
                </div>
              </div>

              {/* AI问诊内容区 - 支持滚动 */}
              <div className="flex-1 min-h-0 overflow-y-auto overflow-x-hidden scrollbar-thin scrollbar-thumb-teal-300 scrollbar-track-transparent">
                <AIConsultation isFloating={true} ref={aiConsultationRef} autoPrompt={autoPrompt} />
              </div>
            </div>
          )}
          
          {/* 缩放手柄 - 仅在非最大化时显示 */}
          {!isMaximized && !isMinimized && (
            <>
              {/* 右边缘 */}
              <div 
                className="absolute top-0 right-0 w-2 h-full cursor-e-resize hover:bg-teal-400/30"
                onMouseDown={(e) => handleResizeStart(e, 'e')}
              />
              {/* 下边缘 */}
              <div 
                className="absolute bottom-0 left-0 w-full h-2 cursor-s-resize hover:bg-teal-400/30"
                onMouseDown={(e) => handleResizeStart(e, 's')}
              />
              {/* 左边缘 */}
              <div 
                className="absolute top-0 left-0 w-2 h-full cursor-w-resize hover:bg-teal-400/30"
                onMouseDown={(e) => handleResizeStart(e, 'w')}
              />
              {/* 上边缘 */}
              <div 
                className="absolute top-0 left-0 w-full h-2 cursor-n-resize hover:bg-teal-400/30"
                onMouseDown={(e) => handleResizeStart(e, 'n')}
              />
              {/* 右下角 */}
              <div 
                className="absolute bottom-0 right-0 w-4 h-4 cursor-se-resize bg-teal-500 rounded-tl-lg"
                onMouseDown={(e) => handleResizeStart(e, 'se')}
              />
              {/* 左下角 */}
              <div 
                className="absolute bottom-0 left-0 w-4 h-4 cursor-sw-resize hover:bg-teal-400/50"
                onMouseDown={(e) => handleResizeStart(e, 'sw')}
              />
              {/* 右上角 */}
              <div 
                className="absolute top-0 right-0 w-4 h-4 cursor-ne-resize hover:bg-teal-400/50"
                onMouseDown={(e) => handleResizeStart(e, 'ne')}
              />
              {/* 左上角 */}
              <div 
                className="absolute top-0 left-0 w-4 h-4 cursor-nw-resize hover:bg-teal-400/50"
                onMouseDown={(e) => handleResizeStart(e, 'nw')}
              />
            </>
          )}
        </div>
      )}
    </>
  );
});

FloatingAIAssistant.displayName = 'FloatingAIAssistant';