import os
import subprocess
import time
import win32gui
import win32con
import pyautogui

def close_windows_with_title(title):
    """关闭所有窗口标题中包含指定字符串的窗口。"""
    win32gui.EnumWindows(
        lambda hwnd, _: win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
        if title in win32gui.GetWindowText(hwnd) and win32gui.IsWindowVisible(hwnd) else None,
        None
    )

def is_window_open(title):
    """检查是否有窗口标题中包含指定字符串的窗口打开。"""
    def callback(hwnd, hwnds):
        if title in win32gui.GetWindowText(hwnd) and win32gui.IsWindowVisible(hwnd):
            hwnds.append(hwnd)

    hwnds = []
    win32gui.EnumWindows(callback, hwnds)
    return len(hwnds) > 0  # 如果找到窗口则返回 True


def start_okww_auto():
    """启动外部程序，并监控其启动状态。"""
    if is_window_open("OK-WW") and is_window_open("v"):
        print("程序启动成功")
        return True
    for attempt in range(3):
        # 检测并关闭名为 "OK-WW" 的窗口
        print('关闭ok-ww')
        close_windows_with_title("OK-WW")
        # 等待 3 秒
        time.sleep(3)
        # 启动外部程序
        # exe_path = os.path.join('..', '..', '..', '3rdparty', 'ok-ww', 'ok-ww.exe')# 使用idea启动
        exe_path = os.path.join('3rdparty', 'ok-ww', 'ok-ww.exe')# 使用打包后的laucher
        subprocess.Popen([exe_path], cwd=os.path.dirname(exe_path))
        time.sleep(10)
        pyautogui.moveTo(1025, 743)
        pyautogui.click()
        time.sleep(3)
        # 监控名为 "OK-WW 启动器" 的窗口
        for _ in range(50):  # 最多等待 50 秒
            if not is_window_open("OK-WW 启动器"):
                print("程序启动成功")
                return True
            time.sleep(1)  # 每秒检查一次
            print("OK-WW 启动器存在")
        # 如果仍然存在，关闭 "OK-WW 启动器"
        close_windows_with_title("OK-WW 启动器")
        print("启动失败，正在重试...")

    '''
    script_path = os.path.join('3rdparty', 'ok-ww', 'main.py')
    # 使用 subprocess.Popen 执行脚本
    process = subprocess.Popen(['python', script_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    time.sleep(5)
    '''
    print("多次启动器启动失败，强行启动")
    return True


def kill_okww_auto():
    close_windows_with_title("OK-WW")

def just_open():
    close_windows_with_title("OK-WW")
    time.sleep(3)
    exe_path = os.path.join('3rdparty', 'ok-ww', 'ok-ww.exe')# 使用打包后的laucher
    subprocess.Popen([exe_path], cwd=os.path.dirname(exe_path))

# 使用示例
if __name__ == "__main__":
    current_directory = os.getcwd()
    print(f"当前工作目录: {current_directory}")
    start_okww_auto()
