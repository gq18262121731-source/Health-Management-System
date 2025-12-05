"""日志配置"""
import os
from typing import Dict, Any

# 日志目录
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
os.makedirs(LOG_DIR, exist_ok=True)

# 日志配置
def get_logging_config(app_env: str = "development") -> Dict[str, Any]:
    """根据环境获取日志配置"""
    is_dev = app_env == "development"
    
    # 基础格式化器配置
    formatters = {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        },
        "detailed": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s",
        }
    }
    
    # 非开发环境才添加json格式化器
    if not is_dev:
        formatters["json"] = {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "class": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "datefmt": "%Y-%m-%d %H:%M:%S"
        }
    
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": formatters,
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": "DEBUG" if is_dev else "INFO",
                "formatter": "detailed" if is_dev else "default",
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "INFO",
                "formatter": "detailed",
                "filename": os.path.join(LOG_DIR, "app.log"),
                "maxBytes": 10 * 1024 * 1024,  # 10MB
                "backupCount": 5,
                "encoding": "utf-8",
            },
            "error_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "ERROR",
                "formatter": "detailed",
                "filename": os.path.join(LOG_DIR, "error.log"),
                "maxBytes": 10 * 1024 * 1024,  # 10MB
                "backupCount": 5,
                "encoding": "utf-8",
            },
            "access_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "INFO",
                "formatter": "detailed",
                "filename": os.path.join(LOG_DIR, "access.log"),
                "maxBytes": 10 * 1024 * 1024,  # 10MB
                "backupCount": 5,
                "encoding": "utf-8",
            }
        },
        "loggers": {
            "": {
                "handlers": ["console", "file", "error_file"],
                "level": "DEBUG" if is_dev else "INFO",
                "propagate": False,
            },
            "fastapi": {
                "handlers": ["console", "access_file"],
                "level": "DEBUG" if is_dev else "INFO",
                "propagate": False,
            },
            "uvicorn": {
                "handlers": ["console"],
                "level": "INFO",
                "propagate": False,
            },
            "sqlalchemy.engine": {
                "handlers": ["console"] if is_dev else [],
                "level": "INFO",
                "propagate": False,
            },
        },
    }


# 默认日志配置
LOGGING_CONFIG = get_logging_config()

# 获取日志记录器函数
def get_logger(name: str):
    """获取指定名称的日志记录器
    
    Args:
        name: 日志记录器名称
        
    Returns:
        logging.Logger: 日志记录器实例
    """
    import logging
    return logging.getLogger(name)