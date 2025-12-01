import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import requests
from sklearn.cluster import KMeans
from sklearn.ensemble import IsolationForest, RandomForestRegressor
from sklearn.model_selection import train_test_split
from statsmodels.tsa.seasonal import seasonal_decompose
from streamlit_mermaid import st_mermaid
import sys
import os

# 加入父目錄到 path 以導入 license_images_data
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from license_images_data import LICENSE_IMAGES
except ImportError:
    LICENSE_IMAGES = {}

# 導入 LLM 圖片 base64 資料
try:
    from llm_images_data import LLM_IMAGES
except ImportError:
    LLM_IMAGES = {}

def generate_process_data(n_samples=1000):
    np.random.seed(42)
    dates = pd.date_range(start='2024-01-01', periods=n_samples, freq='H')

    # Normal process data
    temperature = np.random.normal(150, 5, n_samples)
    pressure = np.random.normal(2.5, 0.2, n_samples)

    # Add some seasonal patterns
    temperature += 10 * np.sin(np.linspace(0, 4*np.pi, n_samples))

    # Add some anomalies
    anomaly_idx = np.random.choice(n_samples, 20, replace=False)
    temperature[anomaly_idx] += np.random.normal(20, 5, 20)
    pressure[anomaly_idx] += np.random.normal(1, 0.2, 20)

    # Create quality metric with some correlation to temp and pressure
    quality = 90 + 0.1*temperature - 2*pressure + np.random.normal(0, 2, n_samples)

    return pd.DataFrame({
        'timestamp': dates,
        'temperature': temperature,
        'pressure': pressure,
        'quality': quality,
        'is_anomaly': np.isin(np.arange(n_samples), anomaly_idx)
    })

def train_anomaly_detector(data):
    # Prepare features
    X = data[['temperature', 'pressure']]

    # Train isolation forest
    iso_forest = IsolationForest(contamination=0.02, random_state=42)
    iso_forest.fit(X)

    return iso_forest

def predict_quality(data):
    # Prepare features and target
    X = data[['temperature', 'pressure']]
    y = data['quality']

    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Train model
    rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
    rf_model.fit(X_train, y_train)

    # Make predictions
    y_pred = rf_model.predict(X)

    return y_pred

def generate_gas_data():
    # Generate sample gas flow data
    timestamps = pd.date_range(start='2024-01-01', periods=100, freq='H')
    np.random.seed(42)

    data = pd.DataFrame({
        'timestamp': timestamps,
        'Ar_flow': np.random.normal(100, 5, 100),
        'N2_flow': np.random.normal(50, 3, 100),
        'O2_flow': np.random.normal(20, 2, 100)
    })

    return data

# 設定全局圖表樣式
CHART_STYLE = {
    'title_font_size': 24,
    'axis_title_font_size': 16,
    'tick_font_size': 14,
    'legend_font_size': 14
}

import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path
import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
import requests
from datetime import datetime
import schedule
import threading
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cross_decomposition import PLSRegression
from sklearn.model_selection import cross_val_predict
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
import matplotlib as mpl

from config import (
    PAGE_CONFIG,
    CHART_CONFIG,
    DB_CONFIG,
    MAIL_CONFIG,
    MODEL_CONFIG
)

from utils import visitor_tracker

# Page configuration
st.set_page_config(
    page_title="Patrick Liou's Resume",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Set font configuration
plt.rcParams['font.sans-serif'] = CHART_CONFIG["font_family"]
plt.rcParams['axes.unicode_minus'] = False
mpl.rcParams['font.family'] = CHART_CONFIG["font_family"]

# Visitor tracking functions
def get_visitor_ip():
    try:
        response = requests.get('https://api.ipify.org?format=json')
        return response.json()['ip']
    except:
        return 'Unknown'

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

    visitor_data['total_visits'] += 1

    if today not in visitor_data['daily_visits']:
        visitor_data['daily_visits'][today] = 0
    visitor_data['daily_visits'][today] += 1

    if today not in visitor_data['ip_records']:
        visitor_data['ip_records'][today] = []
    if ip not in visitor_data['ip_records'][today]:
        visitor_data['ip_records'][today].append(ip)

    save_visitor_data(visitor_data)

    current_time = datetime.now()
    if current_time.hour == 20 and current_time.minute == 0:
        send_daily_report(visitor_data, today)

    return visitor_data['total_visits']

def send_daily_report(visitor_data, today):
    ip_locations = []
    for ip in visitor_data['ip_records'].get(today, []):
        try:
            response = requests.get(f'http://ip-api.com/json/{ip}')
            location = response.json()
            ip_locations.append(
                f"IP: {ip}\n"
                f"Location: {location.get('city', 'Unknown')}, {location.get('country', 'Unknown')}\n"
                f"Organization: {location.get('org', 'Unknown')}"
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
    msg['From'] = MAIL_CONFIG['sender']
    msg['To'] = MAIL_CONFIG['receiver']
    msg['Subject'] = f'Resume Website Visit Report - {today}'
    msg.attach(MIMEText(email_content, 'plain'))

@st.cache_data(ttl=3600)
def generate_gas_data():
    dates = pd.date_range(start='2023-01-01', periods=1000, freq='H')
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

@st.cache_data(ttl=3600)
def train_gas_model(data):
    if len(data) > 1000:
        data = data.tail(1000)

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

        model = RandomForestRegressor(n_estimators=50, random_state=42)
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

def load_profile_image():
    try:
        image_path = "PHOTO.jpg"
        if Path(image_path).exists():
            return image_path
        return None
    except Exception as e:
        st.error(f"Error loading profile image: {e}")
        return None

# Main content
if 'page' not in st.session_state:
    st.session_state.page = "Overview"

# Update visit count
total_visits = visitor_tracker.update_visitor_count()

# Add custom CSS
st.markdown("""
<style>
    .section-header {
        color: #1a1a1a;
        font-size: 2em;
        margin-bottom: 1em;
        border-bottom: 2px solid #4CAF50;
        padding-bottom: 0.5em;
    }

    .skill-category h3, .trait-category h3 {
        color: #2e7d32;
        font-size: 1.5em;
        margin: 1em 0 0.5em 0;
    }

    .skill-list, .trait-list {
        list-style-type: none;
        padding-left: 1.5em;
        margin: 0.5em 0;
    }

    .skill-list li, .trait-list li {
        margin: 0.8em 0;
        font-size: 1.1em;
        line-height: 1.4;
        position: relative;
    }

    .skill-list li:before, .trait-list li:before {
        content: "•";
        color: #4CAF50;
        font-weight: bold;
        position: absolute;
        left: -1em;
    }

    .experience-card {
        margin-bottom: 2em;
        padding-left: 1.5em;
        border-left: 4px solid #4CAF50;
    }

    .experience-card h3 {
        color: #1a1a1a;
        font-size: 1.4em;
        margin-bottom: 0.3em;
    }

    .experience-card h4 {
        color: #4CAF50;
        font-size: 1.2em;
        margin: 0.5em 0;
    }

    .experience-card .highlight {
        color: #666;
        font-style: italic;
        font-size: 1em;
    }

    .education-card {
        margin-bottom: 2em;
        padding-left: 1.5em;
        border-left: 4px solid #4CAF50;
    }

    .education-card h3 {
        color: #1a1a1a;
        font-size: 1.4em;
        margin-bottom: 0.3em;
    }

    .education-card .highlight {
        color: #666;
        font-style: italic;
        font-size: 1em;
    }

    /* Skill Ratings */
    .skill-ratings {
        margin-top: 1.5em;
    }

    .skill-item {
        margin: 1em 0;
    }

    .skill-name {
        display: inline-block;
        width: 150px;
        font-size: 1.1em;
    }

    .skill-bar {
        display: inline-block;
        height: 10px;
        background: #4CAF50;
        border-radius: 5px;
    }

    /* ========== Mobile Responsive Design ========== */
    
    /* Small screens (max-width: 768px) */
    @media screen and (max-width: 768px) {
        /* Basic layout adjustments */
        .main .block-container {
            padding: 1rem 0.5rem !important;
            max-width: 100% !important;
        }
        
        /* Font size adjustments */
        h1 {
            font-size: 1.5rem !important;
        }
        h2 {
            font-size: 1.3rem !important;
        }
        h3 {
            font-size: 1.1rem !important;
        }
        
        /* Profile section */
        .profile-section {
            padding: 1.5rem !important;
        }
        .profile-section h1 {
            font-size: 1.8rem !important;
        }
        .profile-section h2 {
            font-size: 1.2rem !important;
        }
        
        /* Card styles */
        .skill-card, .education-card, .experience-card {
            padding: 1rem !important;
            margin: 0.5rem 0 !important;
        }
        
        /* Tech badges */
        .tech-badge {
            padding: 0.5rem 0.8rem !important;
            font-size: 0.9rem !important;
        }
        .tech-badge .icon {
            font-size: 1.2rem !important;
            margin-right: 0.5rem !important;
        }
        
        /* Streamlit columns - stack vertically */
        [data-testid="column"] {
            width: 100% !important;
            flex: 1 1 100% !important;
            min-width: 100% !important;
        }
        
        /* Image adjustments */
        img {
            max-width: 100% !important;
            height: auto !important;
        }
        
        /* LLM icon area */
        [data-testid="column"] > div > div {
            min-height: auto !important;
        }
        
        /* Text size */
        p, li {
            font-size: 0.95rem !important;
            line-height: 1.5 !important;
        }
        
        /* Table adjustments */
        table {
            font-size: 0.8rem !important;
        }
        
        /* Plotly charts */
        .js-plotly-plot {
            width: 100% !important;
        }
        
        /* Sidebar */
        [data-testid="stSidebar"] {
            width: 100% !important;
            min-width: 100% !important;
        }
        
        /* Project cards */
        div[style*="min-height: 280px"] {
            min-height: auto !important;
            padding: 15px !important;
        }
        div[style*="min-height: 280px"] h3 {
            font-size: 1rem !important;
        }
        div[style*="min-height: 280px"] ul {
            padding-left: 1.2rem !important;
            font-size: 0.85rem !important;
        }
        div[style*="min-height: 280px"] img {
            width: 50px !important;
            height: 50px !important;
        }
        
        /* Five features icons */
        div[style*="width: 100px"] {
            width: 60px !important;
            height: 60px !important;
            padding: 8px !important;
        }
        div[style*="width: 100px"] img {
            width: 40px !important;
            height: 40px !important;
        }
        
        /* Certificate images */
        div[style*="border-radius: 15px"] img {
            max-height: 150px !important;
        }
    }
    
    /* Extra small screens (max-width: 480px) */
    @media screen and (max-width: 480px) {
        .main .block-container {
            padding: 0.5rem 0.3rem !important;
        }
        
        h1 {
            font-size: 1.3rem !important;
        }
        h2 {
            font-size: 1.1rem !important;
        }
        h3 {
            font-size: 1rem !important;
        }
        
        .profile-section h1 {
            font-size: 1.5rem !important;
        }
        
        /* Core platform cards */
        div[style*="padding: 25px"] {
            padding: 12px !important;
        }
        div[style*="padding: 25px"] h3 {
            font-size: 0.95rem !important;
        }
        div[style*="padding: 25px"] img {
            width: 60px !important;
            height: 60px !important;
        }
        div[style*="font-size: 4em"] {
            font-size: 2.5em !important;
        }
    }
    
    /* Tablet adjustments (768px - 1024px) */
    @media screen and (min-width: 769px) and (max-width: 1024px) {
        .main .block-container {
            padding: 1.5rem 1rem !important;
        }
        
        /* Allow two columns */
        [data-testid="column"] {
            min-width: 45% !important;
        }
    }
</style>
""", unsafe_allow_html=True)

# Sidebar navigation
with st.sidebar:
    page = st.radio(
        "Navigation",
        ["📊 Overview", "💼 Work Experience", "🎓 Education",
         "🛠️ Skills", "🌟 Personal Traits", "📈 Project Showcase",
         "🔬 Project Analysis", "🏆 Certifications"]
    )

# Main content area
if page == "📊 Overview":
    col1, col2 = st.columns([1, 2])

    with col1:
        profile_image = load_profile_image()
        if profile_image:
            st.image(profile_image, width=300)

    with col2:
        st.markdown("# Patrick Liou (劉晉亨)")
        st.markdown("### 🤖 Senior Process Integration Engineer | AI & Big Data Expert")
        
        st.markdown("---")
        
        st.markdown("#### 🎯 Core Expertise")
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.info("📊 Big Data Analytics")
            st.info("🔧 Process Integration")
        with col_b:
            st.info("🤖 Machine Learning")
            st.info("📈 Six Sigma")
        with col_c:
            st.info("🧠 Deep Learning")
            st.info("🏭 Smart Manufacturing")
        
        st.markdown("#### 🤖 AI & LLM Expertise")
        col_d, col_e, col_f = st.columns(3)
        with col_d:
            st.warning("💬 Large Language Models (LLM)")
        with col_e:
            st.warning("🔍 RAG Applications")
        with col_f:
            st.warning("🎤 Speech Recognition")

elif page == "💼 Work Experience":
    st.markdown("## 💼 Work Experience")
    
    # Innolux (Current)
    with st.container():
        st.markdown("### 🏢 Innolux Corporation")
        st.markdown("**December 2014 - Present** | Process Engineer / Team Leader")
        st.markdown("""
        - Led smart factory initiatives, implementing Industry 4.0 solutions for significant production efficiency improvements
        - Developed YOLOv4 defect detection models, reducing feedback time and increasing defect detection rate by 60%
        - Led 3 Six Sigma projects, optimizing process parameters and reducing defect rate, saving NT$21 million annually
        - Established intelligent early warning system, improving yield by 15%
        - Built LLM-powered intelligent systems for cross-database queries and anomaly analysis, reducing data processing time by 92%
        - Developed AI-automated equipment status classification and RPSC data analysis systems, improving exception handling efficiency
        - Implemented Whisper speech recognition for automated meeting transcription and intelligent summarization
        """)
    
    st.divider()
    
    # TSMC
    with st.container():
        st.markdown("### 🏢 TSMC")
        st.markdown("**March 2014 - December 2014** | Equipment Engineer")
        st.markdown("""
        - Optimized process tool parameters, improving yield and stability with 4% defect rate improvement
        - Reduced system crash rate to 5%, enhancing equipment availability and capacity utilization
        - Participated in next-generation process development
        """)
    
    st.divider()
    
    # Taiwan Cement
    with st.container():
        st.markdown("### 🏢 Taiwan Cement Corporation")
        st.markdown("**September 2013 - March 2014** | Management Associate")
        st.markdown("""
        - Monitored and optimized production processes, reducing bottleneck operation time by 15%
        - Assisted in developing new PDA system to enhance process automation
        - Implemented process control improvements resulting in better product quality
        """)
    
    st.divider()
    
    # Innolux (Early)
    with st.container():
        st.markdown("### 🏢 Innolux Corporation")
        st.markdown("**January 2010 - September 2013** | Process Engineer")
        st.markdown("""
        - Assisted in new factory setup, completing pilot production ahead of schedule
        - Analyzed equipment failure causes and provided solutions, improving uptime by 25%
        - Developed and implemented process control strategies
        """)
    
    st.divider()
    
    # Core Competencies
    st.markdown("### 🎯 Core Competencies")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Leadership**")
        st.progress(0.95)
        st.markdown("**Technical Innovation**")
        st.progress(0.90)
        st.markdown("**Project Management**")
        st.progress(0.92)
    with col2:
        st.markdown("**Problem Solving**")
        st.progress(0.88)
        st.markdown("**Team Collaboration**")
        st.progress(0.93)

elif page == "🎓 Education":
    st.markdown("## 🎓 Education Background")
    
    # Taiwan AI Academy - AI Tech Leader Program (最新)
    with st.container():
        st.markdown("### 🤖 Taiwan AI Academy")
        st.markdown("**2020 - 2021** | AI Tech Leader Program")
        st.markdown("""
        - Deep Learning & Neural Network Architecture Design
        - AI Project Management & Team Leadership
        - Industrial AI Application Practice
        """)
    
    st.divider()
    
    # Taiwan AI Academy - AI Executive Program
    with st.container():
        st.markdown("### 🤖 Taiwan AI Academy")
        st.markdown("**2018 - 2019** | AI Executive Program")
        st.markdown("""
        - Machine Learning & Data Science Fundamentals
        - AI Strategy Planning & Business Applications
        - Digital Transformation & Innovation Management
        """)
    
    st.divider()
    
    # National Chiao Tung University
    with st.container():
        st.markdown("### 🎓 National Chiao Tung University")
        st.markdown("**September 2015 - January 2018** | Master of Business Administration (MBA)")
        st.markdown("""
        - Focus: Data Analytics & Business Intelligence
        - Research: Digital Transformation in Manufacturing Industry
        - Key Projects: Industry 4.0 Implementation Strategy
        """)
    
    st.divider()
    
    # National Taiwan University
    with st.container():
        st.markdown("### 🎓 National Taiwan University")
        st.markdown("**March 2015 - June 2017** | Continuing Education in Law")
        st.markdown("""
        - Focus: Business Law & Intellectual Property Rights
        - Research: Technology Industry Legal Framework
        - Key Topics: Patent Law, Trade Secrets, Labor Laws
        """)
    
    st.divider()
    
    # NTUST
    with st.container():
        st.markdown("### 🎓 National Taiwan University of Science and Technology")
        st.markdown("**September 2006 - June 2008** | Master of Chemical Engineering")
        st.markdown("""
        - Focus: Process Control & Optimization
        - Research: Advanced Process Control Systems
        - Thesis: Development of Intelligent Process Control Algorithms
        """)
    
    st.divider()
    
    # Feng Chia University
    with st.container():
        st.markdown("### 🎓 Feng Chia University")
        st.markdown("**September 2002 - June 2006** | Bachelor of Chemical Engineering")
        st.markdown("""
        - Focus: Chemical Engineering Fundamentals
        - Research: Process Automation & Control
        - Senior Project: Design of Automated Control Systems
        """)

elif page == "🛠️ Skills":
    st.markdown("## 🛠️ Technical Skills")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info("#### 🔧 Programming & Development")
        st.markdown("""
        - Python (Pandas, NumPy, Scikit-learn, TensorFlow, PyTorch)
        - Deep Learning & Computer Vision (YOLOv4, OpenCV)
        - SQL & Database Management
        - Git Version Control
        """)
        
        st.success("#### 📊 Data Analytics")
        st.markdown("""
        - Statistical Analysis & Data Mining
        - Process Capability Analysis (Cp/Cpk)
        - Design of Experiments (DOE)
        - Time Series Analysis & Forecasting
        """)
    
    with col2:
        st.warning("#### 🏭 Manufacturing Excellence")
        st.markdown("""
        - Six Sigma Black Belt
        - Lean Manufacturing
        - Industry 4.0 Implementation
        - Equipment Performance Optimization
        """)
        
        st.info("#### 👥 Soft Skills")
        st.markdown("""
        - Cross-functional Team Leadership
        - Project Management & Planning
        - Technical Documentation & Presentation
        - Mentoring & Knowledge Transfer
        """)
    
    with col3:
        st.error("#### 🤖 AI & LLM Expertise")
        st.markdown("""
        - 💬 Large Language Models (LLM)
        - 🎵 Vibe Coding (AI-Assisted Development)
        - 🔍 RAG Application Development
        - 🎤 Whisper Speech Recognition
        - 🦜 LangChain / LangFlow
        - 🧠 Prompt Engineering
        - 💻 GitHub Copilot / Cursor AI
        - 🤖 OLLAMA / GPT API Integration
        """)

elif page == "🌟 Personal Traits":
    st.markdown("## 🌟 Personal Traits")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info("#### 🎯 Professional Drive")
        st.markdown("""
        - Strong analytical mindset with attention to detail
        - Results-oriented with focus on continuous improvement
        - Proactive problem-solver with innovative thinking
        - Quick learner adaptable to new technologies
        """)
    
    with col2:
        st.success("#### 👥 Leadership Style")
        st.markdown("""
        - Collaborative team player fostering positive work environment
        - Effective communicator across all organizational levels
        - Mentor focused on team growth and development
        - Strategic thinker with clear goal setting
        """)
    
    with col3:
        st.warning("#### 🌱 Growth Mindset")
        st.markdown("""
        - Passionate about emerging technologies
        - Committed to continuous learning and improvement
        - Open to feedback and new perspectives
        - Resilient under pressure and deadlines
        """)

elif page == "📈 Project Showcase":
    st.markdown("# 🤖 AI & Data Science Projects")
    
    # 大標題區塊
    st.markdown("""
    <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; border-radius: 15px; margin-bottom: 25px; text-align: center;'>
        <h1 style='color: white; margin: 0;'>🤖 Large Language Model Technology & Vision</h1>
        <p style='color: #f0f0f0; margin-top: 10px; font-size: 1.2em;'>
            Semantic Analysis | Image Analysis | Data Analytics | Database Query | Speech Recognition
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # LLM 核心技術圖示區 - 使用 PPT 圖片
    st.markdown("### 🧠 Core Technology Platforms")
    
    # 取得圖片 base64
    ollama_img = LLM_IMAGES.get("slide2_img4", {}).get("base64", "")  # OLLAMA 羊駝圖
    innogpt_img = LLM_IMAGES.get("slide4_img3", {}).get("base64", "")  # INNO GPT 機器人
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        img_html = f'<img src="data:image/png;base64,{ollama_img}" style="width:120px; height:120px; object-fit:contain;">' if ollama_img else '<div style="font-size: 4em;">🦙</div>'
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #232526 0%, #414345 100%); padding: 25px; border-radius: 15px; text-align: center; border: 2px solid #00d4ff;'>
            {img_html}
            <h3 style='color: #00d4ff; margin: 10px 0 0 0;'>OLLAMA</h3>
            <p style='color: #aaa; margin: 10px 0 0 0;'>Local Open-Source LLM</p>
            <p style='color: #888; font-size: 0.85em;'>Llama / Mistral / Gemma</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        img_html = f'<img src="data:image/png;base64,{innogpt_img}" style="width:120px; height:120px; object-fit:contain;">' if innogpt_img else '<div style="font-size: 4em;">🧠</div>'
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%); padding: 25px; border-radius: 15px; text-align: center; border: 2px solid #10a37f;'>
            {img_html}
            <h3 style='color: #10a37f; margin: 10px 0 0 0;'>INNO GPT</h3>
            <p style='color: #aaa; margin: 10px 0 0 0;'>Enterprise Internal API</p>
            <p style='color: #888; font-size: 0.85em;'>RAG / Image Analysis / Data Processing</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); padding: 25px; border-radius: 15px; text-align: center; border: 2px solid #ff6b6b;'>
            <div style='font-size: 4em; margin-bottom: 10px;'>🎙️</div>
            <h3 style='color: #ff6b6b; margin: 0;'>Whisper</h3>
            <p style='color: #aaa; margin: 10px 0 0 0;'>OpenAI Speech Recognition</p>
            <p style='color: #888; font-size: 0.85em;'>Meeting Notes / Speech-to-Text</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 五大功能圖示 - 使用 PPT Slide 1 的圖示
    st.markdown("### ⚡ 5 AI Application Features")
    
    # 取得五大功能圖示
    icon1 = LLM_IMAGES.get("slide1_img1", {}).get("base64", "")  # Semantic Analysis
    icon2 = LLM_IMAGES.get("slide1_img6", {}).get("base64", "")  # Image Analysis
    icon3 = LLM_IMAGES.get("slide1_img3", {}).get("base64", "")  # Data Analytics
    icon4 = LLM_IMAGES.get("slide1_img4", {}).get("base64", "")  # Database Query
    icon5 = LLM_IMAGES.get("slide1_img2", {}).get("base64", "")  # Speech Recognition
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        img_html = f'<img src="data:image/png;base64,{icon1}" style="width:70px; height:70px; object-fit:contain;">' if icon1 else '<span style="font-size: 2.5em;">🗣️</span>'
        st.markdown(f"""
        <div style='text-align: center;'>
            <div style='background: linear-gradient(180deg, #667eea 0%, #764ba2 100%); padding: 15px; border-radius: 15px; width: 100px; height: 100px; margin: 0 auto; display: flex; align-items: center; justify-content: center;'>
                {img_html}
            </div>
            <p style='color: #667eea; font-weight: bold; margin-top: 10px;'>Semantic</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        img_html = f'<img src="data:image/png;base64,{icon2}" style="width:70px; height:70px; object-fit:contain;">' if icon2 else '<span style="font-size: 2.5em;">🖼️</span>'
        st.markdown(f"""
        <div style='text-align: center;'>
            <div style='background: linear-gradient(180deg, #f093fb 0%, #f5576c 100%); padding: 15px; border-radius: 15px; width: 100px; height: 100px; margin: 0 auto; display: flex; align-items: center; justify-content: center;'>
                {img_html}
            </div>
            <p style='color: #f5576c; font-weight: bold; margin-top: 10px;'>Image</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        img_html = f'<img src="data:image/png;base64,{icon3}" style="width:70px; height:70px; object-fit:contain;">' if icon3 else '<span style="font-size: 2.5em;">📊</span>'
        st.markdown(f"""
        <div style='text-align: center;'>
            <div style='background: linear-gradient(180deg, #11998e 0%, #38ef7d 100%); padding: 15px; border-radius: 15px; width: 100px; height: 100px; margin: 0 auto; display: flex; align-items: center; justify-content: center;'>
                {img_html}
            </div>
            <p style='color: #11998e; font-weight: bold; margin-top: 10px;'>Data</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        img_html = f'<img src="data:image/png;base64,{icon4}" style="width:70px; height:70px; object-fit:contain;">' if icon4 else '<span style="font-size: 2.5em;">🗄️</span>'
        st.markdown(f"""
        <div style='text-align: center;'>
            <div style='background: linear-gradient(180deg, #4facfe 0%, #00f2fe 100%); padding: 15px; border-radius: 15px; width: 100px; height: 100px; margin: 0 auto; display: flex; align-items: center; justify-content: center;'>
                {img_html}
            </div>
            <p style='color: #4facfe; font-weight: bold; margin-top: 10px;'>Database</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col5:
        img_html = f'<img src="data:image/png;base64,{icon5}" style="width:70px; height:70px; object-fit:contain;">' if icon5 else '<span style="font-size: 2.5em;">🎤</span>'
        st.markdown(f"""
        <div style='text-align: center;'>
            <div style='background: linear-gradient(180deg, #fa709a 0%, #fee140 100%); padding: 15px; border-radius: 15px; width: 100px; height: 100px; margin: 0 auto; display: flex; align-items: center; justify-content: center;'>
                {img_html}
            </div>
            <p style='color: #fa709a; font-weight: bold; margin-top: 10px;'>Speech</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 📦 Application Project Details")
    
    # 取得更多圖片用於專案卡片
    ollama_card_img = LLM_IMAGES.get("slide2_img4", {}).get("base64", "")  # OLLAMA 羊駝圖
    innogpt_card_img = LLM_IMAGES.get("slide4_img3", {}).get("base64", "")  # INNO GPT 機器人
    
    # 六大功能卡片
    col1, col2, col3 = st.columns(3)
    
    with col1:
        img_html = f'<img src="data:image/png;base64,{ollama_card_img}" style="width:80px; height:80px; object-fit:contain; float:right;">' if ollama_card_img else ''
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); padding: 20px; border-radius: 15px; min-height: 280px;'>
            {img_html}
            <h3 style='color: white; margin-top: 0;'>🔧 Equipment Status Classification</h3>
            <p style='color: #e0ffe0; font-size: 0.9em;'><strong>Tech: OLLAMA Local</strong></p>
            <ul style='color: #f0f0f0; font-size: 0.95em;'>
                <li>Auto-classify equipment status</li>
                <li>Intelligent report queries</li>
                <li>Automatic DB storage</li>
            </ul>
            <p style='color: #ffeb3b; font-size: 0.9em;'>💡 Solved: Scattered equipment data</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        img_html = f'<img src="data:image/png;base64,{ollama_card_img}" style="width:80px; height:80px; object-fit:contain; float:right;">' if ollama_card_img else ''
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); padding: 20px; border-radius: 15px; min-height: 280px;'>
            {img_html}
            <h3 style='color: white; margin-top: 0;'>📝 Release Table Analysis</h3>
            <p style='color: #e0f7ff; font-size: 0.9em;'><strong>Tech: OLLAMA Local</strong></p>
            <ul style='color: #f0f0f0; font-size: 0.95em;'>
                <li>Read & classify COMMENT status</li>
                <li>Release Table report analysis</li>
                <li>Automatic DB storage</li>
            </ul>
            <p style='color: #ffeb3b; font-size: 0.9em;'>💡 Solved: Disorganized COMMENTs</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        img_html = f'<img src="data:image/png;base64,{innogpt_card_img}" style="width:80px; height:80px; object-fit:contain; float:right;">' if innogpt_card_img else ''
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); padding: 20px; border-radius: 15px; min-height: 280px;'>
            {img_html}
            <h3 style='color: white; margin-top: 0;'>🎯 AI Crash Product (RAG)</h3>
            <p style='color: #ffe0f0; font-size: 0.9em;'><strong>Tech: INNO GPT</strong></p>
            <ul style='color: #f0f0f0; font-size: 0.95em;'>
                <li>Historical exception analysis</li>
                <li>AI LOG identification</li>
                <li>Follow-up recommendations</li>
            </ul>
            <p style='color: #ffeb3b; font-size: 0.9em;'>💡 RAG-powered analysis</p>
        </div>
        """, unsafe_allow_html=True)
    
    # 第二排卡片
    col1, col2, col3 = st.columns(3)
    
    with col1:
        img_html = f'<img src="data:image/png;base64,{innogpt_card_img}" style="width:80px; height:80px; object-fit:contain; float:right;">' if innogpt_card_img else ''
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 15px; min-height: 280px;'>
            {img_html}
            <h3 style='color: white; margin-top: 0;'>📊 RPSC Data & EP Analysis</h3>
            <p style='color: #e0e0ff; font-size: 0.9em;'><strong>Tech: INNO GPT API</strong></p>
            <ul style='color: #f0f0f0; font-size: 0.95em;'>
                <li>Plot Trend Charts from RPSC</li>
                <li>GPT image analysis</li>
                <li>EP identification by RULE</li>
            </ul>
            <p style='color: #ffeb3b; font-size: 0.9em;'>💡 Advanced: Auto data processing</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); padding: 20px; border-radius: 15px; min-height: 280px;'>
            <div style='float: right; font-size: 3em;'>🎙️</div>
            <h3 style='color: white; margin-top: 0;'>🎤 Meeting Voice Recording</h3>
            <p style='color: #fff0e0; font-size: 0.9em;'><strong>Tech: Whisper</strong></p>
            <ul style='color: #f0f0f0; font-size: 0.95em;'>
                <li>Auto voice recording</li>
                <li>Intelligent summarization</li>
                <li>Key points extraction</li>
            </ul>
            <p style='color: #333; font-size: 0.9em;'>💡 Speech-to-text automation</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        img_html = f'<img src="data:image/png;base64,{ollama_card_img}" style="width:80px; height:80px; object-fit:contain; float:right;">' if ollama_card_img else ''
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #232526 0%, #414345 100%); padding: 20px; border-radius: 15px; min-height: 280px; border: 2px solid #00d4ff;'>
            {img_html}
            <h3 style='color: #00d4ff; margin-top: 0;'>🔍 Cross-DB Query System</h3>
            <p style='color: #aaa; font-size: 0.9em;'><strong>Tech: GPT/OLLAMA SQL</strong></p>
            <ul style='color: #d0d0d0; font-size: 0.95em;'>
                <li>Yield/Equipment/Release queries</li>
                <li>Anomaly analysis & reports</li>
                <li>Automatic DB storage</li>
            </ul>
            <p style='color: #ffeb3b; font-size: 0.9em;'>⚡ 1 HR → 5 min efficiency</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Project Benefits Chart
    st.markdown("---")
    st.markdown("### 📈 Project Benefits Overview")
    
    benefit_data = {
        "Project": ["Cross-DB Query", "Equipment Status", "Release Table", "RPSC Analysis"],
        "Original Time": [60, 60, 45, 30],
        "Optimized Time": [5, 5, 5, 5],
        "Efficiency Gain": ["92%", "92%", "89%", "83%"]
    }
    
    fig = go.Figure(data=[
        go.Bar(name='Original Time (min)', x=benefit_data["Project"], y=benefit_data["Original Time"], marker_color='rgba(255, 99, 71, 0.7)'),
        go.Bar(name='Optimized Time (min)', x=benefit_data["Project"], y=benefit_data["Optimized Time"], marker_color='rgba(60, 179, 113, 0.7)')
    ])
    
    fig.update_layout(
        title='LLM Project Efficiency Comparison',
        barmode='group',
        title_font_size=20,
        xaxis_title="Project Name",
        yaxis_title="Time (minutes)",
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    st.markdown("""
    ## Real-time Process Monitoring System
    Implemented an advanced monitoring system using real-time metrics for:
    - Real-time temperature and pressure tracking
    - Anomaly detection using Isolation Forest
    - Quality prediction using Random Forest
    """)

    # Generate and process data
    process_data = generate_process_data()

    # Train models
    iso_forest = train_anomaly_detector(process_data)
    predicted_quality = predict_quality(process_data)

    # Add predictions to data
    process_data['anomaly_score'] = iso_forest.score_samples(process_data[['temperature', 'pressure']])
    process_data['predicted_quality'] = predicted_quality

    # Real-time monitoring plot
    st.markdown("### Real-time Process Parameters Monitoring")
    fig = px.line(process_data.iloc[-100:], x='timestamp',
                 y=['temperature', 'pressure'],
                 title='Real-time Process Parameters Monitoring',
                 labels={'timestamp': 'Time',
                        'temperature': 'Temperature (°C)',
                        'pressure': 'Pressure (MPa)',
                        'value': 'Parameter Value'})
    fig.update_layout(
        xaxis_title="Time",
        yaxis_title="Parameter Value",
        legend_title="Parameters",
        title_font_size=CHART_STYLE['title_font_size'],
        font=dict(size=CHART_STYLE['axis_title_font_size']),
        legend=dict(font=dict(size=CHART_STYLE['legend_font_size'])),
        xaxis=dict(tickfont=dict(size=CHART_STYLE['tick_font_size'])),
        yaxis=dict(tickfont=dict(size=CHART_STYLE['tick_font_size']))
    )
    st.plotly_chart(fig)

    # Anomaly detection plot
    st.markdown("""
    ### Anomaly Detection System
    Using Isolation Forest algorithm to detect abnormal process conditions:
    - Identifies outliers in multivariate data
    - Real-time scoring of process conditions
    - Early warning system for potential issues
    """)

    fig = px.scatter(process_data, x='temperature', y='pressure',
                    color='anomaly_score',
                    title='Process Anomaly Detection Analysis',
                    color_continuous_scale='RdYlBu',
                    labels={'temperature': 'Temperature (°C)',
                           'pressure': 'Pressure (MPa)',
                           'anomaly_score': 'Anomaly Score'})
    fig.update_layout(
        xaxis_title="Temperature (°C)",
        yaxis_title="Pressure (MPa)",
        coloraxis_colorbar_title="Anomaly Score",
        title_font_size=CHART_STYLE['title_font_size'],
        font=dict(size=CHART_STYLE['axis_title_font_size']),
        legend=dict(font=dict(size=CHART_STYLE['legend_font_size'])),
        xaxis=dict(tickfont=dict(size=CHART_STYLE['tick_font_size'])),
        yaxis=dict(tickfont=dict(size=CHART_STYLE['tick_font_size']))
    )
    st.plotly_chart(fig)

    # Quality prediction plot
    st.markdown("""
    ### Quality Prediction Model
    Developed a Random Forest model for quality prediction:
    - Real-time quality forecasting
    - Model accuracy tracking
    - Automated parameter optimization
    """)

    fig = px.line(process_data.iloc[-100:], x='timestamp',
                 y=['quality', 'predicted_quality'],
                 title='Quality Control: Actual vs Predicted',
                 labels={'timestamp': 'Time',
                        'quality': 'Actual Quality',
                        'predicted_quality': 'Predicted Quality',
                        'value': 'Quality Score'})
    fig.update_layout(
        xaxis_title="Time",
        yaxis_title="Quality Score",
        legend_title="Quality Metrics",
        title_font_size=CHART_STYLE['title_font_size'],
        font=dict(size=CHART_STYLE['axis_title_font_size']),
        legend=dict(font=dict(size=CHART_STYLE['legend_font_size'])),
        xaxis=dict(tickfont=dict(size=CHART_STYLE['tick_font_size'])),
        yaxis=dict(tickfont=dict(size=CHART_STYLE['tick_font_size']))
    )
    st.plotly_chart(fig)

    # Gas Monitoring System
    st.markdown("""
    ## Gas Flow Monitoring System
    Advanced gas flow monitoring and analysis:
    - Real-time flow rate tracking
    - Multi-gas composition analysis
    - Automated alerts and notifications
    """)

    gas_data = generate_gas_data()

    fig = px.line(gas_data, x='timestamp',
                 y=['Ar_flow', 'N2_flow', 'O2_flow'],
                 title='Gas Flow Monitoring',
                 labels={'timestamp': 'Time',
                        'Ar_flow': 'Argon Flow (sccm)',
                        'N2_flow': 'Nitrogen Flow (sccm)',
                        'O2_flow': 'Oxygen Flow (sccm)',
                        'value': 'Flow Rate (sccm)'})
    fig.update_layout(
        xaxis_title="Time",
        yaxis_title="Flow Rate (sccm)",
        legend_title="Gas Type",
        title_font_size=CHART_STYLE['title_font_size'],
        font=dict(size=CHART_STYLE['axis_title_font_size']),
        legend=dict(font=dict(size=CHART_STYLE['legend_font_size'])),
        xaxis=dict(tickfont=dict(size=CHART_STYLE['tick_font_size'])),
        yaxis=dict(tickfont=dict(size=CHART_STYLE['tick_font_size']))
    )
    st.plotly_chart(fig)

elif page == "🔬 Project Analysis":
    st.markdown("# Advanced Process Analysis")
    
    # LLM Technology Showcase
    st.markdown("## 🤖 Large Language Model Technology & Applications")
    
    st.markdown("""
    Leveraging Large Language Model technology to integrate multiple capabilities for manufacturing intelligence transformation:
    """)
    
    # LLM Core Functions
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("#### 🗣️ Semantic Analysis")
        st.markdown("Natural Language Processing & Understanding")
    with col2:
        st.success("#### 🖼️ Image Analysis")
        st.markdown("Visual Recognition & Defect Detection")
    with col3:
        st.warning("#### 📊 Data Analysis")
        st.markdown("Intelligent Data Processing & Insights")
    
    col4, col5, col6 = st.columns(3)
    with col4:
        st.error("#### 🗄️ Database Query")
        st.markdown("Natural Language to SQL Generation")
    with col5:
        st.info("#### 🎤 Speech Recognition")
        st.markdown("Whisper Meeting Transcription System")
    with col6:
        st.success("#### 🔄 RAG Applications")
        st.markdown("Retrieval-Augmented Generation")
    
    st.markdown("---")
    
    # LLM Architecture Diagram
    st.markdown("### 🏗️ LLM Technical Architecture")
    llm_tech_flow = """
    graph LR
        A[Data Input] --> B{Large Language Model}
        B --> C[OLLAMA<br>Local Deployment]
        B --> D[INNO GPT<br>API Calls]
        B --> E[Whisper<br>Speech Recognition]
        
        C --> F[Status Classification]
        C --> G[Release Analysis]
        D --> H[RAG Processing]
        D --> I[RPSC Analysis]
        E --> J[Meeting Summary]
        
        F --> K[(Database)]
        G --> K
        H --> K
        I --> K
        J --> K
        
        K --> L[Report Generation]
        
        style A fill:#e1f5fe
        style B fill:#fff3e0
        style K fill:#e8f5e9
        style L fill:#fce4ec
    """
    st_mermaid(llm_tech_flow)
    
    st.markdown("---")

    # 1. Multivariate Analysis
    st.markdown("""
    ### Multivariate Process Analysis
    Advanced statistical analysis of process parameters:
    - Correlation analysis
    - Principal Component Analysis (PCA)
    - Factor analysis
    """)

    # Generate process data
    process_data = generate_process_data(500)

    # Correlation heatmap
    corr = process_data[['temperature', 'pressure', 'quality']].corr()
    fig = px.imshow(corr,
                   title='Parameter Correlation Matrix',
                   color_continuous_scale='RdBu',
                   labels={'color': 'Correlation'})
    fig.update_layout(
        title_font_size=CHART_STYLE['title_font_size'],
        font=dict(size=CHART_STYLE['axis_title_font_size']),
        legend=dict(font=dict(size=CHART_STYLE['legend_font_size'])),
        xaxis=dict(tickfont=dict(size=CHART_STYLE['tick_font_size'])),
        yaxis=dict(tickfont=dict(size=CHART_STYLE['tick_font_size']))
    )
    st.plotly_chart(fig)

    # Scatter matrix
    fig = px.scatter_matrix(process_data,
                          dimensions=['temperature', 'pressure', 'quality'],
                          title='Process Parameters Interaction Analysis',
                          labels={'temperature': 'Temperature (°C)',
                                 'pressure': 'Pressure (MPa)',
                                 'quality': 'Quality Score'})
    fig.update_layout(
        title_font_size=CHART_STYLE['title_font_size'],
        font=dict(size=CHART_STYLE['axis_title_font_size']),
        legend=dict(font=dict(size=CHART_STYLE['legend_font_size'])),
        xaxis=dict(tickfont=dict(size=CHART_STYLE['tick_font_size'])),
        yaxis=dict(tickfont=dict(size=CHART_STYLE['tick_font_size']))
    )
    st.plotly_chart(fig)

    # 2. Time Series Analysis
    st.markdown("""
    ### Time Series Analysis & Forecasting
    Implemented advanced time series models:
    - ARIMA modeling
    - Trend analysis
    - Seasonal decomposition
    """)

    # Time series decomposition plot
    ts_data = generate_process_data(200)
    decomposition = seasonal_decompose(ts_data['temperature'], period=24)

    fig = make_subplots(rows=4, cols=1,
                       subplot_titles=('Original Signal', 'Trend Component',
                                     'Seasonal Pattern', 'Residual Noise'))
    fig.add_trace(go.Scatter(x=ts_data.index, y=decomposition.observed,
                           name='Original'), row=1, col=1)
    fig.add_trace(go.Scatter(x=ts_data.index, y=decomposition.trend,
                           name='Trend'), row=2, col=1)
    fig.add_trace(go.Scatter(x=ts_data.index, y=decomposition.seasonal,
                           name='Seasonal'), row=3, col=1)
    fig.add_trace(go.Scatter(x=ts_data.index, y=decomposition.resid,
                           name='Residual'), row=4, col=1)
    fig.update_layout(height=800,
                     title='Time Series Decomposition Analysis',
                     showlegend=False,
                     title_font_size=CHART_STYLE['title_font_size'],
                     font=dict(size=CHART_STYLE['axis_title_font_size']))
    st.plotly_chart(fig)

    # 3. Pattern Recognition
    st.markdown("""
    ### Process Pattern Recognition
    Machine learning-based pattern recognition:
    - Cluster analysis
    - Anomaly detection
    - Pattern classification
    """)

    # Generate data for pattern recognition
    process_data = generate_process_data(1000)

    # K-means clustering
    kmeans = KMeans(n_clusters=3, random_state=42)
    clusters = kmeans.fit_predict(process_data[['temperature', 'pressure']])

    # Clustering plot
    process_data['cluster'] = clusters
    fig = px.scatter(process_data, x='temperature', y='pressure',
                    color='cluster',
                    title='Process Pattern Clustering Analysis',
                    labels={'temperature': 'Temperature (°C)',
                           'pressure': 'Pressure (MPa)',
                           'cluster': 'Cluster'})
    fig.update_layout(
        xaxis_title="Temperature (°C)",
        yaxis_title="Pressure (MPa)",
        legend_title="Cluster",
        title_font_size=CHART_STYLE['title_font_size'],
        font=dict(size=CHART_STYLE['axis_title_font_size']),
        legend=dict(font=dict(size=CHART_STYLE['legend_font_size'])),
        xaxis=dict(tickfont=dict(size=CHART_STYLE['tick_font_size'])),
        yaxis=dict(tickfont=dict(size=CHART_STYLE['tick_font_size']))
    )
    st.plotly_chart(fig)

    # 4. Performance Metrics
    st.markdown("""
    ### Performance Metrics Analysis
    Comprehensive performance monitoring:
    - Quality metrics tracking
    - Efficiency analysis
    - Cost-benefit analysis
    """)

    # Generate performance metrics
    dates = pd.date_range(start='2024-01-01', periods=30)
    metrics_data = pd.DataFrame({
        'date': dates,
        'oee': np.random.normal(85, 3, 30),
        'quality_rate': np.random.normal(98, 1, 30),
        'production_rate': np.random.normal(92, 2, 30)
    })

    # Performance metrics plot
    fig = px.line(metrics_data, x='date',
                 y=['oee', 'quality_rate', 'production_rate'],
                 title='Key Performance Indicators Trend',
                 labels={'date': 'Date',
                        'oee': 'Overall Equipment Effectiveness',
                        'quality_rate': 'Quality Rate',
                        'production_rate': 'Production Rate',
                        'value': 'Percentage (%)'})
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Percentage (%)",
        legend_title="Metrics",
        title_font_size=CHART_STYLE['title_font_size'],
        font=dict(size=CHART_STYLE['axis_title_font_size']),
        legend=dict(font=dict(size=CHART_STYLE['legend_font_size'])),
        xaxis=dict(tickfont=dict(size=CHART_STYLE['tick_font_size'])),
        yaxis=dict(tickfont=dict(size=CHART_STYLE['tick_font_size']))
    )
    st.plotly_chart(fig)

elif page == "🏆 Certifications":
    st.markdown("# 🏆 Professional Certifications")
    
    st.markdown("""
    <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 25px; border-radius: 15px; margin-bottom: 20px;'>
        <h3 style='color: white; margin: 0;'>🌟 Lifelong Learning</h3>
        <p style='color: #f0f0f0; margin-top: 10px;'>
        Beyond continuous improvement in professional skills, I am passionate about exploring knowledge 
        and skills in different fields. In 2024, I obtained several culinary certifications during my spare time, 
        demonstrating my attitude of lifelong learning and enthusiasm for diverse development.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Certification stats cards
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%); padding: 20px; border-radius: 15px; text-align: center;'>
            <h1 style='margin: 0; font-size: 3em;'>🍜</h1>
            <h4 style='margin: 5px 0;'>Chinese Cuisine</h4>
            <span style='background: #4CAF50; color: white; padding: 3px 10px; border-radius: 10px; font-size: 0.8em;'>✓ Obtained</span>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%); padding: 20px; border-radius: 15px; text-align: center;'>
            <h1 style='margin: 0; font-size: 3em;'>🎂</h1>
            <h4 style='margin: 5px 0;'>Baking - Cake</h4>
            <span style='background: #4CAF50; color: white; padding: 3px 10px; border-radius: 10px; font-size: 0.8em;'>✓ Obtained</span>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%); padding: 20px; border-radius: 15px; text-align: center;'>
            <h1 style='margin: 0; font-size: 3em;'>🍝</h1>
            <h4 style='margin: 5px 0;'>Western Cuisine</h4>
            <span style='background: #FF9800; color: white; padding: 3px 10px; border-radius: 10px; font-size: 0.8em;'>⏳ Pending</span>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #d299c2 0%, #fef9d7 100%); padding: 20px; border-radius: 15px; text-align: center;'>
            <h1 style='margin: 0; font-size: 3em;'>🍸</h1>
            <h4 style='margin: 5px 0;'>Bartending</h4>
            <span style='background: #FF9800; color: white; padding: 3px 10px; border-radius: 10px; font-size: 0.8em;'>⏳ Pending</span>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Certification info
    licenses_info = {
        "中餐": {
            "title": "🍜 Chinese Cuisine (Level C)",
            "date": "First Half of 2024",
            "status": "Obtained",
            "status_color": "#4CAF50",
            "description": "Chinese cooking skills certification, including knife skills, heat control, and various Chinese cooking techniques.",
            "gradient": "linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%)"
        },
        "蛋糕": {
            "title": "🎂 Baking - Cake (Level C)",
            "date": "First Half of 2024",
            "status": "Obtained",
            "status_color": "#4CAF50",
            "description": "Western pastry making skills certification, covering sponge cake, chiffon cake, and basic baking techniques.",
            "gradient": "linear-gradient(135deg, #a8edea 0%, #fed6e3 100%)"
        },
        "西餐": {
            "title": "🍝 Western Cuisine (Level C)",
            "date": "Second Half of 2024",
            "status": "Pending",
            "status_color": "#FF9800",
            "description": "Western cooking skills certification, including sauce making, meat processing, and classic Western cooking.",
            "gradient": "linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%)"
        },
        "調酒": {
            "title": "🍸 Bartending (Level B)",
            "date": "Second Half of 2024",
            "status": "Pending",
            "status_color": "#FF9800",
            "description": "Professional bartending skills certification, covering classic cocktail recipes, creative cocktails, and bar service techniques.",
            "gradient": "linear-gradient(135deg, #d299c2 0%, #fef9d7 100%)"
        }
    }
    
    # Display each certification category
    for category, info in licenses_info.items():
        st.markdown(f"""
        <div style='background: {info["gradient"]}; padding: 20px; border-radius: 15px; margin-bottom: 15px;'>
            <div style='display: flex; justify-content: space-between; align-items: center;'>
                <h2 style='margin: 0; color: #333;'>{info['title']}</h2>
                <span style='background: {info["status_color"]}; color: white; padding: 5px 15px; border-radius: 20px; font-weight: bold;'>{info['status']}</span>
            </div>
            <p style='color: #555; margin: 10px 0 5px 0;'>📅 <strong>Obtained</strong>: {info['date']}</p>
            <p style='color: #666; margin: 5px 0;'>{info['description']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Display images for this category
        if category in LICENSE_IMAGES and LICENSE_IMAGES[category]:
            images = LICENSE_IMAGES[category]
            
            # Display 4 images per row
            cols_per_row = 4
            for i in range(0, len(images), cols_per_row):
                cols = st.columns(cols_per_row)
                for j, col in enumerate(cols):
                    if i + j < len(images):
                        img_data = images[i + j]
                        with col:
                            st.markdown(
                                f'<div style="height: 200px; overflow: hidden; border-radius: 10px; margin-bottom: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">'
                                f'<img src="data:image/{img_data["ext"]};base64,{img_data["base64"]}" style="width:100%; height:100%; object-fit:cover;">'
                                f'</div>',
                                unsafe_allow_html=True
                            )
        else:
            st.info("📷 Loading images...")
        
        st.markdown("<br>", unsafe_allow_html=True)
    
    # Learning insights
    st.markdown("""
    <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 25px; border-radius: 15px; margin-top: 20px;'>
        <h2 style='color: white; text-align: center;'>💡 Learning Insights</h2>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); padding: 25px; border-radius: 15px; min-height: 180px;'>
            <h4 style='color: white; margin-top: 0;'>✨ Value of Cross-disciplinary Learning</h4>
            <ul style='color: #f0f0f0; margin-bottom: 0;'>
                <li>Cultivate different ways of thinking</li>
                <li>Enhance creativity and craftsmanship</li>
                <li>Stress relief and work-life balance</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); padding: 25px; border-radius: 15px; min-height: 180px;'>
            <h4 style='color: white; margin-top: 0;'>🚀 Attitude of Lifelong Learning</h4>
            <ul style='color: #f0f0f0; margin-bottom: 0;'>
                <li>Maintain curiosity for new things</li>
                <li>Challenge comfort zone, keep growing</li>
                <li>Treat learning as part of life</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

# Footer
st.markdown("""
---
<div style='text-align: center; padding: 20px;'>
    &copy; 2025 Patrick Liou | AI Enhanced Resume
</div>
""", unsafe_allow_html=True)
