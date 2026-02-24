# gdrive.py

import os
import json
import httpx
from datetime import datetime
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import io

# 讀取環境變數
GOOGLE_SERVICE_ACCOUNT_JSON = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
GOOGLE_DRIVE_FOLDER_ID = os.environ.get("GOOGLE_DRIVE_FOLDER_ID")

# 設定 Google API
SCOPES = ['https://www.googleapis.com/auth/drive']

creds = None
drive_service = None

try:
    if GOOGLE_SERVICE_ACCOUNT_JSON:
        creds_info = json.loads(GOOGLE_SERVICE_ACCOUNT_JSON)
        creds = Credentials.from_service_account_info(creds_info, scopes=SCOPES)
        drive_service = build('drive', 'v3', credentials=creds)
except Exception as e:
    print(f"Error initializing Google Drive: {e}")

async def get_or_create_custom_folder(folder_name):
    """取得或建立自定義名稱的資料夾"""
    if not drive_service:
        return None
    
    try:
        # 搜尋是否已存在該名稱的資料夾
        query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and '{GOOGLE_DRIVE_FOLDER_ID}' in parents and trashed=false"
        results = drive_service.files().list(q=query, spaces='drive', fields='files(id, name)', pageSize=1).execute()
        files = results.get('files', [])
        
        if files:
            return files[0]['id']
        
        # 如果不存在，建立新資料夾
        file_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [GOOGLE_DRIVE_FOLDER_ID]
        }
        folder = drive_service.files().create(body=file_metadata, fields='id').execute()
        return folder.get('id')
    except Exception as e:
        print(f"Error getting/creating custom folder: {e}")
        return None

async def get_or_create_date_folder(custom_folder_id, date_str):
    """在自定義資料夾下建立日期資料夾"""
    if not drive_service:
        return None
    
    try:
        # 搜尋是否已存在該日期的資料夾
        query = f"name='{date_str}' and mimeType='application/vnd.google-apps.folder' and '{custom_folder_id}' in parents and trashed=false"
        results = drive_service.files().list(q=query, spaces='drive', fields='files(id, name)', pageSize=1).execute()
        files = results.get('files', [])
        
        if files:
            return files[0]['id']
        
        # 如果不存在，建立新資料夾
        file_metadata = {
            'name': date_str,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [custom_folder_id]
        }
        folder = drive_service.files().create(body=file_metadata, fields='id').execute()
        return folder.get('id')
    except Exception as e:
        print(f"Error getting/creating date folder: {e}")
        return None

async def get_or_create_message_folder(date_folder_id, message_id):
    """取得或建立用於存放同一訊息的資料夾"""
    if not drive_service:
        return None
    
    try:
        folder_name = f"message_{message_id}"
        query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and '{date_folder_id}' in parents and trashed=false"
        results = drive_service.files().list(q=query, spaces='drive', fields='files(id, name)', pageSize=1).execute()
        files = results.get('files', [])
        
        if files:
            return files[0]['id']
        
        # 建立新資料夾
        file_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [date_folder_id]
        }
        folder = drive_service.files().create(body=file_metadata, fields='id').execute()
        return folder.get('id')
    except Exception as e:
        print(f"Error getting/creating message folder: {e}")
        return None

async def upload_text(content, message_id, custom_folder_name):
    """上傳文字到 Google Drive"""
    if not drive_service:
        return None

    try:
        # 取得自定義資料夾
        custom_folder_id = await get_or_create_custom_folder(custom_folder_name)
        if not custom_folder_id:
            return None
        
        # 取得日期資料夾
        date_str = datetime.now().strftime("%Y-%m-%d")
        date_folder_id = await get_or_create_date_folder(custom_folder_id, date_str)
        if not date_folder_id:
            return None
        
        # 取得訊息資料夾
        message_folder_id = await get_or_create_message_folder(date_folder_id, message_id)
        if not message_folder_id:
            return None
        
        timestamp = datetime.now().strftime("%H-%M-%S")
        file_name = f"text_{timestamp}.txt"
        
        file_metadata = {
            'name': file_name,
            'parents': [message_folder_id]
        }
        
        media = MediaIoBaseUpload(io.BytesIO(content.encode('utf-8')), mimetype='text/plain', resumable=True)
        
        file = drive_service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, webViewLink'
        ).execute()
        
        return file.get('webViewLink')
    except Exception as e:
        print(f"Error uploading text: {e}")
        return None

async def upload_photo(image_url, message_id, custom_folder_name, caption=""):
    """上傳圖片到 Google Drive"""
    if not drive_service:
        return None

    try:
        # 下載圖片
        async with httpx.AsyncClient() as client:
            response = await client.get(image_url)
            response.raise_for_status()
            image_data = response.content

        # 取得自定義資料夾
        custom_folder_id = await get_or_create_custom_folder(custom_folder_name)
        if not custom_folder_id:
            return None
        
        # 取得日期資料夾
        date_str = datetime.now().strftime("%Y-%m-%d")
        date_folder_id = await get_or_create_date_folder(custom_folder_id, date_str)
        if not date_folder_id:
            return None
        
        # 取得訊息資料夾
        message_folder_id = await get_or_create_message_folder(date_folder_id, message_id)
        if not message_folder_id:
            return None

        timestamp = datetime.now().strftime("%H-%M-%S")
        file_name = f"photo_{timestamp}.jpg"
        
        file_metadata = {
            'name': file_name,
            'parents': [message_folder_id],
            'description': caption
        }
        
        media = MediaIoBaseUpload(io.BytesIO(image_data), mimetype='image/jpeg', resumable=True)
        
        file = drive_service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, webViewLink'
        ).execute()
        
        return file.get('webViewLink')
    except Exception as e:
        print(f"Error uploading photo: {e}")
        return None

async def upload_video(video_url, message_id, custom_folder_name, caption=""):
    """上傳影片到 Google Drive"""
    if not drive_service:
        return None

    try:
        # 下載影片
        async with httpx.AsyncClient() as client:
            response = await client.get(video_url, timeout=60.0)
            response.raise_for_status()
            video_data = response.content
        
        # 檢查檔案大小（最大 50MB）
        if len(video_data) > 50 * 1024 * 1024:
            return "Error: Video file exceeds 50MB limit"

        # 取得自定義資料夾
        custom_folder_id = await get_or_create_custom_folder(custom_folder_name)
        if not custom_folder_id:
            return None
        
        # 取得日期資料夾
        date_str = datetime.now().strftime("%Y-%m-%d")
        date_folder_id = await get_or_create_date_folder(custom_folder_id, date_str)
        if not date_folder_id:
            return None
        
        # 取得訊息資料夾
        message_folder_id = await get_or_create_message_folder(date_folder_id, message_id)
        if not message_folder_id:
            return None

        timestamp = datetime.now().strftime("%H-%M-%S")
        file_name = f"video_{timestamp}.mp4"
        
        file_metadata = {
            'name': file_name,
            'parents': [message_folder_id],
            'description': caption
        }
        
        media = MediaIoBaseUpload(io.BytesIO(video_data), mimetype='video/mp4', resumable=True)
        
        file = drive_service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, webViewLink'
        ).execute()
        
        return file.get('webViewLink')
    except Exception as e:
        print(f"Error uploading video: {e}")
        return None

async def generate_daily_summary(custom_folder_name, date_str):
    """生成每日彙總報告"""
    if not drive_service:
        return None
    
    try:
        custom_folder_id = await get_or_create_custom_folder(custom_folder_name)
        if not custom_folder_id:
            return None
        
        date_folder_id = await get_or_create_date_folder(custom_folder_id, date_str)
        if not date_folder_id:
            return None
        
        # 列出該日期資料夾中的所有訊息資料夾
        query = f"mimeType='application/vnd.google-apps.folder' and '{date_folder_id}' in parents and trashed=false"
        results = drive_service.files().list(q=query, spaces='drive', fields='files(id, name)', pageSize=100).execute()
        message_folders = results.get('files', [])
        
        # 生成報告內容
        report_content = f"""朋友圈內容彙總報告
生成時間：{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
日期：{date_str}
分類：{custom_folder_name}

本日共備份 {len(message_folders)} 條訊息

訊息列表：
"""
        for i, folder in enumerate(message_folders, 1):
            report_content += f"{i}. {folder['name']}\n"
        
        report_content += "\n所有檔案已儲存到 Google Drive，請查看相應的連結。\n"
        
        # 上傳報告
        file_metadata = {
            'name': f"daily_summary_{date_str}.txt",
            'parents': [date_folder_id]
        }
        
        media = MediaIoBaseUpload(io.BytesIO(report_content.encode('utf-8')), mimetype='text/plain', resumable=True)
        
        file = drive_service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, webViewLink'
        ).execute()
        
        return file.get('webViewLink')
    except Exception as e:
        print(f"Error generating daily summary: {e}")
        return None

# Google Docs API 支援
docs_service = None

try:
    if GOOGLE_SERVICE_ACCOUNT_JSON:
        docs_service = build('docs', 'v1', credentials=creds)
except Exception as e:
    print(f"Error initializing Google Docs: {e}")

async def create_google_doc(text_content, message_id, custom_folder_name, media_links=None):
    """建立 Google Docs 文件來儲存文字訊息"""
    if not drive_service or not docs_service:
        return None
    
    try:
        # 取得自定義資料夾
        custom_folder_id = await get_or_create_custom_folder(custom_folder_name)
        if not custom_folder_id:
            return None
        
        # 取得日期資料夾
        date_str = datetime.now().strftime("%Y-%m-%d")
        date_folder_id = await get_or_create_date_folder(custom_folder_id, date_str)
        if not date_folder_id:
            return None
        
        # 取得訊息資料夾
        message_folder_id = await get_or_create_message_folder(date_folder_id, message_id)
        if not message_folder_id:
            return None
        
        # 建立 Google Docs 檔案
        timestamp = datetime.now().strftime("%H-%M-%S")
        doc_title = f"text_{timestamp}"
        
        doc_body = {
            'title': doc_title,
            'parents': [message_folder_id]
        }
        
        # 在 Google Drive 中建立文件
        doc = drive_service.files().create(
            body=doc_body,
            mimeType='application/vnd.google-apps.document',
            fields='id, webViewLink'
        ).execute()
        
        doc_id = doc.get('id')
        doc_link = doc.get('webViewLink')
        
        # 準備文件內容
        requests = []
        
        # 添加文字內容
        requests.append({
            'insertText': {
                'text': text_content,
                'location': {'index': 1}
            }
        })
        
        # 添加媒體連結（如果有）
        if media_links:
            requests.append({
                'insertText': {
                    'text': '\n\n相關媒體：\n',
                    'location': {'index': len(text_content) + 1}
                }
            })
            
            current_index = len(text_content) + 14
            for link_type, link_url in media_links:
                link_text = f"• {link_type}: {link_url}\n"
                requests.append({
                    'insertText': {
                        'text': link_text,
                        'location': {'index': current_index}
                    }
                })
                current_index += len(link_text)
        
        # 添加時間戳記
        timestamp_text = f"\n\n建立時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        requests.append({
            'insertText': {
                'text': timestamp_text,
                'location': {'index': 1}
            }
        })
        
        # 應用所有更改
        if requests:
            docs_service.documents().batchUpdate(
                documentId=doc_id,
                body={'requests': requests}
            ).execute()
        
        return doc_link
    
    except Exception as e:
        print(f"Error creating Google Doc: {e}")
        return None
