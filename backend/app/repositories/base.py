from typing import TypeVar, Generic, Type, List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.database import Base

ModelType = TypeVar("ModelType", bound=Base)

class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    def get_by_id(self, db: Session, id: int) -> Optional[ModelType]:
        return db.query(self.model).filter(self.model.id == id).first()

    def get_all(self, db: Session, skip: int = 0, limit: int = 100) -> List[ModelType]:
        return db.query(self.model).offset(skip).limit(limit).all()

    def create(self, db: Session, **kwargs) -> ModelType:
        instance = self.model(**kwargs)
        db.add(instance)
        db.flush()
        return instance

    def create_many(self, db: Session, items: List[Dict[str, Any]]) -> List[ModelType]:
        instances = [self.model(**item) for item in items]
        db.add_all(instances)
        db.flush()
        return instances

    def update(self, db: Session, id: int, **kwargs) -> Optional[ModelType]:
        db.query(self.model).filter(self.model.id == id).update(kwargs, synchronize_session=False)
        db.flush()
        return self.get_by_id(db, id)

    def delete(self, db: Session, id: int) -> bool:
        result = db.query(self.model).filter(self.model.id == id).delete()
        db.flush()
        return result > 0

    def exists(self, db: Session, **filters) -> bool:
        query = db.query(self.model)
        for key, value in filters.items():
            query = query.filter(getattr(self.model, key) == value)
        return query.first() is not None

    def count(self, db: Session, **filters) -> int:
        query = db.query(self.model)
        for key, value in filters.items():
            query = query.filter(getattr(self.model, key) == value)
        return query.count()