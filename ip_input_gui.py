# ip_input_gui.py
import tkinter as tk
from tkinter import messagebox

# 创建IP输入窗口
def create_ip_input_window(title, ip_config=None, on_submit=None):
    def submit():
        diy_ip = entry_ip.get().strip()
        diy_mask = entry_mask.get().strip()
        diy_gateway = entry_gateway.get().strip()
        diy_dns1 = entry_dns1.get().strip()
        diy_dns2 = entry_dns2.get().strip()

        if diy_ip and diy_mask and diy_gateway and diy_dns1:
            if on_submit:
                on_submit(diy_ip, diy_mask, diy_gateway, diy_dns1, diy_dns2)
            root.destroy()
        else:
            messagebox.showerror("错误", "请填写完整的必填项！")

    root = tk.Tk()
    root.title(title)
    root.geometry("400x250")
    root.resizable(False, False)

    # 使用默认配置填充字段
    entry_ip = tk.Entry(root, width=30)
    entry_ip.insert(0, ip_config.get("ip", "") if ip_config else "")
    entry_mask = tk.Entry(root, width=30)
    entry_mask.insert(0, ip_config.get("mask", "") if ip_config else "")
    entry_gateway = tk.Entry(root, width=30)
    entry_gateway.insert(0, ip_config.get("gateway", "") if ip_config else "")
    entry_dns1 = tk.Entry(root, width=30)
    entry_dns1.insert(0, ip_config.get("dns1", "") if ip_config else "")
    entry_dns2 = tk.Entry(root, width=30)
    entry_dns2.insert(0, ip_config.get("dns2", "") if ip_config else "")

    # Labels and Entry widgets
    labels = ["IP 地址：", "子网掩码：", "网关地址：", "首选 DNS：", "备用 DNS (可选)："]
    entries = [entry_ip, entry_mask, entry_gateway, entry_dns1, entry_dns2]

    for i, label in enumerate(labels):
        tk.Label(root, text=label).grid(row=i, column=0, padx=10, pady=5, sticky='e')
        entries[i].grid(row=i, column=1, padx=10, pady=5)

    # 提交按钮
    tk.Button(root, text="提交", command=submit).grid(row=5, column=0, columnspan=2, pady=10)
    root.mainloop()
