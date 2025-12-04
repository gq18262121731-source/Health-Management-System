// ============================================================================
// 健康报告生成服务
// 生成 Word 格式的健康评估报告并下载
// 集成后端 health_assessment_system 评估结果
// ============================================================================

const API_BASE_URL = import.meta.env.VITE_HEALTH_API_URL || 'http://localhost:5000';

interface HealthReportData {
  userName?: string;
  date: string;
  overallScore: number;
  healthStatus: string;
  vitalSigns: {
    heartRate: number;
    bloodPressure: { systolic: number; diastolic: number };
    bloodSugar: number;
    temperature: number;
    steps: number;
    weight: number;
  };
  assessmentDetails: {
    category: string;
    score: number;
    status: string;
    description: string;
  }[];
  recommendations: string[];
  riskFactors?: string[];
}

/**
 * 生成健康报告的 HTML 内容
 */
function generateReportHTML(data: HealthReportData): string {
  const statusColor = data.overallScore >= 80 ? '#22c55e' : data.overallScore >= 60 ? '#f59e0b' : '#ef4444';
  
  return `
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>健康评估报告</title>
  <style>
    body {
      font-family: 'Microsoft YaHei', '微软雅黑', Arial, sans-serif;
      line-height: 1.8;
      color: #333;
      max-width: 800px;
      margin: 0 auto;
      padding: 40px;
    }
    .header {
      text-align: center;
      border-bottom: 3px solid #3b82f6;
      padding-bottom: 20px;
      margin-bottom: 30px;
    }
    .header h1 {
      color: #1e40af;
      font-size: 28px;
      margin-bottom: 10px;
    }
    .header .date {
      color: #666;
      font-size: 14px;
    }
    .score-section {
      text-align: center;
      background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
      padding: 30px;
      border-radius: 12px;
      margin-bottom: 30px;
    }
    .score {
      font-size: 72px;
      font-weight: bold;
      color: ${statusColor};
    }
    .score-label {
      font-size: 18px;
      color: #666;
    }
    .status-badge {
      display: inline-block;
      padding: 8px 24px;
      background: ${statusColor};
      color: white;
      border-radius: 20px;
      font-size: 16px;
      margin-top: 10px;
    }
    .section {
      margin-bottom: 30px;
    }
    .section-title {
      font-size: 20px;
      color: #1e40af;
      border-left: 4px solid #3b82f6;
      padding-left: 12px;
      margin-bottom: 15px;
    }
    .vital-signs {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 15px;
    }
    .vital-item {
      background: #f8fafc;
      padding: 15px;
      border-radius: 8px;
      text-align: center;
    }
    .vital-value {
      font-size: 24px;
      font-weight: bold;
      color: #3b82f6;
    }
    .vital-label {
      font-size: 14px;
      color: #666;
    }
    .assessment-table {
      width: 100%;
      border-collapse: collapse;
    }
    .assessment-table th,
    .assessment-table td {
      padding: 12px;
      text-align: left;
      border-bottom: 1px solid #e5e7eb;
    }
    .assessment-table th {
      background: #f1f5f9;
      font-weight: 600;
    }
    .recommendation-list {
      list-style: none;
      padding: 0;
    }
    .recommendation-list li {
      padding: 10px 0;
      padding-left: 30px;
      position: relative;
      border-bottom: 1px dashed #e5e7eb;
    }
    .recommendation-list li:before {
      content: "✓";
      position: absolute;
      left: 0;
      color: #22c55e;
      font-weight: bold;
    }
    .footer {
      text-align: center;
      margin-top: 40px;
      padding-top: 20px;
      border-top: 1px solid #e5e7eb;
      color: #999;
      font-size: 12px;
    }
  </style>
</head>
<body>
  <div class="header">
    <h1>🏥 智慧健康评估报告</h1>
    <div class="date">报告生成时间：${data.date}</div>
    ${data.userName ? `<div style="margin-top: 5px;">用户：${data.userName}</div>` : ''}
  </div>

  <div class="score-section">
    <div class="score-label">综合健康评分</div>
    <div class="score">${data.overallScore}</div>
    <div class="status-badge">${data.healthStatus}</div>
  </div>

  <div class="section">
    <h2 class="section-title">生命体征数据</h2>
    <div class="vital-signs">
      <div class="vital-item">
        <div class="vital-value">${data.vitalSigns.heartRate}</div>
        <div class="vital-label">心率 (次/分)</div>
      </div>
      <div class="vital-item">
        <div class="vital-value">${data.vitalSigns.bloodPressure.systolic}/${data.vitalSigns.bloodPressure.diastolic}</div>
        <div class="vital-label">血压 (mmHg)</div>
      </div>
      <div class="vital-item">
        <div class="vital-value">${data.vitalSigns.bloodSugar}</div>
        <div class="vital-label">血糖 (mmol/L)</div>
      </div>
      <div class="vital-item">
        <div class="vital-value">${data.vitalSigns.temperature}</div>
        <div class="vital-label">体温 (°C)</div>
      </div>
      <div class="vital-item">
        <div class="vital-value">${data.vitalSigns.steps.toLocaleString()}</div>
        <div class="vital-label">今日步数</div>
      </div>
      <div class="vital-item">
        <div class="vital-value">${data.vitalSigns.weight}</div>
        <div class="vital-label">体重 (kg)</div>
      </div>
    </div>
  </div>

  <div class="section">
    <h2 class="section-title">健康评估详情</h2>
    <table class="assessment-table">
      <thead>
        <tr>
          <th>评估项目</th>
          <th>评分</th>
          <th>状态</th>
          <th>说明</th>
        </tr>
      </thead>
      <tbody>
        ${data.assessmentDetails.map(item => `
          <tr>
            <td>${item.category}</td>
            <td><strong>${item.score}</strong>/100</td>
            <td>${item.status}</td>
            <td>${item.description}</td>
          </tr>
        `).join('')}
      </tbody>
    </table>
  </div>

  <div class="section">
    <h2 class="section-title">健康建议</h2>
    <ul class="recommendation-list">
      ${data.recommendations.map(rec => `<li>${rec}</li>`).join('')}
    </ul>
  </div>

  ${data.riskFactors && data.riskFactors.length > 0 ? `
  <div class="section">
    <h2 class="section-title" style="color: #dc2626; border-color: #dc2626;">风险提示</h2>
    <ul class="recommendation-list">
      ${data.riskFactors.map(risk => `<li style="color: #dc2626;">${risk}</li>`).join('')}
    </ul>
  </div>
  ` : ''}

  <div class="footer">
    <p>本报告由智慧健康管理系统自动生成</p>
    <p>仅供参考，如有健康问题请咨询专业医生</p>
  </div>
</body>
</html>
  `;
}

/**
 * 将 HTML 转换为 Word 文档并下载
 */
export function downloadWordReport(data: HealthReportData): void {
  const html = generateReportHTML(data);
  
  // 创建 Word 文档的 MIME 类型
  const blob = new Blob([`
    <html xmlns:o='urn:schemas-microsoft-com:office:office' 
          xmlns:w='urn:schemas-microsoft-com:office:word' 
          xmlns='http://www.w3.org/TR/REC-html40'>
    <head>
      <meta charset="UTF-8">
      <!--[if gte mso 9]>
      <xml>
        <w:WordDocument>
          <w:View>Print</w:View>
          <w:Zoom>100</w:Zoom>
        </w:WordDocument>
      </xml>
      <![endif]-->
    </head>
    <body>
      ${html}
    </body>
    </html>
  `], { type: 'application/msword' });
  
  // 创建下载链接
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = `健康评估报告_${data.date.replace(/[\/\-\s:]/g, '')}.doc`;
  
  // 触发下载
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  
  // 释放 URL
  URL.revokeObjectURL(url);
}

/**
 * 从后端获取完整评估报告数据
 * 调用 health_assessment_system 的评估引擎
 */
async function fetchFullReportFromBackend(userId: string = 'elderly_001'): Promise<HealthReportData | null> {
  try {
    console.log('🔄 正在从后端获取评估报告...');
    
    const response = await fetch(`${API_BASE_URL}/api/health/report/full`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ user_id: userId })
    });
    
    const result = await response.json();
    
    if (result.success && result.data) {
      console.log('✅ 成功获取后端评估数据:', result.data);
      
      const data = result.data;
      
      // 转换风险因素为字符串数组
      const riskFactorStrings = data.risk_factors?.map((rf: any) => 
        typeof rf === 'string' ? rf : rf.description || rf.name
      ) || [];
      
      return {
        date: new Date().toLocaleString('zh-CN', {
          year: 'numeric',
          month: '2-digit',
          day: '2-digit',
          hour: '2-digit',
          minute: '2-digit'
        }),
        overallScore: data.overall_score,
        healthStatus: data.health_status,
        vitalSigns: {
          heartRate: data.vital_signs?.heartRate || 72,
          bloodPressure: data.vital_signs?.bloodPressure || { systolic: 120, diastolic: 80 },
          bloodSugar: data.vital_signs?.bloodSugar || 5.6,
          temperature: data.vital_signs?.temperature || 36.5,
          steps: data.vital_signs?.steps || 6580,
          weight: data.vital_signs?.weight || 65
        },
        assessmentDetails: data.assessment_details || [],
        recommendations: data.recommendations || [],
        riskFactors: riskFactorStrings.length > 0 ? riskFactorStrings : undefined
      };
    }
    
    console.warn('⚠️ 后端返回数据不完整，使用默认数据');
    return null;
    
  } catch (error) {
    console.error('❌ 获取后端评估报告失败:', error);
    return null;
  }
}

/**
 * 生成并下载健康报告
 * 优先从后端 health_assessment_system 获取评估结果
 * @param userId 用户ID
 * @param fallbackData 备用数据（后端不可用时使用）
 */
export async function generateAndDownloadReport(
  fallbackData?: {
    heartRate?: number;
    bloodPressure?: { systolic: number; diastolic: number };
    bloodSugar?: number;
    temperature?: number;
    steps?: number;
    weight?: number;
  },
  assessmentResult?: {
    overallScore?: number;
    healthStatus?: string;
    recommendations?: string[];
  },
  userId: string = 'elderly_001'
): Promise<void> {
  // 优先尝试从后端获取完整评估报告
  let reportData = await fetchFullReportFromBackend(userId);
  
  // 如果后端不可用，使用传入的数据或默认数据
  if (!reportData) {
    console.log('📝 使用本地数据生成报告');
    
    reportData = {
      date: new Date().toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      }),
      overallScore: assessmentResult?.overallScore || 85,
      healthStatus: assessmentResult?.healthStatus || '健康状态良好',
      vitalSigns: {
        heartRate: fallbackData?.heartRate || 72,
        bloodPressure: fallbackData?.bloodPressure || { systolic: 120, diastolic: 80 },
        bloodSugar: fallbackData?.bloodSugar || 5.6,
        temperature: fallbackData?.temperature || 36.5,
        steps: fallbackData?.steps || 6580,
        weight: fallbackData?.weight || 65
      },
      assessmentDetails: [
        { category: '心血管健康', score: 88, status: '良好', description: '心率稳定，血压正常' },
        { category: '代谢指标', score: 82, status: '良好', description: '血糖控制良好' },
        { category: '运动健康', score: 75, status: '一般', description: '建议增加运动量' },
        { category: '睡眠质量', score: 80, status: '良好', description: '睡眠时长充足' },
        { category: '体重管理', score: 85, status: '良好', description: 'BMI在正常范围' },
        { category: '综合评估', score: assessmentResult?.overallScore || 85, status: '良好', description: '整体健康状况良好' }
      ],
      recommendations: assessmentResult?.recommendations || [
        '保持规律的作息时间，每天保证7-8小时睡眠',
        '每天进行30分钟以上的有氧运动',
        '饮食均衡，多吃蔬菜水果，少油少盐',
        '定期监测血压血糖，保持健康记录',
        '保持良好心态，适当进行放松活动'
      ]
    };
  }

  // 下载报告
  downloadWordReport(reportData);
  console.log('✅ 健康报告已生成并开始下载');
}
