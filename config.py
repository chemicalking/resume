import os
from pathlib import Path

# 基礎配置
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / 'data'
ASSETS_DIR = BASE_DIR / 'assets'

# 頁面配置
PAGE_CONFIG = {
    "page_title": "個人履歷網站",
    "page_icon": "🎈",
    "layout": "wide",
    "initial_sidebar_state": "expanded"
}

# 數據庫配置
DB_CONFIG = {
    "visitor_data_path": BASE_DIR / "visitor_data.json"
}

# 圖表配置
CHART_CONFIG = {
    "template": "plotly_white",
    "font_family": ["Microsoft YaHei", "SimHei", "Arial Unicode MS"]
}

# 郵件配置
MAIL_CONFIG = {
    "smtp_server": os.getenv("SMTP_SERVER", "smtp.gmail.com"),
    "smtp_port": int(os.getenv("SMTP_PORT", "587")),
    "sender_email": os.getenv("SENDER_EMAIL", ""),
    "receiver_email": os.getenv("RECEIVER_EMAIL", "")
}

# AI模型配置
MODEL_CONFIG = {
    "gas_data_path": DATA_DIR / "gas_data.csv",
    "model_path": DATA_DIR / "gas_model.pkl",
    "prediction_hours": 24,
    "training_window": 168  # 7天
}
