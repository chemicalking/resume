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
            return Image.open(img_path)
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
            st.image(profile_image, use_container_width=True, output_format="JPEG", clamp=True)

    with col2:
        st.markdown("""
        <div class='profile-section'>
            <h1>劉晉亨 <span class='highlight'>Patrick Liou</span></h1>
            <h2>🤖 資深製程整合工程師 | AI與大數據專家</h2>

            <div class='skill-section'>
                <div class='skill-card'>
                    <h3>🎯 核心專長</h3>
                    <div class='tech-badges'>
                        <span class='tech-badge' data-type="data">
                            <span class='icon'>💻</span>
                            <span class='text'>大數據分析</span>
                        </span>
                        <span class='tech-badge' data-type="ai">
                            <span class='icon'>🤖</span>
                            <span class='text'>機器學習</span>
                        </span>
                        <span class='tech-badge' data-type="ai">
                            <span class='icon'>🧠</span>
                            <span class='text'>深度學習</span>
                        </span>
                    </div>
                </div>

                <div class='skill-card'>
                    <h3>🎯 專業技能</h3>
                    <div class='tech-badges'>
                        <span class='tech-badge' data-type="process">
                            <span class='icon'>🔩</span>
                            <span class='text'>製程整合</span>
                        </span>
                        <span class='tech-badge' data-type="process">
                            <span class='icon'>📈</span>
                            <span class='text'>六標準差</span>
                        </span>
                        <span class='tech-badge' data-type="data">
                            <span class='icon'>🏭</span>
                            <span class='text'>智能工廠</span>
                        </span>
                    </div>
                </div>
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
            <h3>台積電 (tsmc) </h3>
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
        st.markdown("""
        <div class='education-card'>
            <h3>國立交通大學</h3>
            <p class='highlight'>2015年9月 - 2018年1月</p>
            <h4>管理科學碩士（MBA）</h4>
            <ul>
                <li>專業課程：數據分析與商業智慧、營運管理與策略規劃、專案管理與領導力</li>
                <li>研究方向：製造業數位轉型與AI應用</li>
            </ul>
        </div>

        <div class='education-card'>
            <h3>國立台灣大學</h3>
            <p class='highlight'>2015年3月 - 2017年6月</p>
            <h4>持續教育法律課程</h4>
            <ul>
                <li>專業課程：商業法律、智慧財產權、勞動法規</li>
                <li>研究方向：科技產業法律實務應用</li>
            </ul>
        </div>

        <div class='education-card'>
            <h3>國立台灣科技大學</h3>
            <p class='highlight'>2006年9月 - 2008年6月</p>
            <h4>化學工程碩士</h4>
            <ul>
                <li>專業課程：化工單元操作、反應工程、程序控制</li>
                <li>研究方向：製程最佳化與控制</li>
            </ul>
        </div>

        <div class='education-card'>
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
        st.markdown("### 學習歷程")
        education_chart = """
        graph TD
            A[逢甲大學<br>化工學士] --> B[台科大<br>化工碩士]
            B --> C[台大<br>法律課程]
            C --> D[交大<br>管理碩士]

            style A fill:#f9f,stroke:#333,stroke-width:4px
            style B fill:#bbf,stroke:#333,stroke-width:4px
            style C fill:#ddf,stroke:#333,stroke-width:4px
            style D fill:#dfd,stroke:#333,stroke-width:4px
        """
        st_mermaid(education_chart)

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
    <div class='skill-card'>
        <h3>🔧 技術工具</h3>
        <div class='tech-badges'>
            <span class='tech-badge' data-type="data">
                <span class='icon'>💻</span>
                <span class='text'>Python</span>
            </span>
            <span class='tech-badge' data-type="ai">
                <span class='icon'>🤖</span>
                <span class='text'>深度學習</span>
            </span>
            <span class='tech-badge' data-type="ai">
                <span class='icon'>🔩</span>
                <span class='text'>AutoML</span>
            </span>
            <span class='tech-badge' data-type="process">
                <span class='icon'>📊</span>
                <span class='text'>數據分析</span>
            </span>
            <span class='tech-badge' data-type="process">
                <span class='icon'>📈</span>
                <span class='text'>六標準差</span>
            </span>
            <span class='tech-badge' data-type="data">
                <span class='icon'>🏭</span>
                <span class='text'>智能工廠</span>
            </span>
        </div>
    </div>

    <div class='skill-card'>
        <h3>💡 製程專長</h3>
        <div class='tech-badges'>
            <span class='tech-badge' data-type="process">
                <span class='icon'>🔧</span>
                <span class='text'>半導體製程</span>
            </span>
            <span class='tech-badge' data-type="data">
                <span class='icon'>📊</span>
                <span class='text'>製程參數分析</span>
            </span>
            <span class='tech-badge' data-type="ai">
                <span class='icon'>🎯</span>
                <span class='text'>良率提升</span>
            </span>
            <span class='tech-badge' data-type="process">
                <span class='icon'>🔩</span>
                <span class='text'>設備監控</span>
            </span>
        </div>
    </div>

    <div class='skill-card'>
        <h3>📈 數據分析</h3>
        <div class='tech-badges'>
            <span class='tech-badge' data-type="data">
                <span class='icon'>📊</span>
                <span class='text'>統計分析</span>
            </span>
            <span class='tech-badge' data-type="process">
                <span class='icon'>📉</span>
                <span class='text'>製程能力分析</span>
            </span>
            <span class='tech-badge' data-type="ai">
                <span class='icon'>🎯</span>
                <span class='text'>六標準差</span>
            </span>
        </div>
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

    # 添加 Mermaid 圖表 - 職涯發展歷程
    st.markdown("## 職涯發展歷程")
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

    # 添加 Mermaid 圖表 - 核心能力成長
    st.markdown("## 核心能力成長")
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

    # 添加 Mermaid 圖表 - 學習歷程
    st.markdown("## 學習歷程")
    education_chart = """
    graph TD
        A[逢甲大學<br>化工學士] --> B[台科大<br>化工碩士]
        B --> C[台大<br>資管課程]
        C --> D[交大<br>管理碩士]

        style A fill:#f9f,stroke:#333,stroke-width:4px
        style B fill:#bbf,stroke:#333,stroke-width:4px
        style C fill:#ddf,stroke:#333,stroke-width:4px
        style D fill:#dfd,stroke:#333,stroke-width:4px
    """
    st_mermaid(education_chart)

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
    # 模擬數據
    projects = ["📊良率優化", "🔬氣體監控", "🤖製程分析", "🔧設備監控", "📈品質管制", "📧異常解析", "📈數據分析"]
    progress = [85, 90, 80, 75, 88, 70, 95]

    # 創建條形圖展示項目進度
    st.markdown("### 專案進度概覽")
    # 使用 Plotly 替代 Matplotlib
    fig = px.bar(
        x=progress,
        y=projects,
        orientation='h',
        labels={"x": "進度完成百分比 (%)", "y": ""},
        title="專案進度概覽"
    )
    fig.update_layout(
        title_font_size=20,
        xaxis_range=[0, 100],
        height=400,
        margin=dict(l=0, r=0, t=40, b=0)
    )
    # 添加標籤
    fig.update_traces(
        texttemplate='%{x}%',
        textposition='outside',
        marker_color='rgba(74, 144, 226, 0.7)',
        hoverinfo='text',
        hovertext=[f"{p}: {v}%" for p, v in zip(projects, progress)]
    )
    st.plotly_chart(fig, use_container_width=True)

elif page == "🔬 專案分析":
    st.markdown("# 進階數據分析")

    # 直接顯示所有分析內容，移除下拉選單
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

# 頁腳
st.markdown("""
---
<div style='text-align: center; color: var(--text-color); padding: 20px;'>
    2025 劉晉亨 | AI Enhanced Resume | Built with ❤️ and ❤️
</div>
""", unsafe_allow_html=True)
