from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QSpacerItem, QSizePolicy, QHBoxLayout
from qfluentwidgets import ProgressBar, IndeterminateProgressBar, SettingCardGroup, \
    FluentIcon

from one_dragon.base.operation.one_dragon_env_context import OneDragonEnvContext
from one_dragon.gui.component.interface.vertical_scroll_interface import VerticalScrollInterface
from one_dragon.gui.component.log_display_card import LogDisplayCard
from one_dragon.gui.install_card.all_install_card import AllInstallCard
from one_dragon.gui.install_card.code_install_card import CodeInstallCard
from one_dragon.gui.install_card.ok_ww_install_card import OkWWInstallCard
from one_dragon.gui.install_card.git_install_card import GitInstallCard
from one_dragon.gui.install_card.python_install_card import PythonInstallCard
from one_dragon.gui.install_card.venv_install_card import VenvInstallCard
from one_dragon.utils.i18_utils import gt


class InstallerInterface(VerticalScrollInterface):

    def __init__(self, ctx: OneDragonEnvContext, parent=None):
        VerticalScrollInterface.__init__(self, object_name='install_interface',
                                         parent=parent, content_widget=None,
                                         nav_text_cn='一键安装', nav_icon=FluentIcon.CLOUD_DOWNLOAD)
        self.ctx: OneDragonEnvContext = ctx

    def get_content_widget(self) -> QWidget:
        content_widget = QWidget()
        v_layout = QVBoxLayout(content_widget)

        self.progress_bar = ProgressBar()
        self.progress_bar.setRange(0, 1)
        self.progress_bar.setVisible(False)
        v_layout.addWidget(self.progress_bar)

        self.progress_bar_2 = IndeterminateProgressBar()
        self.progress_bar_2.setVisible(False)
        v_layout.addWidget(self.progress_bar_2)

        self.git_opt = GitInstallCard(self.ctx)
        self.git_opt.progress_changed.connect(self.update_progress)

        # 暂停使用self.code_opt = CodeInstallCard(self.ctx)
        # 暂停使用self.code_opt.progress_changed.connect(self.update_progress)
        # 暂停使用self.code_opt.finished.connect(self._on_code_updated)

        self.python_opt = PythonInstallCard(self.ctx)
        self.python_opt.progress_changed.connect(self.update_progress)

        self.venv_opt = VenvInstallCard(self.ctx)
        self.venv_opt.progress_changed.connect(self.update_progress)

        self.all_opt = AllInstallCard(self.ctx, [self.git_opt, self.python_opt, self.venv_opt])# 暂停使用self.code_opt,

        '''# 暂停使用
        # 添加 ok_ww_opt 选项
        self.ok_ww_opt = OkWWInstallCard(self.ctx)
        self.download_ok_ww_button = QPushButton("下载ok-ww")
        self.download_ok_ww_button.clicked.connect(self.ok_ww_opt.start_download)
        self.download_ok_ww_button.setFixedSize(120, 40)  # 例如，宽度为 120，高度为 40
        # 创建水平布局以将按钮靠右
        button_layout = QHBoxLayout()
        button_layout.addStretch()  # 添加弹性空间，将按钮推到右侧
        button_layout.addWidget(self.download_ok_ww_button)
        # 设置按钮的样式（背景色和文本颜色）
        self.download_ok_ww_button.setStyleSheet("background-color: #4CAF50; color: white;")  # 绿色背景，白色文本
        # 将按钮布局添加到主垂直布局
        v_layout.addLayout(button_layout)
        '''

        update_group = SettingCardGroup(gt('运行环境', 'ui'))
        update_group.addSettingCard(self.all_opt)
        update_group.addSettingCard(self.git_opt)
        # 暂停使用update_group.addSettingCard(self.code_opt)
        update_group.addSettingCard(self.python_opt)
        update_group.addSettingCard(self.venv_opt)

        v_layout.addWidget(update_group)
        log_group = SettingCardGroup(gt('安装日志', 'ui'))
        v_layout.addWidget(log_group)
        self.log_card = LogDisplayCard()
        v_layout.addWidget(self.log_card, stretch=1)

        return content_widget

    def on_interface_shown(self) -> None:
        """
        页面加载完成后 检测各个组件状态并更新显示
        :return:
        """
        VerticalScrollInterface.on_interface_shown(self)
        self.git_opt.check_and_update_display()
        # 暂停使用self.code_opt.check_and_update_display()
        self.python_opt.check_and_update_display()
        self.venv_opt.check_and_update_display()
        self.log_card.set_update_log(True)

    def on_interface_hidden(self) -> None:
        """
        子界面隐藏时的回调
        :return:
        """
        VerticalScrollInterface.on_interface_hidden(self)
        self.log_card.set_update_log(False)

    def update_progress(self, progress: float, message: str) -> None:
        """
        进度回调更新
        :param progress: 进度 0~1
        :param message: 当前信息
        :return:
        """
        if progress == -1:
            self.progress_bar.setVisible(False)
            self.progress_bar_2.setVisible(True)
            self.progress_bar_2.start()
        else:
            self.progress_bar.setVisible(True)
            self.progress_bar.setVal(progress)
            self.progress_bar_2.setVisible(False)
            self.progress_bar_2.stop()

    def _on_code_updated(self, success: bool) -> None:
        """
        代码更新后
        :param success:
        :return:
        """
        if success:
            self.venv_opt.check_and_update_display()
