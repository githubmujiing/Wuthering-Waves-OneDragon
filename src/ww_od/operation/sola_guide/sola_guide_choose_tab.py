from typing import Optional

from one_dragon.base.geometry.point import Point
from one_dragon.base.operation.operation_node import operation_node
from one_dragon.base.operation.operation_round_result import OperationRoundResult
from one_dragon.utils import cv2_utils, str_utils
from one_dragon.utils.i18_utils import gt
from ww_od.context.zzz_context import WContext
from ww_od.operation.zzz_operation import WOperation


class SolaGuideChooseTab(WOperation):

    def __init__(self, ctx: WContext, tab_name: str):
        """
        已经打开了索拉指南了 选择一个 Tab
        :param ctx:
        """
        WOperation.__init__(
            self, ctx,
            op_name='%s %s %s' % (
                gt('索拉指南'),
                gt('选择Tab', 'ui'),
                gt(tab_name)
            )
        )

        self.tab_name: str = tab_name

    @operation_node(name='选择TAB', is_start_node=True)
    def choose_tab(self) -> OperationRoundResult:
        area = self.ctx.screen_loader.get_area('索拉指南tab', '当前tab')
        self.round_by_click_area('索拉指南tab', '活跃度', success_wait=1, retry_wait=1)
        screen = self.screenshot()
        result = self.round_by_ocr(screen, self.tab_name, area)
        if result.is_success:
            return self.round_success(wait=1)
        self.round_by_click_area('索拉指南tab', '周期挑战', success_wait=1, retry_wait=1)
        screen = self.screenshot()
        result = self.round_by_ocr(screen, self.tab_name, area)
        if result.is_success:
            return self.round_success(wait=1)
        self.round_by_click_area('索拉指南tab', '强者之路', success_wait=1, retry_wait=1)
        screen = self.screenshot()
        result = self.round_by_ocr(screen, self.tab_name, area)
        if result.is_success:
            return self.round_success(wait=1)
        self.round_by_click_area('索拉指南tab', '残像探寻', success_wait=1, retry_wait=1)
        screen = self.screenshot()
        result = self.round_by_ocr(screen, self.tab_name, area)
        if result.is_success:
            return self.round_success(wait=1)
        self.round_by_click_area('索拉指南tab', '漂泊日志', success_wait=1, retry_wait=1)
        screen = self.screenshot()
        result = self.round_by_ocr(screen, self.tab_name, area)
        if result.is_success:
            return self.round_success(wait=1)
        else:
            return self.round_fail()




def __debug():
    ctx = WContext()
    ctx.init_by_config()
    ctx.ocr.init_model()
    ctx.start_running()
    op = SolaGuideChooseTab(ctx, '漂泊日志')
    op.execute()


if __name__ == '__main__':
    __debug()