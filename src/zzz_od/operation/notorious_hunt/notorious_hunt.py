import time

from typing import Optional, ClassVar

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
from zzz_od.operation.switch_teams import SwitchTeams
from zzz_od.operation.zzz_operation import WOperation


class NotoriousHunt(WOperation):

    STATUS_CHARGE_NOT_ENOUGH: ClassVar[str] = '体力不足'
    STATUS_CHARGE_ENOUGH: ClassVar[str] = '体力充足'
    STATUS_RUNS_NOT_ENOUGH: ClassVar[str] = '获取次数不足'
    STATUS_RUNS_ENOUGH: ClassVar[str] = '获取次数充足'

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
                gt('战歌重奏'),
                gt(plan.mission_type_name)
            )
        )

        self.charge_left = None
        self.plan: ChargePlanItem = plan

    def handle_init(self) -> None:
        """
        执行前的初始化 由子类实现
        注意初始化要全面 方便一个指令重复使用
        """
        self.charge_left: Optional[int] = None
        self.charge_need: Optional[int] = None
        self.runs : Optional[int] = None

        # 尝试删除self.auto_op: Optional[AutoBattleOperator] = None

    @operation_node(name='向前走', is_start_node=True,)
    def move_forward(self) -> OperationRoundResult:
        if self.plan.mission_type_name == '战歌重奏·命定的纷争':
            self.ctx.controller.move_w(press=True, press_time=1, release=True)
        elif self.plan.mission_type_name == '无冠者之像·心脏':
            self.ctx.controller.move_w(press=True, press_time=0.7, release=True)
        else:
            self.ctx.controller.move_w(press=True, press_time=1.7, release=True)
        return self.round_success()

    @node_from(from_name='向前走')
    @operation_node(name='交互')
    def interact_in(self) -> OperationRoundResult:
        #screen = self.screenshot()
        #area = self.ctx.screen_loader.get_area('大世界', '交互框')
        self.ctx.controller.interact(press=True, press_time=1, release=True)
        #self.round_by_ocr_and_click(screen, self.plan.mission_type_name, area, success_wait=10)
        return self.round_success()

    @node_from(from_name='交互')
    @operation_node(name='识别体力')
    def check_charge(self) -> OperationRoundResult:
        time.sleep(10)
        screen = self.screenshot()
        area = self.ctx.screen_loader.get_area('副本界面', '剩余体力')
        part = cv2_utils.crop_image_only(screen, area.rect)
        ocr_result = self.ctx.ocr.run_ocr_single_line(part)
        self.charge_left = str_utils.get_positive_digits(ocr_result, None)
        print(f"剩余体力: {self.charge_left}")
        if self.charge_left is None:
            return self.round_retry(status='识别 %s 失败' % '剩余体力', wait=1)

        area = self.ctx.screen_loader.get_area('副本界面', '需要体力')
        part = cv2_utils.crop_image_only(screen, area.rect)
        ocr_result = self.ctx.ocr.run_ocr_single_line(part)
        self.charge_need = str_utils.get_positive_digits(ocr_result, None)
        print(f"需要体力: {self.charge_need}")
        if self.charge_need is None:
            return self.round_retry(status='识别 %s 失败' % '需要体力', wait=1)

        if self.charge_need > self.charge_left:
            print("执行返回")
            return self.round_success(NotoriousHunt.STATUS_CHARGE_NOT_ENOUGH)

        self.can_run_times = self.charge_left // self.charge_need
        max_need_run_times = self.plan.plan_times - self.plan.run_times
        print(f"max_need_run_times: {max_need_run_times}")
        print(f"self.can_run_times: {self.can_run_times}")
        if self.can_run_times > max_need_run_times:
            self.can_run_times = max_need_run_times

        return self.round_success(NotoriousHunt.STATUS_CHARGE_ENOUGH)

    @node_from(from_name='识别体力',status='体力充足')
    @operation_node(name='识别获取次数')
    def check_runs(self) -> OperationRoundResult:
        screen = self.screenshot()
        area = self.ctx.screen_loader.get_area('副本界面', '获取次数')
        part = cv2_utils.crop_image_only(screen, area.rect)
        ocr_result = self.ctx.ocr.run_ocr_single_line(part)
        self.runs = str_utils.get_positive_digits(ocr_result, None)
        print(f"获取次数: {self.runs}")
        if self.runs is None:
            return self.round_retry(status='识别 %s 失败' % '获取次数', wait=1)

        if 0 >= self.runs:
            print("执行返回")
            return self.round_success(NotoriousHunt.STATUS_RUNS_NOT_ENOUGH)

        if self.can_run_times > self.runs:
            self.can_run_times = self.runs
        return self.round_success(NotoriousHunt.STATUS_RUNS_ENOUGH)

    @node_from(from_name='识别获取次数', status='获取次数充足')
    @operation_node(name='点击出战')
    def click_start(self) -> OperationRoundResult:
        screen = self.screenshot()
        result1 = self.round_by_click_area('副本界面', '单人挑战', success_wait=2)
        # 防止前面电量识别错误
        area = self.ctx.screen_loader.get_area('副本界面', '结晶波片不足')
        result2 = self.round_by_ocr(screen,'结晶波片不足', area)
        if result2.is_success:
            self.round_by_click_area('副本界面', '取消', success_wait=1)
            return self.round_success(status=NotoriousHunt.STATUS_CHARGE_NOT_ENOUGH)

        return result1

    @node_from(from_name='点击出战')
    @operation_node(name='编队')
    def team(self) -> OperationRoundResult:
        op = SwitchTeams(self.ctx, self.plan)
        return self.round_by_op_result(op.execute())

    @node_from(from_name='判断下一次', status='重新挑战')
    @node_from(from_name='编队')
    @operation_node(name='确认在副本')
    def confirm_copy(self) -> OperationRoundResult:
        screen = self.screenshot()
        result = self.round_by_find_area(screen, '副本大世界', '退出')
        while not result.is_success:
            screen = self.screenshot()
            result = self.round_by_find_area(screen, '副本大世界', '退出',retry_wait=1)
        if result.is_success:
            return self.round_success()

    @node_from(from_name='确认在副本')
    @operation_node(name='监控战斗结束')
    def monitor_battle(self) -> OperationRoundResult:
        op = MonitorBottleBySuccess(self.ctx)
        return self.round_by_op_result(op.execute())

    @node_from(from_name='监控战斗结束', status='全员死亡')
    @operation_node(name='全员死亡')
    def death(self) -> OperationRoundResult:
        return self.round_success(status=self.STATUS_CHARGE_ENOUGH)

    @node_from(from_name='领取奖励', success=False)
    @node_from(from_name='监控战斗结束')
    @operation_node(name='寻找奖励交互', node_max_retry_times=5)
    def after_battle(self) -> OperationRoundResult:
        time.sleep(2)
        op = SearchInteract(self.ctx, '领取', 8)
        result = self.round_by_op_result(op.execute())
        if not result.is_success:
            return self.round_retry()
        return result

    @node_from(from_name='寻找奖励交互')
    @operation_node(name='领取奖励')
    def reward(self) -> OperationRoundResult:
        time.sleep(2)
        screen = self.screenshot()
        area = self.ctx.screen_loader.get_area('战斗', '弹窗右选')
        op = self.round_by_ocr_and_click(screen, '确认', area, success_wait=4)
        if op.is_success:
            self.can_run_times -= 1
            self.ctx.notorious_hunt_config.add_plan_run_times(self.plan)
            return self.round_success()
        else:
            return self.round_fail()

    @node_from(from_name='领取奖励')
    @operation_node(name='判断下一次')
    def check_next(self) -> OperationRoundResult:
        screen = self.screenshot()
        if self.can_run_times == 0:
            area = self.ctx.screen_loader.get_area('战斗', '退出副本')
            return self.round_by_ocr_and_click(screen, '退出副本', area, success_wait=5, retry_wait_round=1)
        else:
            area = self.ctx.screen_loader.get_area('战斗', '重新挑战')
            return self.round_by_ocr_and_click(screen, '重新挑战', area, success_wait=5, retry_wait_round=1)


    def _on_pause(self, e=None):
        WOperation._on_pause(self, e)
        # 尝试删除if self.auto_op is not None:
        # 尝试删除self.auto_op.stop_running()

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
    op = NotoriousHunt(ctx, ChargePlanItem(
        category_name='战歌重奏',
        mission_type_name='无序边境·余烬'
    ))
    op.execute()


if __name__ == '__main__':
    __debug()
