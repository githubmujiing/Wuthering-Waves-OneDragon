from typing import ClassVar

from one_dragon.base.operation.operation_edge import node_from
from one_dragon.base.operation.operation_node import operation_node
from one_dragon.base.operation.operation_round_result import OperationRoundResult
from one_dragon.utils.i18_utils import gt
from ww_od.application.charge_plan.charge_plan_config import ChargePlanItem
from ww_od.context.zzz_context import WContext
from ww_od.operation.open_menu import OpenMenu
from ww_od.operation.zzz_operation import WOperation


class SwitchTeams(WOperation):

    def __init__(self, ctx: WContext, plan: ChargePlanItem):
        WOperation.__init__(self, ctx, op_name=gt('切换编队', 'ui'))
        self.plan: ChargePlanItem = plan

    def handle_init(self):
        pass

    @operation_node(name='画面识别', is_start_node=True)
    def check_teams(self) -> OperationRoundResult:
        """
        识别画面
        :return:
        """
        screen = self.screenshot()
        area = self.ctx.screen_loader.get_area('编队', '编队')
        result = self.round_by_find_and_click_area(screen, '编队', '编队', success_wait=1)
        if result.is_success:
            return self.round_success()

        return self.round_fail()

    @node_from(from_name='画面识别', success=False)
    @operation_node(name='打开菜单')
    def open_menu(self) -> OperationRoundResult:
        op = OpenMenu(self.ctx)
        return self.round_by_op_result(op.execute())

    @node_from(from_name='打开菜单')
    @operation_node(name='打开编队')
    def open_t(self) -> OperationRoundResult:
        screen = self.screenshot()
        area = self.ctx.screen_loader.get_area('菜单', '中部列表')
        result = self.round_by_ocr_and_click(screen,'编队', area=area, success_wait=1)
        return result

    @node_from(from_name='打开编队')
    @node_from(from_name='画面识别', success=True)
    @operation_node(name='切换队伍')
    def switch_teams(self) -> OperationRoundResult:
        if self.plan.team == '默认队伍':
            return self.round_success()
        screen = self.screenshot()
        return self.round_by_click_area('编队', self.plan.team, success_wait=1, retry_wait=1)

    @node_from(from_name='切换队伍', success=True)
    @operation_node(name='出战')
    def go_to_war(self) -> OperationRoundResult:
        screen = self.screenshot()
        return self.round_by_click_area('编队', '出战', success_wait=1, retry_wait=1)



def __debug_op():
    ctx = WContext()
    ctx.init_by_config()
    ctx.ocr.init_model()
    op = SwitchTeams(ctx, ChargePlanItem(
        team='5'
    ))
    ctx.start_running()
    op.execute()


if __name__ == '__main__':
    __debug_op()