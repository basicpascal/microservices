import os
import uvicorn
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pydantic import BaseModel
from typing import List

# Создаем движок базы данных
SQLALCHEMY_DATABASE_URL = "postgresql://secUREusER:StrongEnoughPassword)@51.250.26.59:5432/query"
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Создаем фабрику сессий
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Создаем базовый класс для объявления моделей SQLAlchemy
Base = declarative_base()


# Определяем модель Note для SQLAlchemy
class NoteDB(Base):
    __tablename__ = "notes_kalugin"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    content = Column(String)


# Создаем таблицы в базе данных
Base.metadata.create_all(bind=engine)

# Создаем экземпляр приложения FastAPI
app = FastAPI()


# Подкласс BaseModel для создания модели данных Pydantic для Note
class Note(BaseModel):
    id: int
    title: str
    content: str


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


# Вложенная функция для обработки данных
def process_data(data):
    # Логика обработки данных
    processed_data = data.upper()
    return processed_data


# Маршрут для создания записи
@app.post("/notes/", response_model=Note)
async def create_note(note: Note, db: Session = Depends(get_db)):
    # Вызов вложенной функции для обработки данных
    processed_content = process_data(note.content)
    db_note = NoteDB(title=note.title, content=processed_content)
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    return db_note


# Маршрут для чтения всех записей
@app.get("/notes/", response_model=List[Note])
async def read_notes(db: Session = Depends(get_db)):
    return db.query(NoteDB).all()


# Маршрут для чтения одной записи
@app.get("/notes/{note_id}", response_model=Note)
async def read_note(note_id: int, db: Session = Depends(get_db)):
    note = db.query(NoteDB).filter(NoteDB.id == note_id).first()
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    return note

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv('PORT', 80)))
