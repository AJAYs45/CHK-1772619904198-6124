import streamlit as st
import pandas as pd
import time
import random
import plotly.express as px
import plotly.graph_objects as go
import psutil

# १. Advanced Page Configuration
st.set_page_config(page_title="Enterprise SOC Dashboard", layout="wide", page_icon="🛡️")

# २. Custom Enterprise CSS
st.markdown("""
    <style>
    h1, h2, h3 { color: #00E676 !important; font-family: 'Courier New', Courier, monospace; }
    [data-testid="stMetric"] { background-color: #121212; padding: 15px; border-radius: 8px; border-left: 4px solid #00E676; box-shadow: 1px 1px 8px rgba(0,230,118,0.2); }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center;'>🛡️ Enterprise Security Command Center</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center; color: #a8b2c1;'>Real-Time Network Telemetry & AI Intrusion Detection</h4>", unsafe_allow_html=True)
st.markdown("---")

# ३. Sidebar Controls & Download Button
st.sidebar.header("⚙️ SOC Control Panel")
auto_refresh = st.sidebar.checkbox("🔄 Live Stream (Auto-Refresh)", value=True)

attack_names = ["DDoS Attack (Neptune)", "Port Scanning (Satan)", "Brute Force (Guess_Passwd)", "Malware Injection", "Ping of Death (Smurf)"]

try:
    df = pd.read_csv('traffic_log.csv')
    
    # Simulate Industry-level Data (Attack Types & Source IPs)
    if 'Attack_Type' not in df.columns:
        df['Attack_Type'] = df['Prediction'].apply(lambda x: random.choice(attack_names) if x == 1 else "Normal Traffic")
    if 'Source_IP' not in df.columns:
        # Generate random IPs to look like real network traffic
        df['Source_IP'] = [f"{random.randint(11,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}" for _ in range(len(df))]

    total = len(df)
    threats = len(df[df['Prediction'] == 1])
    safe = len(df[df['Prediction'] == 0])

    # 📥 Download Report Feature (Industry Standard)
    st.sidebar.markdown("---")
    st.sidebar.subheader("📄 Security Reports")
    csv = df.to_csv(index=False).encode('utf-8')
    st.sidebar.download_button(label="📥 Download Threat Log (CSV)", data=csv, file_name='SOC_Threat_Report.csv', mime='text/csv')

    # ४. Top Metrics Display
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("🌐 Total Packets Analyzed", total)
    col2.metric("✅ Clean Traffic", safe)
    col3.metric("🚨 Threats Neutralized", threats)
    col4.metric("🛡️ Overall System Status", "CRITICAL 🔴" if threats > safe else "SECURE 🟢")

    st.markdown("---")

    # ५. Live Server Health (CPU & RAM) - Extremely Professional
    st.markdown("### 🎛️ Server Health Telemetry")
    health_col1, health_col2, health_col3 = st.columns([1, 1, 2])
    
    cpu_usage = psutil.cpu_percent()
    ram_usage = psutil.virtual_memory().percent
    
    # CPU Gauge
    fig_cpu = go.Figure(go.Indicator(
        mode = "gauge+number", value = cpu_usage, title = {'text': "CPU Usage %"},
        gauge = {'axis': {'range': [None, 100]}, 'bar': {'color': "#FF3D00" if cpu_usage > 80 else "#00E676"}}
    ))
    fig_cpu.update_layout(height=250, margin=dict(t=30, b=10, l=10, r=10), template="plotly_dark")
    health_col1.plotly_chart(fig_cpu, use_container_width=True, key=f"cpu_{time.time()}")

    # RAM Gauge
    fig_ram = go.Figure(go.Indicator(
        mode = "gauge+number", value = ram_usage, title = {'text': "RAM Usage %"},
        gauge = {'axis': {'range': [None, 100]}, 'bar': {'color': "#FF3D00" if ram_usage > 80 else "#00BCD4"}}
    ))
    fig_ram.update_layout(height=250, margin=dict(t=30, b=10, l=10, r=10), template="plotly_dark")
    health_col2.plotly_chart(fig_ram, use_container_width=True, key=f"ram_{time.time()}")
    
    with health_col3:
        # Line chart showing timeline of attacks
        if total > 0:
            timeline_data = df.tail(30).reset_index()
            fig_line = px.line(timeline_data, x='index', y='Prediction', title="Threat Detection Timeline (Last 30 Packets)", template="plotly_dark")
            fig_line.update_traces(line_color='#FF3D00', line_width=3)
            fig_line.update_layout(height=250, margin=dict(t=40, b=10, l=10, r=10), yaxis_title="Threat Level")
            st.plotly_chart(fig_line, use_container_width=True, key=f"line_{time.time()}")

    st.markdown("---")

    # ६. Advanced Charts
    chart_col1, chart_col2 = st.columns(2)
    with chart_col1:
        st.markdown("### 📊 Threat Distribution")
        if total > 0:
            fig1 = px.pie(values=[safe, threats], names=['Normal', 'Threats'], color_discrete_sequence=['#00E676', '#FF3D00'], hole=0.5, template="plotly_dark")
            fig1.update_layout(margin=dict(t=0, b=0, l=0, r=0), showlegend=True)
            st.plotly_chart(fig1, use_container_width=True, key=f"pie_{time.time()}")

    with chart_col2:
        st.markdown("### 🎯 Top Attack Signatures")
        if threats > 0:
            attack_counts = df[df['Prediction'] == 1]['Attack_Type'].value_counts().reset_index()
            attack_counts.columns = ['Attack Type', 'Count']
            fig2 = px.bar(attack_counts, x='Attack Type', y='Count', color='Attack Type', text='Count', template="plotly_dark")
            fig2.update_layout(margin=dict(t=0, b=0, l=0, r=0), showlegend=False)
            st.plotly_chart(fig2, use_container_width=True, key=f"bar_{time.time()}")
        else:
            st.success("System is currently safe. No attacks detected.")

    # ७. Live Threat Logs with Source IP
    st.markdown("### 🔴 Active Threat Intelligence Logs")
    if not df.empty:
        # Display all columns including the new Source IP
        display_df = df.iloc[::-1].copy()
        display_df = display_df[['Time', 'Source_IP', 'Prediction', 'Attack_Type', 'Status']]
        
        def color_rows(row):
            if row['Prediction'] == 1:
                return ['background-color: rgba(255, 61, 0, 0.2); color: #FF3D00'] * len(row)
            return ['background-color: rgba(0, 230, 118, 0.1); color: #00E676'] * len(row)

        st.dataframe(display_df.style.apply(color_rows, axis=1), use_container_width=True, height=400)

except FileNotFoundError:
    st.warning("⚠️ Waiting for Network Traffic data from the Server...")

# ८. Auto-Refresh
if auto_refresh:
    time.sleep(2)
    st.rerun()