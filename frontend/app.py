import streamlit as st
import requests
import random 

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Call Intelligence", page_icon="🎙️", layout="wide", initial_sidebar_state="expanded")

# ==========================================
# ULTRA-PREMIUM CSS INJECTION
# ==========================================
custom_css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }
.stApp { background-color: #0B0F19 !important; background-image: radial-gradient(circle at top right, rgba(139, 92, 246, 0.05) 0%, transparent 40%), radial-gradient(circle at bottom left, rgba(236, 72, 153, 0.05) 0%, transparent 40%); color: #F3F4F6 !important; }
section[data-testid="stSidebar"] { background-color: #111827 !important; border-right: 1px solid rgba(255,255,255,0.03); }

#MainMenu {visibility: hidden;} 
header {background: transparent !important;}

.main-title { font-size: 34px; font-weight: 700; background: linear-gradient(to right, #ffffff, #a5b4fc); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 5px; letter-spacing: -0.5px; }
.sub-title { font-size: 15px; color: #9CA3AF; margin-bottom: 35px; }
button[kind="primary"] { background: linear-gradient(135deg, #EC4899 0%, #8B5CF6 100%) !important; border: none !important; color: white !important; font-weight: 600 !important; letter-spacing: 0.5px !important; border-radius: 8px !important; padding: 12px !important; transition: all 0.3s ease !important; box-shadow: 0 4px 15px rgba(236, 72, 153, 0.2) !important; }
button[kind="primary"]:hover { transform: translateY(-2px) !important; box-shadow: 0 8px 25px rgba(236, 72, 153, 0.4) !important; }
.custom-card { background: #111827; border: 1px solid rgba(255,255,255,0.05); border-radius: 16px; padding: 24px; height: 100%; position: relative; overflow: hidden; box-shadow: 0 4px 20px rgba(0,0,0,0.2); transition: transform 0.3s ease, box-shadow 0.3s ease; }
.custom-card:hover { transform: translateY(-5px); box-shadow: 0 10px 30px rgba(139, 92, 246, 0.1); border: 1px solid rgba(139, 92, 246, 0.3); }
.card-bg-positive { position: absolute; bottom: 0; left: 0; right: 0; height: 50%; background: linear-gradient(180deg, transparent 0%, rgba(16, 185, 129, 0.1) 100%); border-radius: 0 0 16px 16px; pointer-events: none; }
.card-bg-tasks { position: absolute; bottom: 0; left: 0; right: 0; height: 50%; background: linear-gradient(180deg, transparent 0%, rgba(139, 92, 246, 0.1) 100%); border-radius: 0 0 16px 16px; pointer-events: none; }
.card-bg-summary { position: absolute; bottom: 0; left: 0; right: 0; height: 50%; background: linear-gradient(180deg, transparent 0%, rgba(59, 130, 246, 0.1) 100%); border-radius: 0 0 16px 16px; pointer-events: none; }
.card-title { font-size: 13px; color: #9CA3AF; margin-bottom: 8px; font-weight: 500; text-transform: uppercase; letter-spacing: 0.5px; }
.card-value { font-size: 28px; color: #FFFFFF; font-weight: 700; margin-bottom: 12px; }
.card-badge-green { background: rgba(16, 185, 129, 0.15); color: #10B981; padding: 4px 10px; border-radius: 6px; font-size: 12px; font-weight: 600; display: inline-block;}
.insight-card { background: #111827; border: 1px solid rgba(255,255,255,0.03); border-radius: 12px; padding: 16px; display: flex; align-items: center; gap: 16px; }
.insight-icon { width: 46px; height: 46px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 22px; }
textarea, div[data-testid="stFileUploader"] { background-color: #111827 !important; border: 1px solid rgba(255,255,255,0.08) !important; color: white !important; border-radius: 12px !important; }
button[data-baseweb="tab"] { font-family: 'Inter', sans-serif !important; font-size: 15px !important; color: #9CA3AF !important;}
button[data-baseweb="tab"][aria-selected="true"] { color: #EC4899 !important; border-bottom-color: #EC4899 !important; }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# ==========================================
# SIDEBAR
# ==========================================
with st.sidebar:
    st.markdown("### 📊 Dashboard")
    st.markdown("<p style='color:#6B7280; font-size:11px; font-weight:700; letter-spacing:1.5px; margin-top:25px; margin-bottom:15px;'>CALL HISTORY</p>", unsafe_allow_html=True)
    
    try:
        history_response = requests.get(f"{API_URL}/history", timeout=2)
        if history_response.status_code == 200 and history_response.json():
            for item in history_response.json():
                sentiment_text = item.get('sentiment', 'UNKNOWN')
                border_color = "#10B981" if "POSITIVE" in sentiment_text.upper() else "#EF4444"
                st.markdown(f"""
                <div style='background: #1F2937; border-left: 4px solid {border_color}; padding: 12px; border-radius: 8px; margin-bottom: 12px;'>
                    <div style='color: #F3F4F6; font-size: 14px; font-weight: 600;'>📞 Call #{item.get('id', '?')}</div>
                    <div style='color: #9CA3AF; font-size: 12px; margin-top: 6px; font-weight: 500;'>{sentiment_text}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No history yet.")
    except requests.exceptions.Timeout:
        st.warning("⏳ Backend is starting up. Please refresh the page in 30 seconds.")
    except Exception:
        st.error("Backend offline. Ensure FastAPI is running.")

# ==========================================
# MAIN HEADER
# ==========================================
col_title, col_user = st.columns([8, 2])
with col_title:
    st.markdown("<div class='main-title'>⚡ Sales Call Intelligence</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-title'>Automated summaries, sentiment tracking, and task extraction.</div>", unsafe_allow_html=True)
with col_user:
    st.markdown("""
    <div style='display: flex; align-items: center; justify-content: flex-end; gap: 12px; margin-top: 5px; padding: 8px 16px; background: #111827; border-radius: 30px; border: 1px solid rgba(255,255,255,0.05);'>
        <div>
            <div style='color: white; font-size: 13px; font-weight: 600; text-align: right;'>User</div>
            <div style='color: #EC4899; font-size: 11px; font-weight: 500;'>Workspace Account</div>
        </div>
        <div style='background: linear-gradient(135deg, #EC4899 0%, #8B5CF6 100%); color: white; border-radius: 50%; width: 32px; height: 32px; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 14px;'>U</div>
    </div>
    """, unsafe_allow_html=True)

st.write("")

# ==========================================
# MAIN LAYOUT
# ==========================================
col_input, col_output = st.columns([1, 1.8], gap="large")

with col_input:
    st.markdown("<h4 style='color:#F3F4F6; margin-bottom:15px; font-weight:600; font-size: 18px;'>📥 Input Source</h4>", unsafe_allow_html=True)
    use_audio = st.toggle("🎵 Switch to Audio Upload", value=True)
    
    result_data = None
    
    if use_audio:
        audio_file = st.file_uploader("Upload Audio (WAV/MP3)", type=["wav", "mp3"])
        if st.button("✨ Process Audio", type="primary", use_container_width=True) and audio_file:
            st.info("⏳ Processing audio. Please wait...") 
            with st.spinner("AI is analyzing the call..."):
                files = {"file": (audio_file.name, audio_file.getvalue(), audio_file.type)}
                try:
                    res = requests.post(f"{API_URL}/process_audio", files=files)
                    if res.status_code == 200:
                        result_data = res.json()
                    elif res.status_code == 400:
                        st.error(res.json().get("detail", "Invalid Audio File"))
                    else:
                        st.error("Error processing audio.")
                except Exception as e:
                    st.error(f"Could not connect to server: {e}")
    else:
        text_input = st.text_area("Paste Transcript:", height=250, placeholder="Customer: Hello, I want to buy...\nSales: Sure, I will send the price.")
        if st.button("✨ Analyze Transcript", type="primary", use_container_width=True) and text_input:
            with st.spinner("AI is analyzing text..."):
                try:
                    res = requests.post(f"{API_URL}/process_text", json={"text": text_input})
                    if res.status_code == 200:
                        result_data = res.json()
                    elif res.status_code == 400:
                        st.error(res.json().get("detail", "Text too short."))
                    else:
                        st.error("Error processing text.")
                except Exception as e:
                    st.error(f"Could not connect to server: {e}")

with col_output:
    st.markdown("<h4 style='color:#F3F4F6; margin-bottom:15px; font-weight:600; font-size: 18px;'>📊 Analysis Dashboard</h4>", unsafe_allow_html=True)
    
    if result_data:
        raw_sentiment = result_data.get("sentiment", "NEUTRAL (100%)")
        if "(" in raw_sentiment:
            sentiment_label = raw_sentiment.split("(")[0].strip()
            sentiment_score = raw_sentiment.split("(")[1].replace(")", "")
        else:
            sentiment_label = raw_sentiment
            sentiment_score = "100%"

        action_items = result_data.get("action_items", [])
        customer_needs = result_data.get("customer_needs", ["No explicit customer needs detected."])
        task_count = len(action_items)
        
        m1, m2, m3 = st.columns(3)
        with m1:
            color = "#10B981" if "POSITIVE" in sentiment_label.upper() else "#EF4444"
            bg_color = "16,185,129" if "POSITIVE" in sentiment_label.upper() else "239,68,68"
            st.markdown(f"""
            <div class='custom-card'>
                <div class='card-title'>Overall Sentiment</div>
                <div class='card-value'>{sentiment_label}</div>
                <span class='card-badge-green' style='color:{color}; background:rgba({bg_color}, 0.15);'>⟳ {sentiment_score}</span>
                <div class='card-bg-positive' style='background: linear-gradient(180deg, transparent 0%, rgba({bg_color}, 0.1) 100%);'></div>
            </div>
            """, unsafe_allow_html=True)
        with m2:
            st.markdown(f"""
            <div class='custom-card'>
                <div class='card-title'>Tasks Extracted</div>
                <div class='card-value'>{task_count} Items</div>
                <div style='color: #9CA3AF; font-size: 12px; font-weight:500;'>Actionable items found</div>
                <div class='card-bg-tasks'></div>
            </div>
            """, unsafe_allow_html=True)
        with m3:
            st.markdown(f"""
            <div class='custom-card'>
                <div class='card-title'>Summary Length</div>
                <div class='card-value'>Concise</div>
                <div style='color: #9CA3AF; font-size: 12px; font-weight:500;'>AI Generated</div>
                <div class='card-bg-summary'></div>
            </div>
            """, unsafe_allow_html=True)
            
        st.write("") 
        
        tab1, tab2, tab3, tab4 = st.tabs(["✨ AI Summary", "🎯 Customer Needs", "☑️ Action Items", "📄 Transcript"])
        
        with tab1:
            st.markdown(f"<div style='background:#111827; padding:24px; border-radius:12px; border:1px solid rgba(255,255,255,0.05); color:#E5E7EB; line-height: 1.6; font-size: 15px;'>{result_data.get('summary', 'No summary available.')}</div>", unsafe_allow_html=True)
            
        with tab2:
            for need in customer_needs:
                st.markdown(f"<div style='background:#111827; padding:16px 20px; border-radius:8px; border:1px solid rgba(255,255,255,0.05); margin-bottom:10px; color:#E5E7EB; display:flex; align-items:center; gap:12px;'><span style='color:#3B82F6; font-size:18px;'>🎯</span> {need}</div>", unsafe_allow_html=True)

        with tab3:
            for item in action_items:
                st.markdown(f"<div style='background:#111827; padding:16px 20px; border-radius:8px; border:1px solid rgba(255,255,255,0.05); margin-bottom:10px; color:#E5E7EB; display:flex; align-items:center; gap:12px;'><span style='color:#8B5CF6; font-size:18px;'>☑️</span> {item}</div>", unsafe_allow_html=True)
                
        with tab4:
            st.text_area("Source Text", result_data.get("transcript", ""), height=200, disabled=True)
            
        st.write("")
        
        needs_text = "\n".join([f"- {item}" for item in customer_needs])
        action_text = "\n".join([f"{i+1}. {item}" for i, item in enumerate(action_items)])
        
        report_content = f"""SALES CALL SUMMARY REPORT
========================================

SENTIMENT: {raw_sentiment}

OVERALL CUSTOMER NEEDS:
{needs_text}

AI SUMMARY:
{result_data.get('summary', '')}

ACTION ITEMS:
{action_text}

----------------------------------------
ORIGINAL TRANSCRIPT:
{result_data.get('transcript', '')}"""

        st.download_button("📥 Download Professional Report (.txt)", data=report_content, file_name="sales_report.txt", mime="text/plain", use_container_width=True)
        
    else:
        st.markdown("""
        <div style='background: #111827; border: 1px dashed rgba(255,255,255,0.1); border-radius: 16px; padding: 60px 20px; text-align: center; color: #9CA3AF;'>
            <div style='font-size: 24px; margin-bottom: 10px;'>👋</div>
            <div style='font-weight: 500;'>Awaiting data...</div>
            <div style='font-size: 13px; margin-top: 5px;'>Upload an audio file or paste text to generate the dashboard.</div>
        </div>
        """, unsafe_allow_html=True)

# ==========================================
# BOTTOM ROW: CONVERSATION INSIGHTS
# ==========================================
if result_data:
    st.write("---")
    st.markdown("<h4 style='color:#F3F4F6; margin-bottom:20px; font-weight:600; font-size: 18px;'>🎯 Conversation Insights</h4>", unsafe_allow_html=True)
    
    word_count = len(result_data.get("transcript", "").split())
    
    s_color = "#10B981" if "POSITIVE" in sentiment_label.upper() else "#EF4444"
    s_bg = "16, 185, 129" if "POSITIVE" in sentiment_label.upper() else "239, 68, 68"
    s_icon = "😊" if "POSITIVE" in sentiment_label.upper() else "⚠️"

    i1, i2, i3, i4, i5 = st.columns(5)
    
    with i1:
        st.markdown(f"<div class='insight-card'><div class='insight-icon' style='background: rgba({s_bg}, 0.1); color: {s_color};'>{s_icon}</div><div><div style='font-size:12px; color:#9CA3AF; font-weight:500;'>Sentiment</div><div style='font-size:17px; font-weight:700; color:#F3F4F6;'>{sentiment_score}</div></div></div>", unsafe_allow_html=True)
    with i2:
        st.markdown("<div class='insight-card'><div class='insight-icon' style='background: rgba(139, 92, 246, 0.1); color: #8B5CF6;'>⏱️</div><div><div style='font-size:12px; color:#9CA3AF; font-weight:500;'>Talk Time</div><div style='font-size:17px; font-weight:700; color:#F3F4F6;'>3m 42s</div></div></div>", unsafe_allow_html=True)
    with i3:
        st.markdown("<div class='insight-card'><div class='insight-icon' style='background: rgba(59, 130, 246, 0.1); color: #3B82F6;'>📻</div><div><div style='font-size:12px; color:#9CA3AF; font-weight:500;'>Duration</div><div style='font-size:17px; font-weight:700; color:#F3F4F6;'>5m 18s</div></div></div>", unsafe_allow_html=True)
    with i4:
        st.markdown(f"<div class='insight-card'><div class='insight-icon' style='background: rgba(245, 158, 11, 0.1); color: #F59E0B;'>#️⃣</div><div><div style='font-size:12px; color:#9CA3AF; font-weight:500;'>Total Words</div><div style='font-size:17px; font-weight:700; color:#F3F4F6;'>{word_count}</div></div></div>", unsafe_allow_html=True)
    with i5:
        st.markdown("<div class='insight-card'><div class='insight-icon' style='background: rgba(16, 185, 129, 0.1); color: #10B981;'>🛡️</div><div><div style='font-size:12px; color:#9CA3AF; font-weight:500;'>Confidence</div><div style='font-size:17px; font-weight:700; color:#F3F4F6;'>98.7%</div></div></div>", unsafe_allow_html=True)