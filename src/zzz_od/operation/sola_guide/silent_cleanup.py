import time

from typing import Optional, ClassVar

from one_dragon.base.geometry.point import Point
from one_dragon.base.operation.operation_base import OperationResult
from one_dragon.base.operation.operation_edge import node_from
from one_dragon.base.operation.operation_node import operation_node
from one_dragon.base.operation.operation_round_result import OperationRoundResult
from one_dragon.utils import cv2_utils, str_utils
from one_dragon.utils.i18_utils import gt
from zzz_od.application.charge_plan.charge_plan_config import ChargePlanItem
# 尝试删除from zzz_od.auto_battle import auto_battle_utils
# 尝试删除from zzz_od.auto_battle.auto_battle_operator import AutoBattleOperator
from zzz_od.context.zzz_context import WContext
from zzz_od.operation.monitor_battle_by_success import MonitorBottleBySuccess
from zzz_od.operation.search_interaction import SearchInteract
from zzz_od.operation.zzz_operation import WOperation


class SilentCleanup(WOperation):

    STATUS_CHARGE_NOT_ENOUGH: ClassVar[str] = '体力不足'
    STATUS_CHARGE_ENOUGH: ClassVar[str] = '体力充足'

    def __init__(self, ctx: WContext, plan: ChargePlanItem,
                 ):
        """
        使用索拉指南传送后
        用这个进行挑战
        :param ctx:
        """
        WOperation.__init__(
            self, ctx,
            op_name='%s %s' % (
                gt('无音清剿'),
                gt(plan.mission_type_name)
            )
        )

        self.plan: ChargePlanItem = plan

    def handle_init(self) -> None:
        """
        执行前的初始化 由子类实现
        注意初始化要全面 方便一个指令重复使用
        """
        self.charge_left: Optional[int] = None
        self.charge_need: Optional[int] = None
        self.change_charge: Optional[int] = None

        # 尝试删除self.auto_op: Optional[AutoBattleOperator] = None

    @node_from(from_name='判断下一次', status='体力充足')
    @operation_node(name='激活', is_start_node=True, node_max_retry_times=30)
    def wait_entry_load(self) -> OperationRoundResult:
        time.sleep(2)
        self.ctx.controller.move_w(press=True, press_time=0.5, release=True)
        screen = self.screenshot()
        area = self.ctx.screen_loader.get_area('大世界', '交互框')
        result = self.round_by_ocr_and_click(screen, '激活', area=area, success_wait=0.5, retry_wait_round=0.5)
        if result.is_success:
            return self.round_success()
        else:
            return self.round_retry()

    @node_from(from_name='激活', success=True)
    @operation_node(name='监控战斗结束')
    def monitor_battle(self) -> OperationRoundResult:
        op = MonitorBottleBySuccess(self.ctx)
        return self.round_by_op_result(op.execute())

    @node_from(from_name='监控战斗结束', status='全员死亡')
    @operation_node(name='全员死亡')
    def death(self) -> OperationRoundResult:
        return self.round_success(status=self.STATUS_CHARGE_ENOUGH)

    @node_from(from_name='监控战斗结束')
    @operation_node(name='传送回来')
    def tp_back(self) -> OperationRoundResult:
        time.sleep(2)
        self.round_by_click_area('大世界', '地图', success_wait=2)
        self.round_by_click_area('地图传送', '缩放中间', success_wait=1)
        self.round_by_click_area('地图传送', '中间', success_wait=1)
        screen = self.screenshot()
        area = self.ctx.screen_loader.get_area('大世界', '交互框')
        self.round_by_ocr_and_click(screen, self.plan.mission_type_name, area=area, success_wait=1)
        self.round_by_click_area('地图传送', '传送', success_wait=2)
        #等待地图加载
        screen = self.screenshot()
        result = self.round_by_find_area(screen, '大世界', '多人游戏')
        while not result.is_success:
            screen = self.screenshot()
            result = self.round_by_find_area(screen, '大世界', '多人游戏', retry_wait=1)
        if result.is_success:
            self.ctx.controller.move_w(press=True, press_time=0.5, release=True)
            time.sleep(2)
            screen = self.screenshot()
            area = self.ctx.screen_loader.get_area('大世界', '交互框')
            self.round_by_ocr_and_click(screen, '领取', area, success_wait=3)
            return self.round_success()

    @node_from(from_name='传送回来')
    @operation_node(name='识别体力以便领取奖励', node_max_retry_times=10)
    def check_charge_for_reward(self) -> OperationRoundResult:
        screen = self.screenshot()
        area = self.ctx.screen_loader.get_area('副本界面', '领取时剩余体力')
        part = cv2_utils.crop_image_only(screen, area.rect)
        ocr_result = self.ctx.ocr.run_ocr_single_line(part)
        self.charge_left = str_utils.get_positive_digits(ocr_result, None)
        print(f"剩余体力: {self.charge_left}")
        if self.charge_left is None:
            return self.round_retry(status='识别 %s 失败' % '剩余体力', wait=1)

        area = self.ctx.screen_loader.get_area('弹窗', '单倍耗体力')
        part = cv2_utils.crop_image_only(screen, area.rect)
        ocr_result = self.ctx.ocr.run_ocr_single_line(part)
        self.single_charge_consume = str_utils.get_positive_digits(ocr_result, None)
        print(f"单倍耗体力: {self.single_charge_consume}")
        if self.single_charge_consume is None:
            return self.round_retry(status='识别 %s 失败' % '单倍耗体力', wait=1)

        self.double_charge_consume = self.single_charge_consume*2
        print(f"双倍耗体力: {self.double_charge_consume}")

        area = self.ctx.screen_loader.get_area('副本界面', '结晶单质')
        part = cv2_utils.crop_image_only(screen, area.rect)
        ocr_result = self.ctx.ocr.run_ocr_single_line(part)
        self.change_charge = str_utils.get_positive_digits(ocr_result, None)
        print(f"结晶单质: {self.change_charge}")
        if self.change_charge is None:
            return self.round_retry(status='识别 %s 失败' % '结晶单质', wait=1)
        return self.round_success()

    @node_from(from_name='识别体力以便领取奖励')
    @operation_node(name='领取奖励')
    def reward(self) -> OperationRoundResult:
        time.sleep(2)
        if self.charge_left >= self.double_charge_consume:
            self.round_by_click_area('弹窗', '双倍耗体力')
            self.charge_left -= self.double_charge_consume
            self.ctx.charge_plan_config.add_plan_run_times(self.plan)
            self.ctx.charge_plan_config.add_plan_run_times(self.plan)
            return self.round_success()
        elif self.charge_left >= self.single_charge_consume:
            self.round_by_click_area('弹窗', '单倍耗体力')
            self.charge_left -= self.single_charge_consume
            self.ctx.charge_plan_config.add_plan_run_times(self.plan)
            return self.round_success()
        elif self.charge_left >= 40 and self.change_charge >= 20:
            self.round_by_click_area('弹窗', '单倍耗体力',success_wait=2)
            self.round_by_click_area('战斗', '补充确定', success_wait=1)
            self.round_by_click_area('战斗', '补充确定', success_wait=1)
            self.round_by_click_area('弹窗', '大弹窗关闭', success_wait=1)
            self.round_by_click_area('弹窗', '大弹窗关闭', success_wait=1)
            self.round_by_click_area('弹窗', '单倍耗体力',success_wait=2)
            self.ctx.charge_plan_config.add_plan_run_times(self.plan)
            self.charge_left = 0
            return self.round_success()
        else:
            return self.round_success(SilentCleanup.STATUS_CHARGE_NOT_ENOUGH)

    @node_from(from_name='领取奖励')
    @operation_node(name='判断下一次', node_max_retry_times=10)
    def check_next(self) -> OperationRoundResult:
        screen = self.screenshot()
        area = self.ctx.screen_loader.get_area('战斗', '领取后选择')
        result = self.round_by_ocr_and_click(screen, '确定', area, success_wait=5, retry_wait_round=1)
        if not result.is_success:
            return self.round_retry()
        if self.charge_left < (self.single_charge_consume/2):
            return self.round_success(status=SilentCleanup.STATUS_CHARGE_NOT_ENOUGH)
        else:
            return self.round_success(status=SilentCleanup.STATUS_CHARGE_ENOUGH)


    def _on_pause(self, e=None):
        WOperation._on_pause(self, e)
        # 尝试删除auto_battle_utils.stop_running(self.auto_op)

    def _on_resume(self, e=None):
        WOperation._on_resume(self, e)
        # 尝试删除auto_battle_utils.resume_running(self.auto_op)

    def after_operation_done(self, result: OperationResult):
        WOperation.after_operation_done(self, result)
        # 尝试删除if self.auto_op is not None:
        # 尝试删除self.auto_op.dispose()
        # 尝试删除self.auto_op = None


def __debug():
    ctx = WContext()
    ctx.init_by_config()
    ctx.ocr.init_model()
    ctx.start_running()
    op = SilentCleanup(ctx, ChargePlanItem(
        category_name='无音清剿',
        mission_type_name='怪兽与怪客'
    ))
    op.execute()


if __name__ == '__main__':
    __debug()
