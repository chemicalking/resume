import streamlit as st
import pandas as pd
from PIL import Image
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import os
from pathlib import Path
import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
import requests
from datetime import datetime, time
import schedule
import threading
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cross_decomposition import PLSRegression
from sklearn.model_selection import cross_val_predict
import time as tm  # 使用別名避免與 datetime.time 衝突
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
# pip freeze > requirements.txt
# .\new_venv\Scripts\activate.ps1
# cd "D:\curso\streamlit\resume"
# streamlit run 01_🎈_resume_app.py
#resume-zgurc7bvpu98gu2n3u2uqw.streamlit.app



# 設置 Matplotlib 支持中文
plt.rcParams['font.family'] = ['SimHei']  # 使用黑體字體
plt.rcParams['axes.unicode_minus'] = False  # 避免負號顯示問題




# 访问统计函数
def get_visitor_ip():
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
    current_time = datetime.now().time()
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
    msg['From'] = 'your_email@example.com'
    msg['To'] = 'lauandhang@yahoo.com.tw'
    msg['Subject'] = f'簡歷網站訪問統計報告 - {today}'
    msg.attach(MIMEText(email_content, 'plain'))

# 添加气体流量监控和AI预测功能
def generate_gas_data():
    dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='H')
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
@st.cache
def train_gas_model(data):
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
        
        model = RandomForestRegressor(n_estimators=100, random_state=42)
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

# 启动定时任务
def run_schedule():
    while True:
        schedule.run_pending()
        time.sleep(60)

# 设置每天20:00发送报告
schedule.every().day.at("20:00").do(lambda: send_daily_report(load_visitor_data(), datetime.now().strftime('%Y-%m-%d')))
threading.Thread(target=run_schedule, daemon=True).start()

# 页面配置
st.set_page_config(
    page_title="劉晉亨的個人簡歷 | Patrick Liou Resume",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 设置全局样式
st.markdown("""
<style>
    /* 主题设置 */
    :root {
        --primary-color: #4A90E2;
        --secondary-color: #50E3C2;
        --background-color: #FFFFFF;
        --text-color: #1A1F36;
        --highlight-color: #2C7BE5;
    }
    
    /* 深色主题 */
    [data-theme="light"] {
        --background-color: #0E1117;
        --text-color: #E0E0E0;
    }
    
    /* 导航菜单样式 */
    .stRadio > label {
        font-size: 1.8em !important;
        font-weight: 600 !important;
    }
        
    
        /* 聯繫方式     */
    .stRadio > label {
        font-size: 2em !important;
        font-weight: 600 !important;
    }
            
    /* 技能标签样式 */
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
    
    /* 技能树样式 */
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
    
    /* 经历卡片样式 */
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
    
    /* 访问计数器样式 */
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
    
    /* 防复制样式 */
    * {
        user-select: none !important;
        -webkit-user-select: none !important;
        -moz-user-select: none !important;
        -ms-user-select: none !important;
    }
    
    /* 水印样式 */
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
    
    /* 标题和文本样式 */
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
    
    /* 图表标题样式 */
    .plotly .gtitle {
        font-size: 2em !important;
    }
</style>

<script>
    // 防复制功能
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

# 在侧边栏添加主题选择
with st.sidebar:
    st.markdown("### 🎯 導航菜單")
    page = st.radio(
        "",
        ["📊 個人總覽", "💼 專業經歷", "🎓 教育背景", "🛠️ 技能專長", "📈 專案展示", "🌟 個人特質"],
        index=0
    )
    
    st.markdown("---")
    st.markdown("### 🌐 語言切換")
    language = st.selectbox("", ["繁體中文", "English"])
    
    st.markdown("---")
    st.markdown("### 🎨 主題設置")
    theme = st.selectbox("", ["淺色主題", "深色主題"], index=0)
    if theme == "深色主題":
        st.markdown("""
        <style>
            :root {
                --primary-color: #4A90E2;
                --secondary-color: #50E3C2;
                --background-color: #0E1117;
                --text-color: #E0E0E0;
                --highlight-color: #50E3C2;
            }
        </style>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    with st.expander("### 📬 聯繫方式", expanded=True):
        st.markdown("""
        
        <div class='contact-info'>
        <div class='email'>📧 lauandhang@yahoo.com.tw</div>
        <div class='email'>📱 0987-504-923</div>
        <div class='email'>📍 新北市</div>
        <div class='email'>💼 LinkedIn: Patrick Liou</div>
        <div class='email'> 💬 Line: Patrick.liou</div>
        <div class='email'>📱 WeChat: Patrick_Liou</div>
      
        """, unsafe_allow_html=True)

# 更新访问计数
total_visits = update_visitor_count()

# 显示访问计数器
visitor_counter = f"""
<div class='visitor-counter'>
    👀 訪問量: {total_visits}
</div>
"""
st.markdown(visitor_counter, unsafe_allow_html=True)

# 添加标题
st.markdown("""
<h1 style='text-align: center; color: var(--primary-color);'>
    劉晉亨的個人簡歷 | Patrick Liou Resume
</h1>
""", unsafe_allow_html=True)

st.markdown("""
<style>
.interview-notice {
    font-size: 24px; /* 字型大小 */
    color: red; /* 字型顏色 */
    background-color: yellow; /* 背景顏色 */
    font-weight: bold; /* 字型加粗 */
    padding: 10px; /* 內邊距 */
    border-radius: 5px; /* 圓角 */
    text-align: center; /* 文字居中 */
    border: 2px solid red; /* 紅色邊框 */
}
</style>
<div class='interview-notice'>
    若需英文面試或加班請 pass | If you need an interview in English or work overtime, please pass
</div>
""", unsafe_allow_html=True)

# 图片处理函数
def load_profile_image():
    try:
        img_path = Path("PHOTO.jpg")
        if img_path.exists():
            return Image.open(img_path)
        else:
            st.warning(f"無法找到圖片：{img_path}")
            return None
    except Exception as e:
        st.warning(f"載入圖片時發生錯誤：{str(e)}")
        return None

# 主要内容区域
if page == "📊 個人總覽":
    col1, col2 = st.columns([1, 2])
    
    with col1:
        profile_image = load_profile_image()
        st.image(profile_image, width=300, use_column_width=True, output_format="JPEG", clamp=True)
        
    with col2:
        st.markdown("""
        # 劉晉亨 <span class='highlight'>Patrick Liou</span>
        ## 🤖 資深薄膜製程工程師 | AI與大數據專家
        

        <div class='skill-card'>
            <h3>🎯 核心專長</h3>
            <span class='tech-badge'>📍大數據分析</span>
            <span class='tech-badge'>📱機器學習</span>
            <span class='tech-badge'>📧深度學習</span>
            <span class='tech-badge'>📍製程整合</span>
            <span class='tech-badge'>📱六標準差</span>
            <span class='tech-badge'>📧智能工廠</span>
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
            <h3>台積電 (TSMC)</h3>
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
        # 添加雷达图
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
            <h4>第25期法律學分班</h4>
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
        # 添加知识领域分布雷达图
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
        # 添加学习进展时间线
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
        
        # 添加专业技能评分
        st.markdown("### 專業技能評分")
        skills_data = {
            "化工專業": 95,
            "數據分析": 90,
            "法律知識": 85,
            "管理能力": 88,
            "研究創新": 92
        }
        
        for skill, score in skills_data.items():
            st.markdown(f"**{skill}**")
            st.progress(score/100)
            st.markdown(f"*{score}%*")

elif page == "🛠️ 技能專長":
    st.markdown("""
    <div class='skill-card'>
        <h3>大數據與人工智慧技術</h3>
        <ul>
            <li>大數據分析與機器學習
                <ul>
                    <li>Python: Pandas, NumPy, Scikit-learn</li>
                    <li>深度學習: TensorFlow, PyTorch, YOLOv4</li>
                    <li>AutoML與LLM應用開發</li>
                </ul>
            </li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # 添加技能评分展示
    st.markdown("### 💫 專業技能評分")
    
    # 创建技能数据
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
    
    # 使用列显示技能评分
    cols = st.columns(len(skills_data))
    for col, (category, skills) in zip(cols, skills_data.items()):
        with col:
            st.markdown(f"#### {category}")
            for skill, level in skills.items():
                st.markdown(f"**{skill}**")
                st.progress(level/100)




def show_project_progress():
    # 模擬數據
    projects = ["📊良率優化", "🔬氣體監控", "🤖製程分析",
                "🔧設備監控", "📈品質管制", "📧異常解析", "📈數據分析"]
    progress = [85, 90, 80, 75, 88, 70, 95]

    # 創建條形圖
    st.markdown("### 專案進度概覽")
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.barh(projects, progress, color='skyblue')
    ax.set_title("專案進度概覽", fontsize=14, pad=10)
    ax.set_xlabel("進度完成百分比 (%)")
    ax.set_xlim(0, 100)
    ax.grid(axis='x', linestyle='--', alpha=0.7)

    # 添加數據標籤
    for i, v in enumerate(progress):
        ax.text(v + 2, i, f"{v}%", va='center')

    # 顯示圖表
    st.pyplot(fig)

    # 使用 Streamlit 的原生表格顯示專案描述
    st.markdown("### 各專案簡介")
    
    # 創建數據框來顯示專案描述
    project_data = {
        "專案名稱": ["📊良率優化", "🔬氣體監控", "🤖製程分析", 
                    "🔧設備監控", "📈品質管制", "📧異常解析", "📈數據分析"],
        "專案描述": ["提升生產良率，降低成本。",
                    "實時監控氣體使用量，確保製程穩定。",
                    "分析生產製程，挖掘改善空間。",
                    "追蹤設備狀態，實現預防性維護。",
                    "運用統計方法監控產品品質。",
                    "快速定位並解決製程異常，通過結合即時監控與歷史數據進行問題診斷。",
                    "利用數據挖掘與可視化技術，提供決策支援。"]
    }
    
    # 使用 Streamlit 的 dataframe 顯示
    st.dataframe(project_data, hide_index=True)

if __name__ == "__main__":
    show_project_progress()

elif page == "🌟 個人特質":
    # 頁面標題
    st.markdown("## 🌟 個人特質")

    # 1. 專業特質圖片展示
    st.markdown("### 🎯 專業特質")
    st.write("以下是我的專業特質展示，結合圖片和數據更直觀地呈現：")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.image("https://via.placeholder.com/150", caption="製程整合經驗")
        st.markdown("- **紮實理論基礎**")
        st.markdown("- **持續學習新技術**")

    with col2:
        st.image("https://via.placeholder.com/150", caption="問題分析能力")
        st.markdown("- **系統性思維方式**")
        st.markdown("- **快速定位問題根因**")
        st.markdown("- **提供有效解決方案**")

    with col3:
        st.image("https://via.placeholder.com/150", caption="創新與解決方案")
        st.markdown("- **開發自動化工具**")
        st.markdown("- **優化工作流程**")
        st.markdown("- **提升效率與效益**")

    # 2. 軟實力的雷達圖展示
    st.markdown("### 🌟 軟實力評估")
    st.write("以下是我的軟實力雷達圖分析，展示多項軟技能的評估結果：")

    # 軟實力數據
    radar_data = {
        "技能": ["團隊合作", "專案管理", "抗壓性", "適應力", "溝通能力"],
        "評分": [90, 92, 88, 95, 85]
    }
    radar_df = pd.DataFrame(radar_data)

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=radar_df["評分"],
        theta=radar_df["技能"],
        fill='toself',
        name='軟實力'
    ))
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100])
        ),
        title="軟實力雷達圖"
    )
    st.plotly_chart(fig)

    # 3. 綜合能力評估圖表
    st.markdown("### 💫 綜合能力評估")
    st.write("以下是我的綜合能力，通過數據視覺化展示評估結果：")

    # 綜合能力數據
    abilities = {
        "領導力": {"score": 90, "description": "團隊管理、專案領導、目標達成"},
        "創新力": {"score": 88, "description": "流程優化、工具開發、問題解決"},
        "執行力": {"score": 95, "description": "專案管理、時程控制、結果導向"},
        "學習力": {"score": 92, "description": "技術更新、知識吸收、自我提升"}
    }

    # 使用列顯示能力評分
    for ability, data in abilities.items():
        st.markdown(f"#### {ability}")
        col1, col2 = st.columns([1, 3])
        with col1:
            st.markdown(f"**評分：{data['score']}**")
        with col2:
            st.progress(data['score'] / 100)
        st.markdown(f"*{data['description']}*")
        st.markdown("---")

    # 添加總結
    st.markdown("""
    ### 🏆 結語
    我擁有扎實的專業技術能力與出色的軟實力，能靈活應對不同挑戰，實現個人與團隊的目標！
    """)

# 页脚
st.markdown("""
---
<div style='text-align: center; color: var(--text-color); padding: 20px;'>
    © 2025 劉晉亨 | AI Enhanced Resume | Built with ❤️ and ❤️
</div>
""", unsafe_allow_html=True)