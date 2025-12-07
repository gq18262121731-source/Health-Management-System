"""
数据库连接与操作管理器
Database Manager

负责管理MySQL数据库连接、执行查询和事务处理
"""

import mysql.connector
from mysql.connector import pooling
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import json
import os

class DatabaseManager:
    """
    数据库管理器
    
    使用连接池管理MySQL连接
    """
    
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self, config: Dict = None):
        """
        初始化数据库连接池
        
        Args:
            config: 数据库配置字典
        """
        if hasattr(self, 'pool'):
            return
            
        # 从配置文件加载
        try:
            import sys
            from pathlib import Path
            sys.path.insert(0, str(Path(__file__).parent.parent / 'config'))
            from db_config import DB_CONFIG
            self.db_config = DB_CONFIG.copy()
        except ImportError:
            # 默认配置
            self.db_config = {
                'host': 'localhost',
                'port': 3306,
                'user': 'root',
                'password': '123456',
                'database': 'health_assessment_db',
                'charset': 'utf8mb4',
                'use_pure': True
            }
        
        if config:
            self.db_config.update(config)
        
        try:
            self.pool = mysql.connector.pooling.MySQLConnectionPool(
                pool_name="health_pool",
                pool_size=5,
                **self.db_config
            )
            print("✓ 数据库连接池初始化成功")
        except Exception as e:
            print(f"⚠️ 数据库连接初始化失败: {e}")
            self.pool = None

    def get_connection(self):
        """获取数据库连接"""
        if not self.pool:
            raise Exception("数据库连接池未初始化")
        return self.pool.get_connection()

    def execute_query(self, query: str, params: tuple = None) -> List[Dict]:
        """
        执行查询语句
        
        Args:
            query: SQL查询语句
            params: 参数元组
            
        Returns:
            结果字典列表
        """
        conn = None
        cursor = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(query, params)
            result = cursor.fetchall()
            return result
        except Exception as e:
            print(f"查询执行失败: {e}")
            return []
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    def execute_update(self, query: str, params: tuple = None) -> int:
        """
        执行更新/插入/删除语句
        
        Args:
            query: SQL语句
            params: 参数元组
            
        Returns:
            影响行数或最后插入ID
        """
        conn = None
        cursor = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            
            if query.strip().upper().startswith("INSERT"):
                return cursor.lastrowid
            return cursor.rowcount
        except Exception as e:
            print(f"更新执行失败: {e}")
            if conn: conn.rollback()
            return -1
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    # ---------------------------------------------------------
    # 具体的业务数据操作方法
    # ---------------------------------------------------------

    def get_elder_info(self, elder_id: int) -> Optional[Dict]:
        """获取老人信息"""
        sql = "SELECT * FROM elder_info WHERE id = %s"
        result = self.execute_query(sql, (elder_id,))
        return result[0] if result else None

    def save_health_record(self, record_data: Dict) -> int:
        """保存健康检测记录"""
        # 动态构建插入语句
        fields = []
        values = []
        placeholders = []
        
        for key, value in record_data.items():
            if value is not None:
                fields.append(key)
                values.append(value)
                placeholders.append("%s")
        
        sql = f"INSERT INTO health_record ({', '.join(fields)}) VALUES ({', '.join(placeholders)})"
        return self.execute_update(sql, tuple(values))

    def save_assessment_result(self, result_data: Dict) -> int:
        """保存评估结果"""
        fields = []
        values = []
        placeholders = []
        
        # 处理JSON字段
        json_fields = ['disease_summary_json', 'reason_struct_json', 'extra_meta_json']
        
        for key, value in result_data.items():
            if value is not None:
                fields.append(key)
                if key in json_fields and isinstance(value, (dict, list)):
                    values.append(json.dumps(value, ensure_ascii=False))
                else:
                    values.append(value)
                placeholders.append("%s")
                
        sql = f"INSERT INTO assessment_result ({', '.join(fields)}) VALUES ({', '.join(placeholders)})"
        return self.execute_update(sql, tuple(values))

    def get_latest_assessment(self, elder_id: int) -> Optional[Dict]:
        """获取最新评估结果"""
        sql = """
        SELECT * FROM assessment_result 
        WHERE elder_id = %s 
        ORDER BY assessment_time DESC 
        LIMIT 1
        """
        result = self.execute_query(sql, (elder_id,))
        if result:
            # 解析JSON字段
            row = result[0]
            json_fields = ['disease_summary_json', 'reason_struct_json', 'extra_meta_json']
            for field in json_fields:
                if row.get(field):
                    try:
                        row[field] = json.loads(row[field])
                    except:
                        pass
            return row
        return None

    def get_health_history(self, elder_id: int, days: int = 30) -> List[Dict]:
        """获取历史健康记录"""
        sql = """
        SELECT * FROM health_record 
        WHERE elder_id = %s AND check_time >= DATE_SUB(NOW(), INTERVAL %s DAY)
        ORDER BY check_time ASC
        """
        return self.execute_query(sql, (elder_id, days))
