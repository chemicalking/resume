import datetime
import json
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, time
import schedule
import threading
import os

class VisitorTracker:
    def __init__(self, data_file='visitor_data.json'):
        self.data_file = data_file
        self._ensure_data_file()
        self._start_scheduler()
    
    def _ensure_data_file(self):
        if not os.path.exists(self.data_file):
            with open(self.data_file, 'w') as f:
                json.dump({
                    'total_visits': 0,
                    'daily_visits': {},
                    'ip_records': {}
                }, f)
    
    def _start_scheduler(self):
        schedule.every().day.at("20:00").do(self.send_daily_report)
        threading.Thread(target=self._run_schedule, daemon=True).start()
    
    def _run_schedule(self):
        while True:
            schedule.run_pending()
            time.sleep(60)
    
    def get_visitor_ip(self):
        try:
            response = requests.get('https://api.ipify.org?format=json')
            return response.json()['ip']
        except:
            return 'unknown'
    
    def load_data(self):
        try:
            with open(self.data_file, 'r') as f:
                return json.load(f)
        except:
            return {'total_visits': 0, 'daily_visits': {}, 'ip_records': {}}
    
    def save_data(self, data):
        with open(self.data_file, 'w') as f:
            json.dump(data, f)
    
    def update_count(self):
        data = self.load_data()
        today = datetime.now().strftime('%Y-%m-%d')
        ip = self.get_visitor_ip()
        
        # 更新总访问量
        data['total_visits'] += 1
        
        # 更新每日访问
        if today not in data['daily_visits']:
            data['daily_visits'][today] = 0
        data['daily_visits'][today] += 1
        
        # 记录IP
        if today not in data['ip_records']:
            data['ip_records'][today] = []
        if ip not in data['ip_records'][today]:
            data['ip_records'][today].append(ip)
        
        self.save_data(data)
        return data['total_visits']
    
    def get_ip_location(self, ip):
        try:
            response = requests.get(f'http://ip-api.com/json/{ip}')
            data = response.json()
            return {
                'city': data.get('city', 'unknown'),
                'country': data.get('country', 'unknown'),
                'org': data.get('org', 'unknown')
            }
        except:
            return {'city': 'unknown', 'country': 'unknown', 'org': 'unknown'}
    
    def send_daily_report(self):
        data = self.load_data()
        today = datetime.now().strftime('%Y-%m-%d')
        
        # 获取IP地理位置信息
        ip_details = []
        for ip in data['ip_records'].get(today, []):
            location = self.get_ip_location(ip)
            ip_details.append(
                f"IP: {ip}\n"
                f"城市: {location['city']}\n"
                f"国家: {location['country']}\n"
                f"组织: {location['org']}\n"
            )
        
        # 构建邮件内容
        email_content = f"""
        訪問統計報告
        日期: {today}
        
        总访问量: {data['total_visits']}
        今日访问量: {data['daily_visits'].get(today, 0)}
        
        访问IP详情:
        {'='*50}
        {''.join(ip_details)}
        {'='*50}
        """
        
        # 发送邮件
        try:
            msg = MIMEMultipart()
            msg['From'] = 'your_email@example.com'  # 需要配置
            msg['To'] = 'lauandhang@yahoo.com.tw'
            msg['Subject'] = f'简历网站访问统计报告 - {today}'
            msg.attach(MIMEText(email_content, 'plain'))
            
            # 配置邮件服务器
            # server = smtplib.SMTP('smtp.example.com', 587)
            # server.starttls()
            # server.login('your_email@example.com', 'your_password')
            # server.send_message(msg)
            # server.quit()
            
            print(f"Report sent successfully for {today}")
        except Exception as e:
            print(f"Failed to send report: {str(e)}")

# 使用示例
if __name__ == '__main__':
    tracker = VisitorTracker()
    # 更新访问计数
    total_visits = tracker.update_count()
    print(f"Total visits: {total_visits}") 