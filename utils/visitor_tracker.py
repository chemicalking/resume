import streamlit as st
import datetime
import json
import os

def get_visitor_ip():
    """獲取訪問者IP地址"""
    try:
        return json.loads(os.getenv("STREAMLIT_BROWSER_GATHER_USAGE_STATS", "false"))
    except:
        return "unknown"

def track_visitor():
    """追蹤訪問者"""
    if 'visitor_count' not in st.session_state:
        st.session_state.visitor_count = 0
    
    if 'last_visit' not in st.session_state:
        st.session_state.visitor_count += 1
        st.session_state.last_visit = datetime.datetime.now()
    
    return st.session_state.visitor_count
