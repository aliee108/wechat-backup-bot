# scheduler.py

import os
import asyncio
from datetime import datetime
from .gdrive import upload_text

async def generate_daily_report():
    """每天生成一份彙總報告"""
    timestamp = datetime.now().strftime("%Y-%m-%d")
    report_content = f"""
朋友圈內容彙總報告
生成時間：{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

本報告自動生成，包含今日所有通過 Telegram Bot 上傳的朋友圈內容。

所有檔案已儲存到 Google Drive，請查看相應的連結。
"""
    
    try:
        file_url = await upload_text(report_content)
        print(f"Daily report generated: {file_url}")
    except Exception as e:
        print(f"Error generating daily report: {e}")
