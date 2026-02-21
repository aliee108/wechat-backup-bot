# main.py

from fastapi import FastAPI, Request
import uvicorn
import os
import sys

# 添加父目錄到 Python 路徑
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from bot import handle_message

app = FastAPI()

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

@app.post(f"/{BOT_TOKEN}")
async def webhook(request: Request):
    update = await request.json()
    await handle_message(update)
    return {"status": "ok"}

@app.get("/")
async def index():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
