import tkinter as tk
import webbrowser
import threading


class AboutInfoThread(threading.Thread):
    def __init__(self):
        super().__init__()
        self.daemon = True  # 设置守护线程，主程序退出时线程自动结束

    def run(self):
        """线程运行显示关于信息"""
        # 创建主窗口
        root = tk.Tk()
        root.title("关于")
        root.resizable(False, False)  # 禁止调整窗口大小

        # 使窗口居中显示
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()

        # 计算居中位置
        window_width = 300
        window_height = 200
        x_position = (screen_width - window_width) // 2
        y_position = (screen_height - window_height) // 2

        # 设置窗口位置
        root.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

        # 软件名称
        tk.Label(root, text="Ethernet IP Switch v1.1").pack(pady=5)

        # 作者
        tk.Label(root, text="Author：hoochanlon").pack(pady=5)

        # 邮箱（可点击）
        email_label = tk.Label(root, text="huchenglon@outlook.com", fg="blue", cursor="hand2")
        email_label.pack(pady=1)

        # 主页（可点击）
        homepage_label = tk.Label(root, text="https://github.com/hoochanlon", fg="blue", cursor="hand2")
        homepage_label.pack(pady=1)

        # 描述
        tk.Label(root, text="一款用于快速切换网络，以及监测网络状态的工具。").pack(pady=1)

        # 绑定点击事件
        email_label.bind("<Button-1>", lambda e: webbrowser.open("mailto:huchenglon@outlook.com"))
        homepage_label.bind("<Button-1>", lambda e: webbrowser.open("https://github.com/hoochanlon"))

        # 窗口关闭事件
        root.protocol("WM_DELETE_WINDOW", root.destroy)

        root.mainloop()


def show_about_info():
    """启动关于信息的线程"""
    thread = AboutInfoThread()
    thread.start()
