import os
import subprocess
import time
import win32gui
import win32con

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
    for attempt in range(6):
        # 检测并关闭名为 "OK-WW" 的窗口
        close_windows_with_title("OK-WW")
        # 等待 3 秒
        time.sleep(3)
        # 启动外部程序
        exe_path = os.path.join('..', '..', '..', '3rdparty', 'ok-ww', 'ok-ww.exe')
        subprocess.Popen([exe_path], cwd=os.path.dirname(exe_path))
        time.sleep(5)
        # 监控名为 "OK-WW 启动器" 的窗口
        for _ in range(30):  # 最多等待 30 秒
            if not is_window_open("OK-WW 启动器"):
                print("程序启动成功")
                return True
            time.sleep(1)  # 每秒检查一次
            print("OK-WW 启动器存在")
        # 如果仍然存在，关闭 "OK-WW 启动器"
        close_windows_with_title("OK-WW 启动器")
        print("启动失败，正在重试...")

    print("多次启动失败，退出程序。")
    return False


def kill_okww_auto():
    close_windows_with_title("OK-WW")

# 使用示例
if __name__ == "__main__":
    current_directory = os.getcwd()
    print(f"当前工作目录: {current_directory}")
    kill_okww_auto()