from typing import Optional

from one_dragon.base.geometry.point import Point
from one_dragon.base.operation.operation_node import operation_node
from one_dragon.base.operation.operation_round_result import OperationRoundResult
from one_dragon.utils import cv2_utils, str_utils
from one_dragon.utils.i18_utils import gt
from ww_od.context.ww_context import WContext
from ww_od.operation.ww_operation import WOperation


class SolaGuideChooseCategory(WOperation):

    def __init__(self, ctx: WContext, category_name: str):
        """
        已经打开了索拉指南了 选择了一个Tab
        目标是选择一个分类
        :param ctx:
        """
        WOperation.__init__(
            self, ctx,
            op_name='%s %s %s' % (
                gt('索拉指南'),
                gt('选择分类', 'ui'),
                gt(category_name)
            )
        )

        self.category_name: str = category_name

    @operation_node(name='选择分类', is_start_node=True)
    def choose_tab(self) -> OperationRoundResult:
        screen = self.screenshot()
        '''
        area = self.ctx.screen_loader.get_area('索拉指南', '分类列表')
        part = cv2_utils.crop_image_only(screen, area.rect)

        target_point: Optional[Point] = None
        ocr_results = self.ctx.ocr.run_ocr(part, merge_line_distance=40)
        for ocr_result, mrl in ocr_results.items():
            if mrl.max is None:
                continue
            if str_utils.find_by_lcs(gt(self.category_name), ocr_result, percent=0.5):
                target_point = area.left_top + mrl.max
                break

        if target_point is None:
            return self.round_retry(status='找不到 %s' % self.category_name, wait=1)

        click = self.ctx.controller.click(target_point)
        '''

        area = self.ctx.screen_loader.get_area('周期挑战', '副本类型')
        return self.round_by_ocr_and_click(screen, self.category_name, area=area, success_wait=2, retry_wait=1)
        return self.round_success(wait=1)


def __debug():
    ctx = WContext()
    ctx.init_by_config()
    ctx.ocr.init_model()
    ctx.start_running()
    op = SolaGuideChooseCategory(ctx, '讨伐强敌')
    op.execute()


if __name__ == '__main__':
    __debug()
