"""基础Repository类"""
from typing import Generic, TypeVar, List, Optional, Dict, Any, Type
from sqlalchemy.orm import Session, Query
from sqlalchemy.exc import SQLAlchemyError
import uuid
from database.database import Base

ModelType = TypeVar('ModelType', bound=Base)


class BaseRepository(Generic[ModelType]):
    """基础数据访问类"""
    
    def __init__(self, db: Session, model: Type[ModelType]):
        self.db = db
        self.model = model
    
    def get_by_id(self, id: uuid.UUID) -> Optional[ModelType]:
        """根据ID获取单个实体"""
        try:
            return self.db.query(self.model).filter(self.model.id == id).first()
        except SQLAlchemyError as e:
            # 记录错误但不抛出，返回None
            print(f"Error getting {self.model.__name__} by id: {e}")
            return None
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """获取所有实体列表"""
        try:
            return self.db.query(self.model).offset(skip).limit(limit).all()
        except SQLAlchemyError as e:
            print(f"Error getting all {self.model.__name__}: {e}")
            return []
    
    def create(self, obj_in: Dict[str, Any]) -> Optional[ModelType]:
        """创建新实体"""
        try:
            db_obj = self.model(**obj_in)
            self.db.add(db_obj)
            self.db.commit()
            self.db.refresh(db_obj)
            return db_obj
        except SQLAlchemyError as e:
            self.db.rollback()
            print(f"Error creating {self.model.__name__}: {e}")
            return None
    
    def update(self, db_obj: ModelType, obj_in: Dict[str, Any]) -> Optional[ModelType]:
        """更新实体"""
        try:
            # 排除None值的更新
            update_data = {k: v for k, v in obj_in.items() if v is not None}
            for field, value in update_data.items():
                setattr(db_obj, field, value)
            
            self.db.add(db_obj)
            self.db.commit()
            self.db.refresh(db_obj)
            return db_obj
        except SQLAlchemyError as e:
            self.db.rollback()
            print(f"Error updating {self.model.__name__}: {e}")
            return None
    
    def delete(self, db_obj: ModelType) -> bool:
        """删除实体"""
        try:
            self.db.delete(db_obj)
            self.db.commit()
            return True
        except SQLAlchemyError as e:
            self.db.rollback()
            print(f"Error deleting {self.model.__name__}: {e}")
            return False
    
    def delete_by_id(self, id: uuid.UUID) -> bool:
        """根据ID删除实体"""
        try:
            obj = self.get_by_id(id)
            if obj:
                self.db.delete(obj)
                self.db.commit()
                return True
            return False
        except SQLAlchemyError as e:
            self.db.rollback()
            print(f"Error deleting {self.model.__name__} by id: {e}")
            return False
    
    def filter_by(self, **kwargs) -> List[ModelType]:
        """根据条件过滤实体列表"""
        try:
            # 过滤掉None值的条件
            filter_kwargs = {k: v for k, v in kwargs.items() if v is not None}
            return self.db.query(self.model).filter_by(**filter_kwargs).all()
        except SQLAlchemyError as e:
            print(f"Error filtering {self.model.__name__}: {e}")
            return []
    
    def get_one(self, **kwargs) -> Optional[ModelType]:
        """根据条件获取单个实体"""
        try:
            filter_kwargs = {k: v for k, v in kwargs.items() if v is not None}
            return self.db.query(self.model).filter_by(**filter_kwargs).first()
        except SQLAlchemyError as e:
            print(f"Error getting one {self.model.__name__}: {e}")
            return None
    
    def count(self, **kwargs) -> int:
        """统计符合条件的实体数量"""
        try:
            filter_kwargs = {k: v for k, v in kwargs.items() if v is not None}
            return self.db.query(self.model).filter_by(**filter_kwargs).count()
        except SQLAlchemyError as e:
            print(f"Error counting {self.model.__name__}: {e}")
            return 0
    
    def exists(self, **kwargs) -> bool:
        """检查是否存在符合条件的实体"""
        try:
            filter_kwargs = {k: v for k, v in kwargs.items() if v is not None}
            return self.db.query(self.model).filter_by(**filter_kwargs).first() is not None
        except SQLAlchemyError as e:
            print(f"Error checking existence of {self.model.__name__}: {e}")
            return False
    
    def get_query(self) -> Query:
        """获取基础查询对象"""
        return self.db.query(self.model)