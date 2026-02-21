# bot.py

import os
import httpx
import sys
from datetime import datetime

# 添加當前目錄到 Python 路徑
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gdrive import upload_text, upload_photo, upload_video

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

# 用於存儲待保存的訊息
pending_messages = {}

async def handle_message(update):
    if "message" not in update:
        return

    message = update["message"]
    chat_id = message["chat"]["id"]
    message_id = message["message_id"]
    
    # 檢查是否為 /start 指令
    if "text" in message:
        text = message["text"]
        if text == "/start":
            await send_message(chat_id, "你好！請轉發朋友圈的內容給我，然後輸入 /save 指令來備份。\n\n支援的媒體類型：\n- 文字\n- 圖片\n- 影片 (MP4, MOV, 最大 50MB)")
            return
        elif text == "/save":
            # 保存待處理的訊息
            if chat_id in pending_messages and pending_messages[chat_id]:
                await save_pending_messages(chat_id)
            else:
                await send_message(chat_id, "沒有待保存的訊息。請先轉發朋友圈內容。")
            return

    # 儲存訊息到 pending_messages
    if chat_id not in pending_messages:
        pending_messages[chat_id] = {
            'texts': [],
            'photos': [],
            'videos': [],
            'message_id': message_id
        }
    
    # 處理文字
    if "text" in message:
        text = message["text"]
        if not text.startswith("/"):  # 忽略指令
            pending_messages[chat_id]['texts'].append(text)
            await send_message(chat_id, f"✓ 已記錄文字訊息")

    # 處理圖片
    if "photo" in message:
        photo = message["photo"][-1]  # 取得最高畫質
        file_id = photo["file_id"]
        file_path = await get_file_path(file_id)
        if file_path:
            pending_messages[chat_id]['photos'].append({
                'file_id': file_id,
                'file_path': file_path,
                'caption': message.get("caption", "")
            })
            await send_message(chat_id, f"✓ 已記錄圖片 ({len(pending_messages[chat_id]['photos'])} 張)")

    # 處理影片
    if "video" in message:
        video = message["video"]
        file_id = video["file_id"]
        file_size = video.get("file_size", 0)
        
        # 檢查檔案大小
        if file_size > 50 * 1024 * 1024:
            await send_message(chat_id, "❌ 影片檔案超過 50MB 限制，無法保存")
            return
        
        file_path = await get_file_path(file_id)
        if file_path:
            pending_messages[chat_id]['videos'].append({
                'file_id': file_id,
                'file_path': file_path,
                'caption': message.get("caption", "")
            })
            await send_message(chat_id, f"✓ 已記錄影片 ({len(pending_messages[chat_id]['videos'])} 個)")

async def save_pending_messages(chat_id):
    """保存待處理的訊息到 Google Drive"""
    if chat_id not in pending_messages or not pending_messages[chat_id]:
        await send_message(chat_id, "沒有待保存的訊息。")
        return
    
    pending = pending_messages[chat_id]
    message_id = pending['message_id']
    
    await send_message(chat_id, "⏳ 正在保存訊息，請稍候...")
    
    saved_count = 0
    errors = []
    
    # 保存文字
    for text in pending['texts']:
        try:
            result = await upload_text(text, message_id)
            if result:
                saved_count += 1
        except Exception as e:
            errors.append(f"文字保存失敗: {str(e)}")
    
    # 保存圖片
    for photo in pending['photos']:
        try:
            image_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{photo['file_path']}"
            result = await upload_photo(image_url, message_id, photo.get('caption', ''))
            if result:
                saved_count += 1
        except Exception as e:
            errors.append(f"圖片保存失敗: {str(e)}")
    
    # 保存影片
    for video in pending['videos']:
        try:
            video_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{video['file_path']}"
            result = await upload_video(video_url, message_id, video.get('caption', ''))
            if result:
                saved_count += 1
        except Exception as e:
            errors.append(f"影片保存失敗: {str(e)}")
    
    # 發送結果訊息
    response = f"✅ 已保存 {saved_count} 個檔案\n"
    response += f"📅 日期：{datetime.now().strftime('%Y-%m-%d')}\n"
    response += f"📁 訊息已按日期和訊息 ID 分類\n"
    
    if errors:
        response += "\n⚠️ 發生以下錯誤：\n"
        for error in errors:
            response += f"- {error}\n"
    
    await send_message(chat_id, response)
    
    # 清除待處理訊息
    pending_messages[chat_id] = None

async def get_file_path(file_id):
    """取得 Telegram 檔案路徑"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{TELEGRAM_API_URL}/getFile", params={"file_id": file_id})
            data = response.json()
            if data["ok"]:
                return data["result"]["file_path"]
        except Exception as e:
            print(f"Error getting file path: {e}")
    return None

async def send_message(chat_id, text):
    """發送訊息給使用者"""
    async with httpx.AsyncClient() as client:
        try:
            await client.post(f"{TELEGRAM_API_URL}/sendMessage", json={"chat_id": chat_id, "text": text})
        except Exception as e:
            print(f"Error sending message: {e}")
