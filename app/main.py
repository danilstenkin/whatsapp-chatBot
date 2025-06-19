from fastapi import FastAPI
from app.routers import whatsapp
from app.db.database import connect_db, disconnect_db
import logging

from dotenv import load_dotenv
load_dotenv()  # обязательно до всех других импортов

app = FastAPI()
app.include_router(whatsapp.router)

@app.get("/")
async def root():
    return {"message": "Бот работает!"}

logger = logging.getLogger("uvicorn.error")

@app.on_event("startup")
async def startup():
    await connect_db()
    logger.info("Database connected")

@app.on_event("shutdown")
async def shutdown():
    await disconnect_db()
    logger.info("Database disconnected")

