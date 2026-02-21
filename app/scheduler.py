# scheduler.py

import os
import asyncio
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gdrive import generate_daily_summary

scheduler = BackgroundScheduler()

def generate_daily_report():
    """定時生成每日報告的同步包裝函數"""
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    asyncio.run(generate_daily_summary(yesterday))
    print(f"Daily report generated for {yesterday}")

def start_scheduler():
    """啟動排程器"""
    try:
        # 每天午夜 (00:00) 生成前一天的報告
        scheduler.add_job(
            generate_daily_report,
            trigger=CronTrigger(hour=0, minute=0),
            id='daily_report',
            name='Generate daily summary report',
            replace_existing=True
        )
        
        if not scheduler.running:
            scheduler.start()
            print("Scheduler started")
    except Exception as e:
        print(f"Error starting scheduler: {e}")

def stop_scheduler():
    """停止排程器"""
    try:
        if scheduler.running:
            scheduler.shutdown()
            print("Scheduler stopped")
    except Exception as e:
        print(f"Error stopping scheduler: {e}")
