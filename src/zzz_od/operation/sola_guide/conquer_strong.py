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
from zzz_od.operation.monitor_bottle_by_boss import MonitorBottleByBoss
from zzz_od.operation.sola_guide.tp_by_sola_guide import TransportBySolaGuide
from zzz_od.operation.zzz_operation import WOperation


class ConquerStrong(WOperation):

    STATUS_CHARGE_NOT_ENOUGH: ClassVar[str] = '体力不足'
    STATUS_CHARGE_ENOUGH: ClassVar[str] = '体力充足'

    def __init__(self, ctx: WContext, plan: ChargePlanItem):
        """
        使用索拉指南传送后
        用这个进行挑战
        :param ctx:
        """
        WOperation.__init__(
            self, ctx,
            op_name='%s %s' % (
                gt('讨伐强敌'),
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

        # 尝试删除self.auto_op: Optional[AutoBattleOperator] = None


        #self.ctx.charge_plan_config.add_plan_run_times(self.plan)

    @node_from(from_name='领取奖励再来一次或结束', status='确定')
    @operation_node(name='等待boss加载', is_start_node=True, node_max_retry_times=420)
    def wait_entry_load(self) -> OperationRoundResult:
        screen = self.screenshot()
        area = self.ctx.screen_loader.get_area('战斗', 'boss名')
        result = self.round_by_ocr(screen, self.plan.mission_type_name,
                                   area=area, success_wait=0.5, retry_wait_round=0.5)
        if result.is_success:
            return self.round_success()
        else:
            return self.round_retry()

    @node_from(from_name='等待boss加载', success=True)
    @operation_node(name='监控战斗结束')
    def monitor_battle(self) -> OperationRoundResult:
        op = MonitorBottleByBoss(self.ctx, self.plan.mission_type_name)
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
        self.round_by_click_area('地图传送', '中间', success_wait=1)
        screen = self.screenshot()
        area = self.ctx.screen_loader.get_area('大世界', '交互框')
        self.round_by_ocr_and_click(screen, '借位信标', area=area, success_wait=1)
        self.round_by_click_area('地图传送', '传送', success_wait=2)
        #等待地图加载
        screen = self.screenshot()
        result = self.round_by_find_area(screen, '大世界', '多人游戏')
        while not result.is_success:
            screen = self.screenshot()
            result = self.round_by_find_area(screen, '大世界', '多人游戏', retry_wait=1)
        if result.is_success:
            return self.round_success()

    @node_from(from_name='传送回来')
    @operation_node(name='领取奖励再来一次或结束', node_max_retry_times=8)
    def reward(self) -> OperationRoundResult:
        time.sleep(2)
        screen = self.screenshot()
        area = self.ctx.screen_loader.get_area('大世界', '交互框')
        self.round_by_ocr_and_click(screen, '领取', area, success_wait=3)

        screen = self.screenshot()
        area_c = self.ctx.screen_loader.get_area('战斗', '弹窗右选')
        result_c = self.round_by_ocr(screen, '确认', area_c)

        area_f = self.ctx.screen_loader.get_area('战斗', '补充结晶波片')
        result_f = self.round_by_ocr(screen, '补充结晶波片', area_f)

        if result_c.is_success:
            self.round_by_ocr_and_click(screen, '确认', area_c, success_wait=4)
            screen = self.screenshot()
            area = self.ctx.screen_loader.get_area('战斗', '领取后选择')
            result = self.round_by_ocr_and_click(screen, '确定', area, success_wait=4)

            self.ctx.charge_plan_config.add_plan_run_times(self.plan)
            print(f"计算后的已刷次数{self.plan.run_times}")
            print(f"计划次数{self.plan.plan_times}")
            if self.plan.plan_times <= self.plan.run_times:
                return self.round_success(status=self.STATUS_CHARGE_ENOUGH)

            return result
        elif result_f.is_success:
            return self.round_success(status=self.STATUS_CHARGE_NOT_ENOUGH)
        else:
            return self.round_retry()

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
    op = ConquerStrong(ctx, ChargePlanItem(
        category_name='讨伐强敌',
        mission_type_name='云闪之鳞'
    ))
    op.execute()


if __name__ == '__main__':
    __debug()
