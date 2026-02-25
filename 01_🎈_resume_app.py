import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image
from pathlib import Path
import datetime
import time
from streamlit_mermaid import st_mermaid
import base64

# 導入證照圖片 base64 資料
try:
    from license_images_data import LICENSE_IMAGES
except ImportError:
    LICENSE_IMAGES = {}

# 導入 LLM 圖片 base64 資料
try:
    from llm_images_data import LLM_IMAGES
except ImportError:
    LLM_IMAGES = {}

# 設定頁面為寬螢幕模式
st.set_page_config(
    page_title="劉晉亨個人履歷",
    page_icon="🎈",
    layout="wide",
    initial_sidebar_state="collapsed"  # 手機上預設收合側邊欄
)

# 自定義 CSS 樣式
st.markdown("""
<style>
    /* 主題設定 */
    :root {
        --primary-color: #4A90E2;
        --secondary-color: #50E3C2;
        --background-color: #FFFFFF;
        --text-color: #1A1F36;
        --highlight-color: #2C7BE5;
        --accent-color: #FF5A5F;
        --gradient-start: #6D5BBA;
        --gradient-end: #8D58BF;
        --glass-color: rgba(255, 255, 255, 0.9);
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

    /* 聯繫方式 */
    .stRadio > label {
        font-size: 2em !important;
        font-weight: 600 !important;
    }

    /* 技能標籤樣式 */
    .tech-badge {
        display: flex;
        align-items: center;
        padding: 0.8rem 1.2rem;
        background: white;
        border-radius: 50px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.05);
        transition: all 0.3s ease;
        cursor: pointer;
        border: 2px solid rgba(74, 144, 226, 0.1);
        font-size: 1.2rem;
    }

    .tech-badge:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 16px rgba(0,0,0,0.1);
        border-color: rgba(74, 144, 226, 0.2);
    }

    .tech-badge .icon {
        font-size: 1.5rem;
        margin-right: 0.8rem;
    }

    .tech-badge .text {
        font-weight: 500;
        color: var(--text-color);
    }

    .tech-badge[data-type="data"] {
        border-color: rgba(74, 144, 226, 0.5);
    }

    .tech-badge[data-type="ai"] {
        border-color: rgba(80, 227, 194, 0.5);
    }

    .tech-badge[data-type="process"] {
        border-color: rgba(255, 152, 0, 0.5);
    }

    /* 技能標籤容器 */
    .tech-badges {
        display: flex;
        flex-wrap: wrap;
        gap: 1rem;
        margin: 2rem 0;
        justify-content: center;
    }

    /* 個人資料區塊樣式 */
    .profile-section {
        background: white;
        padding: 3rem;
        border-radius: 20px;
        box-shadow: 0 15px 30px rgba(0,0,0,0.08);
        margin-bottom: 2.5rem;
        border-left: 5px solid var(--gradient-start);
        position: relative;
        overflow: hidden;
    }

    .profile-section::before {
        content: '';
        position: absolute;
        top: 0;
        right: 0;
        width: 150px;
        height: 150px;
        background: linear-gradient(135deg, var(--gradient-start), var(--gradient-end));
        opacity: 0.05;
        border-radius: 0 0 0 100%;
    }

    .profile-section h1 {
        font-size: 3.5rem;
        margin-bottom: 1rem;
        background: linear-gradient(45deg, var(--primary-color), var(--accent-color));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        display: inline-block;
    }

    .profile-section .highlight {
        background: linear-gradient(45deg, var(--gradient-start), var(--gradient-end));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700;
    }

    .profile-section h2 {
        font-size: 2.2rem;
        color: #555;
        margin-bottom: 2rem;
        position: relative;
        padding-left: 15px;
    }

    .profile-section h2::before {
        content: '';
        position: absolute;
        left: 0;
        top: 0;
        height: 100%;
        width: 5px;
        background: linear-gradient(to bottom, var(--primary-color), var(--secondary-color));
        border-radius: 10px;
    }

    /* 技能卡片樣式 */
    .skill-card {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.08);
        margin: 1.5rem 0;
        width: 100%;
        border: 2px solid rgba(74, 144, 226, 0.1);
        position: relative;
        overflow: hidden;
        transition: all 0.3s ease;
    }

    .skill-card::before {
        content: '';
        position: absolute;
        top: 0;
        right: 0;
        width: 100%;
        height: 100%;
        background: linear-gradient(135deg, rgba(74, 144, 226, 0.05), rgba(80, 227, 194, 0.05));
        opacity: 0;
        transition: opacity 0.3s ease;
    }

    .skill-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 40px rgba(0,0,0,0.1);
        border-color: rgba(74, 144, 226, 0.2);
    }

    .skill-card:hover::before {
        opacity: 1;
    }

    .skill-card h3 {
        color: var(--primary-color);
        margin-bottom: 1.5rem;
        position: relative;
        display: inline-block;
        font-size: 1.8rem;
    }

    .skill-card h3::after {
        content: '';
        position: absolute;
        bottom: -10px;
        left: 0;
        width: 40px;
        height: 3px;
        background: linear-gradient(to right, var(--primary-color), var(--secondary-color));
        border-radius: 10px;
    }

    /* 聯繫方式樣式 */
    .contact-section {
        margin-top: 1.5rem;
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
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 8px 16px rgba(0,0,0,0.1);
        margin-bottom: 1.5rem;
        border: 2px solid #E3F2FD;
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

    /* 技能區塊樣式 */
    .skill-section {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 2rem;
        margin-top: 2rem;
    }

    /* 技能標籤樣式 */
    .tech-badge {
        display: flex;
        align-items: center;
        padding: 0.8rem 1.2rem;
        background: white;
        border-radius: 50px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.05);
        transition: all 0.3s ease;
        cursor: pointer;
        border: 2px solid rgba(74, 144, 226, 0.1);
        font-size: 1.2rem;
        width: 100%;
    }

    .tech-badge:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 16px rgba(0,0,0,0.1);
        border-color: rgba(74, 144, 226, 0.2);
    }

    .tech-badge .icon {
        font-size: 1.5rem;
        margin-right: 0.8rem;
    }

    .tech-badge .text {
        font-weight: 500;
        color: var(--text-color);
    }

    .tech-badge[data-type="data"] {
        border-color: rgba(74, 144, 226, 0.5);
    }

    .tech-badge[data-type="ai"] {
        border-color: rgba(80, 227, 194, 0.5);
    }

    .tech-badge[data-type="process"] {
        border-color: rgba(255, 152, 0, 0.5);
    }

    /* 技能標籤容器 */
    .tech-badges {
        display: flex;
        flex-direction: column;
        gap: 1rem;
        margin: 2rem 0;
    }

    /* ========== 手機響應式設計 ========== */
    
    /* 小螢幕裝置 (max-width: 768px) */
    @media screen and (max-width: 768px) {
        /* 隱藏側邊欄，避免遮擋主內容 */
        [data-testid="stSidebar"] {
            display: none !important;
        }
        
        /* 展開時的側邊欄樣式 */
        [data-testid="stSidebar"][aria-expanded="true"] {
            display: block !important;
            position: fixed !important;
            top: 0 !important;
            left: 0 !important;
            width: 85% !important;
            max-width: 300px !important;
            height: 100vh !important;
            z-index: 9999 !important;
            background: white !important;
            box-shadow: 2px 0 10px rgba(0,0,0,0.2) !important;
        }
        
        /* 主內容區域 - 確保不被遮擋 */
        .main .block-container {
            padding: 1rem 0.8rem !important;
            max-width: 100% !important;
            margin-left: 0 !important;
        }
        
        /* 確保主內容佔滿寬度 */
        .main {
            margin-left: 0 !important;
            width: 100% !important;
        }
        
        /* 移除左邊的空白 */
        section[data-testid="stSidebarContent"] {
            padding: 1rem !important;
        }
        
        /* 標題字體調整 */
        h1 {
            font-size: 1.5rem !important;
        }
        h2 {
            font-size: 1.3rem !important;
        }
        h3 {
            font-size: 1.1rem !important;
        }
        
        /* 個人資料區塊 */
        .profile-section {
            padding: 1.5rem !important;
        }
        .profile-section h1 {
            font-size: 1.8rem !important;
        }
        .profile-section h2 {
            font-size: 1.2rem !important;
        }
        
        /* 卡片樣式調整 */
        .skill-card, .education-card, .experience-card {
            padding: 1rem !important;
            margin: 0.5rem 0 !important;
        }
        
        /* 技能標籤 */
        .tech-badge {
            padding: 0.5rem 0.8rem !important;
            font-size: 0.9rem !important;
        }
        .tech-badge .icon {
            font-size: 1.2rem !important;
            margin-right: 0.5rem !important;
        }
        
        /* Streamlit 列調整 - 讓列變成垂直堆疊 */
        [data-testid="column"] {
            width: 100% !important;
            flex: 1 1 100% !important;
            min-width: 100% !important;
        }
        
        /* 圖片調整 */
        img {
            max-width: 100% !important;
            height: auto !important;
        }
        
        /* LLM 圖示區調整 */
        [data-testid="column"] > div > div {
            min-height: auto !important;
        }
        
        /* 文字大小調整 */
        p, li {
            font-size: 0.95rem !important;
            line-height: 1.5 !important;
        }
        
        /* 表格調整 */
        table {
            font-size: 0.8rem !important;
        }
        
        /* Plotly 圖表調整 */
        .js-plotly-plot {
            width: 100% !important;
        }
        
        /* 專案卡片 - 確保內容不溢出 */
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
        
        /* 五大功能圖示調整 */
        div[style*="width: 100px"] {
            width: 60px !important;
            height: 60px !important;
            padding: 8px !important;
        }
        div[style*="width: 100px"] img {
            width: 40px !important;
            height: 40px !important;
        }
        
        /* 證照圖片調整 */
        div[style*="border-radius: 15px"] img {
            max-height: 150px !important;
        }
    }
    
    /* 超小螢幕 (max-width: 480px) */
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
        
        /* 核心技術平台卡片 */
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
    
    /* 平板裝置調整 (768px - 1024px) */
    @media screen and (min-width: 769px) and (max-width: 1024px) {
        .main .block-container {
            padding: 1.5rem 1rem !important;
        }
        
        /* 允許兩列顯示 */
        [data-testid="column"] {
            min-width: 45% !important;
        }
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

# 圖片處理函數
def load_profile_image():
    try:
        img_path = Path("PHOTO.jpg")
        if img_path.exists():
            return str(img_path)
        else:
            st.warning(f"無法找到圖片：{img_path}")
            return None
    except Exception as e:
        st.warning(f"載入圖片時發生錯誤：{str(e)}")
        return None

# 側邊欄設置
with st.sidebar:
    st.markdown("### 🎯 導航菜單")
    page = st.radio(
        "",
        ["📊 個人總覽", "💼 專業經歷", "🎓 教育背景", "🛠️ 技能專長",
         "🌟 個人特質", "📈 專案展示", "🔬 專案分析", "🏆 證照展示"],
        key="navigation_menu"
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

# 添加標題
st.markdown("""
<h1 style='text-align: center; color: var(--primary-color);'>
    劉晉亨的個人簡歷 | Patrick Liou Resume
</h1>
""", unsafe_allow_html=True)

st.markdown("""
<div style='background-color: #FF5252; color: white; padding: 2rem; border-radius: 8px; margin-bottom: 1.5rem; border: 4px solid #B71C1C; box-shadow: 0 4px 8px rgba(0,0,0,0.2); font-weight: bold; font-size: 2em; text-align: center;'>
    ⚠️ 若需英文面試或加班請 pass | If you need an interview in English or work overtime, please pass ⚠️
</div>
""", unsafe_allow_html=True)

# 主要內容區域
if page == "📊 個人總覽":
    col1, col2 = st.columns([1, 2])

    with col1:
        profile_image = load_profile_image()
        if profile_image:
            st.image(profile_image, width=300)

    with col2:
        st.markdown("# 劉晉亨 Patrick Liou")
        st.markdown("### 🤖 資深製程整合工程師 | AI與大數據專家")
        
        st.markdown("---")
        
        # 核心專長
        st.markdown("#### 🎯 核心專長")
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.info("💻 大數據分析")
        with col_b:
            st.info("🤖 機器學習")
        with col_c:
            st.info("🧠 深度學習")
        
        col_d, col_e, col_f = st.columns(3)
        with col_d:
            st.warning("💬 大語言模型(LLM)")
        with col_e:
            st.warning("🔍 RAG 應用")
        with col_f:
            st.warning("🎤 語音辨識")
        
        # 專業技能
        st.markdown("#### 🎯 專業技能")
        col_g, col_h, col_i = st.columns(3)
        with col_g:
            st.success("🔩 製程整合")
        with col_h:
            st.success("📈 六標準差")
        with col_i:
            st.success("🏭 智能工廠")


elif page == "💼 專業經歷":
    col1, col2 = st.columns([2, 1])

    with col1:
        # 群創光電 (現職)
        with st.container():
            st.markdown("### 🏢 群創光電 (Innolux Corporation)")
            st.markdown("**2014年12月 - 至今** | 製程工程師 / Team Leader")
            st.markdown("""
            - 領導智能工廠專案，成功導入工業4.0解決方案，顯著提升生產效率
            - 開發YOLOv4缺陷檢測模型，縮短反饋時間並提高缺陷檢出率60%
            - 主導3項六標準差專案，優化製程參數並降低產品次品率，節省2100萬台幣/年
            - 建立大語言模型(LLM)智能應用系統，實現跨資料庫查詢與異常分析，資料整理時間縮短92%
            - 開發 AI 自動化機況分類與 RPSC 數據分析系統，提升異常處理效率
            - 導入 Whisper 語音辨識系統，實現會議記錄自動化與智能摘要
            """)
        
        st.divider()
        
        # 台積電
        with st.container():
            st.markdown("### 🏢 台積電 (TSMC)")
            st.markdown("**2014年3月 - 2014年12月** | 設備工程師")
            st.markdown("""
            - 優化製程工具參數，提升產量與穩定性，缺陷率改善4%
            - 減少系統崩潰率至5%，提升設備可用性與產能利用率
            """)
        
        st.divider()
        
        # 台灣水泥
        with st.container():
            st.markdown("### 🏢 台灣水泥 (Taiwan Cement Corp)")
            st.markdown("**2013年9月 - 2014年3月** | 儲備幹部(MA)")
            st.markdown("""
            - 負責生產流程監控與優化，縮短瓶頸工序時間15%
            - 協助開發新PDA系統，提高製程自動化程度
            """)
        
        st.divider()
        
        # 群創光電 (早期)
        with st.container():
            st.markdown("### 🏢 群創光電 (Innolux Corporation)")
            st.markdown("**2010年1月 - 2013年9月** | 製程工程師")
            st.markdown("""
            - 協助建置新廠，完成試量產並縮短建廠時程30%
            - 分析設備故障原因並提供解決方案，提高設備稼動率25%
            """)

    with col2:
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

        # 添加職涯發展歷程
        st.markdown("### 職涯發展歷程")
        career_chart = """
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
        """
        st_mermaid(career_chart)

        st.markdown("### 核心能力成長")
        core_skills_chart = """
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
        """
        st_mermaid(core_skills_chart)

elif page == "🎓 教育背景":
    col1, col2 = st.columns([2, 1])

    with col1:
        # 台灣人工智慧學校 - AI技術領袖班 (最新)
        with st.container():
            st.markdown("### 🤖 台灣人工智慧學校")
            st.markdown("**2020年 - 2021年** | AI技術領袖班")
            st.markdown("""
            - 深度學習與神經網路架構設計
            - AI專案管理與團隊領導
            - 產業AI應用實戰
            """)
        
        st.divider()
        
        # 台灣人工智慧學校 - AI經理人研修班
        with st.container():
            st.markdown("### 🤖 台灣人工智慧學校")
            st.markdown("**2018年 - 2019年** | AI經理人研修班")
            st.markdown("""
            - 機器學習與資料科學基礎
            - AI策略規劃與商業應用
            - 數位轉型與創新管理
            """)
        
        st.divider()
        
        # 交通大學
        with st.container():
            st.markdown("### 🎓 國立交通大學")
            st.markdown("**2015年9月 - 2018年1月** | 管理科學碩士（MBA）")
            st.markdown("""
            - 專業課程：數據分析與商業智慧、營運管理與策略規劃、專案管理與領導力
            - 研究方向：製造業數位轉型與AI應用
            """)
        
        st.divider()
        
        # 台灣大學
        with st.container():
            st.markdown("### 🎓 國立台灣大學")
            st.markdown("**2015年3月 - 2017年6月** | 持續教育法律課程")
            st.markdown("""
            - 專業課程：商業法律、智慧財產權、勞動法規
            - 研究方向：科技產業法律實務應用
            """)
        
        st.divider()
        
        # 台科大
        with st.container():
            st.markdown("### 🎓 國立台灣科技大學")
            st.markdown("**2006年9月 - 2008年6月** | 化學工程碩士")
            st.markdown("""
            - 專業課程：化工單元操作、反應工程、程序控制
            - 研究方向：製程最佳化與控制
            """)
        
        st.divider()
        
        # 逢甲大學
        with st.container():
            st.markdown("### 🎓 逢甲大學")
            st.markdown("**2002年9月 - 2006年6月** | 化學工程學士")
            st.markdown("""
            - 專業課程：化工原理、物理化學、化工熱力學
            - 專題研究：製程監控與自動化
            """)

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
        st.markdown("### 學習歷程")
        education_chart = """
        graph TD
            A[逢甲大學<br>化工學士] --> B[台科大<br>化工碩士]
            B --> C[台大<br>法律課程]
            C --> D[交大<br>管理碩士]
            D --> E[台灣AI學校<br>經理人班]
            E --> F[台灣AI學校<br>技術領袖班]

            style A fill:#f9f,stroke:#333,stroke-width:4px
            style B fill:#bbf,stroke:#333,stroke-width:4px
            style C fill:#ddf,stroke:#333,stroke-width:4px
            style D fill:#dfd,stroke:#333,stroke-width:4px
            style E fill:#ffd,stroke:#333,stroke-width:4px
            style F fill:#fdd,stroke:#333,stroke-width:4px
        """
        st_mermaid(education_chart)

        # 添加專業技能評分
        st.markdown("### 專業技能評分")
        col1, col2, col3 = st.columns(3)

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
        
        with col3:
            st.markdown("#### AI/LLM 應用")
            st.progress(0.88)
            st.markdown("#### Vibe Coding")
            st.progress(0.85)

elif page == "🛠️ 技能專長":
    st.markdown("## 🛠️ 技能專長")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.info("#### 🔧 技術工具")
        st.markdown("""
        - 💻 Python
        - 🤖 深度學習
        - 🔩 AutoML
        - 📊 數據分析
        - 📈 六標準差
        - 🏭 智能工廠
        """)
    
    with col2:
        st.success("#### 💡 製程專長")
        st.markdown("""
        - 🔧 半導體製程
        - 📊 製程參數分析
        - 🎯 良率提升
        - 🔩 設備監控
        """)
    
    with col3:
        st.warning("#### 📈 數據分析")
        st.markdown("""
        - 📊 統計分析
        - 📉 製程能力分析
        - 🎯 六標準差
        """)
    
    with col4:
        st.error("#### 🤖 AI & LLM 專長")
        st.markdown("""
        - 💬 大語言模型 (LLM)
        - 🎵 Vibe Coding
        - 🔍 RAG 應用開發
        - 🎤 Whisper 語音辨識
        - 🦜 LangChain/LangFlow
        - 🧠 Prompt Engineering
        """)

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

    # 三個 Mermaid 圖表並排顯示
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 職涯發展歷程")
        career_chart = """
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
        """
        st_mermaid(career_chart)
    
    with col2:
        st.markdown("### 核心能力成長")
        core_skills_chart = """
        graph TD
            A[數據處理] --> B[數據分析]
            B --> C[AI預測]
            A --> D[資產提升]
            D --> E[智能製造]
            C --> E

            style A fill:#f9f,stroke:#333,stroke-width:4px
            style B fill:#bbf,stroke:#333,stroke-width:4px
            style C fill:#ddf,stroke:#333,stroke-width:4px
            style D fill:#fdd,stroke:#333,stroke-width:4px
            style E fill:#dfd,stroke:#333,stroke-width:4px
        """
        st_mermaid(core_skills_chart)
    
    with col3:
        st.markdown("### 學習歷程")
        education_chart = """
        graph TD
            A[逢甲大學<br>化工學士] --> B[台科大<br>化工碩士]
            B --> C[台大<br>法律課程]
            C --> D[交大<br>管理碩士]
            D --> E[台灣AI學校<br>經理人班]
            E --> F[台灣AI學校<br>技術領袖班]

            style A fill:#f9f,stroke:#333,stroke-width:4px
            style B fill:#bbf,stroke:#333,stroke-width:4px
            style C fill:#ddf,stroke:#333,stroke-width:4px
            style D fill:#dfd,stroke:#333,stroke-width:4px
            style E fill:#ffd,stroke:#333,stroke-width:4px
            style F fill:#fdd,stroke:#333,stroke-width:4px
        """
        st_mermaid(education_chart)

elif page == "🌟 個人特質":
    st.markdown("## 🌟 個人特質")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info("#### 🎯 領導力與團隊合作")
        st.markdown("""
        - 具備優秀的團隊領導能力
        - 良好的溝通技巧
        - 具有同理心
        """)
        
        st.success("#### 💡 專業素養")
        st.markdown("""
        - 高度責任感
        - 注重細節
        - 追求卓越
        """)
    
    with col2:
        st.warning("#### 🚀 學習與創新")
        st.markdown("""
        - 持續學習的熱情
        - 創新思維
        - 解決問題的能力
        """)
        
        st.info("#### 🤝 團隊精神")
        st.markdown("""
        - 良好的團隊合作
        - 積極主動
        - 樂於分享
        """)

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
    # 模擬數據
    projects = ["📊良率優化", "🔬氣體監控", "🤖製程分析", "🔧設備監控", "📈品質管制", "📧異常解析", "📈數據分析"]
    progress = [85, 90, 80, 75, 88, 70, 95]

    # 創建條形圖展示項目進度
    st.markdown("## 專案進度概覽")
    # 使用 Plotly 替代 Matplotlib
    fig = px.bar(
        x=progress,
        y=projects,
        orientation='h',
        labels={"x": "進度完成百分比 (%)", "y": "專案名稱"}
    )
    fig.update_layout(
        xaxis_range=[0, 100],
        height=450,
        margin=dict(l=20, r=50, t=30, b=50),
        font=dict(size=14),
        yaxis=dict(tickfont=dict(size=14)),
        xaxis=dict(tickfont=dict(size=12), title_font=dict(size=14))
    )
    # 添加標籤
    fig.update_traces(
        texttemplate='%{x}%',
        textposition='outside',
        textfont=dict(size=14),
        marker_color='rgba(74, 144, 226, 0.7)',
        hoverinfo='text',
        hovertext=[f"{p}: {v}%" for p, v in zip(projects, progress)]
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # LLM 大語言模型應用專案
    st.markdown("---")
    
    # 大標題區塊
    st.markdown("""
    <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; border-radius: 15px; margin-bottom: 25px; text-align: center;'>
        <h1 style='color: white; margin: 0;'>🤖 大語言模型技術與展望</h1>
        <p style='color: #f0f0f0; margin-top: 10px; font-size: 1.2em;'>
            語意分析 | 圖片分析 | 數據分析 | 資料庫查詢 | 語音辨識
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # LLM 核心技術圖示區 - 使用 PPT 圖片
    st.markdown("### 🧠 核心技術平台")
    
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
            <p style='color: #aaa; margin: 10px 0 0 0;'>本機運行開源 LLM</p>
            <p style='color: #888; font-size: 0.85em;'>Llama / Mistral / Gemma</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        img_html = f'<img src="data:image/png;base64,{innogpt_img}" style="width:120px; height:120px; object-fit:contain;">' if innogpt_img else '<div style="font-size: 4em;">🧠</div>'
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%); padding: 25px; border-radius: 15px; text-align: center; border: 2px solid #10a37f;'>
            {img_html}
            <h3 style='color: #10a37f; margin: 10px 0 0 0;'>INNO GPT</h3>
            <p style='color: #aaa; margin: 10px 0 0 0;'>企業內部 API</p>
            <p style='color: #888; font-size: 0.85em;'>RAG / 圖片分析 / 數據處理</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); padding: 25px; border-radius: 15px; text-align: center; border: 2px solid #ff6b6b;'>
            <div style='font-size: 4em; margin-bottom: 10px;'>🎙️</div>
            <h3 style='color: #ff6b6b; margin: 0;'>Whisper</h3>
            <p style='color: #aaa; margin: 10px 0 0 0;'>OpenAI 語音辨識</p>
            <p style='color: #888; font-size: 0.85em;'>會議紀錄 / 語音轉文字</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 五大功能圖示 - 使用 PPT Slide 1 的圖示
    st.markdown("### ⚡ 五大 AI 應用功能")
    
    # 取得五大功能圖示
    icon1 = LLM_IMAGES.get("slide1_img1", {}).get("base64", "")  # 語意分析
    icon2 = LLM_IMAGES.get("slide1_img6", {}).get("base64", "")  # 圖片分析
    icon3 = LLM_IMAGES.get("slide1_img3", {}).get("base64", "")  # 數據分析
    icon4 = LLM_IMAGES.get("slide1_img4", {}).get("base64", "")  # 資料庫查詢
    icon5 = LLM_IMAGES.get("slide1_img2", {}).get("base64", "")  # 語音辨識
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        img_html = f'<img src="data:image/png;base64,{icon1}" style="width:70px; height:70px; object-fit:contain;">' if icon1 else '<span style="font-size: 2.5em;">🗣️</span>'
        st.markdown(f"""
        <div style='text-align: center;'>
            <div style='background: linear-gradient(180deg, #667eea 0%, #764ba2 100%); padding: 15px; border-radius: 15px; width: 100px; height: 100px; margin: 0 auto; display: flex; align-items: center; justify-content: center;'>
                {img_html}
            </div>
            <p style='color: #667eea; font-weight: bold; margin-top: 10px;'>語意分析</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        img_html = f'<img src="data:image/png;base64,{icon2}" style="width:70px; height:70px; object-fit:contain;">' if icon2 else '<span style="font-size: 2.5em;">🖼️</span>'
        st.markdown(f"""
        <div style='text-align: center;'>
            <div style='background: linear-gradient(180deg, #f093fb 0%, #f5576c 100%); padding: 15px; border-radius: 15px; width: 100px; height: 100px; margin: 0 auto; display: flex; align-items: center; justify-content: center;'>
                {img_html}
            </div>
            <p style='color: #f5576c; font-weight: bold; margin-top: 10px;'>圖片分析</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        img_html = f'<img src="data:image/png;base64,{icon3}" style="width:70px; height:70px; object-fit:contain;">' if icon3 else '<span style="font-size: 2.5em;">📊</span>'
        st.markdown(f"""
        <div style='text-align: center;'>
            <div style='background: linear-gradient(180deg, #11998e 0%, #38ef7d 100%); padding: 15px; border-radius: 15px; width: 100px; height: 100px; margin: 0 auto; display: flex; align-items: center; justify-content: center;'>
                {img_html}
            </div>
            <p style='color: #11998e; font-weight: bold; margin-top: 10px;'>數據分析</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        img_html = f'<img src="data:image/png;base64,{icon4}" style="width:70px; height:70px; object-fit:contain;">' if icon4 else '<span style="font-size: 2.5em;">🗄️</span>'
        st.markdown(f"""
        <div style='text-align: center;'>
            <div style='background: linear-gradient(180deg, #4facfe 0%, #00f2fe 100%); padding: 15px; border-radius: 15px; width: 100px; height: 100px; margin: 0 auto; display: flex; align-items: center; justify-content: center;'>
                {img_html}
            </div>
            <p style='color: #4facfe; font-weight: bold; margin-top: 10px;'>資料庫查詢</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col5:
        img_html = f'<img src="data:image/png;base64,{icon5}" style="width:70px; height:70px; object-fit:contain;">' if icon5 else '<span style="font-size: 2.5em;">🎤</span>'
        st.markdown(f"""
        <div style='text-align: center;'>
            <div style='background: linear-gradient(180deg, #fa709a 0%, #fee140 100%); padding: 15px; border-radius: 15px; width: 100px; height: 100px; margin: 0 auto; display: flex; align-items: center; justify-content: center;'>
                {img_html}
            </div>
            <p style='color: #fa709a; font-weight: bold; margin-top: 10px;'>語音辨識</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 📦 應用專案詳情")
    
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
            <h3 style='color: white; margin-top: 0;'>🔧 機況報表智能分類</h3>
            <p style='color: #e0ffe0; font-size: 0.9em;'><strong>技術: OLLAMA 本機運行</strong></p>
            <ul style='color: #f0f0f0; font-size: 0.95em;'>
                <li>讀取機況內容自動分類狀態</li>
                <li>機況報表智能查詢</li>
                <li>自動存入資料庫</li>
            </ul>
            <p style='color: #ffeb3b; font-size: 0.9em;'>💡 解決: 機況分散不易查詢</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        img_html = f'<img src="data:image/png;base64,{ollama_card_img}" style="width:80px; height:80px; object-fit:contain; float:right;">' if ollama_card_img else ''
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); padding: 20px; border-radius: 15px; min-height: 280px;'>
            {img_html}
            <h3 style='color: white; margin-top: 0;'>📝 Release Table 分析</h3>
            <p style='color: #e0f7ff; font-size: 0.9em;'><strong>技術: OLLAMA 本機運行</strong></p>
            <ul style='color: #f0f0f0; font-size: 0.95em;'>
                <li>讀取 COMMENT 內容分類狀態</li>
                <li>Release Table 報表分析查詢</li>
                <li>自動存入資料庫</li>
            </ul>
            <p style='color: #ffeb3b; font-size: 0.9em;'>💡 解決: 值班COMMENT雜亂無序</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        img_html = f'<img src="data:image/png;base64,{innogpt_card_img}" style="width:80px; height:80px; object-fit:contain; float:right;">' if innogpt_card_img else ''
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); padding: 20px; border-radius: 15px; min-height: 280px;'>
            {img_html}
            <h3 style='color: white; margin-top: 0;'>🎯 當機產品 AI 處理 (RAG)</h3>
            <p style='color: #ffe0f0; font-size: 0.9em;'><strong>技術: INNO GPT</strong></p>
            <ul style='color: #f0f0f0; font-size: 0.95em;'>
                <li>工程師歷史處理異常資料</li>
                <li>AI 分析與識別 LOG 資料</li>
                <li>提出有效後續處理建議</li>
            </ul>
            <p style='color: #ffeb3b; font-size: 0.9em;'>💡 自動化異常處理流程</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col4, col5, col6 = st.columns(3)
    
    with col4:
        img_html = f'<img src="data:image/png;base64,{innogpt_card_img}" style="width:80px; height:80px; object-fit:contain; float:right;">' if innogpt_card_img else ''
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); padding: 20px; border-radius: 15px; min-height: 280px;'>
            {img_html}
            <h3 style='color: #333; margin-top: 0;'>📊 RPSC 數據分析</h3>
            <p style='color: #555; font-size: 0.9em;'><strong>技術: INNO GPT API</strong></p>
            <ul style='color: #444; font-size: 0.95em;'>
                <li>RPSC RAW DATA 繪製 Trend Chart</li>
                <li>餵圖給 GPT 分析</li>
                <li>參考 RULE 找出 EP</li>
                <li>數據清理與自動分析</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col5:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%); padding: 20px; border-radius: 15px; min-height: 280px;'>
            <h3 style='color: #333; margin-top: 0;'>🎤 會議語音紀錄</h3>
            <p style='color: #555; font-size: 0.9em;'><strong>技術: Whisper 語音辨識</strong></p>
            <ul style='color: #444; font-size: 0.95em;'>
                <li>會議語音自動紀錄</li>
                <li>智能會議整理</li>
                <li>重點摘要生成</li>
            </ul>
            <p style='color: #e91e63; font-size: 0.9em;'>💡 會議效率大幅提升</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col6:
        # 同時顯示 OLLAMA 和 INNO GPT 圖片
        img_html1 = f'<img src="data:image/png;base64,{innogpt_card_img}" style="width:60px; height:60px; object-fit:contain;">' if innogpt_card_img else ''
        img_html2 = f'<img src="data:image/png;base64,{ollama_card_img}" style="width:60px; height:60px; object-fit:contain;">' if ollama_card_img else ''
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 15px; min-height: 280px;'>
            <div style='float:right;'>{img_html1}{img_html2}</div>
            <h3 style='color: white; margin-top: 0;'>🔍 跨資料庫智能查詢</h3>
            <p style='color: #e0e0ff; font-size: 0.9em;'><strong>技術: GPT/OLLAMA 生成 SQL</strong></p>
            <ul style='color: #f0f0f0; font-size: 0.95em;'>
                <li>Yield/機況/Release 限制查詢</li>
                <li>跨資料庫異常分析</li>
                <li>報表呈現與自動存檔</li>
            </ul>
            <p style='color: #ffeb3b; font-size: 0.9em;'>💡 查詢時間 1HR → 5min</p>
        </div>
        """, unsafe_allow_html=True)
    
    # 專案效益總覽
    st.markdown("---")
    st.markdown("""
    <div style='background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%); padding: 20px; border-radius: 15px; margin-bottom: 20px;'>
        <h2 style='color: #333; text-align: center; margin: 0;'>📈 專案效益總覽 - 提質、增效、降本、減存</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # 效益指標卡片
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div style='background: #4CAF50; padding: 20px; border-radius: 15px; text-align: center;'>
            <h1 style='color: white; margin: 0; font-size: 2.5em;'>92%</h1>
            <p style='color: #e8f5e9; margin: 5px 0 0 0;'>效率提升</p>
            <p style='color: #c8e6c9; font-size: 0.8em;'>1 HR → 5 min</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style='background: #2196F3; padding: 20px; border-radius: 15px; text-align: center;'>
            <h1 style='color: white; margin: 0; font-size: 2.5em;'>6</h1>
            <p style='color: #e3f2fd; margin: 5px 0 0 0;'>AI 應用專案</p>
            <p style='color: #bbdefb; font-size: 0.8em;'>持續擴展中</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style='background: #FF9800; padding: 20px; border-radius: 15px; text-align: center;'>
            <h1 style='color: white; margin: 0; font-size: 2.5em;'>3</h1>
            <p style='color: #fff3e0; margin: 5px 0 0 0;'>技術平台</p>
            <p style='color: #ffe0b2; font-size: 0.8em;'>OLLAMA/GPT/Whisper</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div style='background: #9C27B0; padding: 20px; border-radius: 15px; text-align: center;'>
            <h1 style='color: white; margin: 0; font-size: 2.5em;'>∞</h1>
            <p style='color: #f3e5f5; margin: 5px 0 0 0;'>應用潛力</p>
            <p style='color: #e1bee7; font-size: 0.8em;'>製造業智能轉型</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    # 效益比較圖表
    benefit_data = {
        "專案名稱": ["跨資料庫查詢", "機況報表分類", "Release Table 分析", "RPSC 數據分析"],
        "原始耗時": [60, 60, 45, 30],
        "優化後耗時": [5, 5, 5, 5],
    }
    
    fig = go.Figure(data=[
        go.Bar(name='原始耗時 (分鐘)', x=benefit_data["專案名稱"], y=benefit_data["原始耗時"], 
               marker_color='rgba(255, 99, 71, 0.7)', text=benefit_data["原始耗時"], textposition='outside'),
        go.Bar(name='優化後耗時 (分鐘)', x=benefit_data["專案名稱"], y=benefit_data["優化後耗時"], 
               marker_color='rgba(60, 179, 113, 0.7)', text=benefit_data["優化後耗時"], textposition='outside')
    ])
    
    fig.update_layout(
        barmode='group',
        xaxis_title="專案名稱",
        yaxis_title="耗時 (分鐘)",
        height=400,
        font=dict(size=14),
        legend=dict(font=dict(size=14)),
        margin=dict(t=30)
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # 技術架構圖
    st.markdown("### 🏗️ 技術架構")
    llm_architecture = """
    graph TD
        A[數據來源] --> B[大語言模型]
        B --> C[OLLAMA 本機運行]
        B --> D[INNO GPT API]
        B --> E[Whisper 語音]
        C --> F[機況分類]
        C --> G[Release分析]
        D --> H[RAG 處理]
        D --> I[RPSC 分析]
        E --> J[會議紀錄]
        F --> K[資料庫]
        G --> K
        H --> K
        I --> K
        J --> K
        K --> L[報表呈現]
        
        style A fill:#f9f,stroke:#333,stroke-width:2px
        style B fill:#bbf,stroke:#333,stroke-width:2px
        style K fill:#dfd,stroke:#333,stroke-width:2px
        style L fill:#fdd,stroke:#333,stroke-width:2px
    """
    st_mermaid(llm_architecture)

elif page == "🔬 專案分析":
    st.markdown("# 進階數據分析")
    
    # LLM 大語言模型技術展示
    st.markdown("## 🤖 大語言模型技術與展望")
    
    st.markdown("""
    運用大語言模型技術，整合多元功能實現製造業智能化轉型：
    """)
    
    # LLM 核心功能展示
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("#### 🗣️ 語意分析")
        st.markdown("自然語言處理與理解")
    with col2:
        st.success("#### 🖼️ 圖片分析")
        st.markdown("視覺識別與缺陷檢測")
    with col3:
        st.warning("#### 📊 數據分析")
        st.markdown("智能數據處理與洞察")
    
    col4, col5, col6 = st.columns(3)
    with col4:
        st.error("#### 🗄️ 資料庫查詢")
        st.markdown("自然語言轉 SQL 查詢")
    with col5:
        st.info("#### 🎤 語音辨識")
        st.markdown("Whisper 會議記錄系統")
    with col6:
        st.success("#### 🔄 RAG 應用")
        st.markdown("知識檢索增強生成")
    
    st.markdown("---")
    
    # LLM 技術架構圖
    st.markdown("### 🏗️ LLM 技術架構")
    llm_tech_flow = """
    graph LR
        A[數據輸入] --> B{大語言模型}
        B --> C[OLLAMA<br>本機運行]
        B --> D[INNO GPT<br>API 調用]
        B --> E[Whisper<br>語音辨識]
        
        C --> F[機況分類]
        C --> G[Release分析]
        D --> H[RAG處理]
        D --> I[RPSC分析]
        E --> J[會議整理]
        
        F --> K[(資料庫)]
        G --> K
        H --> K
        I --> K
        J --> K
        
        K --> L[報表呈現]
        
        style A fill:#e1f5fe
        style B fill:#fff3e0
        style K fill:#e8f5e9
        style L fill:#fce4ec
    """
    st_mermaid(llm_tech_flow)
    
    st.markdown("---")

    # 原有製程分析內容
    st.markdown("""
    ## 製程分析
    - 即時監控與分析製程參數
    - 預測性維護與異常檢測
    - 品質控制與優化
    """, unsafe_allow_html=True)

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

    # 時間序列分析
    st.markdown("## 時間序列分析", unsafe_allow_html=True)
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
    st.markdown("## 品質控制", unsafe_allow_html=True)
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

elif page == "🏆 證照展示":
    st.markdown("# 🏆 證照展示")
    
    st.markdown("""
    <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 25px; border-radius: 15px; margin-bottom: 20px;'>
        <h3 style='color: white; margin: 0;'>🌟 活到老，學到老</h3>
        <p style='color: #f0f0f0; margin-top: 10px;'>
        除了專業技術的持續精進，我也熱衷於探索不同領域的知識與技能。<br>
        2024年，我利用工作之餘考取了多項餐飲相關證照，展現終身學習的態度與多元發展的熱情。
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # 證照統計卡片
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%); padding: 20px; border-radius: 15px; text-align: center;'>
            <h1 style='margin: 0; font-size: 3em;'>🍜</h1>
            <h4 style='margin: 5px 0;'>中餐丙級</h4>
            <span style='background: #4CAF50; color: white; padding: 3px 10px; border-radius: 10px; font-size: 0.8em;'>✓ 已取得</span>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%); padding: 20px; border-radius: 15px; text-align: center;'>
            <h1 style='margin: 0; font-size: 3em;'>🎂</h1>
            <h4 style='margin: 5px 0;'>蛋糕丙級</h4>
            <span style='background: #4CAF50; color: white; padding: 3px 10px; border-radius: 10px; font-size: 0.8em;'>✓ 已取得</span>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%); padding: 20px; border-radius: 15px; text-align: center;'>
            <h1 style='margin: 0; font-size: 3em;'>🍝</h1>
            <h4 style='margin: 5px 0;'>西餐丙級</h4>
            <span style='background: #FF9800; color: white; padding: 3px 10px; border-radius: 10px; font-size: 0.8em;'>⏳ 待取得</span>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #d299c2 0%, #fef9d7 100%); padding: 20px; border-radius: 15px; text-align: center;'>
            <h1 style='margin: 0; font-size: 3em;'>🍸</h1>
            <h4 style='margin: 5px 0;'>調酒乙級</h4>
            <span style='background: #FF9800; color: white; padding: 3px 10px; border-radius: 10px; font-size: 0.8em;'>⏳ 待取得</span>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 證照資訊
    licenses_info = {
        "語言": {
            "title": "🌐 多益英語證照",
            "date": "",
            "status": "已取得",
            "status_color": "#4CAF50",
            "description": "TOEIC 多益英語能力測驗證書，展現國際溝通與跨文化合作能力。",
            "gradient": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)"
        },
        "中餐": {
            "title": "🍜 中餐烹調丙級",
            "date": "2024 上半年",
            "status": "已取得",
            "status_color": "#4CAF50",
            "description": "中式料理基礎技能認證，包含刀工、火候控制及各式中華料理烹調技巧。",
            "gradient": "linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%)"
        },
        "蛋糕": {
            "title": "🎂 烘焙食品丙級 (蛋糕)",
            "date": "2024 上半年",
            "status": "已取得",
            "status_color": "#4CAF50",
            "description": "西點蛋糕製作技能認證，涵蓋海綿蛋糕、戚風蛋糕等基礎烘焙技術。",
            "gradient": "linear-gradient(135deg, #a8edea 0%, #fed6e3 100%)"
        },
        "西餐": {
            "title": "🍝 西餐烹調丙級",
            "date": "2024 下半年",
            "status": "待取得",
            "status_color": "#FF9800",
            "description": "西式料理基礎技能認證，包含醬汁製作、肉類處理及經典西餐烹調。",
            "gradient": "linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%)"
        },
        "調酒": {
            "title": "🍸 調酒乙級",
            "date": "2024 下半年",
            "status": "待取得",
            "status_color": "#FF9800",
            "description": "專業調酒技能認證，涵蓋經典調酒配方、創意調酒及吧台服務技巧。",
            "gradient": "linear-gradient(135deg, #d299c2 0%, #fef9d7 100%)"
        }
    }
    
    # 顯示每個證照類別
    for category, info in licenses_info.items():
        # 構建日期行 - 根據背景決定文字顏色
        is_dark_bg = category == "語言"  # 語言類別使用深色背景
        text_color = "#fff" if is_dark_bg else "#333"
        desc_color = "#e0e0e0" if is_dark_bg else "#555"
        date_color = "#ddd" if is_dark_bg else "#555"
        
        date_html = ""
        if info.get('date'):
            date_html = f"<p style='color: {date_color}; margin: 10px 0 5px 0;'>📅 <strong>取得時間</strong>: {info['date']}</p>"
        
        # 構建完整的 HTML
        gradient = info["gradient"]
        title = info["title"]
        status_color = info["status_color"]
        status = info["status"]
        description = info["description"]
        
        st.markdown(f"""<div style="background: {gradient}; padding: 20px; border-radius: 15px; margin-bottom: 15px;">
<div style="display: flex; justify-content: space-between; align-items: center;">
<h2 style="margin: 0; color: {text_color};">{title}</h2>
<span style="background: {status_color}; color: white; padding: 5px 15px; border-radius: 20px; font-weight: bold;">{status}</span>
</div>
{date_html}
<p style="color: {desc_color}; margin: 5px 0;">{description}</p>
</div>""", unsafe_allow_html=True)
        
        # 顯示該類別的圖片
        if category in LICENSE_IMAGES and LICENSE_IMAGES[category]:
            images = LICENSE_IMAGES[category]
            
            # 每行顯示 4 張圖片
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
            st.info("📷 圖片載入中...")
        
        st.markdown("<br>", unsafe_allow_html=True)
    
    # 學習心得
    st.markdown("""
    <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 25px; border-radius: 15px; margin-top: 20px;'>
        <h2 style='color: white; text-align: center;'>💡 學習心得</h2>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); padding: 25px; border-radius: 15px; min-height: 180px;'>
            <h4 style='color: white; margin-top: 0;'>✨ 跨領域學習的價值</h4>
            <ul style='color: #f0f0f0; margin-bottom: 0;'>
                <li>培養不同領域的思維方式</li>
                <li>增進手作與創造力</li>
                <li>舒壓與工作生活平衡</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); padding: 25px; border-radius: 15px; min-height: 180px;'>
            <h4 style='color: white; margin-top: 0;'>🚀 終身學習的態度</h4>
            <ul style='color: #f0f0f0; margin-bottom: 0;'>
                <li>保持對新事物的好奇心</li>
                <li>挑戰舒適圈，持續成長</li>
                <li>將學習視為生活的一部分</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

# 頁腳
st.markdown("""
---
<div style='text-align: center; color: var(--text-color); padding: 20px;'>
    2025 劉晉亨 | AI Enhanced Resume | Built with ❤️ and ❤️
</div>
""", unsafe_allow_html=True)
