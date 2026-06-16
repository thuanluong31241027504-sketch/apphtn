"""
Xử lý giao tiếp Serial với STM32
Sau này sẽ mở rộng khi kết nối thật
"""

import serial
import serial.tools.list_ports
import threading
import queue

class SerialHandler:
    def __init__(self):
        self.serial = None
        self.is_connected = False
        self.data_queue = queue.Queue()
    
    def list_ports(self):
        """Liệt kê các cổng COM có sẵn"""
        ports = serial.tools.list_ports.comports()
        return [port.device for port in ports]
    
    def connect(self, port, baudrate=115200):
        """Kết nối đến STM32"""
        try:
            self.serial = serial.Serial(port, baudrate, timeout=1)
            self.is_connected = True
            return True
        except Exception as e:
            print(f"Lỗi kết nối: {e}")
            return False
    
    def disconnect(self):
        """Ngắt kết nối"""
        if self.serial and self.serial.is_open:
            self.serial.close()
        self.is_connected = False
    
    def send_command(self, command):
        """Gửi lệnh xuống STM32"""
        if self.is_connected and self.serial:
            self.serial.write(f"{command}\n".encode())
            return True
        return False
    
    def read_data(self):
        """Đọc dữ liệu từ STM32"""
        if self.is_connected and self.serial and self.serial.in_waiting:
            return self.serial.readline().decode().strip()
        return None
