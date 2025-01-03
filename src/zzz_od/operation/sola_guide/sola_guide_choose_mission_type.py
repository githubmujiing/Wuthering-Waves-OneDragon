import difflib
from typing import Optional, List

from one_dragon.base.geometry.point import Point
from one_dragon.base.geometry.rectangle import Rect
from one_dragon.base.operation.operation_edge import node_from
from one_dragon.base.operation.operation_node import operation_node
from one_dragon.base.operation.operation_round_result import OperationRoundResult
from one_dragon.utils import cv2_utils, str_utils
from one_dragon.utils.i18_utils import gt
from zzz_od.context.zzz_context import WContext
from zzz_od.game_data.compendium import CompendiumMissionType
from zzz_od.operation.zzz_operation import WOperation


class SolaGuideChooseMissionType(WOperation):

    def __init__(self, ctx: WContext, mission_type_name: str):
        """
        已经打开了索拉指南了 选择了 Tab 和 分类
        目标是 选择一个关卡传送 点击传送后 不会等待画面加载
        :param ctx:
        """
        WOperation.__init__(
            self, ctx,
            op_name='%s %s %s' % (
                gt('索拉指南'),
                gt('选择副本类型', 'ui'),
                gt(mission_type_name)
            )
        )

        self.mission_type_name: str = mission_type_name

    @operation_node(name='选择副本', is_start_node=True, node_max_retry_times=10)
    def choose_tab(self) -> OperationRoundResult:
        if self.mission_type_name == '贝币':
            self.mission_type_name = '共鸣促剂'
        screen = self.screenshot()
        area = self.ctx.screen_loader.get_area('周期挑战', '副本名称')
        part = cv2_utils.crop_image_only(screen, area.rect)

        mission_type_list: List[CompendiumMissionType] = self.ctx.compendium_service.get_same_category_mission_type_list(self.mission_type_name)
        if mission_type_list is None:
            return self.round_fail('非法的副本分类 %s' % self.mission_type_name)

        before_target_cnt: int = 0  # 在目标副本前面的数量
        target_idx: int = -1
        target_list = []
        for idx, mission_type in enumerate(mission_type_list):
            if mission_type.mission_type_name == self.mission_type_name:
                target_idx = idx
            target_list.append(gt(mission_type.mission_type_name))

        if target_idx == -1:
            return self.round_fail('非法的副本分类 %s' % self.mission_type_name)

        target_point: Optional[Point] = None
        ocr_results = self.ctx.ocr.run_ocr(part)
        for ocr_result, mrl in ocr_results.items():
            if mrl.max is None:
                continue

            results = difflib.get_close_matches(ocr_result, target_list, n=1)

            if results is None or len(results) == 0:
                continue

            idx = target_list.index(results[0])
            if idx == target_idx:
                target_point = area.left_top + mrl.max
                break
            elif idx < target_idx:
                before_target_cnt += 1

        if target_point is None:
            # 滑动
            start = area.center
            end = start + Point(0, -200 if before_target_cnt > 0 else 200)
            self.ctx.controller.drag_to(start=start, end=end)
            return self.round_retry(status='找不到 %s' % self.mission_type_name, wait=1)

        go_lt = target_point + Point(702, 2)
        go_bt = target_point + Point(954, 58)
        # area = self.ctx.screen_loader.get_area('索拉指南', '前往列表')
        go_rect = Rect(go_lt.x, go_lt.y, go_bt.x, go_bt.y)
        # go_rect = area.rect
        part = cv2_utils.crop_image_only(screen, go_rect)
        ocr_results = self.ctx.ocr.run_ocr(part)

        target_go_point: Optional[Point] = None
        for ocr_result, mrl in ocr_results.items():
            if mrl.max is None:
                continue
            if not str_utils.find_by_lcs(gt('前往'), ocr_result, percent=0.5):
                continue
            for mr in mrl:
                go_point = go_rect.left_top + mr.center
                if go_point.y <= target_point.y:
                    continue
                if target_go_point is None or go_point.y < target_go_point.y:
                    target_go_point = go_point

        if target_go_point is None:
            return self.round_retry(status='找不到 %s' % '前往', wait=1)

        click = self.ctx.controller.click(target_go_point)
        return self.round_success(wait=3)

    @node_from(from_name='选择副本')
    @operation_node(name='传送')
    def transmit(self) -> OperationRoundResult:
        return self.round_by_click_area('地图传送', '传送', success_wait=2, retry_wait=1)


def __debug():
    ctx = WContext()
    ctx.init_by_config()
    ctx.ocr.init_model()
    ctx.start_running()
    op = SolaGuideChooseMissionType(ctx, '贝币')
    op.execute()


if __name__ == '__main__':
    __debug()
