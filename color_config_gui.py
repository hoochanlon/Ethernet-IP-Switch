import configparser
import tkinter as tk
from tkinter import messagebox, colorchooser
import os
import sys
import re
from concurrent.futures import ThreadPoolExecutor


# 全局变量用于存储主窗口实例
main_window = None


# 默认颜色配置
DEFAULT_COLORS = {
    'down': '#FF0000',
    'dhcp': '#00FF00',
    'static_ip1': '#0077BE',
    'static_ip2': '#87CEEB',
    'other': '#FFFF00',
    'wifi_up': '#00FF00'
}

# 用户友好的标签名称
USER_FRIENDLY_NAMES = {
    'down': '线路断开',
    'dhcp': '以太网 DHCP',
    'static_ip1': '固定IP 1',
    'static_ip2': '固定IP 2',
    'other': '其他状态',
    'wifi_up': 'Wi-Fi 已连接'
}

def generate_default_config():
    """
    检查配置文件是否存在。
    如果不存在，自动创建默认的 network_colors.ini 文件。
    """
    config_path = get_color_config_path()
    if not os.path.exists(config_path):
        # 如果文件不存在，保存默认配置到这个路径
        save_color_config(DEFAULT_COLORS)


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


# 十六进制颜色验证
def is_valid_hex_color(color):
    """检查颜色是否为有效的十六进制颜色格式"""
    hex_pattern = r'^#([0-9A-Fa-f]{6})$'
    return re.match(hex_pattern, color) is not None


def load_color_config():
    """加载配置文件"""
    config = configparser.ConfigParser()
    config.read(get_color_config_path())
    colors = {}
    for key in DEFAULT_COLORS.keys():
        colors[key] = config.get('colors', key, fallback=DEFAULT_COLORS[key])
    return colors


def save_color_config(colors):
    """保存配置文件"""
    config = configparser.ConfigParser()
    config['colors'] = colors
    with open(get_color_config_path(), 'w') as configfile:
        config.write(configfile)


def reset_color_to_default():
    """恢复默认设置"""
    save_color_config(DEFAULT_COLORS)
    messagebox.showinfo('恢复成功', '颜色配置已恢复为默认值。')
    update_color_entries(DEFAULT_COLORS)


def update_color_entries(colors):
    """更新UI中的颜色值"""
    for key, value in colors.items():
        color_entries[key].delete(0, tk.END)
        color_entries[key].insert(0, value)


def apply_color_changes():
    """应用颜色设置并保存"""
    new_colors = {key: color_entries[key].get() for key in DEFAULT_COLORS.keys()}
    for key, color in new_colors.items():
        if not is_valid_hex_color(color):
            messagebox.showerror('无效颜色', f'{USER_FRIENDLY_NAMES[key]} 的颜色值无效。请输入有效的十六进制颜色（例如：#FF0000）。')
            return
    save_color_config(new_colors)
    messagebox.showinfo('保存成功', '颜色配置已更新。')


def choose_color(key):
    """弹出调色板，允许用户选择颜色并显示十六进制代码"""
    color = colorchooser.askcolor(initialcolor=color_entries[key].get())[1]
    if color:  # 用户选择了颜色
        color_entries[key].delete(0, tk.END)
        color_entries[key].insert(0, color)


def destroy_existing_window():
    """销毁当前窗口实例"""
    global main_window
    if main_window is not None:
        main_window.destroy()
        main_window = None


def create_color_config_gui():
    """创建和显示GUI"""
    global main_window, color_entries

    # 检查是否已存在主窗口，如果存在，先销毁
    destroy_existing_window()

    # 创建新的 GUI 主窗口
    main_window = tk.Tk()
    main_window.title('修改颜色配置')
    main_window.resizable(False, False)

    # 创建并放置控件
    color_entries = {}
    for idx, key in enumerate(DEFAULT_COLORS.keys()):
        tk.Label(main_window, text=f'{USER_FRIENDLY_NAMES[key]} 颜色:').grid(row=idx, column=0, padx=10, pady=5)
        color_entries[key] = tk.Entry(main_window)
        color_entries[key].grid(row=idx, column=1, padx=10, pady=5)
        # 选择颜色按钮
        choose_button = tk.Button(
            main_window, text=f'选择{USER_FRIENDLY_NAMES[key]}颜色', command=lambda k=key: choose_color(k)
        )
        choose_button.grid(row=idx, column=2, padx=10, pady=5)

    # 加载并显示当前配置的颜色
    current_colors = load_color_config()
    main_window.after(0, update_color_entries, current_colors)

    # 保存按钮
    apply_button = tk.Button(main_window, text='应用更改', command=apply_color_changes)
    apply_button.grid(row=len(DEFAULT_COLORS), column=0, columnspan=3, pady=10)

    # 恢复默认按钮
    reset_button = tk.Button(main_window, text='恢复默认', command=reset_color_to_default)
    reset_button.grid(row=len(DEFAULT_COLORS) + 1, column=0, columnspan=3, pady=5)

    # 设置窗口关闭回调
    main_window.protocol("WM_DELETE_WINDOW", lambda: destroy_existing_window())

    # 运行主循环
    main_window.mainloop()


def start_color_config_gui_in_thread():
    # 使用线程池启动 GUI
    executor = ThreadPoolExecutor(max_workers=1)
    """通过线程池启动 GUI"""
    executor.submit(create_color_config_gui)


generate_default_config()

