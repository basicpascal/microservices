import os
from typing import List

import uvicorn
from fastapi import FastAPI, HTTPException, Depends, Form, Header
from keycloak.keycloak_openid import KeycloakOpenID
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker
from prometheus_fastapi_instrumentator import Instrumentator

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

# Данные для подключения к Keycloak
KEYCLOAK_URL = "http://localhost:8180/"
KEYCLOAK_CLIENT_ID = "kalugin"
KEYCLOAK_REALM = "notes_service_realm"
KEYCLOAK_CLIENT_SECRET = "n7ez8h0rsfZ67XWsGpDPl6nlbyBDVv7J"

keycloak_openid = KeycloakOpenID(server_url=KEYCLOAK_URL,
                                 client_id=KEYCLOAK_CLIENT_ID,
                                 realm_name=KEYCLOAK_REALM,
                                 client_secret_key=KEYCLOAK_CLIENT_SECRET)

user_token = ""

Instrumentator().instrument(app).expose(app)

@app.post("/get-token")
async def get_token(username: str = Form(...), password: str = Form(...)):
    try:
        # Получение токена
        token = keycloak_openid.token(grant_type=["password"],
                                      username=username,
                                      password=password)
        return token
    except Exception as e:
        print(e)  # Логирование для диагностики
        raise HTTPException(status_code=400, detail="Не удалось получить токен")


def check_user_roles(token):
    try:
        token_info = keycloak_openid.introspect(token)
        if "testRole" not in token_info["realm_access"]["roles"]:
            raise HTTPException(status_code=403, detail="Access denied")
        return token_info
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token or access denied")


# Подкласс BaseModel для создания модели данных Pydantic для Note
class Note(BaseModel):
    id: int
    title: str
    content: str

    class Config:
        orm_mode = True

# Функция для получения сессии базы данных
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Вложенная функция для обработки данных
def process_data(data):
    # Логика обработки данных
    processed_data = data.upper()
    return processed_data


# Маршрут для создания записи
@app.post("/notes/", response_model=Note)
async def create_note(note: Note, db: Session = Depends(get_db), token: str = Header(...)):
    if check_user_roles(token):
        # Вызов вложенной функции для обработки данных
        processed_content = process_data(note.content)
        db_note = NoteDB(title=note.title, content=processed_content)
        db.add(db_note)
        db.commit()
        db.refresh(db_note)
        return db_note
    else:
        return "Wrong JWT Token"


# Маршрут для чтения всех записей
@app.get("/notes/", response_model=List[Note])
async def read_notes(db: Session = Depends(get_db), token: str = Header(...)):
    if check_user_roles(token):
        return db.query(NoteDB).all()


# Маршрут для чтения одной записи
@app.get("/notes/{note_id}", response_model=Note)
async def read_note(note_id: int, db: Session = Depends(get_db)):
    note = db.query(NoteDB).filter(NoteDB.id == note_id).first()
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    return note


# Маршрут для удаления записи
@app.delete("/notes/{note_id}")
async def delete_note(note_id: int, db: Session = Depends(get_db), token: str = Header(...)):
    if check_user_roles(token):
        note = db.query(NoteDB).filter(NoteDB.id == note_id).first()
        if note is None:
            raise HTTPException(status_code=404, detail="Note not found")
        db.delete(note)
        db.commit()
        return {"message": "Note deleted successfully"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv('PORT', 80)))
