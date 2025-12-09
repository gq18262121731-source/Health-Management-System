"""
物联网设备数据接收路由
======================

接收来自 STM32 + MAX30102 等物联网传感器的健康数据。

技术链路：
  STM32 (I²C) → MAX30102 → ESP8266/WiFi → HTTP POST → FastAPI → 数据库

支持设备：
  - MAX30102: 心率、血氧
  - 血压计模块
  - 体温传感器
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/iot", tags=["IoT设备"])


# ============== 数据模型 ==============

class VitalSign(BaseModel):
    """生命体征数据（来自 STM32 + MAX30102）"""
    heart_rate: int = Field(..., ge=30, le=220, description="心率 (BPM)")
    spo2: Optional[float] = Field(None, ge=70, le=100, description="血氧饱和度 (%)")
    device_id: str = Field(..., description="传感器设备ID，如 STM32_Sensor_001")
    timestamp: Optional[int] = Field(None, description="数据采集时间戳（Unix秒）")
    user_id: Optional[str] = Field(None, description="关联的用户ID")

    class Config:
        json_schema_extra = {
            "example": {
                "heart_rate": 75,
                "spo2": 98.5,
                "device_id": "STM32_MAX30102_001",
                "timestamp": 1733731200,
                "user_id": "elderly_001"
            }
        }


class BloodPressureData(BaseModel):
    """血压数据"""
    systolic: int = Field(..., ge=60, le=250, description="收缩压 (mmHg)")
    diastolic: int = Field(..., ge=40, le=150, description="舒张压 (mmHg)")
    pulse: Optional[int] = Field(None, ge=30, le=220, description="脉搏")
    device_id: str = Field(..., description="设备ID")
    timestamp: Optional[int] = Field(None, description="采集时间戳")
    user_id: Optional[str] = Field(None, description="用户ID")


class TemperatureData(BaseModel):
    """体温数据"""
    temperature: float = Field(..., ge=34.0, le=42.0, description="体温 (℃)")
    device_id: str = Field(..., description="设备ID")
    timestamp: Optional[int] = Field(None, description="采集时间戳")
    user_id: Optional[str] = Field(None, description="用户ID")


class BatchVitalSigns(BaseModel):
    """批量生命体征数据（支持 STM32 缓存后批量上传）"""
    device_id: str
    user_id: Optional[str] = None
    records: List[VitalSign]


# ============== 数据清洗流水线集成 ==============

# 导入数据采集器（延迟导入避免循环依赖）
_data_collector = None

def get_data_collector():
    """获取数据采集器实例（延迟初始化）"""
    global _data_collector
    if _data_collector is None:
        try:
            import sys
            sys.path.insert(0, 'frontend/health_assessment_system')
            from core.data_pipeline import DataCollector, DataSource
            _data_collector = DataCollector()
            logger.info("✅ IoT 数据已接入数据清洗流水线")
        except ImportError as e:
            logger.warning(f"数据清洗流水线未加载: {e}，使用内存缓存")
            _data_collector = None
    return _data_collector


# 内存缓存（用于快速查询，同时作为流水线的备份）
_vital_signs_cache: List[dict] = []
_blood_pressure_cache: List[dict] = []
_temperature_cache: List[dict] = []

MAX_CACHE_SIZE = 1000  # 最大缓存条数

# 设备绑定表（device_id -> user_id）
_device_user_mapping: dict = {
    # 示例：STM32_MAX30102_001 绑定到 elderly_001
    # 实际应从数据库加载
}


def bind_device(device_id: str, user_id: str):
    """绑定设备到用户"""
    _device_user_mapping[device_id] = user_id
    logger.info(f"🔗 设备 {device_id} 已绑定到用户 {user_id}")


def get_user_by_device(device_id: str) -> Optional[str]:
    """根据设备ID获取用户ID"""
    return _device_user_mapping.get(device_id)


def store_vital_sign(data: dict):
    """
    存储生命体征数据
    
    数据流：IoT设备 → 内存缓存 + 数据清洗流水线
    """
    global _vital_signs_cache
    
    # 1. 存入内存缓存（快速查询）
    _vital_signs_cache.append(data)
    if len(_vital_signs_cache) > MAX_CACHE_SIZE:
        _vital_signs_cache = _vital_signs_cache[-MAX_CACHE_SIZE:]
    
    # 2. 接入数据清洗流水线
    collector = get_data_collector()
    if collector:
        try:
            # 尝试根据设备ID查找用户
            user_id = data.get('user_id') or get_user_by_device(data.get('device_id', ''))
            if not user_id:
                user_id = 'unknown_user'  # 未绑定设备暂存
            
            # 心率数据
            if data.get('heart_rate'):
                from core.data_pipeline import DataSource
                success, record, error = collector.collect_single(
                    user_id=user_id,
                    data_type='heart_rate',
                    values={'value': data['heart_rate']},
                    source=DataSource.SENSOR,
                    timestamp=datetime.fromtimestamp(data.get('timestamp', datetime.now().timestamp())),
                    device_id=data.get('device_id')
                )
                if success:
                    logger.debug(f"✅ 心率数据已进入清洗流水线: {record.record_id}")
                else:
                    logger.warning(f"⚠️ 心率数据校验失败: {error}")
            
            # 血氧数据
            if data.get('spo2'):
                from core.data_pipeline import DataSource
                success, record, error = collector.collect_single(
                    user_id=user_id,
                    data_type='spo2',
                    values={'value': data['spo2']},
                    source=DataSource.SENSOR,
                    timestamp=datetime.fromtimestamp(data.get('timestamp', datetime.now().timestamp())),
                    device_id=data.get('device_id')
                )
                if success:
                    logger.debug(f"✅ 血氧数据已进入清洗流水线: {record.record_id}")
                    
        except Exception as e:
            logger.error(f"数据清洗流水线处理失败: {e}")
    
    logger.info(f"💓 收到心率数据: HR={data.get('heart_rate')} SpO2={data.get('spo2')} from {data.get('device_id')}")


def store_blood_pressure(data: dict):
    """
    存储血压数据
    
    数据流：IoT设备 → 内存缓存 + 数据清洗流水线
    """
    global _blood_pressure_cache
    
    # 1. 存入内存缓存
    _blood_pressure_cache.append(data)
    if len(_blood_pressure_cache) > MAX_CACHE_SIZE:
        _blood_pressure_cache = _blood_pressure_cache[-MAX_CACHE_SIZE:]
    
    # 2. 接入数据清洗流水线
    collector = get_data_collector()
    if collector:
        try:
            user_id = data.get('user_id') or get_user_by_device(data.get('device_id', '')) or 'unknown_user'
            
            from core.data_pipeline import DataSource
            success, record, error = collector.collect_single(
                user_id=user_id,
                data_type='blood_pressure',
                values={
                    'systolic': data['systolic'],
                    'diastolic': data['diastolic'],
                    'pulse': data.get('pulse')
                },
                source=DataSource.SENSOR,
                timestamp=datetime.fromtimestamp(data.get('timestamp', datetime.now().timestamp())),
                device_id=data.get('device_id')
            )
            if success:
                logger.debug(f"✅ 血压数据已进入清洗流水线: {record.record_id}")
            else:
                logger.warning(f"⚠️ 血压数据校验失败: {error}")
                
        except Exception as e:
            logger.error(f"数据清洗流水线处理失败: {e}")
    
    logger.info(f"🩸 收到血压数据: {data.get('systolic')}/{data.get('diastolic')} from {data.get('device_id')}")


# ============== API 路由 ==============

@router.post("/vitals/upload", summary="上传生命体征数据")
async def upload_vitals(data: VitalSign, background_tasks: BackgroundTasks):
    """
    接收 STM32 + MAX30102 上传的心率/血氧数据
    
    **STM32 固件示例请求：**
    ```
    POST /api/iot/vitals/upload HTTP/1.1
    Host: 192.168.1.100:8000
    Content-Type: application/json
    
    {"heart_rate": 75, "spo2": 98, "device_id": "STM32_001"}
    ```
    """
    try:
        # 补充时间戳
        record = data.model_dump()
        if not record.get("timestamp"):
            record["timestamp"] = int(datetime.now().timestamp())
        record["received_at"] = datetime.now().isoformat()
        
        # 异步存储（不阻塞响应）
        background_tasks.add_task(store_vital_sign, record)
        
        # 心率异常检测
        alert = None
        if data.heart_rate < 50:
            alert = "⚠️ 心率过缓"
        elif data.heart_rate > 100:
            alert = "⚠️ 心率过速"
        if data.spo2 and data.spo2 < 94:
            alert = "🚨 血氧偏低，请注意！"
        
        return {
            "status": "success",
            "message": "数据接收成功",
            "device_id": data.device_id,
            "alert": alert
        }
        
    except Exception as e:
        logger.error(f"数据存储失败: {e}")
        raise HTTPException(status_code=500, detail=f"存储失败: {str(e)}")


@router.post("/vitals/batch", summary="批量上传生命体征数据")
async def upload_vitals_batch(data: BatchVitalSigns, background_tasks: BackgroundTasks):
    """
    批量上传数据（适用于 STM32 网络不稳定时缓存后批量发送）
    """
    count = 0
    for record in data.records:
        record_dict = record.model_dump()
        record_dict["device_id"] = data.device_id
        record_dict["user_id"] = data.user_id
        record_dict["received_at"] = datetime.now().isoformat()
        background_tasks.add_task(store_vital_sign, record_dict)
        count += 1
    
    return {
        "status": "success",
        "message": f"批量接收 {count} 条数据",
        "device_id": data.device_id
    }


@router.post("/blood-pressure/upload", summary="上传血压数据")
async def upload_blood_pressure(data: BloodPressureData, background_tasks: BackgroundTasks):
    """接收血压计模块上传的血压数据"""
    record = data.model_dump()
    if not record.get("timestamp"):
        record["timestamp"] = int(datetime.now().timestamp())
    record["received_at"] = datetime.now().isoformat()
    
    background_tasks.add_task(store_blood_pressure, record)
    
    # 血压异常检测
    alert = None
    if data.systolic >= 140 or data.diastolic >= 90:
        alert = "⚠️ 血压偏高"
    elif data.systolic < 90 or data.diastolic < 60:
        alert = "⚠️ 血压偏低"
    
    return {
        "status": "success",
        "message": "血压数据接收成功",
        "alert": alert
    }


@router.get("/vitals/latest", summary="获取最新生命体征")
async def get_latest_vitals(device_id: Optional[str] = None, limit: int = 10):
    """获取最新的生命体征数据"""
    records = _vital_signs_cache
    if device_id:
        records = [r for r in records if r.get("device_id") == device_id]
    return {
        "count": len(records[-limit:]),
        "records": records[-limit:]
    }


@router.get("/devices/status", summary="获取设备状态")
async def get_device_status():
    """获取所有已连接设备的状态"""
    # 统计各设备最后一次上传时间
    devices = {}
    for record in _vital_signs_cache:
        device_id = record.get("device_id")
        if device_id:
            devices[device_id] = {
                "last_seen": record.get("received_at"),
                "last_hr": record.get("heart_rate"),
                "last_spo2": record.get("spo2")
            }
    
    return {
        "device_count": len(devices),
        "devices": devices
    }


# ============== 设备绑定管理 ==============

class DeviceBindRequest(BaseModel):
    """设备绑定请求"""
    device_id: str = Field(..., description="设备ID")
    user_id: str = Field(..., description="用户ID")


@router.post("/devices/bind", summary="绑定设备到用户")
async def bind_device_to_user(data: DeviceBindRequest):
    """
    将 IoT 设备绑定到指定用户
    
    绑定后，该设备上传的数据会自动关联到用户，进入数据清洗流水线
    """
    bind_device(data.device_id, data.user_id)
    return {
        "status": "success",
        "message": f"设备 {data.device_id} 已绑定到用户 {data.user_id}",
        "device_id": data.device_id,
        "user_id": data.user_id
    }


@router.get("/devices/bindings", summary="获取设备绑定列表")
async def get_device_bindings():
    """获取所有设备与用户的绑定关系"""
    return {
        "count": len(_device_user_mapping),
        "bindings": _device_user_mapping
    }


@router.get("/pipeline/status", summary="获取数据流水线状态")
async def get_pipeline_status():
    """查看数据清洗流水线的运行状态"""
    collector = get_data_collector()
    
    if collector:
        buffer_size = len(collector._buffer) if hasattr(collector, '_buffer') else 0
        return {
            "status": "connected",
            "message": "IoT 数据已接入数据清洗流水线",
            "buffer_size": buffer_size,
            "supported_types": list(collector.DATA_SCHEMAS.keys())
        }
    else:
        return {
            "status": "disconnected",
            "message": "数据清洗流水线未加载，使用内存缓存",
            "cache_sizes": {
                "vital_signs": len(_vital_signs_cache),
                "blood_pressure": len(_blood_pressure_cache),
                "temperature": len(_temperature_cache)
            }
        }


# ============== WebSocket 实时推送（可选） ==============

from fastapi import WebSocket, WebSocketDisconnect

# 活跃的 WebSocket 连接
active_connections: List[WebSocket] = []


@router.websocket("/ws/vitals")
async def websocket_vitals(websocket: WebSocket):
    """
    WebSocket 实时推送生命体征数据
    
    前端可以通过此接口实时接收 STM32 上传的数据
    """
    await websocket.accept()
    active_connections.append(websocket)
    logger.info(f"🔗 WebSocket 连接建立，当前连接数: {len(active_connections)}")
    
    try:
        while True:
            # 等待客户端消息（保持连接）
            data = await websocket.receive_text()
            # 可以处理客户端的订阅请求
            
    except WebSocketDisconnect:
        active_connections.remove(websocket)
        logger.info(f"🔌 WebSocket 断开，当前连接数: {len(active_connections)}")


async def broadcast_vital_sign(data: dict):
    """向所有 WebSocket 客户端广播新数据"""
    for connection in active_connections:
        try:
            await connection.send_json(data)
        except Exception:
            pass
