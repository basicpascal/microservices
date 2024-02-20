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
SQLALCHEMY_DATABASE_URL = "sqlite:///./categories.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Создаем фабрику сессий
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Создаем базовый класс для объявления моделей SQLAlchemy
Base = declarative_base()


# Определяем модель Category для SQLAlchemy
class Category(Base):
    __tablename__ = "categories"
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


# Корневой маршрут
@app.get("/")
async def root():
    return {"message": "Hello, World!"}


# Маршрут для создания записи
@app.post("/", response_model=CategoryModel)
async def create_category(category: CategoryModel, db: Session = Depends(get_db)):
    db_category = Category(**category.dict())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category


# Маршрут для чтения всех записей
@app.get("/", response_model=List[CategoryModel])
async def read_categories(db: Session = Depends(get_db)):
    return db.query(Category).all()


# Маршрут для чтения одной записи
@app.get("/{category_id}", response_model=CategoryModel)
async def read_category(category_id: int, db: Session = Depends(get_db)):
    category = db.query(Category).filter(Category.id == category_id).first()
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return category

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv('PORT', 80)))
