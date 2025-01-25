import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from statsmodels.tsa.seasonal import seasonal_decompose
import datetime
import json
import os
from PIL import Image
import matplotlib.pyplot as plt
import matplotlib as mpl
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
from datetime import datetime
import schedule
import threading
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import cross_val_predict
from sklearn.linear_model import LinearRegression
from config import (
    PAGE_CONFIG,
    CHART_CONFIG,
    DB_CONFIG,
    MAIL_CONFIG,
    MODEL_CONFIG
)

from utils import visitor_tracker
# pip freeze > requirements.txt
# .\venv\Scripts\activate.ps1
# cd "D:\curso\streamlit\resume"
# streamlit run 01_🎈_resume_app.py
#resume-zgurc7bvpu98gu2n3u2uqw.streamlit.app

# 訪問者追蹤函數
def get_visitor_ip():
    """獲取訪問者IP地址"""
    try:
        response = requests.get('https://api.ipify.org?format=json')
        return response.json()['ip']
    except:
        return '未知'

def load_visitor_data():
    try:
        with open('visitor_data.json', 'r') as f:
            return json.load(f)
    except:
        return {'total_visits': 0, 'daily_visits': {}, 'ip_records': {}}

def save_visitor_data(data):
    with open('visitor_data.json', 'w') as f:
        json.dump(data, f)

def update_visitor_count():
    visitor_data = load_visitor_data()
    today = datetime.now().strftime('%Y-%m-%d')
    ip = get_visitor_ip()
    
    # 更新總訪問量
    visitor_data['total_visits'] += 1
    
    # 更新每日訪問
    if today not in visitor_data['daily_visits']:
        visitor_data['daily_visits'][today] = 0
    visitor_data['daily_visits'][today] += 1
    
    # 記錄IP
    if today not in visitor_data['ip_records']:
        visitor_data['ip_records'][today] = []
    if ip not in visitor_data['ip_records'][today]:
        visitor_data['ip_records'][today].append(ip)
    
    save_visitor_data(visitor_data)
    
    # 檢查是否需要發送報告
    current_time = datetime.now()
    if current_time.hour == 20 and current_time.minute == 0:
        send_daily_report(visitor_data, today)
    
    return visitor_data['total_visits']

def send_daily_report(visitor_data, today):
    # 獲取IP地理位置資訊
    ip_locations = []
    for ip in visitor_data['ip_records'].get(today, []):
        try:
            response = requests.get(f'http://ip-api.com/json/{ip}')
            location = response.json()
            ip_locations.append(
                f"IP: {ip}\n"
                f"位置: {location.get('city', '未知')}, {location.get('country', '未知')}\n"
                f"組織: {location.get('org', '未知')}"
            )
        except:
            ip_locations.append(f"IP: {ip}, 位置: 未知")
    
    # 構建郵件內容
    email_content = (
        f"日期: {today}\n"
        f"今日訪問量: {visitor_data['daily_visits'].get(today, 0)}\n"
        f"訪問IP來源:\n"
        f"{''.join(ip_locations)}"
    )
    
    # 發送郵件
    msg = MIMEMultipart()
    msg['From'] = 'Teriyaki0730@gmail.com'
    msg['To'] = 'lauandhang@yahoo.com.tw'
    msg['Subject'] = f'簡歷網站訪問統計報告 - {today}'
    msg.attach(MIMEText(email_content, 'plain'))

# 添加氣體流量監控和AI預測功能
@st.cache_data(ttl=3600)
def generate_gas_data():
    # 減少生成的資料量
    dates = pd.date_range(start='2023-01-01', periods=1000, freq='H')  # 只生成1000筆資料
    n_samples = len(dates)
    
    base_flow = {
        'Ar': 100,
        'N2': 50,
        'O2': 25,
        'CF4': 30,
        'SF6': 15
    }
    
    data = pd.DataFrame({'timestamp': dates})
    for gas, base in base_flow.items():
        periodic = np.sin(np.linspace(0, 8*np.pi, n_samples)) * base * 0.1
        noise = np.random.normal(0, base * 0.05, n_samples)
        trend = np.linspace(0, base * 0.05, n_samples)
        data[f'{gas}_flow'] = base + periodic + noise + trend
    
    return data

# @st.cache
@st.cache_data(ttl=3600)  # 設置1小時的快取時間
def train_gas_model(data):
    # 限制資料量
    if len(data) > 1000:
        data = data.tail(1000)  # 只使用最近1000筆資料
        
    features = ['hour', 'day_of_week', 'month']
    data['hour'] = data['timestamp'].dt.hour
    data['day_of_week'] = data['timestamp'].dt.dayofweek
    data['month'] = data['timestamp'].dt.month
    
    models = {}
    scalers = {}
    gas_columns = [col for col in data.columns if '_flow' in col]
    
    for gas in gas_columns:
        X = data[features].values
        y = data[gas].values
        
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        model = RandomForestRegressor(n_estimators=50, random_state=42)  # 減少樹的數量
        model.fit(X_scaled, y)
        
        models[gas] = model
        scalers[gas] = scaler
    
    return models, scalers

def predict_gas_flow(models, scalers, hours=24):
    future_times = pd.date_range(
        start=datetime.now(),
        periods=hours,
        freq='H'
    )
    
    future_data = pd.DataFrame({
        'hour': future_times.hour,
        'day_of_week': future_times.dayofweek,
        'month': future_times.month
    })
    
    predictions = pd.DataFrame({'timestamp': future_times})
    for gas, model in models.items():
        X = future_data.values
        X_scaled = scalers[gas].transform(X)
        predictions[gas] = model.predict(X_scaled)
    
    return predictions

# 啟動定時任務
def run_schedule():
    schedule.run_pending()
    
# 改用 Streamlit 的 scheduled_rerun 來處理定時任務
if 'last_run' not in st.session_state:
    st.session_state.last_run = datetime.now()

current_time = datetime.now()
if current_time.hour == 20 and (current_time - st.session_state.last_run).seconds >= 3600:
    send_daily_report(load_visitor_data(), current_time.strftime('%Y-%m-%d'))
    st.session_state.last_run = current_time

# 設置中文字體
plt.rcParams['font.sans-serif'] = CHART_CONFIG["font_family"]
plt.rcParams['axes.unicode_minus'] = False
mpl.rcParams['font.family'] = CHART_CONFIG["font_family"]

# 全局樣式
st.markdown("""
<style>
    /* 主題設定 */
    :root {
        --primary-color: #4A90E2;
        --secondary-color: #50E3C2;
        --background-color: #FFFFFF;
        --text-color: #1A1F36;
        --highlight-color: #2C7BE5;
    }
    
    /* 深色主題 */
    [data-theme="light"] {
        --background-color: #0E1117;
        --text-color: #E0E0E0;
    }
    
    /* 導航菜單樣式 */
    .stRadio > label {
        font-size: 1.8em !important;
        font-weight: 600 !important;
    }
        
    
        /* 聯繫方式     */
    .stRadio > label {
        font-size: 2em !important;
        font-weight: 600 !important;
    }
            
    /* 技能標籤樣式 */
    .tech-badge {
        background: linear-gradient(45deg, var(--primary-color), var(--secondary-color));
        padding: 15px 30px;
        border-radius: 25px;
        margin: 10px;
        display: inline-block;
        color: white;
        font-size: 5em !important;
        font-weight: 600;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    /* 技能樹樣式 */
    .skill-tree {
        margin: 20px 0;
        padding: 20px;
        background: rgba(255,255,255,0.1);
        border-radius: 15px;
    }
    
    .skill-tree-item {
        font-size: 2em !important;
        margin: 10px 0;
        padding-left: 30px;
    }
    
    /* 經歷卡片樣式 */
    .experience-card {
        padding: 25px;
        margin: 15px 0;
        border-radius: 15px;
        background: rgba(255,255,255,0.1);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    
    .experience-card h3 {
        font-size: 4em !important;
        color: var(--primary-color);
    }
    
    .experience-card h4 {
        font-size: 3em !important;
    }
    
    .experience-card li {
        font-size: 1.8em !important;
    }
    
    /* 訪問計數器樣式 */
    .visitor-counter {
        position: fixed;
        top: 100px;
        right: 20px;
        background: linear-gradient(45deg, var(--primary-color), var(--secondary-color));
        padding: 10px 20px;
        border-radius: 30px;
        color: white;
        font-size: 1.6em !important;
        z-index: 1000;
    }
    
    /* 防複製樣式 */
    * {
        user-select: none !important;
        -webkit-user-select: none !important;
        -moz-user-select: none !important;
        -ms-user-select: none !important;
    }
    
    /* 水印樣式 */
    .watermark {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        pointer-events: none;
        background: repeating-linear-gradient(
            45deg,
            rgba(74, 144, 226, 0.1),
            rgba(74, 144, 226, 0.1) 10px,
            rgba(80, 227, 194, 0.1) 10px,
            rgba(80, 227, 194, 0.1) 20px
        );
        z-index: 9999;
    }
    
    /* 標題和文本樣式 */
    h1 {
        font-size: 3em !important;
    }
    
    h2 {
        font-size: 2.5em !important;
    }
    
    h3 {
        font-size: 2.2em !important;
    }
    
    p, li {
        font-size: 1.8em !important;
    }
    
    /* 圖表標題樣式 */
    .plotly .gtitle {
        font-size: 2em !important;
    }
</style>

<script>
    // 防複製功能
    document.addEventListener('contextmenu', e => e.preventDefault());
    document.addEventListener('keydown', e => {
        if (e.ctrlKey || e.keyCode === 44) e.preventDefault();
    });
    
    // 添加水印
    window.onload = function() {
        const watermark = document.createElement('div');
        watermark.className = 'watermark';
        document.body.appendChild(watermark);
    };
</script>
""", unsafe_allow_html=True)

# 自定義 CSS 樣式
st.markdown("""
<style>
    /* 調整選擇框大小 */
    .stSelectbox {
        min-width: 300px !important;
    }
    
    .stSelectbox > div {
        min-height: 45px !important;
    }
    
    /* 調整容器寬度 */
    .element-container, .stMarkdown {
        width: 100% !important;
        max-width: 100% !important;
    }
    
    /* 調整卡片樣式 */
    .skill-card, .experience-card {
        background-color: #ffffff;
        padding: 1.5rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 1rem 0;
        width: 100%;
    }
    
    /* 調整圖表容器 */
    .stPlotlyChart, .stPlot {
        min-height: 400px;
        width: 100% !important;
        background: white;
        padding: 1.5rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* 調整標題樣式 */
    h1, h2, h3 {
        margin: 1.5rem 0;
        color: #1e88e5;
    }
    
    /* 調整技能標籤樣式 */
    .tech-badge {
        display: inline-block;
        padding: 0.5rem 1rem;
        margin: 0.3rem;
        background-color: #f8f9fa;
        border-radius: 20px;
        font-size: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# 添加更多樣式
st.markdown("""
<style>
    /* 個人資料區塊樣式 */
    .profile-section {
        background: white;
        padding: 2rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 2rem;
    }
    
    .profile-section h1 {
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
        color: #1e88e5;
    }
    
    .profile-section h2 {
        font-size: 1.5rem;
        color: #424242;
        margin-bottom: 1.5rem;
    }
    
    /* 技能標籤容器 */
    .tech-badges {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
        margin: 1rem 0;
    }
    
    /* 聯繫方式樣式 */
    .contact-section {
        margin-top: 1.5rem;
        padding: 1rem;
        background: #f8f9fa;
        border-radius: 8px;
    }
    
    .contact-section p {
        margin: 0.5rem 0;
        font-size: 1.1rem;
        color: #424242;
    }
    
    /* 工作經驗區塊樣式 */
    .experience-section {
        margin-top: 2rem;
    }
    
    .experience-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 1.5rem;
    }
    
    .experience-card h3 {
        color: #1e88e5;
        margin-bottom: 0.5rem;
    }
    
    .experience-card h4 {
        color: #424242;
        margin: 0.5rem 0;
    }
    
    .experience-card li {
        font-size: 1.8em !important;
    }
    
    /* 訪問計數器樣式 */
    .visitor-counter {
        position: fixed;
        top: 100px;
        right: 20px;
        background: linear-gradient(45deg, var(--primary-color), var(--secondary-color));
        padding: 10px 20px;
        border-radius: 30px;
        color: white;
        font-size: 1.6em !important;
        z-index: 1000;
    }
    
    /* 防複製樣式 */
    * {
        user-select: none !important;
        -webkit-user-select: none !important;
        -moz-user-select: none !important;
        -ms-user-select: none !important;
    }
    
    /* 水印樣式 */
    .watermark {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        pointer-events: none;
        background: repeating-linear-gradient(
            45deg,
            rgba(74, 144, 226, 0.1),
            rgba(74, 144, 226, 0.1) 10px,
            rgba(80, 227, 194, 0.1) 10px,
            rgba(80, 227, 194, 0.1) 20px
        );
        z-index: 9999;
    }
    
    /* 標題和文本樣式 */
    h1 {
        font-size: 3em !important;
    }
    
    h2 {
        font-size: 2.5em !important;
    }
    
    h3 {
        font-size: 2.2em !important;
    }
    
    p, li {
        font-size: 1.8em !important;
    }
    
    /* 圖表標題樣式 */
    .plotly .gtitle {
        font-size: 2em !important;
    }
</style>

<script>
    // 防複製功能
    document.addEventListener('contextmenu', e => e.preventDefault());
    document.addEventListener('keydown', e => {
        if (e.ctrlKey || e.keyCode === 44) e.preventDefault();
    });
    
    // 添加水印
    window.onload = function() {
        const watermark = document.createElement('div');
        watermark.className = 'watermark';
        document.body.appendChild(watermark);
    };
</script>
""", unsafe_allow_html=True)

# 添加選項欄位樣式
st.markdown("""
<style>
    /* 選項欄位樣式 */
    .tech-list {
        list-style: none;
        padding: 0;
        margin: 1rem 0;
    }
    
    .tech-list li {
        background-color: #f8f9fa;
        margin: 0.5rem 0;
        padding: 0.8rem 1rem;
        border-radius: 8px;
        color: #1e88e5;
        font-weight: 500;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        transition: all 0.3s ease;
    }
    
    .tech-list li:hover {
        background-color: #e3f2fd;
        transform: translateX(5px);
    }
    
    .tech-category {
        font-size: 1.2rem;
        color: #424242;
        margin: 1.5rem 0 1rem 0;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)

# 側邊欄設置
with st.sidebar:
    st.markdown("### 🎯 導航菜單")
    page = st.radio(
        "",
        ["📊 個人總覽", "💼 專業經歷", "🎓 教育背景", "🛠️ 技能專長", 
         "🌟 個人特質", "📈 專案展示", "🔬 專案分析"],
        key="navigation_menu"
    )
    
    st.markdown("---")
    
    # 語言切換
    st.markdown("### 🌐 語言切換")
    language = st.selectbox(
        "",
        ["繁體中文", "English"],
        key="language_selector",
        help="選擇顯示語言"
    )
    
    st.markdown("---")
    
    # 主題設置
    st.markdown("### 🎨 主題設置")
    theme = st.selectbox(
        "",
        ["淺色主題", "深色主題"],
        key="theme_selector",
        help="選擇顯示主題"
    )
    
    # 主題切換邏輯
    if theme == "深色主題":
        st.markdown("""
        <style>
            /* 深色主題樣式 */
            :root {
                --primary-color: #4A90E2;
                --background-color: #1E1E1E;
                --text-color: #E0E0E0;
            }
            
            .stApp {
                background-color: var(--background-color);
                color: var(--text-color);
            }
            
            .stSelectbox select {
                background-color: var(--background-color);
                color: var(--text-color);
            }
        </style>
        """, unsafe_allow_html=True)

# 更新訪問計數
total_visits = visitor_tracker.update_visitor_count()

# 顯示訪問計數器
visitor_counter = f"""
<div class='visitor-counter'>
    👀 訪問量: {total_visits}
</div>
"""
st.markdown(visitor_counter, unsafe_allow_html=True)

# 檢查是否需要發送每日報告
if 'last_run' not in st.session_state:
    st.session_state.last_run = datetime.now()

current_time = datetime.now()
if (current_time - st.session_state.last_run).days >= 1:
    visitor_tracker.send_daily_report()
    st.session_state.last_run = current_time

# 添加標題
st.markdown("""
<h1 style='text-align: center; color: var(--primary-color);'>
    劉晉亨的個人簡歷 | Patrick Liou Resume
</h1>
""", unsafe_allow_html=True)

st.markdown("""
<div style='background-color: #FFE873; padding: 1rem; border-radius: 8px; margin-bottom: 1rem;'>
    若需英文面試或加班請 pass | If you need an interview in English or work overtime, please pass
</div>
""", unsafe_allow_html=True)

# 圖片處理函數
def load_profile_image():
    try:
        img_path = "PHOTO.jpg"
        if img_path.exists():
            return Image.open(img_path)
        else:
            st.warning(f"無法找到圖片：{img_path}")
            return None
    except Exception as e:
        st.warning(f"載入圖片時發生錯誤：{str(e)}")
        return None

# 主要內容區域
if page == "📊 個人總覽":
    col1, col2 = st.columns([1, 2])
    
    with col1:
        profile_image = load_profile_image()
        if profile_image:
            st.image(profile_image, width=300, use_column_width=True, output_format="JPEG", clamp=True)
    
    with col2:
        st.markdown("""
        <div class='profile-section'>
            <h1>劉晉亨 <span class='highlight'>Patrick Liou</span></h1>
            <h2>🤖 資深製程整合工程師 | AI與大數據專家</h2>
            
            <div class='skill-card'>
                <h3>🎯 核心專長</h3>
                <div class='tech-badges'>
                    <span class='tech-badge'>📍大數據分析</span>
                    <span class='tech-badge'>📱機器學習</span>
                    <span class='tech-badge'>📧深度學習</span>
                    <span class='tech-badge'>📍製程整合</span>
                    <span class='tech-badge'>📱六標準差</span>
                    <span class='tech-badge'>📧智能工廠</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # 添加工作經驗部分
    st.markdown("""
    <div class='experience-section'>
        <h2>工作經驗</h2>
        
        <div class='experience-card'>
            <h3>聯電 (UMC)</h3>
            <p class='highlight'>2015年1月 - 至今</p>
            <h4>資深製程整合工程師</h4>
            <ul>
                <li>負責新製程技術導入與優化</li>
                <li>建立智能預警系統，提升良率15%</li>
                <li>開發自動化數據分析工具</li>
            </ul>
        </div>
        
        <div class='experience-card'>
            <h3>台積電 (TSMC)</h3>
            <p class='highlight'>2014年3月 - 2014年12月</p>
            <h4>設備工程師</h4>
            <ul>
                <li>負責設備維護與效能優化</li>
                <li>參與新世代製程開發</li>
            </ul>
        </div>
    </div>
    """, unsafe_allow_html=True)

elif page == "💼 專業經歷":
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        <div class='experience-card'>
            <h3>群創光電 (Innolux Corporation)</h3>
            <p class='highlight'>2014年12月 - 至今</p>
            <h4>製程工程師 / Team Leader</h4>
            <ul>
                <li>領導智能工廠專案，成功導入工業4.0解決方案，顯著提升生產效率</li>
                <li>開發YOLOv4缺陷檢測模型，縮短反饋時間並提高缺陷檢出率60%</li>
                <li>主導3項六標準差專案，優化製程參數並降低產品次品率，節省2100萬台幣/年</li>
            </ul>
        </div>
        
        <div class='experience-card'>
            <h3>台積電 (tsmc) </h3>S
            <p class='highlight'>2014年3月 - 2014年12月</p>
            <h4>設備工程師</h4>
            <ul>
                <li>優化製程工具參數，提升產量與穩定性，缺陷率改善4%</li>
                <li>減少系統崩潰率至5%，提升設備可用性與產能利用率</li>
            </ul>
        </div>

        <div class='experience-card'>
            <h3>台灣水泥 (Taiwan Cement Corp)</h3>
            <p class='highlight'>2013年9月 - 2014年3月</p>
            <h4>儲備幹部(MA)</h4>
            <ul>
                <li>負責生產流程監控與優化，縮短瓶頸工序時間15%</li>
                <li>協助開發新PDA系統，提高製程自動化程度</li>
            </ul>
        </div>

        <div class='experience-card'>
            <h3>群創光電 (Innolux Corporation)</h3>
            <p class='highlight'>2010年1月 - 2013年9月</p>
            <h4>製程工程師</h4>
            <ul>
                <li>協助建置新廠，完成試量產並縮短建廠時程30%</li>
                <li>分析設備故障原因並提供解決方案，提高設備稼動率25%</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    with col2:    
        # 添加雷達圖
        skills = ['領導能力', '技術創新', '專案管理', '問題解決', '團隊協作']
        values = [95, 90, 92, 88, 93]
        
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=skills,
            fill='toself',
            name='核心能力'
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100]
                )),
            showlegend=False,
            title={
                'text': '核心能力評估',
                'font': {'size': 24}
            },
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    
        st.markdown("### 職涯發展歷程")
        st.markdown("""
        ```mermaid
        graph TD
            A[化工背景] --> B[製程整合]
            B --> C[設備優化]
            C --> D[智能製造]
            D --> E[AI應用開發]
            
            style A fill:#f9f,stroke:#333,stroke-width:4px
            style B fill:#bbf,stroke:#333,stroke-width:4px
            style C fill:#ddf,stroke:#333,stroke-width:4px
            style D fill:#fdd,stroke:#333,stroke-width:4px
            style E fill:#dfd,stroke:#333,stroke-width:4px
        ```
        """)
        
        st.markdown("### 核心能力成長")
        st.markdown("""
        ```mermaid
        graph TD
            A[製程知識] --> B[數據分析]
            B --> C[AI技術]
            A --> D[良率提升]
            D --> E[智能製造]
            C --> E
            
            style A fill:#f9f,stroke:#333,stroke-width:4px
            style B fill:#bbf,stroke:#333,stroke-width:4px
            style C fill:#ddf,stroke:#333,stroke-width:4px
            style D fill:#fdd,stroke:#333,stroke-width:4px
            style E fill:#dfd,stroke:#333,stroke-width:4px
        ```
        """)

elif page == "🎓 教育背景":
    col1, col2 = st.columns([2, 1])
    
    with col1:   
        st.markdown("""
        <div class='education-card' style='font-size: 1.8em;'>
            <h3>國立交通大學</h3>
            <p class='highlight'>2015年9月 - 2018年1月</p>
            <h4>管理科學碩士（MBA）</h4>
            <ul>
                <li>專業課程：數據分析與商業智慧、營運管理與策略規劃、專案管理與領導力</li>
                <li>研究方向：製造業數位轉型與AI應用</li>
            </ul>
        </div>

        <div class='education-card' style='font-size: 1.8em;'>
            <h3>國立台灣大學</h3>
            <p class='highlight'>2015年3月 - 2017年6月</p>
            <h4>持續教育法律課程</h4>
            <ul>
                <li>專業課程：商業法律、智慧財產權、勞動法規</li>
                <li>研究方向：科技產業法律實務應用</li>
            </ul>
        </div>

        <div class='education-card' style='font-size: 1.8em;'>
            <h3>國立台灣科技大學</h3>
            <p class='highlight'>2006年9月 - 2008年6月</p>
            <h4>化學工程碩士</h4>
            <ul>
                <li>專業課程：化工單元操作、反應工程、程序控制</li>
                <li>研究方向：製程最佳化與控制</li>
            </ul>
        </div>

        <div class='education-card' style='font-size: 1.8em;'>
            <h3>逢甲大學</h3>
            <p class='highlight'>2002年9月 - 2006年6月</p>
            <h4>化學工程學士</h4>
            <ul>
                <li>專業課程：化工原理、物理化學、化工熱力學</li>
                <li>專題研究：製程監控與自動化</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
    
    
    with col2:
        # 添加知識領域分布雷達圖
        knowledge_areas = ['化工製程', '數據分析', '管理實務', '法律知識', '智能製造']
        knowledge_scores = [95, 90, 85, 80, 92]
        
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=knowledge_scores,
            theta=knowledge_areas,
            fill='toself',
            name='知識領域分布'
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100]
                )),
            showlegend=False,
            title={
                'text': '知識領域分布',
                'font': {'size': 24}
            },
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # 添加學習進展時間線
        st.markdown("""
        ### 學習歷程
        ```mermaid
        graph TD
            A[逢甲大學<br>化工學士] --> B[台科大<br>化工碩士]
            B --> C[台大<br>法律課程]
            C --> D[交大<br>管理碩士]
            
            style A fill:#f9f,stroke:#333,stroke-width:4px
            style B fill:#bbf,stroke:#333,stroke-width:4px
            style C fill:#ddf,stroke:#333,stroke-width:4px
            style D fill:#dfd,stroke:#333,stroke-width:4px
        ```
        """)
        
        # 添加專業技能評分
        st.markdown("### 專業技能評分")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 化工專業")
            st.progress(0.95)
            st.markdown("#### 數據分析")
            st.progress(0.90)
        
        with col2:
            st.markdown("#### 法律知識")
            st.progress(0.85)
            st.markdown("#### 管理能力")
            st.progress(0.88)

elif page == "🛠️ 技能專長":
    st.markdown("""
    <div class='tech-section'>
        <h3 class='tech-category'>🔧 技術工具</h3>
        <ul class='tech-list'>
            <li>🐍 Python: Pandas, NumPy, Scikit-learn</li>
            <li>🧠 深度學習: TensorFlow, PyTorch, YOLOv4</li>
            <li>🤖 AutoML與LLM應用開發</li>
        </ul>
        
    <div class='tech-section'>
        <h3 class='tech-category'>💡 製程專長</h3>
        <ul class='tech-list'>
            <li>🔬 半導體製程整合與優化：協助制定製程策略，減少生產瓶頸。</li>
            <li>📊 製程參數分析與調校：使用數據分析工具（如DOE）進行精準調校。</li>
            <li>🎯 良率提升與異常排除：追蹤缺陷根因，提升生產效能。</li>
            <li>🔧 設備監控與預防保養：結合IoT技術進行設備實時監控。</li>
        </ul>

    <div class='tech-section'>
        <h3 class='tech-category'>📈 數據分析</h3>
        <ul class='tech-list'>
            <li>📊 統計分析與實驗設計 (DOE)：制定有效實驗計畫以探索最佳製程參數。</li>
            <li>📉 製程能力分析 (SPC/CpK)：分析製程穩定性與能力，確保合格率。</li>
            <li>🎯 六標準差 (6-Sigma) 專案：實施數據驅動的改進專案，降低缺陷率。</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # 添加技能評分展示
    st.markdown("### 💫 專業技能評分")
    
    # 創建技能數據
    skills_data = {
        "製程整合能力": {
            "半導體/面板製程": 95,
            "良率分析": 92,
            "缺陷改善": 90,
            "製程優化": 88
        },
        "技術能力": {
            "Python開發": 85,
            "數據分析": 90,
            "機器學習": 82, 
            "自動化開發": 85
        },
        "管理能力": {
            "專案管理": 88,
            "團隊領導": 85,
            "問題解決": 92,
            "溝通協調": 90
        }
    }
    
    # 使用列顯示技能評分
    cols = st.columns(len(skills_data))
    for col, (category, skills) in zip(cols, skills_data.items()):
        with col:
            st.markdown(f"#### {category}")
            for skill, level in skills.items():
                st.markdown(f"**{skill}**")
                st.progress(level/100)

elif page == "🌟 個人特質":
    st.markdown("""
    <style>
    .personality-container {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 1.5rem;
        padding: 1rem;
    }
    .personality-item {
        background: #ffffff;
        border-radius: 8px;
        padding: 1.5rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    .personality-item h3 {
        color: #1e88e5;
        margin-bottom: 1rem;
        font-size: 1.3rem;
    }
    .personality-item ul {
        list-style-type: none;
        padding-left: 0;
    }
    .personality-item li {
        margin-bottom: 0.5rem;
        padding-left: 1.5rem;
        position: relative;
    }
    .personality-item li:before {
        content: "•";
        color: #1e88e5;
        position: absolute;
        left: 0;
    }
    </style>
    
    <div class="personality-container">
        <div class="personality-item">
            <h3>🎯 領導力與團隊合作</h3>
            <ul>
                <li>具備優秀的團隊領導能力</li>
                <li>良好的溝通技巧</li>
                <li>具有同理心</li>
            </ul>
        </div>
        <div class="personality-item">
            <h3>🚀 學習與創新</h3>
            <ul>
                <li>持續學習的熱情</li>
                <li>創新思維</li>
                <li>解決問題的能力</li>
            </ul>
        </div>
        <div class="personality-item">
            <h3>💡 專業素養</h3>
            <ul>
                <li>高度責任感</li>
                <li>注重細節</li>
                <li>追求卓越</li>
            </ul>
        </div>
        <div class="personality-item">
            <h3>🤝 團隊精神</h3>
            <ul>
                <li>良好的團隊合作</li>
                <li>積極主動</li>
                <li>樂於分享</li>
            </ul>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 添加能力評分
    st.markdown("### 🎯 能力評分")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 領導力")
        st.progress(0.85)
        st.markdown("#### 創新力")
        st.progress(0.90)
        
    with col2:
        st.markdown("#### 執行力")
        st.progress(0.95)
        st.markdown("#### 學習力")
        st.progress(0.92)

elif page == "📈 專案展示":
    st.markdown("## PCA 分析結果")
    
    # 生成更明顯的分群數據
    n_samples = 150
    np.random.seed(42)
    
    # 生成三個明顯分開的群集
    cluster1 = np.random.normal(loc=[4, 4], scale=0.5, size=(n_samples//3, 2))
    cluster2 = np.random.normal(loc=[-4, -4], scale=0.5, size=(n_samples//3, 2))
    cluster3 = np.random.normal(loc=[4, -4], scale=0.5, size=(n_samples//3, 2))
    
    # 合併數據
    X = np.vstack([cluster1, cluster2, cluster3])
    
    # 添加群集標籤
    labels = np.array(['製程A'] * (n_samples//3) + ['製程B'] * (n_samples//3) + ['製程C'] * (n_samples//3))
    
    # 創建數據框
    pca_df = pd.DataFrame(X, columns=['特徵1', '特徵2'])
    pca_df['群集'] = labels
    
    # 繪製 PCA 散點圖
    fig = px.scatter(pca_df, x='特徵1', y='特徵2', 
                    color='群集',
                    title='製程參數群集分析',
                    color_discrete_sequence=['#1f77b4', '#ff7f0e', '#2ca02c'],
                    labels={'特徵1': '主成分 1', 
                           '特徵2': '主成分 2',
                           '群集': '製程類型'})
    
    fig.update_layout(
        title_font_size=24,
        font=dict(size=16),
        legend=dict(
            font=dict(size=16),
            title_font=dict(size=16)
        ),
        xaxis=dict(
            title_font=dict(size=16),
            tickfont=dict(size=14)
        ),
        yaxis=dict(
            title_font=dict(size=16),
            tickfont=dict(size=14)
        ),
        plot_bgcolor='white',
        showlegend=True
    )
    
    fig.update_traces(
        marker=dict(size=12, 
                   line=dict(width=1, color='white')),
        selector=dict(mode='markers')
    )
    
    st.plotly_chart(fig)

elif page == "🔬 專案分析":
    st.markdown("# 進階數據分析")
    
    # 直接顯示所有分析內容，移除下拉選單
    st.markdown("""
    ## 製程分析
    - 即時監控與分析製程參數
    - 預測性維護與異常檢測
    - 品質控制與優化
    """)
    
    # 生成製程數據
    process_data = pd.DataFrame(np.random.randn(500, 3), columns=['溫度', '壓力', '品質'])
    
    # 相關性熱圖
    corr = process_data.corr()
    fig = px.imshow(corr, 
                   title='參數相關性矩陣',
                   color_continuous_scale='RdBu',
                   labels={'color': '相關係數'})
    fig.update_layout(
        title_font_size=24,
        font=dict(size=16)
    )
    st.plotly_chart(fig)
    
    # 時間序列分析
    st.markdown("## 時間序列分析")
    dates = pd.date_range(start='2024-01-01', periods=100)
    ts_data = pd.DataFrame({
        '日期': dates,
        '溫度': np.random.normal(25, 2, 100) + np.sin(np.linspace(0, 10, 100)) * 5,
        '壓力': np.random.normal(100, 5, 100) + np.cos(np.linspace(0, 10, 100)) * 10
    })
    
    fig = px.line(ts_data, x='日期', y=['溫度', '壓力'],
                 title='製程參數趨勢分析')
    fig.update_layout(
        title_font_size=24,
        font=dict(size=16),
        legend=dict(font=dict(size=16))
    )
    st.plotly_chart(fig)
    
    # 品質控制圖
    st.markdown("## 品質控制")
    quality_data = pd.DataFrame({
        '樣本': range(1, 51),
        '測量值': np.random.normal(100, 2, 50)
    })
    
    ucl = quality_data['測量值'].mean() + 3 * quality_data['測量值'].std()
    lcl = quality_data['測量值'].mean() - 3 * quality_data['測量值'].std()
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=quality_data['樣本'], y=quality_data['測量值'],
                            mode='lines+markers', name='測量值'))
    fig.add_hline(y=ucl, line_dash="dash", line_color="red", name='UCL')
    fig.add_hline(y=lcl, line_dash="dash", line_color="red", name='LCL')
    fig.update_layout(
        title='品質控制圖',
        title_font_size=24,
        font=dict(size=16),
        xaxis_title="樣本編號",
        yaxis_title="測量值"
    )
    st.plotly_chart(fig)

# 頁腳
st.markdown("""
---
<div style='text-align: center; color: var(--text-color); padding: 20px;'>
    2025 劉晉亨 | AI Enhanced Resume | Built with ❤️ and ❤️
</div>
""", unsafe_allow_html=True)
