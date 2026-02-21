# main.py

from fastapi import FastAPI, Request
import uvicorn
import os
import sys

# 添加父目錄到 Python 路徑
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from bot import handle_message
from scheduler import start_scheduler, stop_scheduler

app = FastAPI()

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

@app.on_event("startup")
async def startup_event():
    """應用程式啟動時執行"""
    start_scheduler()
    print("Application started")

@app.on_event("shutdown")
async def shutdown_event():
    """應用程式關閉時執行"""
    stop_scheduler()
    print("Application stopped")

@app.post(f"/{BOT_TOKEN}")
async def webhook(request: Request):
    update = await request.json()
    await handle_message(update)
    return {"status": "ok"}

@app.get("/")
async def index():
    return {"status": "ok", "message": "Telegram WeChat Backup Bot is running"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
