"""
Ballbot STM32 Control - Realtime Monitoring
Control and monitor Ballbot via Serial communication
"""

import streamlit as st
import serial
import serial.tools.list_ports
import threading
import time
import pandas as pd
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Ballbot Control",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS - Minimal design
st.markdown("""
<style>
    /* Main container */
    .main {
        padding: 0rem 1rem;
    }
    
    /* Headers */
    h1, h2, h3 {
        font-weight: 500;
        letter-spacing: -0.5px;
    }
    
    /* Metric cards */
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 12px;
        padding: 1rem;
        text-align: center;
        border: 1px solid #e9ecef;
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 600;
        color: #1a73e8;
    }
    
    .metric-label {
        font-size: 0.85rem;
        color: #5f6368;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Status indicators */
    .status-connected {
        background-color: #e6f4ea;
        color: #137333;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 500;
    }
    
    .status-disconnected {
        background-color: #fce8e6;
        color: #c5221f;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 500;
    }
    
    /* Command log */
    .log-entry {
        font-family: monospace;
        font-size: 0.8rem;
        padding: 4px 0;
        border-bottom: 1px solid #f0f0f0;
    }
    
    /* Sensor display */
    .sensor-panel {
        background-color: #f8f9fa;
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        border: 1px solid #e9ecef;
    }
    
    /* Buttons */
    .stButton button {
        border-radius: 8px;
        font-weight: 500;
    }
    
    /* Divider */
    hr {
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'serial' not in st.session_state:
    st.session_state.serial = None
if 'connected' not in st.session_state:
    st.session_state.connected = False
if 'distance' not in st.session_state:
    st.session_state.distance = 0
if 'log_data' not in st.session_state:
    st.session_state.log_data = []
if 'rx_log' not in st.session_state:
    st.session_state.rx_log = []
if 'tx_log' not in st.session_state:
    st.session_state.tx_log = []
if 'reading_thread' not in st.session_state:
    st.session_state.reading_thread = None
if 'motor_speeds' not in st.session_state:
    st.session_state.motor_speeds = [0, 0, 0]

# Helper functions
def get_ports():
    ports = serial.tools.list_ports.comports()
    return [p.device for p in ports]

def connect_serial(port, baud=115200):
    try:
        ser = serial.Serial(port, baud, timeout=0.5)
        time.sleep(1.5)
        return ser
    except Exception as e:
        st.error(f"Connection failed: {e}")
        return None

def disconnect_serial():
    if st.session_state.serial and st.session_state.serial.is_open:
        st.session_state.serial.close()
    st.session_state.connected = False
    st.session_state.serial = None

def send_command(cmd):
    if st.session_state.connected and st.session_state.serial:
        try:
            full_cmd = cmd + '\n'
            st.session_state.serial.write(full_cmd.encode())
            st.session_state.tx_log.insert(0, f"[{datetime.now().strftime('%H:%M:%S')}] TX: {cmd}")
            if len(st.session_state.tx_log) > 20:
                st.session_state.tx_log.pop()
            return True
        except Exception as e:
            st.error(f"Send failed: {e}")
            return False
    return False

def read_serial_loop():
    while st.session_state.connected and st.session_state.serial:
        try:
            if st.session_state.serial.in_waiting:
                line = st.session_state.serial.readline().decode('utf-8', errors='ignore').strip()
                if line:
                    # Parse distance data
                    if 'DIST' in line.upper() or 'MM' in line:
                        parts = line.split(':')
                        if len(parts) > 1:
                            try:
                                val = int(''.join(filter(str.isdigit, parts[1])))
                                st.session_state.distance = val
                            except:
                                pass
                    
                    # Store log
                    st.session_state.rx_log.insert(0, f"[{datetime.now().strftime('%H:%M:%S')}] RX: {line}")
                    if len(st.session_state.rx_log) > 20:
                        st.session_state.rx_log.pop()
            
            time.sleep(0.05)
        except:
            time.sleep(0.1)

# Sidebar - Connection panel
with st.sidebar:
    st.markdown("## Connection")
    
    ports = get_ports()
    selected_port = st.selectbox("Serial Port", ports if ports else ["No port found"])
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Connect", use_container_width=True):
            if selected_port and selected_port != "No port found":
                ser = connect_serial(selected_port)
                if ser:
                    st.session_state.serial = ser
                    st.session_state.connected = True
                    thread = threading.Thread(target=read_serial_loop, daemon=True)
                    thread.start()
                    st.rerun()
    
    with col2:
        if st.button("Disconnect", use_container_width=True):
            disconnect_serial()
            st.rerun()
    
    # Status indicator
    if st.session_state.connected:
        st.markdown('<div class="status-connected">Connected</div>', unsafe_allow_html=True)
        st.caption(f"Port: {selected_port}")
    else:
        st.markdown('<div class="status-disconnected">Disconnected</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # System info
    st.markdown("## System")
    st.caption("STM32F103C8T6")
    st.caption("VL53L0X Laser Sensor")
    st.caption("OLED Display")
    st.caption("TB6612 Motor Driver")

# Main content
st.title("Ballbot Control System")

# Status bar
if st.session_state.connected:
    st.markdown(f'<div style="display: flex; justify-content: space-between; margin-bottom: 1rem;"><span>Port: {selected_port}</span><span>Baudrate: 115200</span><span>Connected: Yes</span></div>', unsafe_allow_html=True)
else:
    st.markdown('<div style="background-color: #fce8e6; padding: 0.75rem; border-radius: 8px; margin-bottom: 1rem;">Not connected. Please connect to serial port.</div>', unsafe_allow_html=True)

# Main layout columns
col_left, col_right = st.columns([2, 1])

with col_left:
    # Sensor panel
    st.markdown("### Laser Sensor")
    
    col_dist1, col_dist2, col_dist3 = st.columns(3)
    with col_dist1:
        st.markdown(f"""
        <div class="sensor-panel">
            <div class="metric-value">{st.session_state.distance}</div>
            <div class="metric-label">Distance (mm)</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col_dist2:
        st.markdown(f"""
        <div class="sensor-panel">
            <div class="metric-value">{"---"}</div>
            <div class="metric-label">Laser 2</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col_dist3:
        st.markdown(f"""
        <div class="sensor-panel">
            <div class="metric-value">{"---"}</div>
            <div class="metric-label">Laser 3</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Motor control
    st.markdown("### Motor Control")
    
    motor_cols = st.columns(3)
    speeds = [0, 0, 0]
    
    for i, col in enumerate(motor_cols):
        with col:
            st.markdown(f"**Motor {i+1}**")
            speeds[i] = st.slider("", 0, 100, st.session_state.motor_speeds[i], key=f"m{i}", label_visibility="collapsed")
            st.progress(speeds[i] / 100)
    
    # Update motor speeds
    if speeds != st.session_state.motor_speeds:
        st.session_state.motor_speeds = speeds.copy()
        if st.session_state.connected:
            cmd = f"MOTOR:{speeds[0]},{speeds[1]},{speeds[2]}"
            send_command(cmd)
    
    # Command buttons
    st.markdown("### Commands")
    cmd_cols = st.columns(4)
    
    with cmd_cols[0]:
        if st.button("Read Sensor", use_container_width=True):
            send_command("GET_DIST")
    
    with cmd_cols[1]:
        if st.button("LED ON", use_container_width=True):
            send_command("LED_ON")
    
    with cmd_cols[2]:
        if st.button("LED OFF", use_container_width=True):
            send_command("LED_OFF")
    
    with cmd_cols[3]:
        if st.button("Reset", use_container_width=True):
            send_command("RESET")
    
    st.markdown("---")
    
    # Control pad
    st.markdown("### Direction Control")
    pad_cols = st.columns(3)
    
    with pad_cols[0]:
        st.write("")
    with pad_cols[1]:
        if st.button("Forward", use_container_width=True):
            send_command("DIR:FWD")
    with pad_cols[2]:
        st.write("")
    
    with pad_cols[0]:
        if st.button("Left", use_container_width=True):
            send_command("DIR:LEFT")
    with pad_cols[1]:
        if st.button("Stop", use_container_width=True):
            send_command("DIR:STOP")
    with pad_cols[2]:
        if st.button("Right", use_container_width=True):
            send_command("DIR:RIGHT")
    
    with pad_cols[0]:
        st.write("")
    with pad_cols[1]:
        if st.button("Backward", use_container_width=True):
            send_command("DIR:BWD")
    with pad_cols[2]:
        st.write("")

with col_right:
    # OLED Display simulation
    st.markdown("### OLED Display")
    st.markdown(f"""
    <div style="background-color: #1a1a2e; border-radius: 12px; padding: 1rem; text-align: center;">
        <div style="color: #00ff88; font-family: monospace; font-size: 12px;">Ballbot Control</div>
        <div style="color: #ffffff; font-size: 32px; font-weight: bold; margin: 0.5rem 0;">{st.session_state.distance}</div>
        <div style="color: #888888; font-size: 10px;">Distance (mm)</div>
        <hr style="margin: 0.5rem 0;">
        <div style="color: #ffffff; font-family: monospace; font-size: 10px; text-align: left;">
            M1: {st.session_state.motor_speeds[0]}%<br>
            M2: {st.session_state.motor_speeds[1]}%<br>
            M3: {st.session_state.motor_speeds[2]}%
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Communication logs
    st.markdown("### Communication")
    
    log_tabs = st.tabs(["Received", "Sent"])
    
    with log_tabs[0]:
        if st.session_state.rx_log:
            for log in st.session_state.rx_log[:10]:
                st.text(log)
        else:
            st.caption("No data received")
    
    with log_tabs[1]:
        if st.session_state.tx_log:
            for log in st.session_state.tx_log[:10]:
                st.text(log)
        else:
            st.caption("No commands sent")

# Footer
st.markdown("---")
st.caption("Ballbot Control System | STM32F103C8 | VL53L0X | OLED | TB6612")
