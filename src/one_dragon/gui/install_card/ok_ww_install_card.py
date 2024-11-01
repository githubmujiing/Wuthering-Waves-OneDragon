import os
import requests
import zipfile

from PySide6.QtWidgets import QMessageBox

from zzz_od.operation.control_okww_auto import start_okww_auto


class OkWWInstallCard:
    def __init__(self, ctx):
        self.ctx = ctx  # 传入的上下文对象
        self.download_url = "https://github.com/ok-oldking/ok-wuthering-waves/releases/download/v0.3.113/ok-ww-v0.3.113.zip"
        self.download_dir = os.path.join(os.getcwd(), "..", "..", "..", "3rdparty")  # 下载目录

        # 确保下载目录存在
        os.makedirs(self.download_dir, exist_ok=True)

    def download(self):
        # 下载文件
        print(f"下载到: {self.download_dir}")
        response = requests.get(self.download_url)
        zip_file_path = os.path.join(self.download_dir, "ok-ww-v0.3.113.zip")

        with open(zip_file_path, 'wb') as f:
            f.write(response.content)
        print(f"1正在下载: {zip_file_path}")
        return zip_file_path

    def extract(self, zip_file_path):
        # 解压缩文件
        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            zip_ref.extractall(self.download_dir)
        print(f"正在将: {zip_file_path} 解压到 {self.download_dir}")

    def show_download_notice1(self):
        # 创建并显示一个信息弹窗
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setText("下载需要五分钟，耐心等待")
        msg_box.setWindowTitle("提示")
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec()

    def show_download_notice2(self):
        # 创建并显示一个信息弹窗
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setText("下载已经完成。ok-ww在3rdparty文件夹需要去打开初始化")
        msg_box.setWindowTitle("提示")
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec()

    def start_download(self):
        # 开始下载和解压缩
        current_directory = os.getcwd()
        self.show_download_notice1()
        print(f"当前工作目录: {current_directory}")
        print("开始下载...")
        zip_file_path = self.download()
        self.extract(zip_file_path)
        print("解压完成")
        self.show_download_notice2()
