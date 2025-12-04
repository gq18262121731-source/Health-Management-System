import React, { useEffect, useRef, useState } from 'react';

// ============================================================================
// 动态粒子类型定义
// ============================================================================
interface Particle {
  id: number;
  x: number;
  y: number;
  size: number;
  speedX: number;
  speedY: number;
  opacity: number;
  color: string;
  pulsePhase: number;
}

// ============================================================================
// 动态粒子背景组件
// ============================================================================
function AnimatedParticles({ particleCount = 120 }: { particleCount?: number }) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const particlesRef = useRef<Particle[]>([]);
  const animationRef = useRef<number>();
  const mouseRef = useRef({ x: 0, y: 0 });

  // 粒子颜色配置
  const colors = [
    'rgba(59, 130, 246, 0.6)',   // blue-500
    'rgba(6, 182, 212, 0.5)',    // cyan-500
    'rgba(139, 92, 246, 0.5)',   // purple-500
    'rgba(16, 185, 129, 0.4)',   // emerald-500
    'rgba(99, 102, 241, 0.5)',   // indigo-500
    'rgba(236, 72, 153, 0.4)',   // pink-500
  ];

  // 初始化粒子
  const initParticles = (width: number, height: number) => {
    const particles: Particle[] = [];
    for (let i = 0; i < particleCount; i++) {
      particles.push({
        id: i,
        x: Math.random() * width,
        y: Math.random() * height,
        size: Math.random() * 4 + 1,
        speedX: (Math.random() - 0.5) * 0.8,
        speedY: (Math.random() - 0.5) * 0.8,
        opacity: Math.random() * 0.5 + 0.2,
        color: colors[Math.floor(Math.random() * colors.length)],
        pulsePhase: Math.random() * Math.PI * 2,
      });
    }
    particlesRef.current = particles;
  };

  // 绘制粒子和连线
  const draw = (ctx: CanvasRenderingContext2D, width: number, height: number, time: number) => {
    ctx.clearRect(0, 0, width, height);
    
    const particles = particlesRef.current;
    
    // 绘制粒子间的连线
    ctx.lineWidth = 0.5;
    for (let i = 0; i < particles.length; i++) {
      for (let j = i + 1; j < particles.length; j++) {
        const dx = particles[i].x - particles[j].x;
        const dy = particles[i].y - particles[j].y;
        const distance = Math.sqrt(dx * dx + dy * dy);
        
        if (distance < 120) {
          const opacity = (1 - distance / 120) * 0.15;
          ctx.strokeStyle = `rgba(99, 102, 241, ${opacity})`;
          ctx.beginPath();
          ctx.moveTo(particles[i].x, particles[i].y);
          ctx.lineTo(particles[j].x, particles[j].y);
          ctx.stroke();
        }
      }
    }
    
    // 绘制粒子
    particles.forEach((particle) => {
      // 脉冲效果
      const pulse = Math.sin(time * 0.002 + particle.pulsePhase) * 0.3 + 0.7;
      const currentSize = particle.size * pulse;
      const currentOpacity = particle.opacity * pulse;
      
      // 绘制光晕
      const gradient = ctx.createRadialGradient(
        particle.x, particle.y, 0,
        particle.x, particle.y, currentSize * 3
      );
      gradient.addColorStop(0, particle.color.replace(/[\d.]+\)$/, `${currentOpacity})`));
      gradient.addColorStop(1, 'rgba(0, 0, 0, 0)');
      
      ctx.beginPath();
      ctx.arc(particle.x, particle.y, currentSize * 3, 0, Math.PI * 2);
      ctx.fillStyle = gradient;
      ctx.fill();
      
      // 绘制核心
      ctx.beginPath();
      ctx.arc(particle.x, particle.y, currentSize, 0, Math.PI * 2);
      ctx.fillStyle = particle.color.replace(/[\d.]+\)$/, `${currentOpacity * 1.5})`);
      ctx.fill();
    });
  };

  // 更新粒子位置
  const update = (width: number, height: number) => {
    particlesRef.current.forEach((particle) => {
      // 基础移动
      particle.x += particle.speedX;
      particle.y += particle.speedY;
      
      // 鼠标交互 - 轻微排斥效果
      const dx = particle.x - mouseRef.current.x;
      const dy = particle.y - mouseRef.current.y;
      const distance = Math.sqrt(dx * dx + dy * dy);
      if (distance < 100 && distance > 0) {
        const force = (100 - distance) / 100 * 0.5;
        particle.x += (dx / distance) * force;
        particle.y += (dy / distance) * force;
      }
      
      // 边界处理 - 循环
      if (particle.x < -10) particle.x = width + 10;
      if (particle.x > width + 10) particle.x = -10;
      if (particle.y < -10) particle.y = height + 10;
      if (particle.y > height + 10) particle.y = -10;
    });
  };

  // 动画循环
  const animate = (time: number) => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    
    const width = canvas.width;
    const height = canvas.height;
    
    update(width, height);
    draw(ctx, width, height, time);
    
    animationRef.current = requestAnimationFrame(animate);
  };

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    
    // 设置 canvas 尺寸
    const resizeCanvas = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
      initParticles(canvas.width, canvas.height);
    };
    
    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);
    
    // 鼠标移动监听
    const handleMouseMove = (e: MouseEvent) => {
      mouseRef.current = { x: e.clientX, y: e.clientY };
    };
    window.addEventListener('mousemove', handleMouseMove);
    
    // 启动动画
    animationRef.current = requestAnimationFrame(animate);
    
    return () => {
      window.removeEventListener('resize', resizeCanvas);
      window.removeEventListener('mousemove', handleMouseMove);
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      className="absolute inset-0 pointer-events-none"
      style={{ opacity: 0.8 }}
    />
  );
}

// ============================================================================
// 科技感背景组件 - 用于老人端和子女端界面
// ============================================================================
export function TechBackground() {
  return (
    <div className="fixed inset-0 z-0 pointer-events-none overflow-hidden">
      {/* 渐变背景 */}
      <div className="absolute inset-0 bg-gradient-to-br from-slate-50 via-blue-50/30 to-cyan-50/50" />
      
      {/* 动态粒子层 - 大幅增加密度 */}
      <AnimatedParticles particleCount={150} />
      
      {/* 网格背景 - 更密集 */}
      <div 
        className="absolute inset-0 opacity-[0.05]"
        style={{
          backgroundImage: `
            linear-gradient(rgba(59, 130, 246, 0.5) 1px, transparent 1px),
            linear-gradient(90deg, rgba(59, 130, 246, 0.5) 1px, transparent 1px)
          `,
          backgroundSize: '40px 40px'
        }}
      />
      
      {/* 额外的斜线网格 */}
      <div 
        className="absolute inset-0 opacity-[0.02]"
        style={{
          backgroundImage: `
            linear-gradient(45deg, rgba(139, 92, 246, 0.3) 1px, transparent 1px),
            linear-gradient(-45deg, rgba(139, 92, 246, 0.3) 1px, transparent 1px)
          `,
          backgroundSize: '80px 80px'
        }}
      />
      
      {/* 密集浮动粒子群 - 左侧 */}
      {[...Array(20)].map((_, i) => (
        <div
          key={`left-particle-${i}`}
          className="absolute w-1 h-1 bg-blue-400/40 rounded-full animate-float-random"
          style={{
            left: `${2 + Math.random() * 15}%`,
            top: `${5 + (i * 4.5)}%`,
            animationDelay: `${i * 0.3}s`,
            animationDuration: `${4 + Math.random() * 4}s`
          }}
        />
      ))}
      
      {/* 密集浮动粒子群 - 右侧 */}
      {[...Array(20)].map((_, i) => (
        <div
          key={`right-particle-${i}`}
          className="absolute w-1 h-1 bg-purple-400/40 rounded-full animate-float-random"
          style={{
            right: `${2 + Math.random() * 15}%`,
            top: `${5 + (i * 4.5)}%`,
            animationDelay: `${i * 0.3 + 0.15}s`,
            animationDuration: `${4 + Math.random() * 4}s`
          }}
        />
      ))}
      
      {/* 中间区域浮动粒子 */}
      {[...Array(30)].map((_, i) => (
        <div
          key={`center-particle-${i}`}
          className="absolute rounded-full animate-float-random"
          style={{
            width: `${2 + Math.random() * 3}px`,
            height: `${2 + Math.random() * 3}px`,
            backgroundColor: i % 2 === 0 ? 'rgba(59, 130, 246, 0.25)' : 'rgba(139, 92, 246, 0.25)',
            left: `${15 + Math.random() * 70}%`,
            top: `${Math.random() * 100}%`,
            animationDelay: `${Math.random() * 5}s`,
            animationDuration: `${5 + Math.random() * 5}s`
          }}
        />
      ))}
      
      {/* 左上角装饰圆 - 添加动画 */}
      <div className="absolute -top-32 -left-32 w-96 h-96 animate-blob">
        <div className="absolute inset-0 bg-gradient-to-br from-blue-400/20 to-cyan-400/10 rounded-full blur-3xl" />
        <div className="absolute inset-8 bg-gradient-to-br from-blue-300/15 to-transparent rounded-full blur-2xl" />
      </div>
      
      {/* 右上角装饰圆 - 添加动画 */}
      <div className="absolute -top-20 -right-20 w-80 h-80 animate-blob animation-delay-2000">
        <div className="absolute inset-0 bg-gradient-to-bl from-purple-400/15 to-pink-400/10 rounded-full blur-3xl" />
      </div>
      
      {/* 左下角装饰 - 添加动画 */}
      <div className="absolute -bottom-40 -left-40 w-[500px] h-[500px] animate-blob animation-delay-4000">
        <div className="absolute inset-0 bg-gradient-to-tr from-emerald-400/10 to-teal-400/5 rounded-full blur-3xl" />
      </div>
      
      {/* 右下角装饰 - 添加动画 */}
      <div className="absolute -bottom-32 -right-32 w-96 h-96 animate-blob animation-delay-6000">
        <div className="absolute inset-0 bg-gradient-to-tl from-blue-500/15 to-indigo-400/10 rounded-full blur-3xl" />
      </div>
      
      {/* 额外的浮动粒子效果（CSS动画） */}
      <div className="absolute top-1/4 left-1/4 w-2 h-2 bg-blue-400/40 rounded-full animate-float-slow" />
      <div className="absolute top-1/3 right-1/4 w-3 h-3 bg-cyan-400/30 rounded-full animate-float-medium" style={{ animationDelay: '0.5s' }} />
      <div className="absolute bottom-1/4 left-1/3 w-2 h-2 bg-purple-400/30 rounded-full animate-float-fast" style={{ animationDelay: '1s' }} />
      <div className="absolute top-2/3 right-1/3 w-2 h-2 bg-emerald-400/30 rounded-full animate-float-slow" style={{ animationDelay: '1.5s' }} />
      <div className="absolute top-1/2 left-1/6 w-1.5 h-1.5 bg-blue-300/40 rounded-full animate-float-medium" style={{ animationDelay: '2s' }} />
      <div className="absolute bottom-1/3 right-1/6 w-2 h-2 bg-indigo-400/30 rounded-full animate-float-fast" style={{ animationDelay: '0.8s' }} />
      
      {/* 上升粒子效果 */}
      <div className="absolute bottom-0 left-1/5 w-1 h-1 bg-blue-400/50 rounded-full animate-rise" />
      <div className="absolute bottom-0 left-2/5 w-1.5 h-1.5 bg-cyan-400/40 rounded-full animate-rise" style={{ animationDelay: '2s' }} />
      <div className="absolute bottom-0 left-3/5 w-1 h-1 bg-purple-400/50 rounded-full animate-rise" style={{ animationDelay: '4s' }} />
      <div className="absolute bottom-0 left-4/5 w-1.5 h-1.5 bg-emerald-400/40 rounded-full animate-rise" style={{ animationDelay: '6s' }} />
      <div className="absolute bottom-0 right-1/5 w-1 h-1 bg-indigo-400/50 rounded-full animate-rise" style={{ animationDelay: '3s' }} />
      <div className="absolute bottom-0 right-2/5 w-1 h-1 bg-pink-400/40 rounded-full animate-rise" style={{ animationDelay: '5s' }} />
      
      {/* 科技线条装饰 - 左侧（扩大到内容附近） */}
      <svg className="absolute left-0 top-0 h-full w-[25%] opacity-[0.12]" viewBox="0 0 250 800" preserveAspectRatio="none">
        {/* 主线条 - 更宽更粗 */}
        <path 
          d="M0,50 Q80,100 50,200 T120,350 T40,500 T150,650 T80,800" 
          stroke="url(#leftGradient)" 
          strokeWidth="2" 
          fill="none"
          className="animate-line-draw"
        />
        <path 
          d="M30,0 Q150,80 80,180 T180,320 T60,480 T200,640 T100,800" 
          stroke="url(#leftGradient)" 
          strokeWidth="1.5" 
          fill="none"
          className="animate-line-draw"
          style={{ animationDelay: '0.5s' }}
        />
        <path 
          d="M60,0 Q200,120 120,250 T220,400 T100,550 T240,700 T150,800" 
          stroke="url(#leftGradient)" 
          strokeWidth="1" 
          fill="none"
          className="animate-line-draw"
          style={{ animationDelay: '1s' }}
        />
        {/* 流动光点 - 左侧 */}
        <circle r="4" fill="url(#glowGradient)">
          <animateMotion 
            dur="10s" 
            repeatCount="indefinite"
            path="M0,50 Q80,100 50,200 T120,350 T40,500 T150,650 T80,800"
          />
        </circle>
        <circle r="3" fill="url(#glowGradient2)">
          <animateMotion 
            dur="8s" 
            repeatCount="indefinite"
            path="M30,0 Q150,80 80,180 T180,320 T60,480 T200,640 T100,800"
          />
        </circle>
        <circle r="2" fill="url(#glowGradient)">
          <animateMotion 
            dur="12s" 
            repeatCount="indefinite"
            path="M60,0 Q200,120 120,250 T220,400 T100,550 T240,700 T150,800"
          />
        </circle>
        <defs>
          <linearGradient id="leftGradient" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#3b82f6" stopOpacity="0" />
            <stop offset="20%" stopColor="#3b82f6" stopOpacity="0.8" />
            <stop offset="50%" stopColor="#06b6d4" stopOpacity="1" />
            <stop offset="80%" stopColor="#3b82f6" stopOpacity="0.8" />
            <stop offset="100%" stopColor="#06b6d4" stopOpacity="0" />
          </linearGradient>
          <radialGradient id="glowGradient">
            <stop offset="0%" stopColor="#3b82f6" stopOpacity="1" />
            <stop offset="50%" stopColor="#06b6d4" stopOpacity="0.8" />
            <stop offset="100%" stopColor="#06b6d4" stopOpacity="0" />
          </radialGradient>
          <radialGradient id="glowGradient2">
            <stop offset="0%" stopColor="#06b6d4" stopOpacity="1" />
            <stop offset="100%" stopColor="#3b82f6" stopOpacity="0" />
          </radialGradient>
        </defs>
      </svg>
      
      {/* 科技线条装饰 - 右侧（扩大到内容附近） */}
      <svg className="absolute right-0 top-0 h-full w-[25%] opacity-[0.12]" viewBox="0 0 250 800" preserveAspectRatio="none">
        {/* 主线条 - 更宽更粗 */}
        <path 
          d="M250,50 Q170,100 200,200 T130,350 T210,500 T100,650 T170,800" 
          stroke="url(#rightGradient)" 
          strokeWidth="2" 
          fill="none"
          className="animate-line-draw"
          style={{ animationDelay: '0.3s' }}
        />
        <path 
          d="M220,0 Q100,80 170,180 T70,320 T190,480 T50,640 T150,800" 
          stroke="url(#rightGradient)" 
          strokeWidth="1.5" 
          fill="none"
          className="animate-line-draw"
          style={{ animationDelay: '0.8s' }}
        />
        <path 
          d="M190,0 Q50,120 130,250 T30,400 T150,550 T10,700 T100,800" 
          stroke="url(#rightGradient)" 
          strokeWidth="1" 
          fill="none"
          className="animate-line-draw"
          style={{ animationDelay: '1.3s' }}
        />
        {/* 流动光点 - 右侧 */}
        <circle r="4" fill="url(#glowGradientRight)">
          <animateMotion 
            dur="10s" 
            repeatCount="indefinite"
            path="M250,50 Q170,100 200,200 T130,350 T210,500 T100,650 T170,800"
          />
        </circle>
        <circle r="3" fill="url(#glowGradientRight2)">
          <animateMotion 
            dur="8s" 
            repeatCount="indefinite"
            path="M220,0 Q100,80 170,180 T70,320 T190,480 T50,640 T150,800"
          />
        </circle>
        <circle r="2" fill="url(#glowGradientRight)">
          <animateMotion 
            dur="12s" 
            repeatCount="indefinite"
            path="M190,0 Q50,120 130,250 T30,400 T150,550 T10,700 T100,800"
          />
        </circle>
        <defs>
          <linearGradient id="rightGradient" x1="100%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor="#8b5cf6" stopOpacity="0" />
            <stop offset="20%" stopColor="#8b5cf6" stopOpacity="0.8" />
            <stop offset="50%" stopColor="#ec4899" stopOpacity="1" />
            <stop offset="80%" stopColor="#8b5cf6" stopOpacity="0.8" />
            <stop offset="100%" stopColor="#ec4899" stopOpacity="0" />
          </linearGradient>
          <radialGradient id="glowGradientRight">
            <stop offset="0%" stopColor="#8b5cf6" stopOpacity="1" />
            <stop offset="50%" stopColor="#ec4899" stopOpacity="0.8" />
            <stop offset="100%" stopColor="#ec4899" stopOpacity="0" />
          </radialGradient>
          <radialGradient id="glowGradientRight2">
            <stop offset="0%" stopColor="#ec4899" stopOpacity="1" />
            <stop offset="100%" stopColor="#8b5cf6" stopOpacity="0" />
          </radialGradient>
        </defs>
      </svg>
      
      {/* 中央流动线条 */}
      <svg className="absolute left-1/2 top-0 h-full w-px opacity-[0.1] -translate-x-1/2" viewBox="0 0 2 800" preserveAspectRatio="none">
        <line x1="1" y1="0" x2="1" y2="800" stroke="url(#centerGradient)" strokeWidth="2" strokeDasharray="10 20" className="animate-dash" />
        <circle r="4" fill="#3b82f6" opacity="0.6">
          <animateMotion dur="5s" repeatCount="indefinite" path="M1,0 L1,800" />
        </circle>
        <defs>
          <linearGradient id="centerGradient" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor="#3b82f6" stopOpacity="0" />
            <stop offset="50%" stopColor="#8b5cf6" stopOpacity="1" />
            <stop offset="100%" stopColor="#06b6d4" stopOpacity="0" />
          </linearGradient>
        </defs>
      </svg>
      
      {/* 数据流动效果 - 左边（增强版） */}
      <div className="absolute left-8 top-1/4 flex flex-col gap-3 opacity-30">
        <div className="flex gap-1 items-center">
          <div className="w-2 h-2 bg-blue-400 rounded-full animate-ping" style={{ animationDuration: '2s' }} />
          <div className="w-8 h-1 bg-gradient-to-r from-blue-400 to-transparent rounded animate-data-flow" />
          <div className="w-4 h-1 bg-blue-300 rounded animate-pulse" style={{ animationDelay: '0.2s' }} />
        </div>
        <div className="flex gap-1 items-center">
          <div className="w-1.5 h-1.5 bg-cyan-400 rounded-full animate-ping" style={{ animationDuration: '2.5s', animationDelay: '0.5s' }} />
          <div className="w-6 h-1 bg-gradient-to-r from-cyan-400 to-transparent rounded animate-data-flow" style={{ animationDelay: '0.3s' }} />
          <div className="w-10 h-1 bg-cyan-300 rounded animate-pulse" style={{ animationDelay: '0.6s' }} />
        </div>
        <div className="flex gap-1 items-center">
          <div className="w-2 h-2 bg-blue-500 rounded-full animate-ping" style={{ animationDuration: '3s', animationDelay: '1s' }} />
          <div className="w-12 h-1 bg-gradient-to-r from-blue-500 to-transparent rounded animate-data-flow" style={{ animationDelay: '0.6s' }} />
          <div className="w-3 h-1 bg-blue-300 rounded animate-pulse" style={{ animationDelay: '1s' }} />
        </div>
      </div>
      
      {/* 左侧 - 旋转雷达扫描 */}
      <div className="absolute left-16 top-[45%]">
        <svg width="80" height="80" viewBox="0 0 80 80" className="animate-spin-slow">
          <circle cx="40" cy="40" r="35" fill="none" stroke="#3b82f6" strokeWidth="0.5" opacity="0.2" />
          <circle cx="40" cy="40" r="25" fill="none" stroke="#06b6d4" strokeWidth="0.5" opacity="0.3" />
          <circle cx="40" cy="40" r="15" fill="none" stroke="#3b82f6" strokeWidth="0.5" opacity="0.4" />
          <path d="M40,40 L40,5" stroke="url(#radarGradient)" strokeWidth="2" opacity="0.6" />
          <circle cx="40" cy="40" r="3" fill="#3b82f6" opacity="0.8" />
          <defs>
            <linearGradient id="radarGradient" x1="0%" y1="100%" x2="0%" y2="0%">
              <stop offset="0%" stopColor="#3b82f6" stopOpacity="0.8" />
              <stop offset="100%" stopColor="#06b6d4" stopOpacity="0" />
            </linearGradient>
          </defs>
        </svg>
      </div>
      
      {/* 左侧 - 心电图效果 */}
      <div className="absolute left-10 top-[60%] opacity-20">
        <svg width="100" height="40" viewBox="0 0 100 40">
          <path 
            d="M0,20 L15,20 L20,20 L25,5 L30,35 L35,10 L40,25 L45,20 L100,20" 
            fill="none" 
            stroke="#3b82f6" 
            strokeWidth="1.5"
            className="animate-ecg"
          />
        </svg>
      </div>
      
      {/* 数据流动效果 - 右边（增强版） */}
      <div className="absolute right-8 bottom-1/4 flex flex-col gap-3 opacity-30">
        <div className="flex gap-1 justify-end items-center">
          <div className="w-4 h-1 bg-purple-300 rounded animate-pulse" />
          <div className="w-8 h-1 bg-gradient-to-l from-purple-400 to-transparent rounded animate-data-flow-reverse" />
          <div className="w-2 h-2 bg-purple-400 rounded-full animate-ping" style={{ animationDuration: '2s' }} />
        </div>
        <div className="flex gap-1 justify-end items-center">
          <div className="w-10 h-1 bg-indigo-300 rounded animate-pulse" style={{ animationDelay: '0.5s' }} />
          <div className="w-6 h-1 bg-gradient-to-l from-indigo-400 to-transparent rounded animate-data-flow-reverse" style={{ animationDelay: '0.3s' }} />
          <div className="w-1.5 h-1.5 bg-indigo-400 rounded-full animate-ping" style={{ animationDuration: '2.5s', animationDelay: '0.5s' }} />
        </div>
        <div className="flex gap-1 justify-end items-center">
          <div className="w-3 h-1 bg-purple-300 rounded animate-pulse" style={{ animationDelay: '0.9s' }} />
          <div className="w-12 h-1 bg-gradient-to-l from-purple-500 to-transparent rounded animate-data-flow-reverse" style={{ animationDelay: '0.6s' }} />
          <div className="w-2 h-2 bg-purple-500 rounded-full animate-ping" style={{ animationDuration: '3s', animationDelay: '1s' }} />
        </div>
      </div>
      
      {/* 右侧 - DNA 双螺旋 */}
      <div className="absolute right-14 top-[40%]">
        <svg width="30" height="120" viewBox="0 0 30 120" className="opacity-20">
          <path d="M5,0 Q25,15 5,30 Q25,45 5,60 Q25,75 5,90 Q25,105 5,120" fill="none" stroke="#8b5cf6" strokeWidth="1.5" className="animate-dna" />
          <path d="M25,0 Q5,15 25,30 Q5,45 25,60 Q5,75 25,90 Q5,105 25,120" fill="none" stroke="#ec4899" strokeWidth="1.5" className="animate-dna" style={{ animationDelay: '0.5s' }} />
          {/* 连接线 */}
          <line x1="8" y1="15" x2="22" y2="15" stroke="#a855f7" strokeWidth="0.8" opacity="0.5" />
          <line x1="8" y1="45" x2="22" y2="45" stroke="#a855f7" strokeWidth="0.8" opacity="0.5" />
          <line x1="8" y1="75" x2="22" y2="75" stroke="#a855f7" strokeWidth="0.8" opacity="0.5" />
          <line x1="8" y1="105" x2="22" y2="105" stroke="#a855f7" strokeWidth="0.8" opacity="0.5" />
        </svg>
      </div>
      
      {/* 右侧 - 波形图 */}
      <div className="absolute right-10 top-[65%] opacity-20">
        <svg width="100" height="40" viewBox="0 0 100 40">
          <path 
            d="M0,20 Q10,10 20,20 T40,20 T60,20 T80,20 T100,20" 
            fill="none" 
            stroke="#8b5cf6" 
            strokeWidth="1.5"
            className="animate-wave"
          />
        </svg>
      </div>
      
      {/* 六边形装饰 - 动态旋转 */}
      <div className="absolute left-12 bottom-1/3 opacity-15 animate-spin-very-slow">
        <svg width="60" height="70" viewBox="0 0 60 70">
          <polygon points="30,0 60,17.5 60,52.5 30,70 0,52.5 0,17.5" fill="none" stroke="#3b82f6" strokeWidth="1" strokeDasharray="5 3" />
          <polygon points="30,10 50,22 50,48 30,60 10,48 10,22" fill="none" stroke="#06b6d4" strokeWidth="0.5" />
        </svg>
      </div>
      <div className="absolute right-16 top-1/3 opacity-15 animate-spin-very-slow-reverse">
        <svg width="50" height="58" viewBox="0 0 60 70">
          <polygon points="30,0 60,17.5 60,52.5 30,70 0,52.5 0,17.5" fill="none" stroke="#8b5cf6" strokeWidth="1" strokeDasharray="5 3" />
          <polygon points="30,10 50,22 50,48 30,60 10,48 10,22" fill="none" stroke="#ec4899" strokeWidth="0.5" />
        </svg>
      </div>
      
      {/* 数字矩阵效果 - 左侧 */}
      <div className="absolute left-6 top-[75%] font-mono text-[8px] text-blue-400/30 leading-tight animate-matrix">
        <div>01001</div>
        <div>10110</div>
        <div>01101</div>
        <div>11010</div>
      </div>
      
      {/* 数字矩阵效果 - 右侧 */}
      <div className="absolute right-6 top-[20%] font-mono text-[8px] text-purple-400/30 leading-tight animate-matrix" style={{ animationDelay: '1s' }}>
        <div>11010</div>
        <div>01101</div>
        <div>10010</div>
        <div>01011</div>
      </div>
      
      {/* 圆环装饰 - 动态脉冲 */}
      <div className="absolute left-20 top-1/2 w-16 h-16 border border-blue-300/20 rounded-full animate-ring-pulse" />
      <div className="absolute left-24 top-1/2 mt-2 w-8 h-8 border border-cyan-300/30 rounded-full animate-ring-pulse" style={{ animationDelay: '0.5s' }} />
      <div className="absolute right-24 bottom-1/2 w-20 h-20 border border-purple-300/15 rounded-full animate-ring-pulse" style={{ animationDelay: '1s' }} />
      <div className="absolute right-28 bottom-1/2 mb-4 w-10 h-10 border border-indigo-300/25 rounded-full animate-ring-pulse" style={{ animationDelay: '1.5s' }} />
      
      {/* 闪烁节点 - 更多分布 */}
      <div className="absolute left-[15%] top-[30%] w-1 h-1 bg-blue-400 rounded-full animate-twinkle" />
      <div className="absolute left-[10%] top-[50%] w-1.5 h-1.5 bg-cyan-400 rounded-full animate-twinkle" style={{ animationDelay: '0.3s' }} />
      <div className="absolute left-[12%] top-[70%] w-1 h-1 bg-blue-300 rounded-full animate-twinkle" style={{ animationDelay: '0.6s' }} />
      <div className="absolute right-[15%] top-[25%] w-1 h-1 bg-purple-400 rounded-full animate-twinkle" style={{ animationDelay: '0.9s' }} />
      <div className="absolute right-[10%] top-[55%] w-1.5 h-1.5 bg-pink-400 rounded-full animate-twinkle" style={{ animationDelay: '1.2s' }} />
      <div className="absolute right-[12%] top-[80%] w-1 h-1 bg-indigo-300 rounded-full animate-twinkle" style={{ animationDelay: '1.5s' }} />
      
      {/* ============================================================================ */}
      {/* 左侧空旷区域填充 */}
      {/* ============================================================================ */}
      
      {/* 左侧 - 垂直数据流 */}
      <div className="absolute left-[3%] top-[10%] h-[80%] w-px">
        <div className="h-full w-full bg-gradient-to-b from-transparent via-blue-400/30 to-transparent animate-vertical-flow" />
        <div className="absolute top-0 left-0 w-2 h-2 bg-blue-400/60 rounded-full animate-drop" />
        <div className="absolute top-0 left-0 w-2 h-2 bg-cyan-400/60 rounded-full animate-drop" style={{ animationDelay: '2s' }} />
        <div className="absolute top-0 left-0 w-2 h-2 bg-blue-300/60 rounded-full animate-drop" style={{ animationDelay: '4s' }} />
      </div>
      
      {/* 左侧 - 第二条垂直流 */}
      <div className="absolute left-[6%] top-[5%] h-[90%] w-px">
        <div className="h-full w-full bg-gradient-to-b from-transparent via-cyan-400/20 to-transparent animate-vertical-flow" style={{ animationDelay: '1s' }} />
        <div className="absolute top-0 left-0 w-1.5 h-1.5 bg-cyan-400/50 rounded-full animate-drop" style={{ animationDelay: '1s' }} />
        <div className="absolute top-0 left-0 w-1.5 h-1.5 bg-blue-400/50 rounded-full animate-drop" style={{ animationDelay: '3s' }} />
      </div>
      
      {/* 左侧 - 浮动方块群 */}
      <div className="absolute left-[4%] top-[15%] w-3 h-3 border border-blue-400/30 rotate-45 animate-float-rotate" />
      <div className="absolute left-[7%] top-[25%] w-2 h-2 border border-cyan-400/40 rotate-45 animate-float-rotate" style={{ animationDelay: '0.5s' }} />
      <div className="absolute left-[5%] top-[35%] w-4 h-4 border border-blue-300/25 rotate-45 animate-float-rotate" style={{ animationDelay: '1s' }} />
      <div className="absolute left-[8%] top-[55%] w-2.5 h-2.5 border border-cyan-300/35 rotate-45 animate-float-rotate" style={{ animationDelay: '1.5s' }} />
      <div className="absolute left-[3%] top-[65%] w-3 h-3 border border-blue-400/30 rotate-45 animate-float-rotate" style={{ animationDelay: '2s' }} />
      <div className="absolute left-[6%] top-[85%] w-2 h-2 border border-cyan-400/40 rotate-45 animate-float-rotate" style={{ animationDelay: '2.5s' }} />
      
      {/* 左侧 - 连接线网络 */}
      <svg className="absolute left-[2%] top-[20%] w-[10%] h-[60%] opacity-20">
        <line x1="10" y1="0" x2="50" y2="80" stroke="#3b82f6" strokeWidth="0.5" className="animate-line-fade" />
        <line x1="50" y1="80" x2="20" y2="160" stroke="#06b6d4" strokeWidth="0.5" className="animate-line-fade" style={{ animationDelay: '0.5s' }} />
        <line x1="20" y1="160" x2="60" y2="240" stroke="#3b82f6" strokeWidth="0.5" className="animate-line-fade" style={{ animationDelay: '1s' }} />
        <line x1="60" y1="240" x2="30" y2="320" stroke="#06b6d4" strokeWidth="0.5" className="animate-line-fade" style={{ animationDelay: '1.5s' }} />
        <circle cx="10" cy="0" r="2" fill="#3b82f6" className="animate-node-pulse" />
        <circle cx="50" cy="80" r="2" fill="#06b6d4" className="animate-node-pulse" style={{ animationDelay: '0.5s' }} />
        <circle cx="20" cy="160" r="2" fill="#3b82f6" className="animate-node-pulse" style={{ animationDelay: '1s' }} />
        <circle cx="60" cy="240" r="2" fill="#06b6d4" className="animate-node-pulse" style={{ animationDelay: '1.5s' }} />
        <circle cx="30" cy="320" r="2" fill="#3b82f6" className="animate-node-pulse" style={{ animationDelay: '2s' }} />
      </svg>
      
      {/* 左侧 - 脉冲环 */}
      <div className="absolute left-[5%] top-[45%]">
        <div className="w-12 h-12 rounded-full border border-blue-400/20 animate-ripple" />
        <div className="absolute inset-0 w-12 h-12 rounded-full border border-blue-400/20 animate-ripple" style={{ animationDelay: '1s' }} />
        <div className="absolute inset-0 w-12 h-12 rounded-full border border-blue-400/20 animate-ripple" style={{ animationDelay: '2s' }} />
        <div className="absolute inset-[20%] w-[60%] h-[60%] bg-blue-400/30 rounded-full animate-pulse" />
      </div>
      
      {/* 左侧 - 进度条组 */}
      <div className="absolute left-[2%] top-[78%] flex flex-col gap-2 opacity-25">
        <div className="w-16 h-1 bg-slate-300/50 rounded overflow-hidden">
          <div className="h-full bg-gradient-to-r from-blue-400 to-cyan-400 rounded animate-progress" style={{ width: '70%' }} />
        </div>
        <div className="w-12 h-1 bg-slate-300/50 rounded overflow-hidden">
          <div className="h-full bg-gradient-to-r from-cyan-400 to-blue-400 rounded animate-progress" style={{ width: '85%', animationDelay: '0.5s' }} />
        </div>
        <div className="w-14 h-1 bg-slate-300/50 rounded overflow-hidden">
          <div className="h-full bg-gradient-to-r from-blue-400 to-cyan-400 rounded animate-progress" style={{ width: '55%', animationDelay: '1s' }} />
        </div>
      </div>
      
      {/* ============================================================================ */}
      {/* 右侧空旷区域填充 */}
      {/* ============================================================================ */}
      
      {/* 右侧 - 垂直数据流 */}
      <div className="absolute right-[3%] top-[10%] h-[80%] w-px">
        <div className="h-full w-full bg-gradient-to-b from-transparent via-purple-400/30 to-transparent animate-vertical-flow-reverse" />
        <div className="absolute bottom-0 left-0 w-2 h-2 bg-purple-400/60 rounded-full animate-drop-up" />
        <div className="absolute bottom-0 left-0 w-2 h-2 bg-pink-400/60 rounded-full animate-drop-up" style={{ animationDelay: '2s' }} />
        <div className="absolute bottom-0 left-0 w-2 h-2 bg-indigo-400/60 rounded-full animate-drop-up" style={{ animationDelay: '4s' }} />
      </div>
      
      {/* 右侧 - 第二条垂直流 */}
      <div className="absolute right-[6%] top-[5%] h-[90%] w-px">
        <div className="h-full w-full bg-gradient-to-b from-transparent via-pink-400/20 to-transparent animate-vertical-flow-reverse" style={{ animationDelay: '1s' }} />
        <div className="absolute bottom-0 left-0 w-1.5 h-1.5 bg-pink-400/50 rounded-full animate-drop-up" style={{ animationDelay: '1s' }} />
        <div className="absolute bottom-0 left-0 w-1.5 h-1.5 bg-purple-400/50 rounded-full animate-drop-up" style={{ animationDelay: '3s' }} />
      </div>
      
      {/* 右侧 - 浮动方块群 */}
      <div className="absolute right-[4%] top-[15%] w-3 h-3 border border-purple-400/30 rotate-45 animate-float-rotate-reverse" />
      <div className="absolute right-[7%] top-[25%] w-2 h-2 border border-pink-400/40 rotate-45 animate-float-rotate-reverse" style={{ animationDelay: '0.5s' }} />
      <div className="absolute right-[5%] top-[35%] w-4 h-4 border border-indigo-300/25 rotate-45 animate-float-rotate-reverse" style={{ animationDelay: '1s' }} />
      <div className="absolute right-[8%] top-[55%] w-2.5 h-2.5 border border-purple-300/35 rotate-45 animate-float-rotate-reverse" style={{ animationDelay: '1.5s' }} />
      <div className="absolute right-[3%] top-[65%] w-3 h-3 border border-pink-400/30 rotate-45 animate-float-rotate-reverse" style={{ animationDelay: '2s' }} />
      <div className="absolute right-[6%] top-[85%] w-2 h-2 border border-indigo-400/40 rotate-45 animate-float-rotate-reverse" style={{ animationDelay: '2.5s' }} />
      
      {/* 右侧 - 连接线网络 */}
      <svg className="absolute right-[2%] top-[20%] w-[10%] h-[60%] opacity-20">
        <line x1="90" y1="0" x2="50" y2="80" stroke="#8b5cf6" strokeWidth="0.5" className="animate-line-fade" />
        <line x1="50" y1="80" x2="80" y2="160" stroke="#ec4899" strokeWidth="0.5" className="animate-line-fade" style={{ animationDelay: '0.5s' }} />
        <line x1="80" y1="160" x2="40" y2="240" stroke="#8b5cf6" strokeWidth="0.5" className="animate-line-fade" style={{ animationDelay: '1s' }} />
        <line x1="40" y1="240" x2="70" y2="320" stroke="#ec4899" strokeWidth="0.5" className="animate-line-fade" style={{ animationDelay: '1.5s' }} />
        <circle cx="90" cy="0" r="2" fill="#8b5cf6" className="animate-node-pulse" />
        <circle cx="50" cy="80" r="2" fill="#ec4899" className="animate-node-pulse" style={{ animationDelay: '0.5s' }} />
        <circle cx="80" cy="160" r="2" fill="#8b5cf6" className="animate-node-pulse" style={{ animationDelay: '1s' }} />
        <circle cx="40" cy="240" r="2" fill="#ec4899" className="animate-node-pulse" style={{ animationDelay: '1.5s' }} />
        <circle cx="70" cy="320" r="2" fill="#8b5cf6" className="animate-node-pulse" style={{ animationDelay: '2s' }} />
      </svg>
      
      {/* 右侧 - 脉冲环 */}
      <div className="absolute right-[5%] top-[45%]">
        <div className="w-12 h-12 rounded-full border border-purple-400/20 animate-ripple" />
        <div className="absolute inset-0 w-12 h-12 rounded-full border border-purple-400/20 animate-ripple" style={{ animationDelay: '1s' }} />
        <div className="absolute inset-0 w-12 h-12 rounded-full border border-purple-400/20 animate-ripple" style={{ animationDelay: '2s' }} />
        <div className="absolute inset-[20%] w-[60%] h-[60%] bg-purple-400/30 rounded-full animate-pulse" />
      </div>
      
      {/* 右侧 - 进度条组 */}
      <div className="absolute right-[2%] top-[78%] flex flex-col gap-2 opacity-25 items-end">
        <div className="w-16 h-1 bg-slate-300/50 rounded overflow-hidden">
          <div className="h-full bg-gradient-to-l from-purple-400 to-pink-400 rounded animate-progress-reverse ml-auto" style={{ width: '75%' }} />
        </div>
        <div className="w-12 h-1 bg-slate-300/50 rounded overflow-hidden">
          <div className="h-full bg-gradient-to-l from-pink-400 to-purple-400 rounded animate-progress-reverse ml-auto" style={{ width: '60%', animationDelay: '0.5s' }} />
        </div>
        <div className="w-14 h-1 bg-slate-300/50 rounded overflow-hidden">
          <div className="h-full bg-gradient-to-l from-indigo-400 to-purple-400 rounded animate-progress-reverse ml-auto" style={{ width: '90%', animationDelay: '1s' }} />
        </div>
      </div>
      
      {/* 左侧 - 圆点阵列 */}
      <div className="absolute left-[1%] top-[5%] grid grid-cols-3 gap-2 opacity-20">
        {[...Array(9)].map((_, i) => (
          <div key={`left-dot-${i}`} className="w-1 h-1 bg-blue-400 rounded-full animate-twinkle" style={{ animationDelay: `${i * 0.2}s` }} />
        ))}
      </div>
      
      {/* 右侧 - 圆点阵列 */}
      <div className="absolute right-[1%] top-[5%] grid grid-cols-3 gap-2 opacity-20">
        {[...Array(9)].map((_, i) => (
          <div key={`right-dot-${i}`} className="w-1 h-1 bg-purple-400 rounded-full animate-twinkle" style={{ animationDelay: `${i * 0.2 + 0.1}s` }} />
        ))}
      </div>
      
      {/* 左侧 - 弧形装饰 */}
      <svg className="absolute left-0 top-[30%] w-16 h-32 opacity-15">
        <path d="M0,0 Q60,64 0,128" fill="none" stroke="url(#arcGradientLeft)" strokeWidth="1" className="animate-arc-draw" />
        <defs>
          <linearGradient id="arcGradientLeft" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor="#3b82f6" stopOpacity="0" />
            <stop offset="50%" stopColor="#06b6d4" stopOpacity="1" />
            <stop offset="100%" stopColor="#3b82f6" stopOpacity="0" />
          </linearGradient>
        </defs>
      </svg>
      
      {/* 右侧 - 弧形装饰 */}
      <svg className="absolute right-0 top-[30%] w-16 h-32 opacity-15">
        <path d="M64,0 Q4,64 64,128" fill="none" stroke="url(#arcGradientRight)" strokeWidth="1" className="animate-arc-draw" style={{ animationDelay: '1s' }} />
        <defs>
          <linearGradient id="arcGradientRight" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor="#8b5cf6" stopOpacity="0" />
            <stop offset="50%" stopColor="#ec4899" stopOpacity="1" />
            <stop offset="100%" stopColor="#8b5cf6" stopOpacity="0" />
          </linearGradient>
        </defs>
      </svg>
      
      {/* 底部 - 横向数据流 */}
      <div className="absolute bottom-[3%] left-[5%] w-[40%] h-px">
        <div className="w-full h-full bg-gradient-to-r from-transparent via-blue-400/30 to-transparent animate-horizontal-flow" />
      </div>
      <div className="absolute bottom-[3%] right-[5%] w-[40%] h-px">
        <div className="w-full h-full bg-gradient-to-l from-transparent via-purple-400/30 to-transparent animate-horizontal-flow-reverse" />
      </div>
      
      {/* ============================================================================ */}
      {/* 额外密集填充 - 让整个背景更加丰富 */}
      {/* ============================================================================ */}
      
      {/* 左侧 - 更多垂直线条 */}
      {[...Array(8)].map((_, i) => (
        <div
          key={`left-line-${i}`}
          className="absolute w-px bg-gradient-to-b from-transparent via-blue-400/20 to-transparent animate-vertical-flow"
          style={{
            left: `${1 + i * 2}%`,
            top: '0',
            height: '100%',
            animationDelay: `${i * 0.5}s`
          }}
        />
      ))}
      
      {/* 右侧 - 更多垂直线条 */}
      {[...Array(8)].map((_, i) => (
        <div
          key={`right-line-${i}`}
          className="absolute w-px bg-gradient-to-b from-transparent via-purple-400/20 to-transparent animate-vertical-flow-reverse"
          style={{
            right: `${1 + i * 2}%`,
            top: '0',
            height: '100%',
            animationDelay: `${i * 0.5}s`
          }}
        />
      ))}
      
      {/* 左侧 - 密集圆点矩阵 */}
      <div className="absolute left-[1%] top-[10%] grid grid-cols-5 gap-3 opacity-25">
        {[...Array(25)].map((_, i) => (
          <div
            key={`left-matrix-${i}`}
            className="w-1.5 h-1.5 rounded-full animate-twinkle"
            style={{
              backgroundColor: i % 3 === 0 ? '#3b82f6' : i % 3 === 1 ? '#06b6d4' : '#60a5fa',
              animationDelay: `${i * 0.15}s`
            }}
          />
        ))}
      </div>
      
      {/* 右侧 - 密集圆点矩阵 */}
      <div className="absolute right-[1%] top-[10%] grid grid-cols-5 gap-3 opacity-25">
        {[...Array(25)].map((_, i) => (
          <div
            key={`right-matrix-${i}`}
            className="w-1.5 h-1.5 rounded-full animate-twinkle"
            style={{
              backgroundColor: i % 3 === 0 ? '#8b5cf6' : i % 3 === 1 ? '#ec4899' : '#a855f7',
              animationDelay: `${i * 0.15 + 0.1}s`
            }}
          />
        ))}
      </div>
      
      {/* 左侧 - 更多浮动圆环 */}
      {[...Array(6)].map((_, i) => (
        <div
          key={`left-ring-${i}`}
          className="absolute border border-blue-400/15 rounded-full animate-ring-pulse"
          style={{
            left: `${3 + (i % 3) * 4}%`,
            top: `${20 + i * 12}%`,
            width: `${20 + (i % 3) * 10}px`,
            height: `${20 + (i % 3) * 10}px`,
            animationDelay: `${i * 0.4}s`
          }}
        />
      ))}
      
      {/* 右侧 - 更多浮动圆环 */}
      {[...Array(6)].map((_, i) => (
        <div
          key={`right-ring-${i}`}
          className="absolute border border-purple-400/15 rounded-full animate-ring-pulse"
          style={{
            right: `${3 + (i % 3) * 4}%`,
            top: `${20 + i * 12}%`,
            width: `${20 + (i % 3) * 10}px`,
            height: `${20 + (i % 3) * 10}px`,
            animationDelay: `${i * 0.4 + 0.2}s`
          }}
        />
      ))}
      
      {/* 左侧 - 飞行光点 */}
      {[...Array(5)].map((_, i) => (
        <div
          key={`left-fly-${i}`}
          className="absolute w-1 h-1 bg-cyan-400/60 rounded-full animate-fly-across"
          style={{
            top: `${15 + i * 18}%`,
            animationDelay: `${i * 1.5}s`
          }}
        />
      ))}
      
      {/* 右侧 - 飞行光点 */}
      {[...Array(5)].map((_, i) => (
        <div
          key={`right-fly-${i}`}
          className="absolute w-1 h-1 bg-pink-400/60 rounded-full animate-fly-across-reverse"
          style={{
            top: `${25 + i * 18}%`,
            animationDelay: `${i * 1.5 + 0.75}s`
          }}
        />
      ))}
      
      {/* 左侧 - 脉冲波纹组 */}
      <div className="absolute left-[8%] top-[15%]">
        {[...Array(3)].map((_, i) => (
          <div
            key={`left-ripple-${i}`}
            className="absolute w-16 h-16 border border-blue-400/20 rounded-full animate-ripple"
            style={{ animationDelay: `${i * 1}s` }}
          />
        ))}
      </div>
      <div className="absolute left-[5%] top-[70%]">
        {[...Array(3)].map((_, i) => (
          <div
            key={`left-ripple2-${i}`}
            className="absolute w-12 h-12 border border-cyan-400/20 rounded-full animate-ripple"
            style={{ animationDelay: `${i * 1 + 0.5}s` }}
          />
        ))}
      </div>
      
      {/* 右侧 - 脉冲波纹组 */}
      <div className="absolute right-[8%] top-[15%]">
        {[...Array(3)].map((_, i) => (
          <div
            key={`right-ripple-${i}`}
            className="absolute w-16 h-16 border border-purple-400/20 rounded-full animate-ripple"
            style={{ animationDelay: `${i * 1}s` }}
          />
        ))}
      </div>
      <div className="absolute right-[5%] top-[70%]">
        {[...Array(3)].map((_, i) => (
          <div
            key={`right-ripple2-${i}`}
            className="absolute w-12 h-12 border border-pink-400/20 rounded-full animate-ripple"
            style={{ animationDelay: `${i * 1 + 0.5}s` }}
          />
        ))}
      </div>
      
      {/* 左侧 - 旋转三角形 */}
      <svg className="absolute left-[4%] top-[35%] w-8 h-8 opacity-20 animate-spin-very-slow">
        <polygon points="16,0 32,28 0,28" fill="none" stroke="#3b82f6" strokeWidth="1" />
      </svg>
      <svg className="absolute left-[10%] top-[55%] w-6 h-6 opacity-15 animate-spin-very-slow-reverse">
        <polygon points="12,0 24,21 0,21" fill="none" stroke="#06b6d4" strokeWidth="1" />
      </svg>
      
      {/* 右侧 - 旋转三角形 */}
      <svg className="absolute right-[4%] top-[35%] w-8 h-8 opacity-20 animate-spin-very-slow-reverse">
        <polygon points="16,0 32,28 0,28" fill="none" stroke="#8b5cf6" strokeWidth="1" />
      </svg>
      <svg className="absolute right-[10%] top-[55%] w-6 h-6 opacity-15 animate-spin-very-slow">
        <polygon points="12,0 24,21 0,21" fill="none" stroke="#ec4899" strokeWidth="1" />
      </svg>
      
      {/* 左侧 - 更多数字流 */}
      <div className="absolute left-[2%] top-[40%] font-mono text-[6px] text-blue-400/20 leading-tight animate-matrix">
        <div>1010101</div>
        <div>0110110</div>
        <div>1101001</div>
        <div>0011010</div>
        <div>1100101</div>
      </div>
      <div className="absolute left-[12%] top-[60%] font-mono text-[6px] text-cyan-400/20 leading-tight animate-matrix" style={{ animationDelay: '1.5s' }}>
        <div>0101010</div>
        <div>1001101</div>
        <div>0110010</div>
        <div>1010101</div>
      </div>
      
      {/* 右侧 - 更多数字流 */}
      <div className="absolute right-[2%] top-[40%] font-mono text-[6px] text-purple-400/20 leading-tight animate-matrix" style={{ animationDelay: '0.5s' }}>
        <div>1101010</div>
        <div>0010110</div>
        <div>1011001</div>
        <div>0100101</div>
        <div>1110010</div>
      </div>
      <div className="absolute right-[12%] top-[60%] font-mono text-[6px] text-pink-400/20 leading-tight animate-matrix" style={{ animationDelay: '2s' }}>
        <div>0011010</div>
        <div>1100101</div>
        <div>0101100</div>
        <div>1010011</div>
      </div>
      
      {/* 顶部 - 横向扫描线 */}
      <div className="absolute top-[5%] left-0 w-full h-px">
        <div className="w-20 h-full bg-gradient-to-r from-transparent via-blue-400/50 to-transparent animate-scan-line" />
      </div>
      <div className="absolute top-[95%] left-0 w-full h-px">
        <div className="w-20 h-full bg-gradient-to-r from-transparent via-purple-400/50 to-transparent animate-scan-line" style={{ animationDelay: '3s' }} />
      </div>
      
      {/* 左侧 - 垂直扫描线 */}
      <div className="absolute left-[5%] top-0 w-px h-full">
        <div className="w-full h-16 bg-gradient-to-b from-transparent via-cyan-400/40 to-transparent animate-scan-line-vertical" />
      </div>
      
      {/* 右侧 - 垂直扫描线 */}
      <div className="absolute right-[5%] top-0 w-px h-full">
        <div className="w-full h-16 bg-gradient-to-b from-transparent via-pink-400/40 to-transparent animate-scan-line-vertical" style={{ animationDelay: '2s' }} />
      </div>
      
      {/* 额外的闪烁星点 - 分布更广 */}
      {[...Array(40)].map((_, i) => (
        <div
          key={`star-${i}`}
          className="absolute rounded-full animate-twinkle"
          style={{
            width: `${1 + Math.random() * 2}px`,
            height: `${1 + Math.random() * 2}px`,
            backgroundColor: i % 4 === 0 ? '#3b82f6' : i % 4 === 1 ? '#8b5cf6' : i % 4 === 2 ? '#06b6d4' : '#ec4899',
            opacity: 0.3,
            left: `${Math.random() * 100}%`,
            top: `${Math.random() * 100}%`,
            animationDelay: `${Math.random() * 4}s`,
            animationDuration: `${1.5 + Math.random() * 2}s`
          }}
        />
      ))}
    </div>
  );
}

// ============================================================================
// 添加到全局样式的动画
// ============================================================================
export const techBackgroundStyles = `
/* 慢速浮动 */
@keyframes float-slow {
  0%, 100% {
    transform: translateY(0px) translateX(0px);
    opacity: 0.3;
  }
  25% {
    transform: translateY(-20px) translateX(10px);
    opacity: 0.5;
  }
  50% {
    transform: translateY(-10px) translateX(-10px);
    opacity: 0.4;
  }
  75% {
    transform: translateY(-25px) translateX(5px);
    opacity: 0.6;
  }
}

/* 中速浮动 */
@keyframes float-medium {
  0%, 100% {
    transform: translateY(0px) translateX(0px) scale(1);
    opacity: 0.3;
  }
  33% {
    transform: translateY(-15px) translateX(15px) scale(1.1);
    opacity: 0.5;
  }
  66% {
    transform: translateY(-8px) translateX(-12px) scale(0.9);
    opacity: 0.4;
  }
}

/* 快速浮动 */
@keyframes float-fast {
  0%, 100% {
    transform: translateY(0px) translateX(0px) rotate(0deg);
    opacity: 0.3;
  }
  25% {
    transform: translateY(-12px) translateX(8px) rotate(90deg);
    opacity: 0.6;
  }
  50% {
    transform: translateY(-6px) translateX(-6px) rotate(180deg);
    opacity: 0.4;
  }
  75% {
    transform: translateY(-18px) translateX(4px) rotate(270deg);
    opacity: 0.5;
  }
}

/* 上升动画 */
@keyframes rise {
  0% {
    transform: translateY(0) translateX(0);
    opacity: 0;
  }
  10% {
    opacity: 0.6;
  }
  90% {
    opacity: 0.6;
  }
  100% {
    transform: translateY(-100vh) translateX(20px);
    opacity: 0;
  }
}

/* Blob 变形动画 */
@keyframes blob {
  0%, 100% {
    transform: translate(0, 0) scale(1);
  }
  25% {
    transform: translate(20px, -20px) scale(1.05);
  }
  50% {
    transform: translate(-10px, 10px) scale(0.95);
  }
  75% {
    transform: translate(15px, 15px) scale(1.02);
  }
}

/* 旋转脉冲 */
@keyframes spin-pulse {
  0% {
    transform: rotate(0deg) scale(1);
    opacity: 0.1;
  }
  50% {
    transform: rotate(180deg) scale(1.1);
    opacity: 0.15;
  }
  100% {
    transform: rotate(360deg) scale(1);
    opacity: 0.1;
  }
}

.animate-float-slow {
  animation: float-slow 8s ease-in-out infinite;
}

.animate-float-medium {
  animation: float-medium 5s ease-in-out infinite;
}

.animate-float-fast {
  animation: float-fast 3s ease-in-out infinite;
}

.animate-rise {
  animation: rise 10s linear infinite;
}

.animate-blob {
  animation: blob 12s ease-in-out infinite;
}

.animate-spin-pulse {
  animation: spin-pulse 20s linear infinite;
}

/* 动画延迟 */
.animation-delay-2000 {
  animation-delay: 2s;
}

.animation-delay-4000 {
  animation-delay: 4s;
}

.animation-delay-6000 {
  animation-delay: 6s;
}
`;
