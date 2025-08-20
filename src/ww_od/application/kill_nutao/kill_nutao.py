import time

from one_dragon.base.operation.operation_edge import node_from
from one_dragon.base.operation.operation_node import operation_node
from one_dragon.base.operation.operation_round_result import OperationRoundResult
from one_dragon.utils.i18_utils import gt
from ww_od.application.ww_application import WApplication
from ww_od.context.ww_context import WContext
from ww_od.operation.control_okww_auto import start_okww_auto
from ww_od.operation.monitor_bottle_by_boss import MonitorBottleByBoss
from ww_od.operation.search_interaction import SearchInteract
from ww_od.operation.sola_guide.tp_by_sola_guide import TransportBySolaGuide


class KillNutao(WApplication):

    def __init__(self, ctx: WContext):
        """
        每天自动接收邮件奖励
        """
        WApplication.__init__(
            self,
            ctx=ctx, app_id='kill_nutao',
            op_name=gt('杀一次朔雷之鳞', 'ui'),
            run_record=ctx.kill_nutao_run_record
        )

    def handle_init(self) -> None:
        """
        执行前的初始化 由子类实现
        注意初始化要全面 方便一个指令重复使用
        """
        pass

    @operation_node(name='启动自动战斗', is_start_node=True)
    def start_auto(self) -> OperationRoundResult:
        start_okww_auto()
        self.round_by_click_area('菜单', '返回', success_wait=2)
        return self.round_success()

    @node_from(from_name='监控战斗结束', status='全员死亡')
    @node_from(from_name='启动自动战斗')
    @operation_node(name='传送', node_max_retry_times=3)
    def transport(self) -> OperationRoundResult:
        op = TransportBySolaGuide(self.ctx,
                                  "周期演算",
                                  '讨伐强敌',
                                  "朔雷之鳞")
        result = self.round_by_op_result(op.execute())
        if result.is_success:
            return result
        return self.round_retry()

    @node_from(from_name='传送')
    @operation_node(name='是否可以战斗')
    def is_battle(self) -> OperationRoundResult:
        time.sleep(2)
        screen = self.screenshot()
        area = self.ctx.screen_loader.get_area('战斗', 'boss名')
        result = self.round_by_ocr(screen, '朔雷之鳞', area=area, success_wait=0.5)
        if not result.is_success:
            return self.round_fail(status='需要往前')
        return result

    @node_from(from_name='是否可以战斗', success=False)
    @operation_node(name='向前走')
    def move_forward(self) -> OperationRoundResult:
        self.ctx.controller.move_w(press=True, press_time=9, release=True)
        return self.round_success()

    @node_from(from_name='是否可以战斗', status='朔雷之鳞')
    @node_from(from_name='向前走')
    @operation_node(name='监控战斗结束')
    def monitor_battle(self) -> OperationRoundResult:
        op = MonitorBottleByBoss(self.ctx, boss='朔雷之鳞')
        return self.round_by_op_result(op.execute())

    @node_from(from_name='监控战斗结束')
    @operation_node(name='获得声骇如果有')
    def take_echo(self) -> OperationRoundResult:
        time.sleep(2)
        op = SearchInteract(self.ctx, '吸收', 3)
        self.round_by_op_result(op.execute())
        return self.round_success()

    @node_from(from_name='获得声骇如果有')
    @operation_node(name='脱战')
    def out_of_fight(self) -> OperationRoundResult:
        op = TransportBySolaGuide(self.ctx,
                                  '周期挑战',
                                  '模拟领域',
                                  '共鸣促剂')
        return self.round_by_op_result(op.execute())

def __debug():
    ctx = WContext()
    ctx.init_by_config()
    ctx.ocr.init_model()
    ctx.start_running()
    op = KillNutao(ctx)
    op.execute()


if __name__ == '__main__':
    __debug()

