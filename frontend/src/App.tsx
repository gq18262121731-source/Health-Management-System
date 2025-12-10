import React, { useState, useEffect, useRef } from 'react';
import { VoiceProvider } from './contexts/VoiceContext';
import { Navbar } from './components/layout/LayoutComponents';
import { AIConsultation } from './components/consultation/AIConsultation';
import { PsychologyPage } from './components/psychology/PsychologyPage';
import { MyInfo } from './components/MyInfo';
import { LoginPage } from './components/login/LoginPage';
import { ElderlyLoginPage } from './components/login/ElderlyLoginPage';
import { ChildrenLoginPage } from './components/login/ChildrenLoginPage';
import { CommunityLoginPage } from './components/login/CommunityLoginPage';
import { ChildrenDashboard } from './components/children/ChildrenDashboard';
import { CommunityDashboard } from './components/community/CommunityDashboard';
import { FloatingAIAssistant, FloatingAIAssistantRef } from './components/elderly/FloatingAIAssistant';
import { VoiceControlBar } from './components/elderly/VoiceControlBar';
import { AIAnalysisButton } from './components/elderly/AIAnalysisButton';
import { FullDuplexVoiceAssistant } from './components/elderly/FullDuplexVoiceAssistant';
import { HealthCardWithAI } from './components/elderly/HealthCardWithAI';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './components/ui/card';
import { Button } from './components/ui/button';
import { 
  Activity, 
  Heart, 
  Droplets, 
  Thermometer, 
  Clock, 
  FileText, 
  Download, 
  ChevronLeft,
  Loader2
} from 'lucide-react';
import { MoodQuickCard } from './components/dashboard/MoodQuickCard';
import { HealthAssessmentReport } from './components/dashboard/HealthAssessmentReport';
import { 
  HeartRateChart, 
  SleepAnalysisChart, 
  BloodPressureChart, 
  HealthRadarChart 
} from './components/dashboard/HealthCharts';
import { HealthRadarWithAssessment } from './components/dashboard/HealthRadarWithAssessment';
import { TechBackground } from './components/ui/TechBackground';
import { getTodayHealthData, TodayHealthData } from './services/healthDataApi';
import { generateAndDownloadReport } from './services/reportGenerator';

// ============================================================================
// 应用主文件：智慧健康管理系统
// 
// 老人端涉及的主要API:
// - GET /api/v1/elderly/health/today - 获取今日健康数据（体温、血糖、血压、心率、步数、体重）
// - GET /api/v1/elderly/reports/current - 获取当前报告
// - GET /api/v1/elderly/reports/history?page=1&pageSize=10 - 获取历史报告列表
// - GET /api/v1/elderly/health/charts/heartrate?period=week - 获取心率趋势图数据
// - GET /api/v1/elderly/health/charts/sleep?period=week - 获取睡眠分析数据
// - GET /api/v1/elderly/health/charts/bloodpressure?period=week - 获取血压趋势数据
// - GET /api/v1/elderly/health/charts/radar - 获取健康雷达图数据
// 
// 功能模块：
// 1. 角色选择和登录流程管理
// 2. 老人端：今日健康、历史报告、AI助手、心理健康、个人信息
// 3. 子女端：跳转到 ChildrenDashboard
// 4. 社区端：跳转到 CommunityDashboard
// 5. 可拖动的AI助手悬浮窗
// ============================================================================

export default function App() {
  const [selectedRole, setSelectedRole] = useState<'elderly' | 'children' | 'community' | null>(null);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [activeTab, setActiveTab] = useState('analysis');
  const [showHistoricalReports, setShowHistoricalReports] = useState(false);
  const [initialMood, setInitialMood] = useState<string | null>(null);
  const aiAssistantRef = React.useRef<FloatingAIAssistantRef>(null);
  
  // 动态健康数据状态
  const [healthData, setHealthData] = useState<TodayHealthData | null>(null);
  const [healthDataLoading, setHealthDataLoading] = useState(false);
  const [isGeneratingReport, setIsGeneratingReport] = useState(false);

  // 生成并下载健康报告（调用后端 health_assessment_system）
  const handleGenerateReport = async () => {
    setIsGeneratingReport(true);
    
    try {
      // 调用后端评估系统生成报告
      await generateAndDownloadReport(
        healthData ? {
          heartRate: healthData.vitalSigns.heartRate.value,
          bloodPressure: { 
            systolic: healthData.vitalSigns.bloodPressure.systolic, 
            diastolic: healthData.vitalSigns.bloodPressure.diastolic 
          },
          bloodSugar: healthData.vitalSigns.bloodSugar.value,
          temperature: healthData.vitalSigns.temperature.value,
          steps: healthData.activity.steps,
          weight: healthData.weight.value
        } : undefined,
        {
          overallScore: 85,
          healthStatus: '健康状态良好',
          recommendations: [
            '保持规律的作息时间，每天保证7-8小时睡眠',
            '每天进行30分钟以上的有氧运动',
            '饮食均衡，多吃蔬菜水果，少油少盐',
            '定期监测血压血糖，保持健康记录',
            '保持良好心态，适当进行放松活动'
          ]
        },
        'demo'  // 用户ID
      );
    } catch (error) {
      console.error('生成报告失败:', error);
    } finally {
      setIsGeneratingReport(false);
    }
  };

  // 获取今日健康数据
  useEffect(() => {
    if (isLoggedIn && selectedRole === 'elderly') {
      const fetchHealthData = async () => {
        setHealthDataLoading(true);
        try {
          // 使用实际登录的用户ID（这里暂时用 demo 或 elderly_001）
          const result = await getTodayHealthData('demo');
          if (result.success && result.data) {
            setHealthData(result.data);
          }
        } catch (error) {
          console.error('获取健康数据失败:', error);
        } finally {
          setHealthDataLoading(false);
        }
      };
      
      fetchHealthData();
      
      // 每分钟刷新一次数据
      const interval = setInterval(fetchHealthData, 60000);
      return () => clearInterval(interval);
    }
  }, [isLoggedIn, selectedRole]);

  // AI分析处理函数
  const handleAIAnalysis = (prompt: string) => {
    aiAssistantRef.current?.openWithPrompt(prompt);
  };

  // Handle role selection (from role selection page)
  const handleSelectRole = (role: 'elderly' | 'children' | 'community') => {
    setSelectedRole(role);
    setIsLoggedIn(false); // 选择角色后，需要登录
  };

  // Handle successful login
  const handleLogin = () => {
    setIsLoggedIn(true);
  };

  // Handle back from login page
  const handleBackToRoleSelection = () => {
    setSelectedRole(null);
    setIsLoggedIn(false);
  };

  // Handle logout
  const handleLogout = () => {
    setSelectedRole(null);
    setIsLoggedIn(false);
    setActiveTab('analysis');
    // 停止任何正在播放的语音
    window.speechSynthesis.cancel();
  };

  // Step 1: Show role selection page
  if (!selectedRole) {
    return <LoginPage onSelectRole={handleSelectRole} />;
  }

  // Step 2: Show login page for selected role
  if (selectedRole && !isLoggedIn) {
    if (selectedRole === 'elderly') {
      return <ElderlyLoginPage onBack={handleBackToRoleSelection} onLogin={handleLogin} />;
    }
    if (selectedRole === 'children') {
      return <ChildrenLoginPage onBack={handleBackToRoleSelection} onLogin={handleLogin} />;
    }
    if (selectedRole === 'community') {
      return <CommunityLoginPage onBack={handleBackToRoleSelection} onLogin={handleLogin} />;
    }
  }

  // Step 3: Show dashboard after successful login
  if (selectedRole === 'children' && isLoggedIn) {
    return (
      <VoiceProvider>
        <ChildrenDashboard onLogout={handleLogout} />
        <FloatingAIAssistant ref={aiAssistantRef} />
      </VoiceProvider>
    );
  }

  if (selectedRole === 'community' && isLoggedIn) {
    return (
      <VoiceProvider>
        <CommunityDashboard onLogout={handleLogout} />
        <FloatingAIAssistant ref={aiAssistantRef} />
      </VoiceProvider>
    );
  }

  // Otherwise show elderly dashboard (existing code)
  // Reset historical reports view when changing tabs
  const handleTabChange = (tab: string) => {
    setActiveTab(tab);
    if (tab !== 'reports') {
      setShowHistoricalReports(false);
    }
  };

  // Navigate to psychology page with mood
  const handleNavigateToMood = (mood: string) => {
    setInitialMood(mood);
    handleTabChange('psychology');
  };

  return (
    <VoiceProvider>
    <div className="min-h-screen w-full bg-slate-50 text-slate-900 dark:text-slate-50 font-sans relative">
      {/* 科技感背景 */}
      <TechBackground />
      
      {/* Left Sidebar Navigation */}
      <Navbar activeTab={activeTab} setActiveTab={handleTabChange} onLogout={handleLogout} />
      
      {/* Main Content - 左侧留出侧边栏空间 */}
      <div className="flex flex-col relative z-10 ml-[590px]">
        {/* 顶部导航栏 - sticky固定在顶部，自动填满宽度 */}
        <div 
          className="sticky top-0 z-50 h-20 flex items-center justify-end pr-6"
          style={{
            background: 'linear-gradient(to bottom, #0d9488, #0f9a8d)',
          }}
        >
          {/* 语音控制栏 - 右侧 */}
          <VoiceControlBar 
            className="" 
            healthData={healthData}
            userName={healthData?.userName || '您'}
            onNavigate={(route) => {
              // 处理语音导航命令（路由名与后端 voice_control_service.py 对应）
              console.log('语音导航:', route);
              if (route === 'back') {
                setShowHistoricalReports(false);
              } else if (route === 'analysis') {
                setActiveTab('analysis');
                setShowHistoricalReports(false);
              } else if (route === 'reports') {
                setActiveTab('reports');
              } else if (route === 'consultation') {
                setActiveTab('consultation');
              } else if (route === 'psychology') {
                setActiveTab('psychology');
              } else if (route === 'myinfo') {
                setActiveTab('myinfo');
              }
            }}
            onEmergency={() => {
              // 紧急呼救（模拟通知）
              console.log('🚨 紧急呼救触发！');
              alert('🚨 紧急呼救已触发！正在通知您的紧急联系人...');
              // TODO: 实际项目中可以发送通知到后端
            }}
            onGenerateReport={() => {
              // 生成报告
              console.log('📋 语音触发生成报告');
              setActiveTab('reports');
              handleGenerateReport();
            }}
            onSetReminder={(data) => {
              // 设置提醒（暂时用 alert 模拟）
              console.log('⏰ 设置提醒:', data);
              // TODO: 实现真正的提醒系统
              if (data.time) {
                alert(`已设置${data.time}的${data.type === 'medication' ? '吃药' : ''}提醒`);
              }
            }}
          />
        </div>
        
        <main className="flex-1 p-6 pl-8">
          <div className="mx-auto max-w-7xl space-y-6">
            
            {/* --- View: Health Analysis (Default Dashboard) --- */}
            {activeTab === 'analysis' && (
              <>
                {/* Welcome Section */}
                <div className="flex items-center justify-between">
                  <div className="flex flex-col gap-1">
                    <h2 className="text-2xl font-bold tracking-tight text-[40px]">下午好, 张三</h2>
                    <p className="text-muted-foreground text-[24px]">这是你今天的健康监测概览。</p>
                  </div>
                  <div className="text-lg text-muted-foreground text-[32px] font-bold">
                    {new Date().toLocaleDateString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric', weekday: 'long' })}
                  </div>
                </div>

                {/* Stats Grid - 4:6 Layout */}
                <div className="grid gap-4 grid-cols-10">
                  {/* Left: Comprehensive Indicators - 4 columns */}
                  <div className="col-span-4">
                    <Card className="h-full bg-gradient-to-br from-purple-100 to-purple-50 border-purple-200">
                      <CardHeader className="pb-3">
                        <CardTitle className="text-lg font-medium text-muted-foreground flex items-center gap-2 text-[36px]">
                          <Thermometer className="h-5 w-5 text-purple-500" />
                          综合指标
                        </CardTitle>
                      </CardHeader>
                      <CardContent className="space-y-6">
                        {healthDataLoading ? (
                          <div className="flex items-center justify-center py-8">
                            <Loader2 className="h-6 w-6 animate-spin text-purple-500" />
                            <span className="ml-2 text-muted-foreground">加载中...</span>
                          </div>
                        ) : (
                          <>
                            {/* Temperature */}
                            <div className="space-y-2">
                              <div className="text-base text-muted-foreground text-[32px]">体温</div>
                              <div className="flex items-end justify-between">
                                <div className="flex items-baseline gap-2">
                                  <span className="text-5xl font-bold">{healthData?.vitalSigns.temperature.value || 36.5}</span>
                                  <span className="text-xl text-muted-foreground">°C</span>
                                </div>
                                <div className="text-base text-orange-600 flex items-center gap-1">
                                  <span>{healthData?.vitalSigns.temperature.status || '正常'}</span>
                                </div>
                              </div>
                            </div>
                            
                            {/* Steps */}
                            <div className="space-y-2 pt-4 border-t">
                              <div className="text-base text-muted-foreground text-[32px]">步数</div>
                              <div className="flex items-end justify-between">
                                <div className="flex items-baseline gap-2">
                                  <span className="text-5xl font-bold">{(healthData?.activity.steps || 0).toLocaleString()}</span>
                                  <span className="text-xl text-muted-foreground">步</span>
                                </div>
                                <div className="text-base text-green-600">
                                  <span>目标 {(healthData?.activity.goal || 10000).toLocaleString()}步</span>
                                </div>
                              </div>
                            </div>
                            
                            {/* Weight */}
                            <div className="space-y-2 pt-4 border-t">
                              <div className="text-base text-muted-foreground text-[32px]">体重</div>
                              <div className="flex items-end justify-between">
                                <div className="flex items-baseline gap-2">
                                  <span className="text-5xl font-bold">{healthData?.weight.value || 65}</span>
                                  <span className="text-xl text-muted-foreground">kg</span>
                                </div>
                                <div className="text-base text-blue-600">
                                  <span>BMI: {healthData?.weight.bmi || 22} {healthData?.weight.bmiStatus || '正常'}</span>
                                </div>
                              </div>
                            </div>
                          </>
                        )}
                      </CardContent>
                    </Card>
                  </div>

                  {/* Right: Blood Sugar, Blood Pressure, Heart Rate - 6 columns */}
                  <div className="col-span-6 space-y-4">
                    {/* Blood Sugar */}
                    <HealthCardWithAI
                      icon={Droplets}
                      iconColor="text-amber-500"
                      value={healthData?.vitalSigns.bloodSugar.value || 5.5}
                      unit="mmol/L"
                      title="血糖"
                      status={healthData?.vitalSigns.bloodSugar.status || '正常'}
                      statusColor="text-muted-foreground"
                      bgGradient="bg-gradient-to-br from-amber-100 to-amber-50"
                      borderColor="border-amber-200"
                      dataType="血糖"
                      onAnalyze={handleAIAnalysis}
                    />

                    {/* Blood Pressure */}
                    <HealthCardWithAI
                      icon={Activity}
                      iconColor="text-blue-500"
                      value={`${healthData?.vitalSigns.bloodPressure.systolic || 120}/${healthData?.vitalSigns.bloodPressure.diastolic || 80}`}
                      unit="mmHg"
                      title="血压"
                      status={healthData?.vitalSigns.bloodPressure.status || '正常'}
                      statusColor="text-muted-foreground"
                      bgGradient="bg-gradient-to-br from-blue-100 to-blue-50"
                      borderColor="border-blue-200"
                      dataType="血压"
                      onAnalyze={handleAIAnalysis}
                    />

                    {/* Heart Rate */}
                    <HealthCardWithAI
                      icon={Heart}
                      iconColor="text-rose-500"
                      value={healthData?.vitalSigns.heartRate.value || 75}
                      unit="bpm"
                      title="平均心率"
                      status={healthData?.vitalSigns.heartRate.change ? `${healthData.vitalSigns.heartRate.change > 0 ? '+' : ''}${healthData.vitalSigns.heartRate.change}bpm 较昨日` : '正常'}
                      statusColor={healthData?.vitalSigns.heartRate.change && healthData.vitalSigns.heartRate.change > 0 ? 'text-green-600' : 'text-muted-foreground'}
                      bgGradient="bg-gradient-to-br from-rose-100 to-rose-50"
                      borderColor="border-rose-200"
                      dataType="心率"
                      onAnalyze={handleAIAnalysis}
                    />
                  </div>
                </div>

                {/* Mood Quick Card */}
                <MoodQuickCard onNavigateToMood={handleNavigateToMood} />

                {/* AI 健康评估雷达图 - 集成 health_assessment_system */}
                <HealthRadarWithAssessment userId="demo" />

                {/* Charts Section */}
                <div className="space-y-4">
                  <HeartRateChart />
                  <SleepAnalysisChart />
                  <BloodPressureChart />
                  <HealthRadarChart />
                </div>
              </>
            )}

            {/* --- View: AI Consultation --- 使用讯飞星火 API */}
            {activeTab === 'consultation' && (
              <div className="space-y-6">
                {/* 全双工语音助手 - 参考 FireRedChat */}
                <FullDuplexVoiceAssistant 
                  className="bg-gradient-to-br from-indigo-50 to-purple-50 border-indigo-200"
                  onMessage={(msg) => console.log('语音消息:', msg)}
                />
                
                {/* 文字对话 */}
                <AIConsultation />
              </div>
            )}

            {/* --- View: Reports --- */}
            {activeTab === 'reports' && (
              <>
                {!showHistoricalReports ? (
                  /* Current Health Report Center - Default View */
                  <div className="space-y-6">
                    <div className="flex items-center justify-between">
                      <h2 className="text-3xl font-bold tracking-tight">健康报告中心</h2>
                      <Button 
                        size="lg" 
                        variant="outline"
                        className="text-lg px-6 py-6"
                        onClick={() => setShowHistoricalReports(true)}
                      >
                        <Clock className="mr-2 h-5 w-5" />
                        历史报告
                      </Button>
                    </div>

                    {/* AI 智能健康评估 - 集成 health_assessment_system */}
                    <HealthAssessmentReport 
                      userId="demo" 
                      userName="张三"
                      onReportGenerated={(report) => console.log('报告生成:', report)}
                    />

                    {/* Current Report Analysis */}
                    <Card className="bg-gradient-to-br from-blue-50 to-cyan-50 border-blue-200">
                      <CardHeader>
                        <div className="flex items-start justify-between">
                          <div className="space-y-2">
                            <CardTitle className="text-3xl">当前健康数据分析</CardTitle>
                            <CardDescription className="text-xl">更新于 2024-11-26 14:30</CardDescription>
                          </div>
                          <div className="p-3 bg-blue-100 text-blue-600 rounded-lg">
                            <Activity className="h-8 w-8" />
                          </div>
                        </div>
                      </CardHeader>
                      <CardContent className="space-y-6">
                        {/* Key Metrics Grid */}
                        <div className="grid grid-cols-2 gap-4">
                          <Card className="bg-white/80">
                            <CardContent className="pt-6">
                              <div className="space-y-2">
                                <div className="text-lg text-muted-foreground flex items-center gap-2">
                                  <Heart className="h-5 w-5 text-rose-500" />
                                  平均心率
                                </div>
                                <div className="flex items-baseline gap-2">
                                  <span className="text-5xl font-bold">72</span>
                                  <span className="text-xl text-muted-foreground">bpm</span>
                                </div>
                                <p className="text-lg text-green-600">正常范围</p>
                              </div>
                            </CardContent>
                          </Card>

                          <Card className="bg-white/80">
                            <CardContent className="pt-6">
                              <div className="space-y-2">
                                <div className="text-lg text-muted-foreground flex items-center gap-2">
                                  <Activity className="h-5 w-5 text-blue-500" />
                                  血压
                                </div>
                                <div className="flex items-baseline gap-2">
                                  <span className="text-5xl font-bold">118/75</span>
                                  <span className="text-xl text-muted-foreground">mmHg</span>
                                </div>
                                <p className="text-lg text-green-600">正常范围</p>
                              </div>
                            </CardContent>
                          </Card>

                          <Card className="bg-white/80">
                            <CardContent className="pt-6">
                              <div className="space-y-2">
                                <div className="text-lg text-muted-foreground flex items-center gap-2">
                                  <Droplets className="h-5 w-5 text-amber-500" />
                                  血糖
                                </div>
                                <div className="flex items-baseline gap-2">
                                  <span className="text-5xl font-bold">5.2</span>
                                  <span className="text-xl text-muted-foreground">mmol/L</span>
                                </div>
                                <p className="text-lg text-green-600">正常范围</p>
                              </div>
                            </CardContent>
                          </Card>

                          <Card className="bg-white/80">
                            <CardContent className="pt-6">
                              <div className="space-y-2">
                                <div className="text-lg text-muted-foreground flex items-center gap-2">
                                  <Thermometer className="h-5 w-5 text-purple-500" />
                                  体温
                                </div>
                                <div className="flex items-baseline gap-2">
                                  <span className="text-5xl font-bold">36.5</span>
                                  <span className="text-xl text-muted-foreground">°C</span>
                                </div>
                                <p className="text-lg text-green-600">正常范围</p>
                              </div>
                            </CardContent>
                          </Card>
                        </div>

                        {/* Health Summary */}
                        <Card className="bg-white/80">
                          <CardHeader>
                            <CardTitle className="text-2xl">综合健康评估</CardTitle>
                          </CardHeader>
                          <CardContent>
                            <div className="space-y-4">
                              <p className="text-xl text-muted-foreground leading-relaxed">
                                您的健康状况总体良好。各项生理指标均在正常范围内，建议继续保持良好的生活习惯。
                              </p>
                              <div className="space-y-3 pt-4 border-t">
                                <h4 className="text-xl font-semibold">健建议</h4>
                                <ul className="space-y-2 text-lg text-muted-foreground">
                                  <li className="flex items-start gap-2">
                                    <span className="text-green-500 mt-1">✓</span>
                                    <span>保持规律的作息时间，每天睡眠7-8小时</span>
                                  </li>
                                  <li className="flex items-start gap-2">
                                    <span className="text-green-500 mt-1">✓</span>
                                    <span>继续保持每天8000步以上的运动量</span>
                                  </li>
                                  <li className="flex items-start gap-2">
                                    <span className="text-green-500 mt-1">✓</span>
                                    <span>注意饮食均衡，适量摄入蔬菜水果</span>
                                  </li>
                                  <li className="flex items-start gap-2">
                                    <span className="text-green-500 mt-1">✓</span>
                                    <span>定期监测血压血糖，保持健康记录</span>
                                  </li>
                                </ul>
                              </div>
                            </div>
                          </CardContent>
                        </Card>

                        <div className="flex gap-3">
                          <Button 
                            variant="default" 
                            size="lg" 
                            className="flex-1 text-lg py-6"
                            onClick={handleGenerateReport}
                            disabled={isGeneratingReport}
                          >
                            {isGeneratingReport ? (
                              <>
                                <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                                生成中...
                              </>
                            ) : (
                              <>
                                <FileText className="mr-2 h-5 w-5" />
                                生成完整报告
                              </>
                            )}
                          </Button>
                        </div>
                      </CardContent>
                    </Card>
                  </div>
                ) : (
                  /* Historical Reports List View */
                  <div className="space-y-6">
                    <div className="flex items-center gap-4">
                      <Button 
                        variant="ghost" 
                        size="lg"
                        onClick={() => setShowHistoricalReports(false)}
                        className="text-lg"
                      >
                        <ChevronLeft className="mr-2 h-5 w-5" />
                        返回
                      </Button>
                      <h2 className="text-3xl font-bold tracking-tight">历史报告</h2>
                    </div>

                    {/* Historical Reports List - Long Bar Style */}
                    <div className="space-y-3">
                      {[
                        { title: '2024年10月健康月报', date: '2024-11-01', summary: '本月健康状况总体良好。平均心率保稳定，睡眠质量较上月提升15%。建议继续保持当前的运动频率。' },
                        { title: '2024年9月健康月报', date: '2024-10-01', summary: '睡眠质量有所下降，建议调整作息时间。血压指标正常，继续保持良好的饮食习惯。' },
                        { title: '2024年8月康月报', date: '2024-09-01', summary: '整体健康状况优秀。运动量较上月增加20%，各项生理指标均在正常范围内。' },
                        { title: '2024年7月健康月报', date: '2024-08-01', summary: '心率略有上升，建议减少咖啡因摄入。睡眠时长充足，质量良好。' },
                        { title: '2024年6月健康月报', date: '2024-07-01', summary: '整体健康状况良好。建议增加户外活动时间，补充维生素D。' },
                      ].map((report, i) => (
                        <Card key={i} className="hover:shadow-lg transition-all cursor-pointer border-l-4 border-l-green-500">
                          <CardContent className="py-6">
                            <div className="flex items-center justify-between gap-6">
                              <div className="flex items-center gap-6 flex-1">
                                <div className="p-3 bg-green-50 text-green-600 rounded-lg shrink-0">
                                  <FileText className="h-7 w-7" />
                                </div>
                                <div className="flex-1 space-y-2">
                                  <div className="flex items-baseline gap-4">
                                    <h3 className="text-2xl font-semibold">{report.title}</h3>
                                    <span className="text-lg text-muted-foreground">生成于 {report.date}</span>
                                  </div>
                                  <p className="text-lg text-muted-foreground leading-relaxed">
                                    {report.summary}
                                  </p>
                                </div>
                              </div>
                              <Button variant="ghost" size="lg" className="text-xl px-8 py-6 shrink-0">
                                预览
                              </Button>
                            </div>
                          </CardContent>
                        </Card>
                      ))}
                    </div>
                  </div>
                )}
              </>
            )}

            {/* --- View: Psychology --- */}
            {activeTab === 'psychology' && (
              <PsychologyPage initialMood={initialMood} />
            )}

            {/* --- View: My Info --- */}
            {activeTab === 'myinfo' && (
              <MyInfo />
            )}

          </div>
        </main>
      </div>
      
      {/* 悬浮AI助手 - 所有页面显示 */}
      <FloatingAIAssistant ref={aiAssistantRef} />
    </div>
    </VoiceProvider>
  );
}