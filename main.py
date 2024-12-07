from core_gui import start_tray

# 启动托盘图标
if __name__ == "__main__":
    start_tray()

'''
pyinstaller -w -F -i "C:\\Users\\administrator\\Desktop\\Ethernet-IP-Switch\\images\\logo.ico" --noconsole --onefile ^
--add-data "C:\\Users\\administrator\\Desktop\\Ethernet-IP-Switch\\images;images" ^
--name "Ethernet-IP-Switch" ^
--distpath "C:\\Users\\administrator\\Desktop" ^
C:\\Users\\administrator\\Desktop\\Ethernet-IP-Switch\\main.py
'''