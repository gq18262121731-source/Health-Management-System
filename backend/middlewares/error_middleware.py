"""错误处理中间件"""
from typing import Any, Callable
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError, HTTPException
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, NoResultFound
import logging

from utils.common_utils import ResponseUtils
from config.logging import get_logger

# 获取日志记录器
logger = get_logger(__name__)


class ErrorHandler:
    """错误处理器类"""
    
    @staticmethod
    def register(app: FastAPI) -> None:
        """注册所有错误处理函数
        
        Args:
            app: FastAPI应用实例
        """
        # 注册请求验证错误处理
        app.add_exception_handler(RequestValidationError, ErrorHandler.handle_request_validation_error)
        
        # 注册HTTP异常处理
        app.add_exception_handler(HTTPException, ErrorHandler.handle_http_exception)
        
        # 注册SQLAlchemy错误处理
        app.add_exception_handler(SQLAlchemyError, ErrorHandler.handle_sqlalchemy_error)
        
        # 注册通用异常处理
        app.add_exception_handler(Exception, ErrorHandler.handle_generic_exception)
    
    @staticmethod
    async def handle_request_validation_error(request: Request, exc: RequestValidationError) -> JSONResponse:
        """处理请求验证错误
        
        Args:
            request: HTTP请求
            exc: 请求验证错误异常
            
        Returns:
            JSONResponse: 错误响应
        """
        # 记录错误日志
        logger.error(f"请求验证错误: {exc.errors()}, 请求路径: {request.url.path}")
        
        # 构建详细的错误信息
        error_details = []
        for error in exc.errors():
            field = ".".join([str(loc) for loc in error.get("loc", [])])
            msg = error.get("msg", "字段验证失败")
            error_details.append(f"{field}: {msg}")
        
        # 返回格式化的错误响应
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=ResponseUtils.error_response(
                code=422,
                message="请求参数验证失败",
                error_data={"detail": error_details}
            )
        )
    
    @staticmethod
    async def handle_http_exception(request: Request, exc: HTTPException) -> JSONResponse:
        """处理HTTP异常
        
        Args:
            request: HTTP请求
            exc: HTTP异常
            
        Returns:
            JSONResponse: 错误响应
        """
        # 记录错误日志（非404和401错误）
        if exc.status_code not in [404, 401]:
            logger.error(f"HTTP错误: {exc.status_code} - {exc.detail}, 请求路径: {request.url.path}")
        
        # 返回格式化的错误响应
        return JSONResponse(
            status_code=exc.status_code,
            content=ResponseUtils.error_response(
                code=exc.status_code,
                message=exc.detail or "HTTP请求失败"
            )
        )
    
    @staticmethod
    async def handle_sqlalchemy_error(request: Request, exc: SQLAlchemyError) -> JSONResponse:
        """处理SQLAlchemy错误
        
        Args:
            request: HTTP请求
            exc: SQLAlchemy错误
            
        Returns:
            JSONResponse: 错误响应
        """
        # 记录详细的数据库错误
        logger.error(f"数据库错误: {str(exc)}, 请求路径: {request.url.path}", exc_info=True)
        
        # 针对不同类型的数据库错误返回不同的错误消息
        if isinstance(exc, IntegrityError):
            # 处理唯一约束、外键约束等完整性错误
            message = "数据完整性错误，可能违反了唯一性约束或外键约束"
            if "duplicate key" in str(exc).lower() or "重复键" in str(exc):
                message = "该记录已存在，请检查输入信息"
        elif isinstance(exc, NoResultFound):
            # 处理查询无结果的情况
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content=ResponseUtils.error_response(
                    code=404,
                    message="请求的资源不存在"
                )
            )
        else:
            # 其他数据库错误
            message = "数据库操作失败，请稍后重试"
        
        # 返回格式化的错误响应
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ResponseUtils.error_response(
                code=500,
                message=message,
                error_data={"type": "database_error"}
            )
        )
    
    @staticmethod
    async def handle_generic_exception(request: Request, exc: Exception) -> JSONResponse:
        """处理通用异常
        
        Args:
            request: HTTP请求
            exc: 通用异常
            
        Returns:
            JSONResponse: 错误响应
        """
        # 记录详细的错误堆栈信息
        logger.error(f"未处理的异常: {str(exc)}, 请求路径: {request.url.path}", exc_info=True)
        
        # 返回格式化的错误响应
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ResponseUtils.error_response(
                code=500,
                message="服务器内部错误，请稍后重试",
                error_data={"type": "internal_error"}
            )
        )


def create_global_exception_handler() -> Callable:
    """创建全局异常处理函数
    
    Returns:
        Callable: 异常处理函数
    """
    async def exception_handler(request: Request, exc: Exception) -> JSONResponse:
        """全局异常处理函数
        
        Args:
            request: HTTP请求
            exc: 异常
            
        Returns:
            JSONResponse: 错误响应
        """
        # 根据异常类型调用对应的处理方法
        if isinstance(exc, RequestValidationError):
            return await ErrorHandler.handle_request_validation_error(request, exc)
        elif isinstance(exc, HTTPException):
            return await ErrorHandler.handle_http_exception(request, exc)
        elif isinstance(exc, SQLAlchemyError):
            return await ErrorHandler.handle_sqlalchemy_error(request, exc)
        else:
            return await ErrorHandler.handle_generic_exception(request, exc)
    
    return exception_handler


class BusinessError(Exception):
    """自定义业务错误异常
    
    用于在业务逻辑中抛出特定的业务错误，便于统一处理。
    """
    
    def __init__(self, code: int, message: str, error_data: Any = None):
        """初始化业务错误
        
        Args:
            code: 错误码
            message: 错误消息
            error_data: 错误数据
        """
        self.code = code
        self.message = message
        self.error_data = error_data
        super().__init__(message)


async def handle_business_error(request: Request, exc: BusinessError) -> JSONResponse:
    """处理业务错误
    
    Args:
        request: HTTP请求
        exc: 业务错误异常
        
    Returns:
        JSONResponse: 错误响应
    """
    # 记录业务错误日志（非严重错误级别）
    logger.warning(f"业务错误: {exc.code} - {exc.message}, 请求路径: {request.url.path}")
    
    # 返回格式化的错误响应
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST if exc.code < 500 else status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ResponseUtils.error_response(
            code=exc.code,
            message=exc.message,
            error_data=exc.error_data
        )
    )