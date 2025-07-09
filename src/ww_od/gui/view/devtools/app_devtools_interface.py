from qfluentwidgets import FluentIcon

from one_dragon.gui.component.interface.pivot_navi_interface import PivotNavigatorInterface
from one_dragon.gui.view.devtools.devtools_screen_manage_interface import DevtoolsScreenManageInterface
from one_dragon.gui.view.devtools.devtools_template_helper_interface import DevtoolsTemplateHelperInterface
from ww_od.context.zzz_context import WContext
from ww_od.gui.view.devtools.devtools_screenshot_helper_interface import DevtoolsScreenshotHelperInterface


class AppDevtoolsInterface(PivotNavigatorInterface):

    def __init__(self,
                 ctx: WContext,
                 parent=None):
        self.ctx: WContext = ctx
        PivotNavigatorInterface.__init__(self, object_name='app_devtools_interface', parent=parent,
                                         nav_text_cn='开发工具', nav_icon=FluentIcon.DEVELOPER_TOOLS)

    def create_sub_interface(self):
        """
        创建下面的子页面
        :return:
        """
        self.add_sub_interface(DevtoolsScreenshotHelperInterface(self.ctx))
        self.add_sub_interface(DevtoolsTemplateHelperInterface(self.ctx))
        self.add_sub_interface(DevtoolsScreenManageInterface(self.ctx))
