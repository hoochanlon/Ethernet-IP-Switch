import os
import re
import subprocess
import sys
import threading
import time
from tkinter import Tk, messagebox,colorchooser
from tkinter import simpledialog
from tkinter.scrolledtext import ScrolledText
import pystray
from pystray import MenuItem as item
from PIL import Image, ImageDraw
import network_config  # 导入网络配置模块
import ip_input_gui  # 导入IP输入界面模块
import psutil
import configparser
from concurrent.futures import ThreadPoolExecutor
import tkinter as tk
from pystray import Menu, MenuItem
from color_config_gui import start_color_config_gui_in_thread
from about_info import show_about_info


# 获取配置文件路径
def get_color_config_path():
    if hasattr(sys, '_MEIPASS'):
        # 打包环境，使用临时文件夹
        return os.path.join(sys._MEIPASS, 'network_colors.ini')
    else:
        # 开发环境，使用当前工作目录，假设配置文件在桌面上
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
        color_ini_path = os.path.join(desktop_path, "Ethernet-IP-Switch")
        return os.path.join(color_ini_path, 'network_colors.ini')


# 读取配置文件
def load_colors():
    config = configparser.ConfigParser()
    config.read(get_color_config_path())
    colors = config['colors']
    return {key: value for key, value in colors.items()}

# 创建透明背景的圆形图标
def create_icon(color):
    size = (64, 64)
    image = Image.new('RGBA', size, (0, 0, 0, 0))  # 创建透明背景的图标
    draw = ImageDraw.Draw(image)

    # 获取颜色配置
    colors = load_colors()

    # 使用颜色配置中的十六进制颜色
    fill_color = colors.get(color, "#FFFF00")  # 默认黄色

    # 绘制圆形
    draw.ellipse([0, 0, size[0], size[1]], fill=fill_color)
    return image

# 更新托盘图标状态
def update_icon(icon):
    # 获取颜色配置
    colors = load_colors()

    # 检查以太网状态
    eth_status = network_config.check_ethernet_status()
    # 检查 WiFi 状态
    wifi_status = network_config.check_wifi_status()

    if eth_status == 'down' and wifi_status == 'down':
        icon.icon = create_icon('down')  # 无连接，图标变为红色
    elif eth_status == 'up':
        # 以太网优先处理
        dhcp_status = network_config.check_dhcp()
        ip, mask, gateway, dns1, dns2 = network_config.get_current_ip_config()

        if dhcp_status == "是":
            icon.icon = create_icon('dhcp')  # DHCP 模式，绿色
        elif ip == network_config.load_static_config().get("static_ip1", ""):
            icon.icon = create_icon('static_ip1')  # 内网固定 IP 1
        elif ip == network_config.load_static_config().get("static_ip2", ""):
            icon.icon = create_icon('static_ip2')  # 内网固定 IP 2
        else:
            icon.icon = create_icon('other')  # 未知配置，黄色
    elif wifi_status == 'up':
        icon.icon = create_icon('wifi_up')  # WiFi 正常，绿色
    else:
        icon.icon = create_icon('other')  # 其他情况，默认黄色


# 切换到 DHCP
def switch_to_dhcp(icon, item):
    network_config.switch_to_dhcp()
    update_icon(icon)

# 切换到固定静态 IP1
def switch_to_fixed_static1(icon, item):
    network_config.switch_to_fixed_static1()
    update_icon(icon)

# 切换到固定静态 IP2
def switch_to_fixed_static2(icon, item):
    network_config.switch_to_fixed_static2()
    update_icon(icon)

# 配置固定 IP1
def configure_fixed_static1(icon, item):
    # 加载当前固定IP1配置
    current_config = network_config.load_static_config()

    def on_submit(ip, mask, gateway, dns1, dns2):
        # 调用独立的验证函数
        if not network_config.validate_inputs(ip, mask, gateway, dns1, dns2):
            return
        # 保存配置
        network_config.save_static_config1(ip, mask, gateway, dns1, dns2)
        messagebox.showinfo("成功", "固定IP(1)配置已保存！")

    # 创建并启动一个新线程来打开 IP 配置窗口
    def open_ip_input_window():
        ip_input_gui.create_ip_input_window("配置本机内网固定IP(1)地址", ip_config=current_config, on_submit=on_submit)

    # 提交任务给线程池
    executor.submit(open_ip_input_window)

# 配置固定 IP2
def configure_fixed_static2(icon, item):
    # 加载当前固定IP2配置
    current_config = network_config.load_static_config()

    def on_submit(ip, mask, gateway, dns1, dns2):
        # 调用独立的验证函数
        if not network_config.validate_inputs(ip, mask, gateway, dns1, dns2):
            return
        # 保存配置
        network_config.save_static_config2(ip, mask, gateway, dns1, dns2)
        messagebox.showinfo("成功", "固定IP(2)配置已保存！")

    # 创建并启动一个新线程来打开 IP 配置窗口
    def open_ip_input_window():
        ip_input_gui.create_ip_input_window("配置本机内网固定IP(2)地址", ip_config=current_config, on_submit=on_submit)

    # 提交任务给线程池
    executor.submit(open_ip_input_window)


# 手动修改其他静态 IP
def switch_to_custom_static(icon, item):
    # 创建一个新的线程来运行 IP 输入窗口，以避免阻塞主线程
    def open_ip_input_window():
        # 打开输入窗口，传递处理函数
        def on_submit(ip, mask, gateway, dns1, dns2):
            # 调用验证函数
            if not network_config.validate_inputs(ip, mask, gateway, dns1, dns2):
                return
            # 临时修改IP
            network_config.switch_to_temporary_static(ip, mask, gateway, dns1, dns2)
            update_icon(icon)  # 更新托盘图标

        ip_input_gui.create_ip_input_window("快速修改IP地址", on_submit=on_submit)

    # 提交任务给线程池
    executor.submit(open_ip_input_window)



# # 查看配置文件内容
def view_config_file(icon, item):
    config_path = network_config.get_config_path()
    
    def open_config_file():
        root = tk.Tk()
        root.title("查看配置文件")

        # 创建一个可滚动的文本框，用来显示文件内容
        text_area = ScrolledText(root, width=40, height=20, wrap=tk.WORD, state=tk.DISABLED)
        text_area.pack(padx=10, pady=10)

        # 读取并显示文件内容
        def load_content():
            if os.path.exists(config_path):
                try:
                    with open(config_path, "r") as file:
                        content = file.read()
                        text_area.config(state=tk.NORMAL)
                        text_area.delete(1.0, tk.END)
                        text_area.insert(tk.END, content)
                        text_area.config(state=tk.DISABLED)
                except Exception:
                    text_area.config(state=tk.NORMAL)
                    text_area.delete(1.0, tk.END)
                    text_area.insert(tk.END, "无法加载配置文件内容。")
                    text_area.config(state=tk.DISABLED)
            else:
                text_area.config(state=tk.NORMAL)
                text_area.delete(1.0, tk.END)
                text_area.insert(tk.END, "配置文件不存在。")
                text_area.config(state=tk.DISABLED)

        load_content()

        # 添加按钮以清空配置文件
        def clear_config():
            network_config.delete_static_ini()
            text_area.config(state=tk.NORMAL)
            text_area.delete(1.0, tk.END)
            text_area.insert(tk.END, "配置文件已清空或不存在。")
            text_area.config(state=tk.DISABLED)

        clear_button = tk.Button(root, text="清空配置", command=clear_config)
        clear_button.pack(pady=10)

        # 设置窗口大小，并启动
        root.geometry("330x330")
        root.resizable(False, False) 
        root.mainloop()

    if os.path.exists(config_path):
        # 在新线程中打开文件窗口，以避免阻塞主线程
        executor.submit(open_config_file)
    else:
        # 创建空窗口直接显示不存在的消息
        def show_empty_window():
            root = tk.Tk()
            root.title("查看配置文件")
            text_area = ScrolledText(root, width=40, height=20, wrap=tk.WORD, state=tk.DISABLED)
            text_area.pack(padx=10, pady=10)
            text_area.config(state=tk.NORMAL)
            text_area.insert(tk.END, "配置文件不存在。")
            text_area.config(state=tk.DISABLED)
            root.geometry("300x300")
            root.resizable(False, False) 
            root.mainloop()

        executor.submit(show_empty_window)



# 获取配置文件路径，打包后使用 sys._MEIPASS，否则使用桌面路径
def network_names_path():
    if getattr(sys, 'frozen', False):
        # 打包成 .exe 后的路径
        return os.path.join(sys._MEIPASS, "network_names.ini")
    else:
        # 开发环境中的路径
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
        static_fixed_ini_path = os.path.join(desktop_path, "Ethernet-IP-Switch")
        return os.path.join(static_fixed_ini_path, "network_names.ini")

CONFIG_FILE = network_names_path()

# 加载配置文件中的网络名称
def load_network_names():
    config = configparser.ConfigParser()
    if os.path.exists(CONFIG_FILE):
        config.read(CONFIG_FILE)
    else:
        # 如果没有配置文件，使用默认名称
        config['NetworkNames'] = {
            'dhcp_name': '切换到DHCP',
            'static_ip1_name': '切换到内网固定IP(1)',
            'static_ip2_name': '切换到内网固定IP(2)'
        }
        with open(CONFIG_FILE, 'w') as configfile:
            config.write(configfile)

    return config['NetworkNames']

# 保存网络名称到配置文件
def save_network_names(names_dict):
    config = configparser.ConfigParser()
    config['NetworkNames'] = names_dict
    with open(CONFIG_FILE, 'w') as configfile:
        config.write(configfile)


# 修改网络名称
def modify_network_names(icon, names_dict):
    def prompt_for_names():
        root = tk.Tk()  # 创建 Tk 对象
        root.title("修改切换网络的名称")
        root.geometry("400x250")  # 设置窗口大小
        root.resizable(False, False)  # 禁止调整窗口大小

        # 添加标题
        title_label = tk.Label(root, text="修改切换网络的名称", font=("仿宋", 14))
        title_label.pack(pady=10)

        # 默认名称
        default_names = {
            'dhcp_name': '切换到DHCP',
            'static_ip1_name': '切换到内网固定IP(1)',
            'static_ip2_name': '切换到内网固定IP(2)'
        }

        # DHCP 名称
        frame_dhcp = tk.Frame(root)
        frame_dhcp.pack(pady=5, fill="x", padx=20)
        label_dhcp = tk.Label(frame_dhcp, text="DHCP 名称:")
        label_dhcp.pack(side="left", padx=5)
        entry_dhcp = tk.Entry(frame_dhcp, width=30)
        entry_dhcp.insert(0, names_dict.get('dhcp_name', default_names['dhcp_name']))
        entry_dhcp.pack(side="right")

        # 内网固定 IP1 名称
        frame_static1 = tk.Frame(root)
        frame_static1.pack(pady=5, fill="x", padx=20)
        label_static_ip1 = tk.Label(frame_static1, text="内网固定 IP(1):")
        label_static_ip1.pack(side="left", padx=5)
        entry_static_ip1 = tk.Entry(frame_static1, width=30)
        entry_static_ip1.insert(0, names_dict.get('static_ip1_name', default_names['static_ip1_name']))
        entry_static_ip1.pack(side="right")

        # 内网固定 IP2 名称
        frame_static2 = tk.Frame(root)
        frame_static2.pack(pady=5, fill="x", padx=20)
        label_static_ip2 = tk.Label(frame_static2, text="内网固定 IP(2):")
        label_static_ip2.pack(side="left", padx=5)
        entry_static_ip2 = tk.Entry(frame_static2, width=30)
        entry_static_ip2.insert(0, names_dict.get('static_ip2_name', default_names['static_ip2_name']))
        entry_static_ip2.pack(side="right")

        # 恢复默认操作
        def restore_defaults():
            entry_dhcp.delete(0, tk.END)
            entry_dhcp.insert(0, default_names['dhcp_name'])

            entry_static_ip1.delete(0, tk.END)
            entry_static_ip1.insert(0, default_names['static_ip1_name'])

            entry_static_ip2.delete(0, tk.END)
            entry_static_ip2.insert(0, default_names['static_ip2_name'])

        # 提交操作
        def on_submit():
            # 更新名称字典
            names_dict['dhcp_name'] = entry_dhcp.get()
            names_dict['static_ip1_name'] = entry_static_ip1.get()
            names_dict['static_ip2_name'] = entry_static_ip2.get()

            save_network_names(names_dict)  # 保存修改后的名称
            update_tray_menu(icon, names_dict)  # 更新菜单显示

            root.destroy()  # 关闭窗口

        # 按钮框架
        button_frame = tk.Frame(root)
        button_frame.pack(pady=20)

        # 恢复默认按钮
        restore_button = tk.Button(button_frame, text="恢复默认", command=restore_defaults, width=15)
        restore_button.pack(side="left", padx=10)

        # 提交按钮
        submit_button = tk.Button(button_frame, text="提交", command=on_submit, width=15)
        submit_button.pack(side="right", padx=10)

        root.mainloop()  # 启动窗口

    # 在新线程中启动窗口，避免阻塞主程序
    threading.Thread(target=prompt_for_names).start()


# # 更新托盘菜单中的网络名称
# def update_tray_menu(icon, names_dict):
#     # 创建子菜单
#     conf_menu = Menu(
#         MenuItem('设置固定IP(1)', configure_fixed_static1),
#         MenuItem('设置固定IP(2)', configure_fixed_static2),
#         MenuItem('查看IP配置文件', view_config_file),
#         MenuItem('修改切换网络的名称', lambda icon, item: modify_network_names(icon, names_dict)),
#         MenuItem('修改颜色标识配置', lambda icon, item: start_gui_in_thread())
#     )

#     # 创建主菜单
#     icon.menu = Menu(
#         MenuItem(names_dict.get('dhcp_name', '切换到DHCP'), switch_to_dhcp),
#         MenuItem(names_dict.get('static_ip1_name', '切换到内网固定IP(1)'), switch_to_fixed_static1),
#         MenuItem(names_dict.get('static_ip2_name', '切换到内网固定IP(2)'), switch_to_fixed_static2),
#         MenuItem('快速修改IP地址', switch_to_custom_static),
#         MenuItem('设置与查看', conf_menu),  # 将子菜单添加到主菜单中
#         MenuItem('退出', lambda icon, item: icon.stop())
#     )

# 记录菜单项的状态
is_color_configured = False  # 初始状态为可点击

# 更新托盘菜单中的网络名称
def update_tray_menu(icon, names_dict):
    global is_color_configured

    def disable_color_config_menu(icon, item):
        global is_color_configured
        if not is_color_configured:
            start_color_config_gui_in_thread() # 执行相关操作
            is_color_configured = True
            update_tray_menu(icon, names_dict)  # 更新托盘菜单

    # 创建子菜单
    conf_menu = Menu(
        MenuItem('设置固定IP(1)', configure_fixed_static1),
        MenuItem('设置固定IP(2)', configure_fixed_static2),
        MenuItem('查看IP配置文件', view_config_file),
        MenuItem('修改切换网络的名称', lambda icon, item: modify_network_names(icon, names_dict)),
        MenuItem(
            '修改颜色标识配置' if not is_color_configured else '颜色标识已配置',
            disable_color_config_menu,
            enabled=not is_color_configured  # 禁用菜单项
        )
    )

    # 创建主菜单
    icon.menu = Menu(
        MenuItem(names_dict.get('dhcp_name', '切换到DHCP'), switch_to_dhcp),
        MenuItem(names_dict.get('static_ip1_name', '切换到内网固定IP(1)'), switch_to_fixed_static1),
        MenuItem(names_dict.get('static_ip2_name', '切换到内网固定IP(2)'), switch_to_fixed_static2),
        MenuItem('快速修改IP地址', switch_to_custom_static),
        MenuItem('设置与查看', conf_menu),  # 将子菜单添加到主菜单中
        MenuItem('关于', lambda icon, item: show_about_info()),
        MenuItem('退出', lambda icon, item: icon.stop())
    )


# 启动托盘菜单
def start_tray():
    global executor  # 线程池对象，必须在全局范围定义
    executor = ThreadPoolExecutor(max_workers=6)  # 创建线程池，限制最大线程数为4

    icon = pystray.Icon("Network Monitor")  # 创建图标对象
    icon.icon = create_icon('pink')  # 设置初始图标为粉色
    # 加载网络名称配置
    names_dict = load_network_names()
    # 更新托盘菜单
    update_tray_menu(icon, names_dict)


    # 定时更新图标
    def update():
        while True:
            update_icon(icon)  # 更新图标
            time.sleep(5)

    threading.Thread(target=update, daemon=True).start()
    icon.run()  # 运行托盘图标





