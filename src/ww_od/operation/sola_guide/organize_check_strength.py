import time
from typing import Optional, ClassVar

from one_dragon.base.operation.operation_base import OperationResult
from one_dragon.base.operation.operation_edge import node_from
from one_dragon.base.operation.operation_node import operation_node
from one_dragon.base.operation.operation_round_result import OperationRoundResult
from one_dragon.utils import cv2_utils, str_utils
from one_dragon.utils.i18_utils import gt
from ww_od.context.ww_context import WContext
from ww_od.operation.back_to_normal_world import BackToNormalWorld
from ww_od.operation.ww_operation import WOperation
from one_dragon.base.geometry.point import Point


class OrganizeCheckStrength(WOperation):

    STATUS_CHARGE_NOT_ENOUGH: ClassVar[str] = '体力不足'
    STATUS_CHARGE_ENOUGH: ClassVar[str] = '体力充足'

    def __init__(self, ctx: WContext
                 ):
        """
        开始体力计划前整理体力
        确保体力充足
        :param ctx:
        """
        WOperation.__init__(
            self, ctx,
            op_name='%s %s' % (
                gt('整理兑换体力'),
                gt('good')
            )
        )

        self.exchange_quantity = 0
        self.change_charge = None
        self.double_charge_consume: Optional[int] = None
        self.single_charge_consume: Optional[int] = None
        self.charge_left: Optional[int] = None
        self.charge_need: Optional[int] = None

    def handle_init(self) -> None:
        """
        执行前的初始化 由子类实现
        注意初始化要全面 方便一个指令重复使用
        """
        self.charge_left: Optional[int] = None
        self.charge_need: Optional[int] = None

    @operation_node(name='打开地图', is_start_node=True,)
    def open_map(self) -> OperationRoundResult:
        op = BackToNormalWorld(self.ctx)
        op.execute()
        self.round_by_click_area('大世界', '地图', success_wait=2)
        return self.round_success()

    @node_from(from_name='打开地图')
    @operation_node(name='识别体力', node_max_retry_times=5)
    def identify_strength(self) -> OperationRoundResult:
        screen = self.screenshot()
        area = self.ctx.screen_loader.get_area('地图传送', '剩余体力')
        part = cv2_utils.crop_image_only(screen, area.rect)
        ocr_result = self.ctx.ocr.run_ocr_single_line(part)
        self.charge_left = str_utils.get_positive_digits(ocr_result, None)
        print(f"剩余体力: {self.charge_left}")
        if self.charge_left is None:
            return self.round_retry(status='识别 %s 失败' % '剩余体力', wait=1)
        area = self.ctx.screen_loader.get_area('地图传送', '结晶单质')
        part = cv2_utils.crop_image_only(screen, area.rect)
        ocr_result = self.ctx.ocr.run_ocr_single_line(part)
        self.change_charge = str_utils.get_positive_digits(ocr_result, None)
        print(f"结晶单质: {self.change_charge}")
        if self.change_charge is None:
            return self.round_retry(status='识别 %s 失败' % '结晶单质', wait=1)
        return self.round_success()

    @node_from(from_name='识别体力')
    @operation_node(name='判断体力')
    def change_strength1(self) -> OperationRoundResult:
        if self.change_charge == 480 and self.charge_left >= 200:
            self.exchange_quantity = 420-self.charge_left
        elif self.charge_left < 240 and self.change_charge > 240-self.charge_left :
            self.exchange_quantity = 240-self.charge_left
        else:
            self.exchange_quantity = 0
        print(f"应换体力: {self.exchange_quantity}")
        self.round_by_click_area('地图传送', '补充体力', success_wait=1)
        self.round_by_click_area('地图传送', '确认', success_wait=2)
        return self.round_success()

    @node_from(from_name='判断体力')
    @operation_node(name='兑换体力', node_max_retry_times=5)
    def change_strength2(self) -> OperationRoundResult:
        # 开始兑换
        if self.exchange_quantity == 0:
            return self.round_success()
        else:
            # 选择兑换次数最大值坐标：1193, 650。最小值坐标：570, 650。相差：623
            if self.change_charge >= 240:
                change_charge = 240
            else:
                change_charge = self.change_charge
            click_point_x = 570+((self.exchange_quantity/change_charge)*623)
            print(click_point_x)
            self.ctx.controller.click(pos=Point(click_point_x, 650))
            time.sleep(2)
            screen = self.screenshot()
            area = self.ctx.screen_loader.get_area('地图传送', '兑换次数')
            part = cv2_utils.crop_image_only(screen, area.rect)
            ocr_result = self.ctx.ocr.run_ocr_single_line(part)
            base_time = str_utils.get_positive_digits(ocr_result, None)
            if abs(base_time - self.exchange_quantity) <= 2:    # abs为取绝对值
                self.round_by_click_area('地图传送', '确认', success_wait=1)
                return self.round_success()
            else:
                print(f"实际换体力: {base_time}")
                return self.round_success(status='换体力失败')




    def _on_pause(self, e=None):
        WOperation._on_pause(self, e)

    def _on_resume(self, e=None):
        WOperation._on_resume(self, e)

    def after_operation_done(self, result: OperationResult):
        WOperation.after_operation_done(self, result)

def __debug():
    ctx = WContext()
    ctx.init_by_config()
    ctx.ocr.init_model()
    ctx.start_running()
    op = OrganizeCheckStrength(ctx)
    op.execute()


if __name__ == '__main__':
    __debug()
