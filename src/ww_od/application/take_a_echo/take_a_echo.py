import time

from one_dragon.base.operation.operation_edge import node_from
from one_dragon.base.operation.operation_node import operation_node
from one_dragon.base.operation.operation_round_result import OperationRoundResult
from one_dragon.utils.i18_utils import gt
from ww_od.application.zzz_application import WApplication
from ww_od.context.zzz_context import WContext
from ww_od.operation.back_to_normal_world import BackToNormalWorld
from ww_od.operation.control_okww_auto import start_okww_auto, kill_okww_auto
from ww_od.operation.monitor_battle_by_success import MonitorBottleBySuccess
from ww_od.operation.monitor_bottle_by_boss import MonitorBottleByBoss
from ww_od.operation.move_search import MoveSearch
from ww_od.operation.open_menu import OpenMenu
from ww_od.operation.search_interaction import SearchInteract
from ww_od.operation.sola_guide.tp_by_sola_guide import TransportBySolaGuide
from ww_od.operation.switch_teams import SwitchTeams


class TakeAEcho(WApplication):

    def __init__(self, ctx: WContext):
        """
        每天自动接收邮件奖励
        """
        WApplication.__init__(
            self,
            ctx=ctx, app_id='take_a_echo',
            op_name=gt('获得一个龟龟声骇', 'ui'),
            run_record=ctx.take_a_echo_run_record
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
        return self.round_success()

    @node_from(from_name='监控战斗结束', status='全员死亡')
    @node_from(from_name='启动自动战斗')
    @operation_node(name='传送')
    def transport(self) -> OperationRoundResult:
        op = TransportBySolaGuide(self.ctx,
                                  "周期演算",
                                  '战歌重奏',
                                  "昔日咏叹之钟·战歌重奏")
        result = self.round_by_op_result(op.execute())
        if result.is_success:
            return result
        return self.round_retry()

    @node_from(from_name='传送')
    @operation_node(name='向前走')
    def move_forward(self) -> OperationRoundResult:
        self.ctx.controller.move_w(press=True, press_time=7, release=True)
        return self.round_success()

    @node_from(from_name='向前走')
    @node_from(from_name='重新挑战')
    @operation_node(name='等待boss刷新', node_max_retry_times=180)
    def wait_boss(self) -> OperationRoundResult:
        time.sleep(1)
        screen = self.screenshot()
        area = self.ctx.screen_loader.get_area('战斗', 'boss名')
        result = self.round_by_ocr(screen, '鸣钟之龟', area=area, success_wait=0.5)
        if result.is_success:
            return self.round_success()
        return self.round_retry()
    '''
    @node_from(from_name='向前走')
    @operation_node(name='交互')
    def interact_in(self) -> OperationRoundResult:
        #screen = self.screenshot()
        #area = self.ctx.screen_loader.get_area('大世界', '交互框')
        self.ctx.controller.interact(press=True, press_time=1, release=True)
        #self.round_by_ocr_and_click(screen, self.plan.mission_type_name, area, success_wait=10)
        return self.round_success()

    @node_from(from_name='交互')
    @operation_node(name='点击出战', node_max_retry_times=30)
    def click_start(self) -> OperationRoundResult:
        time.sleep(7)
        screen = self.screenshot()
        area = self.ctx.screen_loader.get_area('副本界面', '等级区域')
        # result = self.round_by_ocr_and_click(screen, '推荐等级70', area, success_wait=1, retry_wait_round=2)
        result1 = self.round_by_click_area('副本界面', '单人挑战', success_wait=1, retry_wait_round=1)
        screen = self.screenshot()
        area = self.ctx.screen_loader.get_area('弹窗', '右选项')
        self.round_by_ocr_and_click(screen,'确认', area, success_wait=3, retry_wait=3)
        if not result1.is_success:
            return self.round_retry()
        return result1

    @node_from(from_name='点击出战')
    @operation_node(name='编队')
    def team(self) -> OperationRoundResult:
        return self.round_by_click_area('编队', '出战', success_wait=1, retry_wait=1)

    @node_from(from_name='再来一次')
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
    '''

    @node_from(from_name='等待boss刷新')
    @operation_node(name='监控战斗结束')
    def monitor_battle(self) -> OperationRoundResult:
        op = MonitorBottleByBoss(self.ctx, boss='鸣钟之龟')
        return self.round_by_op_result(op.execute())

    @node_from(from_name='监控战斗结束')
    @operation_node(name='吸收声骇')
    def after_battle(self) -> OperationRoundResult:
        time.sleep(2)
        op = SearchInteract(self.ctx, '吸收', 1)
        return self.round_by_op_result(op.execute())

    @node_from(from_name='吸收声骇', success=False)
    @operation_node(name='重新挑战')
    def re_battle(self) -> OperationRoundResult:
        time.sleep(2)
        op = MoveSearch(self.ctx, '重新挑战', move_time=15)
        result = self.round_by_op_result(op.execute())
        if not result.is_success:
            op = SearchInteract(self.ctx, '重新挑战', circles=3)
            result = self.round_by_op_result(op.execute())
        return self.round_success(status='重新挑战')

    '''
    @node_from(from_name='吸收声骇', success=False)
    @operation_node(name='再来一次')
    def again(self) -> OperationRoundResult:
        time.sleep(2)
        self.round_by_click_area('副本大世界', '退出', success_wait=2)
        area = self.ctx.screen_loader.get_area('弹窗', '选项')
        screen = self.screenshot()
        return self.round_by_ocr_and_click(screen, '重新挑战', area, success_wait=5, retry_wait_round=1)
    '''

    @node_from(from_name='吸收声骇')
    @operation_node(name='返回大世界')
    def back_to_world(self) -> OperationRoundResult:
        time.sleep(1)
        op = BackToNormalWorld(self.ctx)
        return self.round_by_op_result(op.execute())

    @node_from(from_name='返回大世界')
    @operation_node(name='脱战')
    def out_of_fight(self) -> OperationRoundResult:
        op = TransportBySolaGuide(self.ctx,
                                  '周期挑战',
                                  '模拟领域',
                                  '共鸣促剂')
        return self.round_by_op_result(op.execute())

    '''
    @node_from(from_name='返回大世界')
    @operation_node(name='关闭自动战斗')
    def close_auto(self) -> OperationRoundResult:
        kill_okww_auto()
        time.sleep(2)
        return self.round_success()
    '''

    '''
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
    '''

def __debug():
    ctx = WContext()
    ctx.init_by_config()
    ctx.ocr.init_model()
    ctx.start_running()
    op = TakeAEcho(ctx)
    op.execute()


if __name__ == '__main__':
    __debug()

