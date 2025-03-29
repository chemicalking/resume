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
            return Image.open(image_path)
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
</style>
""", unsafe_allow_html=True)

# Sidebar navigation
with st.sidebar:
    page = st.radio(
        "Navigation",
        ["📊 Overview", "💼 Work Experience", "🎓 Education",
         "🛠️ Skills", "🌟 Personal Traits", "📈 Project Showcase",
         "🔬 Project Analysis"]
    )

# Main content area
if page == "📊 Overview":
    col1, col2 = st.columns([1, 2])

    with col1:
        profile_image = load_profile_image()
        if profile_image:
            st.image(profile_image, width=300, use_column_width=True)

    with col2:
        st.markdown("""
        <div class='profile-section'>
            <h1>Patrick Liou (劉晉亨)</h1>
            <h2>🤖 Senior Process Integration Engineer | AI & Big Data Expert</h2>

            <div class='skill-card'>
                <h3>🎯 Core Expertise</h3>
                <div class='tech-badges'>
                    <span class='tech-badge'>📊 Big Data Analytics</span>
                    <span class='tech-badge'>🤖 Machine Learning</span>
                    <span class='tech-badge'>🧠 Deep Learning</span>
                    <span class='tech-badge'>🔧 Process Integration</span>
                    <span class='tech-badge'>📈 Six Sigma</span>
                    <span class='tech-badge'>🏭 Smart Manufacturing</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

elif page == "💼 Work Experience":
    st.markdown("""
    <div class='experience-section'>
        <h2 class='section-header'>Work Experience</h2>

        <div class='experience-card'>
            <h3>Innolux Corporation</h3>
            <p class='highlight'>December 2014 - Present</p>
            <h4>Process Engineer / Team Leader</h4>
            <ul class='skill-list'>
                <li>Led smart factory initiatives, implementing Industry 4.0 solutions for significant production efficiency improvements</li>
                <li>Developed YOLOv4 defect detection models, reducing feedback time and increasing defect detection rate by 60%</li>
                <li>Led 3 Six Sigma projects, optimizing process parameters and reducing defect rate, saving NT$21 million annually</li>
                <li>Established intelligent early warning system, improving yield by 15%</li>
            </ul>
        </div>

        <div class='experience-card'>
            <h3>TSMC</h3>
            <p class='highlight'>March 2014 - December 2014</p>
            <h4>Equipment Engineer</h4>
            <ul class='skill-list'>
                <li>Optimized process tool parameters, improving yield and stability with 4% defect rate improvement</li>
                <li>Reduced system crash rate to 5%, enhancing equipment availability and capacity utilization</li>
                <li>Participated in next-generation process development</li>
            </ul>
        </div>

        <div class='experience-card'>
            <h3>Taiwan Cement Corporation</h3>
            <p class='highlight'>September 2013 - March 2014</p>
            <h4>Management Associate</h4>
            <ul class='skill-list'>
                <li>Monitored and optimized production processes, reducing bottleneck operation time by 15%</li>
                <li>Assisted in developing new PDA system to enhance process automation</li>
                <li>Implemented process control improvements resulting in better product quality</li>
            </ul>
        </div>

        <div class='experience-card'>
            <h3>Innolux Corporation</h3>
            <p class='highlight'>January 2010 - September 2013</p>
            <h4>Process Engineer</h4>
            <ul class='skill-list'>
                <li>Assisted in new factory setup, completing pilot production ahead of schedule</li>
                <li>Analyzed equipment failure causes and provided solutions, improving uptime by 25%</li>
                <li>Developed and implemented process control strategies</li>
            </ul>
        </div>

        <div class='skills-section'>
            <h3 class='section-header'>Core Competencies</h3>
            <div class='skill-ratings'>
                <div class='skill-item'>
                    <span class='skill-name'>Leadership</span>
                    <div class='skill-bar' style='width: 95%;'></div>
                </div>
                <div class='skill-item'>
                    <span class='skill-name'>Technical Innovation</span>
                    <div class='skill-bar' style='width: 90%;'></div>
                </div>
                <div class='skill-item'>
                    <span class='skill-name'>Project Management</span>
                    <div class='skill-bar' style='width: 92%;'></div>
                </div>
                <div class='skill-item'>
                    <span class='skill-name'>Problem Solving</span>
                    <div class='skill-bar' style='width: 88%;'></div>
                </div>
                <div class='skill-item'>
                    <span class='skill-name'>Team Collaboration</span>
                    <div class='skill-bar' style='width: 93%;'></div>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

elif page == "🎓 Education":
    st.markdown("""
    <div class='education-section'>
        <h2 class='section-header'>Education Background</h2>

        <div class='education-card'>
            <h3>National Chiao Tung University</h3>
            <p class='highlight'>September 2015 - January 2018</p>
            <h4>Master of Business Administration (MBA)</h4>
            <ul class='skill-list'>
                <li>Focus: Data Analytics & Business Intelligence</li>
                <li>Research: Digital Transformation in Manufacturing Industry</li>
                <li>Key Projects: Industry 4.0 Implementation Strategy</li>
                <li>GPA: 3.9/4.0</li>
            </ul>
        </div>

        <div class='education-card'>
            <h3>National Taiwan University</h3>
            <p class='highlight'>March 2015 - June 2017</p>
            <h4>Continuing Education in Law</h4>
            <ul class='skill-list'>
                <li>Focus: Business Law & Intellectual Property Rights</li>
                <li>Research: Technology Industry Legal Framework</li>
                <li>Key Topics: Patent Law, Trade Secrets, Labor Laws</li>
            </ul>
        </div>

        <div class='education-card'>
            <h3>National Taiwan University of Science and Technology</h3>
            <p class='highlight'>September 2006 - June 2008</p>
            <h4>Master of Chemical Engineering</h4>
            <ul class='skill-list'>
                <li>Focus: Process Control & Optimization</li>
                <li>Research: Advanced Process Control Systems</li>
                <li>Thesis: Development of Intelligent Process Control Algorithms</li>
                <li>GPA: 3.85/4.0</li>
            </ul>
        </div>

        <div class='education-card'>
            <h3>Feng Chia University</h3>
            <p class='highlight'>September 2002 - June 2006</p>
            <h4>Bachelor of Chemical Engineering</h4>
            <ul class='skill-list'>
                <li>Focus: Chemical Engineering Fundamentals</li>
                <li>Research: Process Automation & Control</li>
                <li>Senior Project: Design of Automated Control Systems</li>
                <li>GPA: 3.8/4.0</li>
            </ul>
        </div>
    </div>
    """, unsafe_allow_html=True)

elif page == "🛠️ Skills":
    st.markdown("""
    <div class='tech-section'>
        <h2 class='section-header'>Technical Skills</h2>

        <div class='skill-category'>
            <h3>🔧 Programming & Development</h3>
            <ul class='skill-list'>
                <li>Python (Pandas, NumPy, Scikit-learn, TensorFlow, PyTorch)</li>
                <li>Deep Learning & Computer Vision (YOLOv4, OpenCV)</li>
                <li>SQL & Database Management</li>
                <li>Git Version Control</li>
            </ul>
        </div>

        <div class='skill-category'>
            <h3>📊 Data Analytics</h3>
            <ul class='skill-list'>
                <li>Statistical Analysis & Data Mining</li>
                <li>Process Capability Analysis (Cp/Cpk)</li>
                <li>Design of Experiments (DOE)</li>
                <li>Time Series Analysis & Forecasting</li>
            </ul>
        </div>

        <div class='skill-category'>
            <h3>🏭 Manufacturing Excellence</h3>
            <ul class='skill-list'>
                <li>Six Sigma Black Belt</li>
                <li>Lean Manufacturing</li>
                <li>Industry 4.0 Implementation</li>
                <li>Equipment Performance Optimization</li>
            </ul>
        </div>

        <div class='skill-category'>
            <h3>👥 Soft Skills</h3>
            <ul class='skill-list'>
                <li>Cross-functional Team Leadership</li>
                <li>Project Management & Planning</li>
                <li>Technical Documentation & Presentation</li>
                <li>Mentoring & Knowledge Transfer</li>
            </ul>
        </div>
    </div>
    """, unsafe_allow_html=True)

elif page == "🌟 Personal Traits":
    st.markdown("""
    <div class='traits-section'>
        <h2 class='section-header'>Personal Traits</h2>

        <div class='trait-category'>
            <h3>🎯 Professional Drive</h3>
            <ul class='trait-list'>
                <li>Strong analytical mindset with attention to detail</li>
                <li>Results-oriented with focus on continuous improvement</li>
                <li>Proactive problem-solver with innovative thinking</li>
                <li>Quick learner adaptable to new technologies</li>
            </ul>
        </div>

        <div class='trait-category'>
            <h3>👥 Leadership Style</h3>
            <ul class='trait-list'>
                <li>Collaborative team player fostering positive work environment</li>
                <li>Effective communicator across all organizational levels</li>
                <li>Mentor focused on team growth and development</li>
                <li>Strategic thinker with clear goal setting</li>
            </ul>
        </div>

        <div class='trait-category'>
            <h3>🌱 Growth Mindset</h3>
            <ul class='trait-list'>
                <li>Passionate about emerging technologies</li>
                <li>Committed to continuous learning and improvement</li>
                <li>Open to feedback and new perspectives</li>
                <li>Resilient under pressure and deadlines</li>
            </ul>
        </div>
    </div>
    """, unsafe_allow_html=True)

elif page == "📈 Project Showcase":
    st.markdown("# 🤖 AI & Data Science Projects")

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

# Footer
st.markdown("""
---
<div style='text-align: center; padding: 20px;'>
    &copy; 2025 Patrick Liou | AI Enhanced Resume
</div>
""", unsafe_allow_html=True)
