import streamlit as st
import pandas as pd
import os
import json
from datetime import datetime

st.set_page_config(
    page_title="SecurePOS AI",
    page_icon="🛡️",
    layout="wide"
)

# Title
st.title("🛡️ SecurePOS AI - Theft Detection Dashboard")
st.markdown("**Real-Time Monitoring System** | Powered by YOLOv8 AI")

# Try to load real-time data
realtime_data = {}
if os.path.exists("realtime_data.json"):
    try:
        with open("realtime_data.json", "r") as f:
            realtime_data = json.load(f)
    except Exception as e:
        st.warning(f"Could not load real-time data: {e}")

# ============================================
# TOP METRICS
# ============================================
col1, col2, col3, col4 = st.columns(4)

with col1:
    status = realtime_data.get("status", "unknown")
    if status == "running":
        st.metric("🟢 System", "ACTIVE", delta="Monitoring")
    else:
        st.metric("🔴 System", "OFFLINE", delta="Not Running")

with col2:
    current_time = realtime_data.get("current_time", "0:00:00")
    st.metric("⏱️ Video Time", current_time)

with col3:
    people_count = realtime_data.get("people_count", 0)
    st.metric("👥 People", people_count)

with col4:
    objects = realtime_data.get("objects_detected", [])
    st.metric("📦 Objects", len(objects))

st.divider()

# ============================================
# VIDEO TIMELINE
# ============================================
st.subheader("🎬 Video Timeline - Real Time Playback")

current_time = realtime_data.get("current_time", "0:00:00")
time_parts = current_time.split(':')

try:
    total_seconds = int(time_parts[0]) * 3600 + int(time_parts[1]) * 60 + int(time_parts[2])
except:
    total_seconds = 0

# Progress bar
progress = min(total_seconds / 8, 1.0)
st.progress(progress)

col_time1, col_time2, col_time3 = st.columns(3)
with col_time1:
    st.info(f"**Current: {current_time}**")
with col_time2:
    st.info(f"**Elapsed: {total_seconds}s**")
with col_time3:
    st.info(f"**Duration: 8s**")

st.divider()

# ============================================
# LIVE THEFT ALERTS
# ============================================
st.subheader("🚨 LIVE THEFT ALERTS")

alerts = realtime_data.get("alerts", [])

if alerts:
    for alert in reversed(alerts[-5:]):
        col_alert1, col_alert2 = st.columns([3, 1])
        with col_alert1:
            st.error(f"⚠️ {alert['message']}")
        with col_alert2:
            if os.path.exists(alert.get("image", "")):
                try:
                    st.image(alert["image"], width=150)
                except:
                    pass
else:
    st.success("✅ No theft detected")

st.divider()

# ============================================
# POS TRANSACTIONS (SYNCED WITH VIDEO)
# ============================================
st.subheader("💳 POS Transaction Logs - Synchronized with Video")

if os.path.exists("pos_logs.csv"):
    logs = pd.read_csv("pos_logs.csv")
    current_time_display = realtime_data.get("current_time", "0:00:00")
    current_pos = realtime_data.get("current_pos_transaction", [])
    
    # Create display table
    display_logs = logs.copy()
    display_logs['Video Time'] = display_logs['timestamp'].astype(str)
    display_logs['Status'] = display_logs['timestamp'].astype(str).apply(
        lambda x: "🟢 ACTIVE NOW" if x == current_time_display else "✓ Past"
    )
    display_logs['Authorization'] = "✓ Yes"
    
    st.dataframe(
        display_logs[['Video Time', 'event', 'Status', 'Authorization']],
        hide_index=True
    )
    
    # Show active transaction
    if current_pos:
        st.success(f"✓ **At Video Time {current_time_display}** - AUTHORIZED: {current_pos[0]['event']}")
    else:
        st.info(f"⏱️ **Current Video Time: {current_time_display}**")
else:
    st.warning("No POS logs found")

st.divider()

# ============================================
# CAPTURED EVIDENCE
# ============================================
st.subheader("📸 Captured Theft Evidence")

image_folder = "theft_images"
if os.path.exists(image_folder):
    images = sorted(os.listdir(image_folder), reverse=True)
    if images:
        cols = st.columns(3)
        for idx, img in enumerate(images[:6]):
            with cols[idx % 3]:
                try:
                    st.image(f"{image_folder}/{img}", width=300, caption=img)
                except:
                    pass
    else:
        st.info("No evidence images yet")
else:
    st.info("No evidence folder")

st.divider()

# ============================================
# ALERT HISTORY
# ============================================
st.subheader("📜 Alert History")

if os.path.exists("alerts.txt"):
    with open("alerts.txt", "r") as f:
        alerts_history = f.readlines()
    
    if alerts_history:
        st.write(f"**Total Alerts: {len(alerts_history)}**")
        with st.expander("View all historical alerts"):
            for alert in reversed(alerts_history):
                st.text(alert.strip())
    else:
        st.success("No alerts in history")
else:
    st.info("No alert history yet")

st.divider()

# ============================================
# FOOTER
# ============================================
st.markdown("---")
st.markdown(
    f"**SecurePOS AI v1.0** | Real-Time Theft Detection | Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
)

# Auto-refresh every 2 seconds
st.markdown(
    """
    <script>
        setTimeout(function() {
            location.reload();
        }, 2000);
    </script>
    """,
    unsafe_allow_html=True,
)
