"""
Ballbot STM32 Control Interface
Giao diện điều khiển và giám sát Ballbot
"""

import streamlit as st
import time
from datetime import datetime

# Cấu hình trang
st.set_page_config(
    page_title="Ballbot STM32 Control",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS tùy chỉnh để tăng tính thẩm mỹ
st.markdown("""
<style>
    .stButton button {
        width: 100%;
        border-radius: 10px;
        height: 60px;
        font-size: 18px;
        font-weight: bold;
    }
    .stMetric {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 10px;
    }
    .title {
        text-align: center;
        color: #1e88e5;
    }
</style>
""", unsafe_allow_html=True)

# Tiêu đề chính
st.markdown('<h1 class="title">🤖 Ballbot STM32 Control Center</h1>', unsafe_allow_html=True)
st.markdown("---")

# Sidebar - Thông tin dự án
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/robot.png", width=80)
    st.markdown("## 📋 Thông tin")
    st.info("""
    **Dự án Ballbot**
    - 3 động cơ GA25
    - 2 driver TB6612
    - 3 laser VL53L0X
    - 1 MPU6050
    - 1 OLED
    """)
    
    st.markdown("---")
    st.markdown("### 🔌 Kết nối")
    connected = st.checkbox("Kết nối STM32", value=False)
    if connected:
        st.success("✅ Đã kết nối")
    else:
        st.warning("⚠️ Chưa kết nối")
    
    st.markdown("---")
    st.markdown("### 🎮 Trạng thái")
    status_placeholder = st.empty()

# Tab layout
tab1, tab2, tab3, tab4 = st.tabs([
    "🎮 Điều khiển", 
    "📊 Cảm biến", 
    "⚙️ Cấu hình", 
    "📈 Biểu đồ"
])

# ==================== TAB 1: ĐIỀU KHIỂN ====================
with tab1:
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 🏎️ Động cơ")
        speed1 = st.slider("Motor 1", 0, 100, 0, key="m1")
        speed2 = st.slider("Motor 2", 0, 100, 0, key="m2")
        speed3 = st.slider("Motor 3", 0, 100, 0, key="m3")
        
        if st.button("🟢 START ALL", type="primary"):
            st.success("Đã gửi lệnh START")
            status_placeholder.info("Motor đang chạy...")
        
        if st.button("🔴 STOP ALL"):
            st.warning("Đã gửi lệnh STOP")
            status_placeholder.warning("Motor đã dừng")
    
    with col2:
        st.markdown("### 🎯 Hướng di chuyển")
        if st.button("⬆️ TIẾN"):
            st.success("Tiến lên")
        if st.button("⬇️ LÙI"):
            st.success("Lùi lại")
        if st.button("⬅️ TRÁI"):
            st.success("Rẽ trái")
        if st.button("➡️ PHẢI"):
            st.success("Rẽ phải")
    
    with col3:
        st.markdown("### 💡 Điều khiển khác")
        led_state = st.toggle("LED PB12", value=False)
        if led_state:
            st.success("LED đã bật")
        else:
            st.info("LED đã tắt")
        
        buzzer = st.button("🔊 BUZZER")
        if buzzer:
            st.warning("Kêu BEEP!")

# ==================== TAB 2: CẢM BIẾN ====================
with tab2:
    st.markdown("### 📡 Cảm biến khoảng cách VL53L0X")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Laser 1", "---", "mm")
    with col2:
        st.metric("Laser 2", "---", "mm")
    with col3:
        st.metric("Laser 3", "---", "mm")
    
    st.markdown("---")
    st.markdown("### ⚡ Cảm biến góc MPU6050")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Góc Roll", "---", "°")
        st.metric("Gia tốc X", "---", "g")
    with col2:
        st.metric("Góc Pitch", "---", "°")
        st.metric("Gia tốc Y", "---", "g")
    
    if st.button("🔄 Cập nhật dữ liệu"):
        with st.spinner("Đang đọc cảm biến..."):
            time.sleep(1)
            st.success("Đã cập nhật!")

# ==================== TAB 3: CẤU HÌNH ====================
with tab3:
    st.markdown("### ⚙️ Cấu hình hệ thống")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🔧 PID Controller")
        kp = st.number_input("Kp", value=1.5, step=0.1, format="%.2f")
        ki = st.number_input("Ki", value=0.0, step=0.1, format="%.2f")
        kd = st.number_input("Kd", value=0.0, step=0.1, format="%.2f")
        
        if st.button("💾 Lưu PID"):
            st.success(f"Đã lưu PID: Kp={kp}, Ki={ki}, Kd={kd}")
    
    with col2:
        st.markdown("#### 🔄 I2C Settings")
        i2c_speed = st.selectbox("Tốc độ I2C", ["100kHz", "400kHz", "1MHz"])
        st.selectbox("Bus I2C", ["I2C1 (PB6,PB7)", "I2C2 (PB10,PB11)"])
        
        if st.button("🔄 Reset hệ thống"):
            st.warning("Đang reset...")
            time.sleep(1)
            st.success("Đã reset xong!")

# ==================== TAB 4: BIỂU ĐỒ ====================
with tab4:
    st.markdown("### 📈 Biểu đồ dữ liệu realtime")
    
    # Dữ liệu mẫu (sau này thay bằng dữ liệu thật từ STM32)
    import pandas as pd
    import numpy as np
    
    # Tạo dữ liệu giả lập
    timestamps = [f"{i}s" for i in range(20)]
    distances1 = np.random.randint(100, 500, 20)
    distances2 = np.random.randint(100, 500, 20)
    distances3 = np.random.randint(100, 500, 20)
    
    df = pd.DataFrame({
        'Thời gian': timestamps,
        'Laser 1': distances1,
        'Laser 2': distances2,
        'Laser 3': distances3
    })
    
    st.line_chart(df.set_index('Thời gian'))
    
    # Hiển thị bảng dữ liệu
    with st.expander("📋 Xem dữ liệu chi tiết"):
        st.dataframe(df, use_container_width=True)

# ==================== FOOTER ====================
st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: gray;'>Ballbot Project - STM32F103C8 | VL53L0X | MPU6050 | OLED</p>",
    unsafe_allow_html=True
)

# Cập nhật trạng thái trong sidebar mỗi giây
if connected:
    status_placeholder.success("✅ Hệ thống đang hoạt động")
else:
    status_placeholder.warning("⚠️ Chưa kết nối STM32")
