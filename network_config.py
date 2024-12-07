import os
import configparser
import subprocess
import time
import sys
import psutil
import re
from tkinter import messagebox

def get_config_path():
    # 判断是否是打包环境
    if hasattr(sys, '_MEIPASS'):
        # 获取打包后的资源路径
        config_path = os.path.join(sys._MEIPASS, "static.ini")
    else:
        # 获取桌面路径
        config_path = os.path.join(os.path.expanduser("~"), "Desktop", "Ethernet-IP-Switch", "static.ini")
    
    return config_path

# 删除配置文件
def delete_static_ini():
    """
    删除 static.ini 文件。如果文件存在，则删除；如果不存在，则打印提示信息。
    """
    config_path = get_config_path()
    if os.path.exists(config_path):
        try:
            os.remove(config_path)
            print(f"{config_path} 已成功删除。")
        except Exception as e:
            print(f"删除文件时出错: {e}")
    else:
        print(f"{config_path} 不存在，无需删除。")

# 读取配置文件
def load_static_config():
    config = configparser.ConfigParser()
    config_path = get_config_path()

    if os.path.exists(config_path):
        config.read(config_path)
        return {
            "static_ip1": config.get("STATIC1", "IP", fallback=""),
            "static_mask1": config.get("STATIC1", "Mask", fallback=""),
            "static_gateway1": config.get("STATIC1", "Gateway", fallback=""),
            "static_dns1_1": config.get("STATIC1", "DNS1", fallback=""),
            "static_dns2_1": config.get("STATIC1", "DNS2", fallback=""),

            "static_ip2": config.get("STATIC2", "IP", fallback=""),
            "static_mask2": config.get("STATIC2", "Mask", fallback=""),
            "static_gateway2": config.get("STATIC2", "Gateway", fallback=""),
            "static_dns1_2": config.get("STATIC2", "DNS1", fallback=""),
            "static_dns2_2": config.get("STATIC2", "DNS2", fallback=""),
        }
    return {}

# 保存固定 IP1 配置
def save_static_config1(ip, mask, gateway, dns1, dns2):
    config = configparser.ConfigParser()
    config_path = get_config_path()

    if os.path.exists(config_path):
        config.read(config_path)
    else:
        config.add_section("STATIC1")

    config["STATIC1"] = {
        "IP": ip,
        "Mask": mask,
        "Gateway": gateway,
        "DNS1": dns1,
        "DNS2": dns2,
    }

    # 确保配置文件目录存在
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    
    with open(config_path, "w") as config_file:
        config.write(config_file)

# 保存固定 IP2 配置
def save_static_config2(ip, mask, gateway, dns1, dns2):
    config = configparser.ConfigParser()
    config_path = get_config_path()

    if os.path.exists(config_path):
        config.read(config_path)
    else:
        config.add_section("STATIC2")

    config["STATIC2"] = {
        "IP": ip,
        "Mask": mask,
        "Gateway": gateway,
        "DNS1": dns1,
        "DNS2": dns2,
    }

    # 确保配置文件目录存在
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    
    with open(config_path, "w") as config_file:
        config.write(config_file)

# 切换到 DHCP
def switch_to_dhcp():
    subprocess.run('netsh interface ip set address name="以太网" source=dhcp', shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
    subprocess.run('netsh interface ip set dns name="以太网" source=dhcp', shell=True, creationflags=subprocess.CREATE_NO_WINDOW)

# 切换到固定静态 IP1
def switch_to_fixed_static1():
    config = load_static_config()
    static_ip = config.get("static_ip1")
    static_mask = config.get("static_mask1")
    static_gateway = config.get("static_gateway1")
    static_dns1 = config.get("static_dns1_1")
    static_dns2 = config.get("static_dns2_1")

    if static_ip and static_mask and static_gateway and static_dns1:
        subprocess.run(f'netsh interface ip set address name="以太网" static {static_ip} {static_mask} {static_gateway}', shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
        subprocess.run(f'netsh interface ip set dns name="以太网" static {static_dns1}', shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
        if static_dns2:
            subprocess.run(f'netsh interface ip add dns name="以太网" {static_dns2} index=2', shell=True, creationflags=subprocess.CREATE_NO_WINDOW)

# 切换到固定静态 IP2
def switch_to_fixed_static2():
    config = load_static_config()
    static_ip = config.get("static_ip2")
    static_mask = config.get("static_mask2")
    static_gateway = config.get("static_gateway2")
    static_dns1 = config.get("static_dns1_2")
    static_dns2 = config.get("static_dns2_2")

    if static_ip and static_mask and static_gateway and static_dns1:
        subprocess.run(f'netsh interface ip set address name="以太网" static {static_ip} {static_mask} {static_gateway}', shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
        subprocess.run(f'netsh interface ip set dns name="以太网" static {static_dns1}', shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
        if static_dns2:
            subprocess.run(f'netsh interface ip add dns name="以太网" {static_dns2} index=2', shell=True, creationflags=subprocess.CREATE_NO_WINDOW)

# 获取当前的 IP 配置
def get_current_ip_config():
    command = 'netsh interface ip show config name="以太网"'
    result = subprocess.run(command, capture_output=True, text=True, shell=True, creationflags=subprocess.CREATE_NO_WINDOW)

    ip, mask, gateway, dns1, dns2 = None, None, None, None, None
    for line in result.stdout.splitlines():
        if "IP 地址" in line and not ip:
            ip = line.split(":")[1].strip()
        if "子网掩码" in line and not mask:
            mask = line.split(":")[1].strip()
        if "默认网关" in line and not gateway:
            gateway = line.split(":")[1].strip()
        if "DNS 服务器" in line:
            if not dns1:
                dns1 = line.split(":")[1].strip()
            elif not dns2:
                dns2 = line.strip()

    return ip, mask, gateway, dns1, dns2


# 检查网络是否启用 DHCP
def check_dhcp():
    # 你可以根据需要指定接口名称，默认为 "以太网"
    interface = "以太网"
    
    # 临时文件用于保存命令输出
    temp_file = os.path.join(os.getenv('TEMP'), 'display_dhcp_status_output.txt')
    
    # 运行 netsh 命令来获取 DHCP 配置
    subprocess.run(f'netsh interface ip show config name={interface} > "{temp_file}"', 
                   shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
    
    dhcp_status = None
    retries = 5  # 如果遇到权限问题，尝试几次
    
    while retries > 0:
        try:
            with open(temp_file, 'r', encoding='gbk') as file:
                # 搜索 "DHCP 已启用" 来判断 DHCP 是否开启
                for line in file:
                    if "DHCP 已启用" in line:
                        dhcp_status = line.split(":")[1].strip()
            break
        except PermissionError:
            time.sleep(1)  # 如果遇到权限问题，稍等后重试
            retries -= 1
    
    os.remove(temp_file)  # 删除临时文件
    
    return dhcp_status

# 配置临时IP
def switch_to_temporary_static(ip, mask, gateway, dns1, dns2=None):
    """
    临时更改IP设置（不保存到INI文件）。
    """
    try:
        # 设置 IP 地址
        subprocess.run(["netsh", "interface", "ip", "set", "address", "name=以太网", "source=static", f"addr={ip}", f"mask={mask}", f"gateway={gateway}"], 
                       check=True, creationflags=subprocess.CREATE_NO_WINDOW)

        # 设置 DNS
        subprocess.run(["netsh", "interface", "ip", "set", "dns", "name=以太网", f"static={dns1}"], 
                       check=True, creationflags=subprocess.CREATE_NO_WINDOW)

        if dns2:
            subprocess.run(["netsh", "interface", "ip", "add", "dns", "name=以太网", f"{dns2}", "index=2"], 
                           check=True, creationflags=subprocess.CREATE_NO_WINDOW)

        print(f"IP 设置已更改：{ip}, {mask}, {gateway}, {dns1}, {dns2}")
    except subprocess.CalledProcessError as e:
        print(f"设置 IP 失败: {e}")


# 检查以太网连接状态
def check_ethernet_status():
    # 获取所有网络接口信息
    net_if_stats = psutil.net_if_stats()
    for interface, stats in net_if_stats.items():
        # 假设以太网接口名为 'Ethernet'，可以根据实际情况调整
        if interface.lower() == '以太网':
            if stats.isup:  # 如果网口连接状态为 up
                return 'up'
            else:
                return 'down'
    return 'unknown'  # 如果未找到以太网接口


def check_wifi_status():
    # 支持的 WiFi 接口名称（根据语言和系统调整）
    wifi_names = ['wi-fi', '无线网络连接', 'wlan']
    
    # 获取所有网络接口信息
    net_if_stats = psutil.net_if_stats()
    
    for interface, stats in net_if_stats.items():
        # 检查接口名是否匹配
        if interface.lower() in wifi_names:
            # 返回连接状态
            return 'up' if stats.isup else 'down'
    
    # 如果没有找到 WiFi 接口，返回 'down'
    return 'down'
# wifi_status = check_wifi_status()
# print(f"WiFi 状态: {wifi_status}")


def validate_ip(ip):
    """验证单个 IP 地址格式是否合法"""
    pattern = r"^(25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9]?[0-9])(\.(25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9]?[0-9])){3}$"
    return re.match(pattern, ip) is not None

def validate_inputs(ip, mask, gateway, dns1, dns2):
    """验证 IP、子网掩码、网关和 DNS 配置的合法性"""
    if not validate_ip(ip):
        messagebox.showerror("错误", f"无效的 IP 地址: {ip}")
        return False
    if not validate_ip(mask):
        messagebox.showerror("错误", f"无效的子网掩码: {mask}")
        return False
    if not validate_ip(gateway):
        messagebox.showerror("错误", f"无效的网关地址: {gateway}")
        return False
    # DNS 地址可以为空，只有在非空时才验证
    if dns1 and not validate_ip(dns1):
        messagebox.showerror("错误", f"无效的 DNS1 地址: {dns1}")
        return False
    if dns2 and not validate_ip(dns2):
        messagebox.showerror("错误", f"无效的 DNS2 地址: {dns2}")
        return False
    return True
