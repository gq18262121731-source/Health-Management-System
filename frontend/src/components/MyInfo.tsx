import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { User, Phone, MapPin, Calendar, Heart, Edit2, Save, X } from 'lucide-react';
import { Avatar, AvatarFallback, AvatarImage } from './ui/avatar';
import { VoiceInputButton } from './ui/VoiceInputButton';

export function MyInfo() {
  const [isEditing, setIsEditing] = useState(false);
  const [userInfo, setUserInfo] = useState({
    name: '张三',
    age: 68,
    gender: '男',
    phone: '138****8832',
    address: '北京市朝阳区健康社区5号楼301',
    emergencyContact: '李四',
    emergencyPhone: '139****6688',
    bloodType: 'A型',
    chronicDiseases: ['高血压', '糖尿病'],
    allergies: '青霉素',
    idNumber: '110101******1234',
    registrationDate: '2023年3月15日',
  });

  const handleSave = () => {
    setIsEditing(false);
    // 这里可以添加保存逻辑
  };

  return (
    <div className="space-y-6 p-6">
      {/* 顶部个人卡片 */}
      <Card className="border-2 shadow-lg">
        <CardHeader className="bg-gradient-to-r from-green-50 to-blue-50">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-6">
              <Avatar className="h-32 w-32 border-4 border-white shadow-md">
                <AvatarImage src="https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=400&h=400&fit=crop" alt="用户头像" />
                <AvatarFallback className="text-[40px]">{userInfo.name[0]}</AvatarFallback>
              </Avatar>
              <div className="space-y-2">
                <h1 className="text-[48px] font-bold text-slate-900">{userInfo.name}</h1>
                <div className="flex gap-6 text-[24px] text-slate-600">
                  <span>{userInfo.age}岁</span>
                  <span>|</span>
                  <span>{userInfo.gender}</span>
                  <span>|</span>
                  <span>{userInfo.bloodType}</span>
                </div>
                <p className="text-[20px] text-slate-500">注册日期: {userInfo.registrationDate}</p>
              </div>
            </div>
            <Button
              size="lg"
              variant={isEditing ? "outline" : "default"}
              onClick={() => setIsEditing(!isEditing)}
              className="text-[22px] px-8 h-14"
            >
              {isEditing ? (
                <>
                  <X className="mr-2 h-6 w-6" />
                  取消编辑
                </>
              ) : (
                <>
                  <Edit2 className="mr-2 h-6 w-6" />
                  编辑信息
                </>
              )}
            </Button>
          </div>
        </CardHeader>
      </Card>

      {/* 详细信息网格 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* 基本信息 */}
        <Card className="border-2">
          <CardHeader className="bg-slate-50">
            <CardTitle className="text-[32px] flex items-center gap-3">
              <User className="h-8 w-8 text-green-600" />
              基本信息
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-6 pt-6">
            <InfoRow label="姓名" value={userInfo.name} isEditing={isEditing} />
            <InfoRow label="年龄" value={`${userInfo.age}岁`} isEditing={isEditing} />
            <InfoRow label="性别" value={userInfo.gender} isEditing={isEditing} />
            <InfoRow label="身份证号" value={userInfo.idNumber} isEditing={isEditing} />
            <InfoRow label="血型" value={userInfo.bloodType} isEditing={isEditing} />
          </CardContent>
        </Card>

        {/* 联系信息 */}
        <Card className="border-2">
          <CardHeader className="bg-slate-50">
            <CardTitle className="text-[32px] flex items-center gap-3">
              <Phone className="h-8 w-8 text-blue-600" />
              联系信息
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-6 pt-6">
            <InfoRow label="手机号码" value={userInfo.phone} isEditing={isEditing} />
            <InfoRow label="居住地址" value={userInfo.address} isEditing={isEditing} multiline />
            <InfoRow label="紧急联系人" value={userInfo.emergencyContact} isEditing={isEditing} />
            <InfoRow label="紧急联系电话" value={userInfo.emergencyPhone} isEditing={isEditing} />
          </CardContent>
        </Card>

        {/* 健康档案 */}
        <Card className="border-2 lg:col-span-2">
          <CardHeader className="bg-slate-50">
            <CardTitle className="text-[32px] flex items-center gap-3">
              <Heart className="h-8 w-8 text-red-600" />
              健康档案
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-6 pt-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="space-y-3">
                <label className="text-[24px] font-medium text-slate-700">慢性疾病</label>
                <div className="flex flex-wrap gap-3">
                  {userInfo.chronicDiseases.map((disease, index) => (
                    <span
                      key={index}
                      className="px-6 py-3 bg-orange-100 text-orange-700 rounded-full text-[20px] font-medium"
                    >
                      {disease}
                    </span>
                  ))}
                </div>
              </div>
              <div className="space-y-3">
                <label className="text-[24px] font-medium text-slate-700">药物过敏</label>
                <div className="flex flex-wrap gap-3">
                  <span className="px-6 py-3 bg-red-100 text-red-700 rounded-full text-[20px] font-medium">
                    {userInfo.allergies}
                  </span>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* 保存按钮 */}
      {isEditing && (
        <div className="flex justify-center pt-4">
          <Button
            size="lg"
            onClick={handleSave}
            className="text-[28px] px-16 h-16 bg-green-600 hover:bg-green-700"
          >
            <Save className="mr-3 h-7 w-7" />
            保存修改
          </Button>
        </div>
      )}
    </div>
  );
}

// 信息行组件
interface InfoRowProps {
  label: string;
  value: string;
  isEditing: boolean;
  multiline?: boolean;
}

function InfoRow({ label, value, isEditing, multiline = false }: InfoRowProps) {
  const [inputValue, setInputValue] = useState(value);

  return (
    <div className="flex flex-col gap-2">
      <label className="text-[24px] font-medium text-slate-700">{label}</label>
      {isEditing ? (
        <div className="relative flex gap-2">
          {multiline ? (
            <textarea
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              className="flex-1 px-4 py-3 text-[22px] border-2 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500"
              rows={2}
            />
          ) : (
            <input
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              className="flex-1 px-4 py-3 text-[22px] border-2 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500"
            />
          )}
          
          {/* 语音输入按钮 */}
          <VoiceInputButton
            onVoiceResult={(text) => setInputValue(text)}
            size="md"
          />
        </div>
      ) : (
        <p className="text-[24px] text-slate-900 px-4 py-3 bg-slate-50 rounded-lg">{value}</p>
      )}
    </div>
  );
}