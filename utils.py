import json
import requests
from datetime import datetime
from pathlib import Path

def load_visitor_data():
    """
    載入訪客數據
    """
    try:
        with open(str(Path(__file__).parent / "visitor_data.json"), 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {'total_visits': 0, 'daily_visits': {}, 'ip_records': {}}

def save_visitor_data(data):
    """
    儲存訪客數據
    """
    with open(str(Path(__file__).parent / "visitor_data.json"), 'w') as f:
        json.dump(data, f)

def get_visitor_ip():
    """
    取得訪客 IP 地址
    """
    try:
        response = requests.get('https://api.ipify.org?format=json')
        return response.json()['ip']
    except:
        return 'Unknown'

def update_visitor_count():
    """
    更新訪客計數
    """
    visitor_data = load_visitor_data()
    today = datetime.now().strftime('%Y-%m-%d')
    ip = get_visitor_ip()

    visitor_data['total_visits'] += 1

    if today not in visitor_data['daily_visits']:
        visitor_data['daily_visits'][today] = 0
    visitor_data['daily_visits'][today] += 1

    if today not in visitor_data['ip_records']:
        visitor_data['ip_records'][today] = []
    if ip not in visitor_data['ip_records'][today]:
        visitor_data['ip_records'][today].append(ip)

    save_visitor_data(visitor_data)
    return visitor_data['total_visits']

def send_daily_report(visitor_data, today):
    """
    發送每日訪客報告
    """
    ip_locations = []
    for ip in visitor_data['ip_records'].get(today, []):
        try:
            response = requests.get(f'http://ip-api.com/json/{ip}')
            location = response.json()
            ip_locations.append(
                f"IP: {ip}\n"
                f"Location: {location.get('city', 'Unknown')}, {location.get('country', 'Unknown')}\n"
                f"Organization: {location.get('org', 'Unknown')}
            )
        except:
            ip_locations.append(f"IP: {ip}, Location: Unknown")

    email_content = (
        f"Date: {today}\n"
        f"Today's Visits: {visitor_data['daily_visits'].get(today, 0)}\n"
        f"Visitor IP Sources:\n"
        f"{''.join(ip_locations)}"
    )

    msg = MIMEMultipart()
    msg['From'] = "sender@example.com"
    msg['To'] = "receiver@example.com"
    msg['Subject'] = f'Resume Website Visit Report - {today}'
    msg.attach(MIMEText(email_content, 'plain'))

    # TODO: 實作郵件發送功能
    pass

def load_profile_image():
    """
    載入個人照片
    """
    try:
        image_path = "PHOTO.jpg"
        if Path(image_path).exists():
            return Image.open(image_path)
        return None
    except Exception as e:
        st.error(f"Error loading profile image: {e}")
        return None
