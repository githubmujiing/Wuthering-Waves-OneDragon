import time

from typing import Optional, ClassVar

from one_dragon.base.geometry.point import Point
from one_dragon.base.operation.operation_base import OperationResult
from one_dragon.base.operation.operation_edge import node_from
from one_dragon.base.operation.operation_node import operation_node
from one_dragon.base.operation.operation_round_result import OperationRoundResult
from one_dragon.utils import cv2_utils, str_utils
from one_dragon.utils.i18_utils import gt
from ww_od.application.charge_plan.charge_plan_config import ChargePlanItem
# 尝试删除from ww_od.auto_battle import auto_battle_utils
# 尝试删除from ww_od.auto_battle.auto_battle_operator import AutoBattleOperator
from ww_od.context.ww_context import WContext
from ww_od.operation.back_to_normal_world import BackToNormalWorld
from ww_od.operation.monitor_battle_by_success import MonitorBottleBySuccess
from ww_od.operation.move_search import MoveSearch
from ww_od.operation.search_interaction import SearchInteract
from ww_od.operation.sola_guide.tp_by_sola_guide import TransportBySolaGuide
from ww_od.operation.ww_operation import WOperation


class NewSilentCleanup(WOperation):

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
                gt('新无音清剿'),
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

    @operation_node(name='激活', is_start_node=True, node_max_retry_times=30)
    def wait_entry_load(self) -> OperationRoundResult:
        time.sleep(2)
        if self.plan.mission_type_name == '黎乔利群岛无音区':
            self.ctx.controller.move_a(press=True, press_time=0.5, release=True)
            self.ctx.controller.move_w(press=True, press_time=9, release=True)
            return self.round_success()
        elif self.plan.mission_type_name == '槲生半岛无音区':
            self.ctx.controller.move_d(press=True, press_time=1.2, release=True)
            self.ctx.controller.move_w(press=True, press_time=12, release=True)
            return self.round_success()
        elif self.plan.mission_type_name == '悲叹墓岛无音区':
            self.ctx.controller.move_a(press=True, press_time=2, release=True)
            self.ctx.controller.move_w(press=True, press_time=3, release=True)
            self.ctx.controller.move_a(press=True, press_time=8, release=True)
            return self.round_success()
        else:
            self.ctx.controller.move_w(press=True, press_time=9, release=True)
            return self.round_success()

    @node_from(from_name='判断下一次', status='重新挑战')
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
    @operation_node(name='寻找奖励并交互', node_max_retry_times=3)
    def search_interact(self) -> OperationRoundResult:
            time.sleep(2)
            op1 = MoveSearch(self.ctx, '领取', move_time=10)
            result = self.round_by_op_result(op1.execute())
            if not result.is_success:
                op2 = SearchInteract(self.ctx, '领取', circles=3)
                result = self.round_by_op_result(op2.execute())
            if not result.is_success:
                return self.round_retry(wait_round_time=1)
            else:
                time.sleep(2)
                screen = self.screenshot()
                area = self.ctx.screen_loader.get_area('弹窗', '标题')
                result = self.round_by_ocr(screen, "领取奖励", area)
                if not result.is_success:
                    self.round_by_click_area('弹窗', '关闭')    # 以防领取奖励标题识别失误。
                    return self.round_retry(status='交互失误')
                return self.round_success()

    @node_from(from_name='寻找奖励并交互')
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
            self.change_charge = 0
            return self.round_success(status='识别 %s 失败' % '结晶单质', wait=1)
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
        elif self.charge_left >= self.single_charge_consume/2 and self.change_charge >= self.single_charge_consume:
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
            return self.round_success(NewSilentCleanup.STATUS_CHARGE_NOT_ENOUGH)

    @node_from(from_name='领取奖励')
    @operation_node(name='判断下一次', node_max_retry_times=10)
    def check_next(self) -> OperationRoundResult:
        time.sleep(1)
        screen = self.screenshot()
        area = self.ctx.screen_loader.get_area('战斗', '领取后选择')
        result = self.round_by_ocr_and_click(screen, '确定', area, success_wait=5, retry_wait_round=1)
        if not result.is_success:
            return self.round_retry()
        if self.charge_left < (self.single_charge_consume/2):
            return self.round_success(status=NewSilentCleanup.STATUS_CHARGE_NOT_ENOUGH)
        elif self.plan.plan_times <= self.plan.run_times:
            return self.round_success(status=NewSilentCleanup.STATUS_CHARGE_ENOUGH)
        else:
            op = BackToNormalWorld(self.ctx)
            self.round_by_op_result(op.execute())
            return self.round_success(status='重新挑战')

    @node_from(from_name='领取奖励', status='体力不足')
    @node_from(from_name='判断下一次', status='体力不足')
    @operation_node(name='脱战')
    def out_of_fight(self) -> OperationRoundResult:
        op = TransportBySolaGuide(self.ctx,
                                  '周期挑战',
                                  '模拟领域',
                                  '共鸣促剂')
        self.round_by_op_result(op.execute())
        return self.round_success(status=self.STATUS_CHARGE_NOT_ENOUGH)


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

    def tp_by_sola_guide(self):
        pass


def __debug():
    ctx = WContext()
    ctx.init_by_config()
    ctx.ocr.init_model()
    ctx.start_running()
    op = NewSilentCleanup(ctx, ChargePlanItem(
        tab_name='周期挑战',
        category_name='无音清剿',
        mission_type_name='黎乔利群岛无音区',
        run_times=0,
        plan_times=5,
    ))
    op.execute()


if __name__ == '__main__':
    __debug()
