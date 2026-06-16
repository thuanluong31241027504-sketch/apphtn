"""
Ballbot STM32 Monitor - OLED & VL53L0X
Realtime monitoring of laser distance and OLED display
"""

import streamlit as st
import serial
import serial.tools.list_ports
import threading
import time
import re
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Ballbot Monitor",
    page_icon="",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Custom CSS - Minimal design
st.markdown("""
<style>
    /* Main container */
    .main {
        padding: 0rem 1rem;
    }
    
    /* Typography */
    h1, h2, h3 {
        font-weight: 500;
        letter-spacing: -0.3px;
    }
    
    /* OLED Simulation */
    .oled-screen {
        background-color: #111;
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        border: 1px solid #333;
    }
    
    .oled-title {
        color: #0f0;
        font-family: monospace;
        font-size: 12px;
        letter-spacing: 1px;
    }
    
    .oled-distance {
        color: #fff;
        font-size: 48px;
        font-weight: bold;
        font-family: monospace;
        margin: 0.5rem 0;
    }
    
    .oled-label {
        color: #666;
        font-size: 10px;
        font-family: monospace;
    }
    
    .oled-divider {
        border-color: #333;
        margin: 0.75rem 0;
    }
    
    /* Status indicators */
    .status-connected {
        background-color: #e6f4ea;
        color: #137333;
        padding: 4px 12px;
        border-radius: 16px;
        font-size: 0.75rem;
        font-weight: 500;
        display: inline-block;
    }
    
    .status-disconnected {
        background-color: #fce8e6;
        color: #c5221f;
        padding: 4px 12px;
        border-radius: 16px;
        font-size: 0.75rem;
        font-weight: 500;
        display: inline-block;
    }
    
    /* Sensor card */
    .sensor-card {
        background-color: #f8f9fa;
        border-radius: 12px;
        padding: 1rem;
        text-align: center;
        border: 1px solid #e9ecef;
    }
    
    .sensor-value {
        font-size: 2rem;
        font-weight: 600;
        color: #1a73e8;
    }
    
    .sensor-label {
        font-size: 0.7rem;
        color: #5f6368;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Log panel */
    .log-panel {
        background-color: #f5f5f5;
        border-radius: 8px;
        padding: 0.75rem;
        font-family: monospace;
        font-size: 0.7rem;
        height: 200px;
        overflow-y: auto;
    }
    
    /* Divider */
    hr {
        margin: 1rem 0;
    }
    
    /* Info box */
    .info-box {
        background-color: #e8f0fe;
        padding: 0.75rem;
        border-radius: 8px;
        font-size: 0.8rem;
    }
    
    .warning-box {
        background-color: #fce8e6;
        padding: 0.75rem;
        border-radius: 8px;
        font-size: 0.8rem;
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
if 'rx_log' not in st.session_state:
    st.session_state.rx_log = []
if 'tx_log' not in st.session_state:
    st.session_state.tx_log = []

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
        except:
            return False
    return False

def read_serial_loop():
    while st.session_state.connected and st.session_state.serial:
        try:
            if st.session_state.serial.in_waiting:
                line = st.session_state.serial.readline().decode('utf-8', errors='ignore').strip()
                if line:
                    # Parse distance from STM32
                    if 'Distance:' in line:
                        numbers = re.findall(r'\d+', line)
                        if numbers:
                            st.session_state.distance = int(numbers[0])
                    elif 'DIST' in line.upper():
                        numbers = re.findall(r'\d+', line)
                        if numbers:
                            st.session_state.distance = int(numbers[0])
                    
                    # Store log
                    st.session_state.rx_log.insert(0, f"[{datetime.now().strftime('%H:%M:%S')}] RX: {line}")
                    if len(st.session_state.rx_log) > 30:
                        st.session_state.rx_log.pop()
            time.sleep(0.05)
        except:
            time.sleep(0.1)

# Sidebar - Connection
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
    
    # Status
    if st.session_state.connected:
        st.markdown('<div class="status-connected">Connected</div>', unsafe_allow_html=True)
        st.caption(f"Port: {selected_port}")
        st.caption("Baudrate: 115200")
    else:
        st.markdown('<div class="status-disconnected">Disconnected</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # System info
    st.markdown("## System")
    st.caption("MCU: STM32F103C8T6")
    st.caption("Sensor: VL53L0X (Laser ToF)")
    st.caption("Display: OLED SSD1306")
    st.caption("I2C1: OLED (PB6, PB7)")
    st.caption("I2C2: VL53L0X (PB10, PB11)")

# Main content
st.title("Ballbot Monitor")
st.caption("Real-time monitoring of OLED display and VL53L0X distance sensor")

# Status bar
if st.session_state.connected:
    st.markdown(f'<div class="info-box">Connected to {selected_port} | Receiving sensor data</div>', unsafe_allow_html=True)
else:
    st.markdown('<div class="warning-box">Not connected. Please connect to serial port.</div>', unsafe_allow_html=True)

st.markdown("---")

# Two columns: OLED Simulation and Sensor Data
col_oled, col_sensor = st.columns([2, 1])

with col_oled:
    st.markdown("### OLED Display")
    
    # OLED simulation with distance
    st.markdown(f"""
    <div class="oled-screen">
        <div class="oled-title">BALLBOT SYSTEM</div>
        <div class="oled-distance">{st.session_state.distance}</div>
        <div class="oled-label">Distance (mm)</div>
        <hr class="oled-divider">
        <div class="oled-label">VL53L0X Laser Sensor</div>
        <div class="oled-label">I2C2 (PB10, PB11)</div>
    </div>
    """, unsafe_allow_html=True)

with col_sensor:
    st.markdown("### Sensor Data")
    
    st.markdown(f"""
    <div class="sensor-card">
        <div class="sensor-value">{st.session_state.distance}</div>
        <div class="sensor-label">Distance (mm)</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Detection status
    if 20 < st.session_state.distance < 800:
        st.success("Object detected")
    elif st.session_state.distance >= 800:
        st.info("Object far away")
    else:
        st.warning("No object detected")

st.markdown("---")

# Control buttons
st.markdown("### Control")

cmd_cols = st.columns(2)

with cmd_cols[0]:
    if st.button("Read Distance", use_container_width=True):
        send_command("GET_DIST")

with cmd_cols[1]:
    if st.button("Refresh Display", use_container_width=True):
        send_command("REFRESH")

st.markdown("---")

# Communication logs
st.markdown("### Communication Log")

log_col1, log_col2 = st.columns(2)

with log_col1:
    st.markdown("**Received**")
    with st.container(height=250):
        if st.session_state.rx_log:
            for log in st.session_state.rx_log[:15]:
                st.text(log)
        else:
            st.caption("No data received")

with log_col2:
    st.markdown("**Sent**")
    with st.container(height=250):
        if st.session_state.tx_log:
            for log in st.session_state.tx_log[:15]:
                st.text(log)
        else:
            st.caption("No commands sent")

# Footer
st.markdown("---")
st.caption("Ballbot Monitoring System | STM32F103C8 | VL53L0X | OLED SSD1306")
