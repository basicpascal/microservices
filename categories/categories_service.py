import os
import uvicorn
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Создаем движок базы данных
SQLALCHEMY_DATABASE_URL = "postgresql://secUREusER:StrongEnoughPassword)@51.250.26.59:5432/query"
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Создаем фабрику сессий
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Создаем базовый класс для объявления моделей SQLAlchemy
Base = declarative_base()


# Определяем модель Category для SQLAlchemy
class Category(Base):
    __tablename__ = "categories_kalugin"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)


# Создаем таблицы в базе данных
Base.metadata.create_all(bind=engine)

# Создаем экземпляр приложения FastAPI
app = FastAPI()


# Подкласс BaseModel для создания модели данных Pydantic для Category
class CategoryModel(BaseModel):
    id: int
    name: str


# Функция для получения сессии базы данных
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Маршрут для создания записи
@app.post("/categories/", response_model=CategoryModel)
async def create_category(category: CategoryModel, db: Session = Depends(get_db)):
    db_category = Category(**category.dict())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category


# Маршрут для чтения всех записей
@app.get("/categories/", response_model=List[CategoryModel])
async def read_categories(db: Session = Depends(get_db)):
    return db.query(Category).all()


# Маршрут для чтения одной записи
@app.get("/categories/{category_id}", response_model=CategoryModel)
async def read_category(category_id: int, db: Session = Depends(get_db)):
    category = db.query(Category).filter(Category.id == category_id).first()
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


# Маршрут для удаления записи
@app.delete("/categories/{category_id}")
async def delete_category(category_id: int, db: Session = Depends(get_db)):
    category = db.query(Category).filter(Category.id == category_id).first()
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    db.delete(category)
    db.commit()
    return {"message": "Category deleted successfully"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv('PORT', 80)))
