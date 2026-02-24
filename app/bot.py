# bot.py

import os
import httpx
import sys
from datetime import datetime

# 添加當前目錄到 Python 路徑
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gdrive import upload_text, upload_photo, upload_video, create_google_doc

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

# 預設資料夾名稱
DEFAULT_FOLDER_NAMES = ["朋友圈", "生活分享", "每日記錄", "備份"]

# 用於存儲待保存的訊息和自定義資料夾名稱
pending_messages = {}
user_folder_names = {}

async def handle_message(update):
    if "message" not in update:
        return

    message = update["message"]
    chat_id = message["chat"]["id"]
    message_id = message["message_id"]
    
    # 檢查是否為文字指令
    if "text" in message:
        text = message["text"]
        
        if text == "/start":
            await send_start_message(chat_id)
            return
        
        elif text == "/setfolder":
            await send_folder_selection_message(chat_id)
            return
        
        elif text == "/save":
            # 保存待處理的訊息
            if chat_id in pending_messages and pending_messages[chat_id]:
                folder_name = user_folder_names.get(chat_id, DEFAULT_FOLDER_NAMES[0])
                await save_pending_messages(chat_id, folder_name)
            else:
                await send_message(chat_id, "沒有待保存的訊息。請先轉發朋友圈內容。")
            return
        
        # 檢查是否為預設資料夾名稱選擇
        if text in DEFAULT_FOLDER_NAMES:
            user_folder_names[chat_id] = text
            await send_message(chat_id, f"✓ 已選擇資料夾：{text}\n\n現在請轉發朋友圈內容，完成後輸入 /save 保存。")
            return
        
        # 檢查是否為自定義資料夾名稱
        if text.startswith("📁 "):
            # 用戶輸入的自定義名稱
            custom_name = text[3:].strip()
            if custom_name:
                user_folder_names[chat_id] = custom_name
                await send_message(chat_id, f"✓ 已設定資料夾名稱：{custom_name}\n\n現在請轉發朋友圈內容，完成後輸入 /save 保存。")
                return
        
        # 如果不是指令，檢查是否為自定義資料夾名稱輸入
        # 用戶可以直接輸入任何文字作為資料夾名稱
        if not text.startswith("/"):
            # 檢查是否在等待自定義資料夾名稱
            if chat_id not in user_folder_names or user_folder_names[chat_id] is None:
                # 假設用戶想要設定自定義資料夾名稱
                user_folder_names[chat_id] = text
                await send_message(chat_id, f"✓ 已設定資料夾名稱：{text}\n\n現在請轉發朋友圈內容，完成後輸入 /save 保存。")
                return
            
            # 否則作為普通文字訊息處理
            if chat_id not in pending_messages:
                pending_messages[chat_id] = {
                    'texts': [],
                    'photos': [],
                    'videos': [],
                    'message_id': message_id
                }
            
            pending_messages[chat_id]['texts'].append(text)
            await send_message(chat_id, f"✓ 已記錄文字訊息")
            return

    # 初始化待保存訊息
    if chat_id not in pending_messages:
        pending_messages[chat_id] = {
            'texts': [],
            'photos': [],
            'videos': [],
            'message_id': message_id
        }
    
    # 如果用戶還沒選擇資料夾名稱，提示選擇
    if chat_id not in user_folder_names or user_folder_names[chat_id] is None:
        await send_folder_selection_message(chat_id)
        return

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

async def send_start_message(chat_id):
    """發送開始訊息"""
    message_text = """👋 歡迎使用朋友圈備份機器人！

📋 使用步驟：
1️⃣ 輸入 /setfolder 選擇或自定義資料夾名稱
2️⃣ 轉發朋友圈的文字、圖片或影片
3️⃣ 完成後輸入 /save 保存到 Google Drive

💡 提示：
- 支援的媒體類型：文字、圖片、影片 (MP4, MOV, 最大 50MB)
- 文字訊息會保存為 Google Docs
- 每條文字訊息建立獨立的 Doc 檔案
- Doc 檔案中會嵌入相關的圖片和影片連結
- 同一篇貼文的所有內容會放在同一個資料夾中

🔧 指令：
/start - 顯示此訊息
/setfolder - 選擇或自定義資料夾名稱
/save - 保存待處理的訊息"""
    
    await send_message(chat_id, message_text)

async def send_folder_selection_message(chat_id):
    """發送資料夾選擇訊息"""
    message_text = """📁 請選擇資料夾名稱：

預設選項：
"""
    for i, name in enumerate(DEFAULT_FOLDER_NAMES, 1):
        message_text += f"{i}. {name}\n"
    
    message_text += f"\n或者直接輸入自定義資料夾名稱（例如：我的朋友圈、工作備份等）"
    
    await send_message(chat_id, message_text)

async def save_pending_messages(chat_id, folder_name):
    """保存待處理的訊息到 Google Drive"""
    if chat_id not in pending_messages or not pending_messages[chat_id]:
        await send_message(chat_id, "沒有待保存的訊息。")
        return
    
    pending = pending_messages[chat_id]
    message_id = pending['message_id']
    
    await send_message(chat_id, "⏳ 正在保存訊息，請稍候...")
    
    saved_count = 0
    errors = []
    
    # 保存文字（使用 Google Docs）
    for text in pending['texts']:
        try:
            # 準備媒體連結
            media_links = []
            
            # 添加圖片連結
            for i, photo in enumerate(pending['photos'], 1):
                media_links.append(('圖片', photo.get('file_path', 'N/A')))
            
            # 添加影片連結
            for i, video in enumerate(pending['videos'], 1):
                media_links.append(('影片', video.get('file_path', 'N/A')))
            
            result = await create_google_doc(text, message_id, folder_name, media_links if media_links else None)
            if result:
                saved_count += 1
        except Exception as e:
            errors.append(f"文字保存失敗: {str(e)}")
    
    # 保存圖片
    for photo in pending['photos']:
        try:
            image_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{photo['file_path']}"
            result = await upload_photo(image_url, message_id, folder_name, photo.get('caption', ''))
            if result:
                saved_count += 1
        except Exception as e:
            errors.append(f"圖片保存失敗: {str(e)}")
    
    # 保存影片
    for video in pending['videos']:
        try:
            video_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{video['file_path']}"
            result = await upload_video(video_url, message_id, folder_name, video.get('caption', ''))
            if result:
                saved_count += 1
        except Exception as e:
            errors.append(f"影片保存失敗: {str(e)}")
    
    # 發送結果訊息
    response = f"✅ 已保存 {saved_count} 個檔案\n"
    response += f"📅 日期：{datetime.now().strftime('%Y-%m-%d')}\n"
    response += f"📁 資料夾：{folder_name}\n"
    response += f"📍 訊息已按日期和訊息 ID 分類\n"
    
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
