import json
from datetime import datetime
import requests
from pathlib import Path
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
from typing import Dict, Any, Optional

from config import DB_CONFIG, MAIL_CONFIG

# 配置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class VisitorTracker:
    def __init__(self):
        self.data_file = DB_CONFIG["visitor_data_path"]
        self._ensure_data_file()
    
    def _ensure_data_file(self) -> None:
        """確保訪問數據文件存在"""
        if not self.data_file.exists():
            self.data_file.parent.mkdir(parents=True, exist_ok=True)
            self._save_data({"total_visits": 0, "visits_by_date": {}})
    
    def _load_data(self) -> Dict[str, Any]:
        """載入訪問數據"""
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"載入訪問數據時發生錯誤：{str(e)}")
            return {"total_visits": 0, "visits_by_date": {}}
    
    def _save_data(self, data: Dict[str, Any]) -> None:
        """保存訪問數據"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存訪問數據時發生錯誤：{str(e)}")
    
    def get_visitor_ip(self) -> str:
        """獲取訪問者IP地址"""
        try:
            response = requests.get('https://api.ipify.org?format=json')
            return response.json()['ip']
        except Exception as e:
            logger.error(f"獲取IP地址時發生錯誤：{str(e)}")
            return '未知'
    
    def update_visitor_count(self) -> int:
        """更新訪問計數"""
        try:
            data = self._load_data()
            today = datetime.now().strftime('%Y-%m-%d')
            
            # 更新總訪問量
            data['total_visits'] += 1
            
            # 更新每日訪問量
            if today not in data['visits_by_date']:
                data['visits_by_date'][today] = 0
            data['visits_by_date'][today] += 1
            
            self._save_data(data)
            return data['total_visits']
        except Exception as e:
            logger.error(f"更新訪問計數時發生錯誤：{str(e)}")
            return 0
    
    def send_daily_report(self, date: Optional[str] = None) -> bool:
        """發送每日訪問報告"""
        try:
            if not all([MAIL_CONFIG["smtp_server"], 
                       MAIL_CONFIG["sender_email"], 
                       MAIL_CONFIG["receiver_email"]]):
                logger.warning("郵件配置不完整，跳過發送報告")
                return False
                
            data = self._load_data()
            date = date or datetime.now().strftime('%Y-%m-%d')
            daily_visits = data['visits_by_date'].get(date, 0)
            
            email_content = f"""
            訪問統計報告 - {date}
            
            總訪問量：{data['total_visits']}
            今日訪問量：{daily_visits}
            """
            
            msg = MIMEMultipart()
            msg['From'] = MAIL_CONFIG["sender_email"]
            msg['To'] = MAIL_CONFIG["receiver_email"]
            msg['Subject'] = f'簡歷網站訪問統計報告 - {date}'
            msg.attach(MIMEText(email_content, 'plain'))
            
            with smtplib.SMTP(MAIL_CONFIG["smtp_server"], MAIL_CONFIG["smtp_port"]) as server:
                server.starttls()
                server.login(MAIL_CONFIG["sender_email"], MAIL_CONFIG.get("sender_password", ""))
                server.send_message(msg)
            
            return True
        except Exception as e:
            logger.error(f"發送每日報告時發生錯誤：{str(e)}")
            return False

# 創建單例實例
visitor_tracker = VisitorTracker()
