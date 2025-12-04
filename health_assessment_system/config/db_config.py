"""
数据库配置文件
Database Configuration

MySQL 连接配置
"""

import os

# 数据库配置
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 3306)),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', '123456'),
    'database': os.getenv('DB_NAME', 'health_assessment_db'),
    'charset': 'utf8mb4',
    'use_pure': True,
    'autocommit': True,
}

# 连接池配置
POOL_CONFIG = {
    'pool_name': 'health_pool',
    'pool_size': 5,
}
