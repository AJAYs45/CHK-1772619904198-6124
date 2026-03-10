import streamlit as st
import pandas as pd
import time
import random
import plotly.express as px
import os
import json

# १. Advanced Page Configuration
st.set_page_config(page_title="CHAKRAVYUH 2.0 - SOC", layout="wide", page_icon="🛡️")

# २. Custom CSS (सायबर सिक्युरिटी थीमसाठी)
st.markdown("""
    <style>
    h1, h2, h3 { color: #00E676 !important; font-family: 'Courier New', Courier, monospace; }
    [data-testid="stMetric"] { background-color: #1E1E1E; padding: 15px; border-radius: 10px; border-left: 5px solid #00E676; box-shadow: 2px 2px 10px rgba(0,0,0,0.5); }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center;'>🛡️ CHAKRAVYUH 2.0: COMMAND CENTER</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center; color: #a8b2c1;'>Real-Time AI Network Threat Intelligence</h4>", unsafe_allow_html=True)
st.markdown("---")

attack_names = ["DDoS Attack (Neptune)", "Port Scanning (Satan)", "Brute Force (Guess_Passwd)", "Malware Injection", "Ping of Death (Smurf)"]

try:
    # डेटा फाईल वाचणे
    df = pd.read_csv('traffic_log.csv')
    df['Packet_No'] = df.index + 1 
    
    if 'Attack_Type' not in df.columns:
        df['Attack_Type'] = df['Prediction'].apply(lambda x: random.choice(attack_names) if x == 1 else "Normal Traffic")

    # ३. 🔐 Admin Access Control (Sidebar)
    st.sidebar.header("🔐 Admin Firewall Rules")
    
    if not os.path.exists('blocklist.json'):
        with open('blocklist.json', 'w') as f: json.dump([], f)
    with open('blocklist.json', 'r') as f:
        blocklist = json.load(f)

    unique_ips = df['Source_IP'].unique().tolist() if 'Source_IP' in df.columns else []
    
    st.sidebar.markdown("### 🚫 Block Malicious IPs")
    selected_blocked_ips = st.sidebar.multiselect("Select IPs to Block Permanently:", options=unique_ips, default=[ip for ip in blocklist if ip in unique_ips])

    if st.sidebar.button("Apply Firewall Rules 🛑"):
        with open('blocklist.json', 'w') as f:
            json.dump(selected_blocked_ips, f)
        st.sidebar.success("Firewall Rules Updated! Selected IPs are blocked.")

    st.sidebar.markdown("---")
    auto_refresh = st.sidebar.checkbox("🔄 Auto-Refresh Dashboard", value=True)
    st.sidebar.info("💡 **Tip:** Uncheck to pause live monitoring and analyze past threats.")

    total = len(df)
    threats = len(df[df['Prediction'] == 1])
    safe = len(df[df['Prediction'] == 0])

    # ४. Top Metrics Display
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("🌐 Total Network Packets", total)
    col2.metric("✅ Clean Traffic", safe)
    col3.metric("🚨 Threats Blocked", threats)
    col4.metric("🛡️ System Status", "CRITICAL 🔴" if threats > safe else "SECURE 🟢")

    st.markdown("---")

    # ५. Advanced Dark Charts
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.markdown("### 📊 Traffic Distribution")
        if total > 0:
            fig1 = px.pie(values=[safe, threats], names=['Normal', 'Threats'], 
                          color_discrete_sequence=['#00E676', '#FF3D00'], hole=0.5, template="plotly_dark")
            fig1.update_traces(textposition='inside', textinfo='percent+label')
            fig1.update_layout(margin=dict(t=0, b=0, l=0, r=0), showlegend=False)
            st.plotly_chart(fig1, use_container_width=True, key=f"pie_{time.time()}")

    with chart_col2:
        st.markdown("### 🎯 Top Attack Vectors")
        if threats > 0:
            attack_counts = df[df['Prediction'] == 1]['Attack_Type'].value_counts().reset_index()
            attack_counts.columns = ['Attack Type', 'Count']
            fig2 = px.bar(attack_counts, x='Attack Type', y='Count', color='Attack Type', text='Count', template="plotly_dark")
            fig2.update_layout(margin=dict(t=0, b=0, l=0, r=0), showlegend=False)
            st.plotly_chart(fig2, use_container_width=True, key=f"bar_{time.time()}")
        else:
            st.success("System is currently safe. No attacks detected.")

    # ६. Live Logs (User Name आणि IP सोबत)
    st.markdown("### 🔴 Live System Logs (Real-time Sync)")
    
    if not df.empty:
        display_df = df.iloc[::-1].copy()
        
        # जर फाईलमध्ये खरोखर नवीन कॉलम्स असतील तरच ते दाखवणे
        if 'User_Name' in display_df.columns and 'Source_IP' in display_df.columns:
            display_df = display_df[['Packet_No', 'Time', 'User_Name', 'Source_IP', 'Attack_Type', 'Status']]
        else:
            display_df = display_df[['Packet_No', 'Time', 'Prediction', 'Attack_Type', 'Status']]
        
        def color_rows(row):
            if 'Attack' in row['Status'] or row.get('Prediction') == 1:
                return ['background-color: rgba(255, 61, 0, 0.2); color: #FF3D00'] * len(row)
            return ['background-color: rgba(0, 230, 118, 0.1); color: #00E676'] * len(row)

        st.dataframe(display_df.style.apply(color_rows, axis=1), use_container_width=True, height=400)

except FileNotFoundError:
    st.warning("⚠️ Waiting for Network Traffic data from the Server...")

# ७. Smooth Auto-Refresh Logic
if auto_refresh:
    time.sleep(1.5)
    st.rerun()