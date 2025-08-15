#!/bin/python3
# NobleProg Tech Ltd 2025 all rights reserved
# NobleProg Tech Ltd is registered in SAR Hong Kong
# This software is copyrighted
# To purchuse hardware of ddminiscreen visit www.dadesktop.com and ebay site
# ddsupport+ddminiscreen@nobleprog.com
import subprocess
import glob
import sys
import re

def get_miniscreen_on_motherboard():
    def compute_depth(path):
        return len([part for part in path.split('/') if part != ''])
    
    device_names = glob.glob('/dev/ttyACM*')

    if not device_names:
        print("No ttyACM devices found.")
        return None
    
    try:
        cmd = ['udevadm', 'info', '-q', 'path', '-n'] + device_names
        result = subprocess.run(
            cmd,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
    
        output_lines = result.stdout.strip().splitlines()
    
        if len(output_lines) != len(device_names):
            print(f"Warning: Returned {len(output_lines)} paths for {len(device_names)} devices")
    
        depths = [compute_depth(dev_path) for dev_path in output_lines]
        min_depth = min(depths) if depths else 0

        acm_devices = [
            dev_path for dev_path, depth in zip(output_lines, depths)
            if depth == min_depth
        ]
        #print(acm_devices)

    
    except subprocess.CalledProcessError as e:
        print(f"Error querying devices: {e.stderr.strip()}")
    except FileNotFoundError:
        print("Error: 'udevadm' command not found. Please ensure udev is installed.")
    
    if not acm_devices:
        return None
    
    pattern = r'tty/([^/]+)$'
    match = re.search(pattern, acm_devices[0])
    if match:
        tty_device = match.group(1)
        device_name = f'/dev/{tty_device}'
        #print(f"\nMiniScreen running on {device_name}")
        return device_name
    else:
        return None


com_name = get_miniscreen_on_motherboard()

if not com_name:
    #print(f"\nNo usb mini screen found, please plug in one to USB port which on motherboard")
    sys.exit(1)

import serial,time,psutil
from PIL import Image, ImageDraw, ImageFont

RED = 0xf800
GREEN = 0x07e0
BLUE = 0x001f
WHITE = 0xffff
BLACK = 0x0000
YELLOW = 0xFFE0

size_USE_X1=160
size_USE_Y1=80

State_change = 1
def SER_Read():
    global Device_State
    try:
        Data_U1 = ser.read(ser.in_waiting)
        return Data_U1
    except: 
        Device_State = 0
        ser.close()
        return 0

State_change = 1
try:
    ser=serial.Serial(com_name,19200,timeout=0.5)
except OSError:
    sys.exit(1)

def LCD_Set_Color(LCD_D0, LCD_D1):
    hex_use = int(2).to_bytes(1, byteorder="little")
    hex_use = hex_use + int(2).to_bytes(1, byteorder="little")
    hex_use = hex_use + int(LCD_D0 // 256).to_bytes(1, byteorder="little")
    hex_use = hex_use + int(LCD_D0 % 256).to_bytes(1, byteorder="little")
    hex_use = hex_use + int(LCD_D1 // 256).to_bytes(1, byteorder="little")
    hex_use = hex_use + int(LCD_D1 % 256).to_bytes(1, byteorder="little")
    SER_Write(hex_use)

def LCD_Set_Size(LCD_D0, LCD_D1):
    hex_use = int(2).to_bytes(1, byteorder="little")
    hex_use = hex_use + int(1).to_bytes(1, byteorder="little")
    hex_use = hex_use + int(LCD_D0 // 256).to_bytes(1, byteorder="little")
    hex_use = hex_use + int(LCD_D0 % 256).to_bytes(1, byteorder="little")
    hex_use = hex_use + int(LCD_D1 // 256).to_bytes(1, byteorder="little")
    hex_use = hex_use + int(LCD_D1 % 256).to_bytes(1, byteorder="little")
    SER_Write(hex_use)
 
def SER_Write(Data_U0):
    global Device_State
    try:
        if (False == ser.is_open):
            Device_State = 0
        ser.write(Data_U0)
    except:
        Device_State = 0
        ser.close()

def LCD_Set_XY(LCD_D0, LCD_D1):
    hex_use = int(2).to_bytes(1, byteorder="little")
    hex_use = hex_use + int(0).to_bytes(1, byteorder="little")
    hex_use = hex_use + int(LCD_D0 // 256).to_bytes(1, byteorder="little")
    hex_use = hex_use + int(LCD_D0 % 256).to_bytes(1, byteorder="little")
    hex_use = hex_use + int(LCD_D1 // 256).to_bytes(1, byteorder="little")
    hex_use = hex_use + int(LCD_D1 % 256).to_bytes(1, byteorder="little")
    SER_Write(hex_use)

def LCD_Photo(LCD_X, LCD_Y, LCD_X_Size, LCD_Y_Size, Page_Add):
    global Device_State
    LCD_Set_XY(LCD_X, LCD_Y)
    LCD_Set_Size(LCD_X_Size, LCD_Y_Size)
    hex_use = int(2).to_bytes(1, byteorder="little")
    hex_use = hex_use + int(3).to_bytes(1, byteorder="little")
    hex_use = hex_use + int(0).to_bytes(1, byteorder="little")
    hex_use = hex_use + int(Page_Add // 256).to_bytes(1, byteorder="little")
    hex_use = hex_use + int(Page_Add % 256).to_bytes(1, byteorder="little")
    hex_use = hex_use + int(0).to_bytes(1, byteorder="little")
    SER_Write(hex_use)
    while (1):
        time.sleep(0.001)
        recv = SER_Read()
        if (recv == 0):
            return 0
        elif (len(recv) != 0):
            if ((recv[0] != hex_use[0]) or (recv[1] != hex_use[1])):
                Device_State = 0
            break

def LCD_ASCII_32X64_MIX(LCD_X, LCD_Y, Txt, LCD_FC, BG_Page, Num_Page):
    global Device_State
    LCD_Set_XY(LCD_X, LCD_Y)
    LCD_Set_Color(LCD_FC, BG_Page)
    hex_use = int(2).to_bytes(1, byteorder="little")
    hex_use = hex_use + int(3).to_bytes(1, byteorder="little")
    hex_use = hex_use + int(5).to_bytes(1, byteorder="little")
    hex_use = hex_use + int(ord(Txt)).to_bytes(1, byteorder="little")
    hex_use = hex_use + int(Num_Page // 256).to_bytes(1, byteorder="little")
    hex_use = hex_use + int(Num_Page % 256).to_bytes(1, byteorder="little")
    SER_Write(hex_use)
    print(hex_use)
    while (1):
        recv = SER_Read() 
        if (recv == 0):
            return 0
        elif (len(recv) != 0):
            if ((recv[0] != hex_use[0]) or (recv[1] != hex_use[1])):
                Device_State = 0
            break

def show_PC_time():
    global State_change
    FC = YELLOW
    photo_add = 3826
    num_add = 3651
    if (State_change == 1):
        State_change = 0
        LCD_Photo(0, 0, 160, 80, photo_add)
        LCD_ASCII_32X64_MIX(56 + 8, 8, ':', FC, photo_add, num_add)
    if (State_change == 0):
        LCD_ASCII_32X64_MIX(0 + 8, 8, chr((time_h // 10) + 48), FC, photo_add, num_add)
        LCD_ASCII_32X64_MIX(32 + 8, 8, chr((time_h % 10) + 48), FC, photo_add, num_add)
        LCD_ASCII_32X64_MIX(80 + 8, 8, chr((time_m // 10) + 48), FC, photo_add, num_add)
        LCD_ASCII_32X64_MIX(112 + 8, 8, chr((time_m % 10) + 48), FC, photo_add, num_add)
        time.sleep(0.2)


def LCD_ADD(LCD_X, LCD_Y, LCD_X_Size, LCD_Y_Size):  #
    global Device_State
    LCD_Set_XY(LCD_X, LCD_Y)
    LCD_Set_Size(LCD_X_Size, LCD_Y_Size)
    hex_use = int(2).to_bytes(1, byteorder="little")
    hex_use = hex_use + int(3).to_bytes(1, byteorder="little")
    hex_use = hex_use + int(7).to_bytes(1, byteorder="little")
    hex_use = hex_use + int(0).to_bytes(1, byteorder="little")
    hex_use = hex_use + int(0).to_bytes(1, byteorder="little")
    hex_use = hex_use + int(0).to_bytes(1, byteorder="little")
    SER_Write(hex_use)
    while (1):
        time.sleep(0.001)
        recv = SER_Read()
        if (recv == 0):
            return 0
        elif (len(recv) != 0):
            if ((recv[0] != hex_use[0]) or (recv[1] != hex_use[1])):
                Device_State = 0
            break

def Screen_Date_Process(Photo_data):
    Photo_data_use = Photo_data
    hex_use = bytearray()
    for j in range(0, size_USE_X1 * size_USE_Y1 // 128):
        data_w = Photo_data_use[:128]
        Photo_data_use = Photo_data_use[128:]
        cmp_use = []
        for i in range(0, 64):
            cmp_use.append(data_w[i * 2 + 0] * 65536 + data_w[i * 2 + 1])
        result = max(set(cmp_use), key=cmp_use.count)
        hex_use.append(2)
        hex_use.append(4)
        color_ram = result
        hex_use.append(color_ram >> 24)
        color_ram = color_ram % 16777216
        hex_use.append(color_ram >> 16)
        color_ram = color_ram % 65536
        hex_use.append(color_ram >> 8)
        hex_use.append(color_ram % 256)
        for i in range(0, 64):
            if ((data_w[i * 2 + 0] * 65536 + data_w[i * 2 + 1]) != result):
                hex_use.append(4)
                hex_use.append(i)
                hex_use.append(data_w[i * 2 + 0] >> 8)
                hex_use.append(data_w[i * 2 + 0] % 256)
                hex_use.append(data_w[i * 2 + 1] >> 8)
                hex_use.append(data_w[i * 2 + 1] % 256)
        hex_use.append(2)
        hex_use.append(3)
        hex_use.append(8)
        hex_use.append(1)
        hex_use.append(0)
        hex_use.append(0)
    if (size_USE_X1 * size_USE_Y1 * 2 % 256 != 0):
        data_w = Photo_data_use
        for i in range(size_USE_X1 * size_USE_Y1 * 2 % 256, 256):
            data_w.append(0xffff)
        for i in range(0, 64):
            hex_use.append(4)
            hex_use.append(i)
            hex_use.append(data_w[i * 2 + 0] >> 8)
            hex_use.append(data_w[i * 2 + 0] % 256)
            hex_use.append(data_w[i * 2 + 1] >> 8)
            hex_use.append(data_w[i * 2 + 1] % 256)
        hex_use.append(2)
        hex_use.append(3)
        hex_use.append(8)
        hex_use.append(0)
        hex_use.append(size_USE_X1 * size_USE_Y1 * 2 % 256)
        hex_use.append(0)
    return hex_use

netspeed_last_refresh_time = None
netspeed_last_refresh_snetio = None
netspeed_plot_data = None
def sizeof_fmt(num, suffix="B", base=1024.0):
    # Use KiB for small value
    if abs(num) < base:
        return f"{num / base:3.1f}Ki{suffix}"
    for unit in ("", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"):
        if abs(num) < base:
            return f"{num:3.1f}{unit}{suffix}"
        num /= base
    return f"{num:.1f}Yi{suffix}"

import socket

def get_ip_starting_with_192():
    for iface, addrs in psutil.net_if_addrs().items():
        for addr in addrs:
            if addr.family == socket.AF_INET and addr.address.startswith("192."):
                return addr.address


def show_server_info(text_color=(255, 128, 0)):
    im1 = Image.new('RGB', (size_USE_X1, size_USE_Y1), (0, 0, 0))
    draw = ImageDraw.Draw(im1)
    font_size = 16
    font = ImageFont.truetype("DejaVuSerif.ttf", font_size)
    total_memory = psutil.virtual_memory().total / (1024 ** 3)
    draw.text((0, 0), f"{total_memory:.0f} GB", fill=(255, 155,155), font=font)
    text = time.strftime('%Y%m%d  %H:%M:%S',time.localtime())
    draw.text((0, 20), text, fill=(0,255, 0), font=font)
    import socket
    hostname = socket.gethostname()
    draw.text((0, 40), hostname, fill=(0,255,255), font=font)
    ip = get_ip_starting_with_192()
    # print(f"DEBUG: Got ip={ip}")
    if ip is None:
        ip = "NA"
    draw.text((0, 60), ip, fill=text_color, font=font)


    im2 = im1.load()
    hex_16RGB = []
    for y in range(0, size_USE_Y1):
        for x in range(0, size_USE_X1):
            hex_16RGB.append(
                ((im2[x, y][0] >> 3) << 11) | ((im2[x, y][1] >> 2) << 5) | (im2[x, y][2] >> 3))
    hexstream = Screen_Date_Process(hex_16RGB)
    LCD_ADD((160 - size_USE_X1) // 2, (80 - size_USE_Y1) // 2, size_USE_X1, size_USE_Y1)
    SER_Write(hexstream)
    time.sleep(1)


hex_code = int(0).to_bytes(1, byteorder="little")
hex_code = hex_code + b'MSNCN'
SER_Write(hex_code)
time.sleep(0.25)

show_server_info()
