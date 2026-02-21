# bot.py

import os
import httpx
import sys

# 添加當前目錄到 Python 路徑
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gdrive import upload_text, upload_photo

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

async def handle_message(update):
    if "message" not in update:
        return

    message = update["message"]
    chat_id = message["chat"]["id"]

    if "text" in message:
        text = message["text"]
        if text == "/start":
            await send_message(chat_id, "你好！請將朋友圈的文字或圖片轉發給我，我會自動儲存到 Google Drive。")
        else:
            # 上傳文字
            file_url = await upload_text(f"來自朋友圈的訊息：\n\n{text}")
            await send_message(chat_id, f"文字已儲存：{file_url}")

    if "photo" in message:
        # 取得最高畫質的圖片
        photo = message["photo"][-1]
        file_id = photo["file_id"]
        
        # 取得檔案路徑
        file_path = await get_file_path(file_id)
        if not file_path:
            await send_message(chat_id, "無法取得圖片資訊，請稍後再試。")
            return

        # 下載圖片並上傳
        image_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"
        file_url = await upload_photo(image_url, message.get("caption", ""))
        await send_message(chat_id, f"圖片已儲存：{file_url}")

async def get_file_path(file_id):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{TELEGRAM_API_URL}/getFile", params={"file_id": file_id})
        data = response.json()
        if data["ok"]:
            return data["result"]["file_path"]
    return None

async def send_message(chat_id, text):
    async with httpx.AsyncClient() as client:
        await client.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": text})
