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

async def upload_text(content):
    if not drive_service:
        return "Google Drive not configured."

    try:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        file_name = f"text_{timestamp}.txt"
        
        file_metadata = {
            'name': file_name,
            'parents': [GOOGLE_DRIVE_FOLDER_ID]
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
        return f"Error: {str(e)}"

async def upload_photo(image_url, caption):
    if not drive_service:
        return "Google Drive not configured."

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(image_url)
            response.raise_for_status()
            image_data = response.content

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        file_name = f"photo_{timestamp}.jpg"
        
        file_metadata = {
            'name': file_name,
            'parents': [GOOGLE_DRIVE_FOLDER_ID],
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
        return f"Error: {str(e)}"
