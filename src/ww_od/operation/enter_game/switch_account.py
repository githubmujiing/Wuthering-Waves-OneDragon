from one_dragon.base.operation.operation_edge import node_from
from one_dragon.base.operation.operation_node import operation_node
from one_dragon.base.operation.operation_round_result import OperationRoundResult
from one_dragon.utils.i18_utils import gt
from ww_od.context.ww_context import WContext
from ww_od.operation.enter_game.enter_game import EnterGame
from ww_od.operation.open_menu import OpenMenu
from ww_od.operation.ww_operation import WOperation


class SwitchAccount(WOperation):

    def __init__(self, ctx: WContext):
        self.ctx: WContext = ctx
        WOperation.__init__(self, ctx, op_name=gt('切换账号', 'ui'))

    @operation_node(name='打开菜单', is_start_node=True)
    def open_menu(self) -> OperationRoundResult:
        op = OpenMenu(self.ctx)
        return self.round_by_op_result(op.execute())

    @node_from(from_name='打开菜单')
    @operation_node(name='点击登出')
    def click_logout(self) -> OperationRoundResult:
        return self.round_by_click_area('菜单', '登出', success_wait=1)

    @node_from(from_name='点击登出')
    @operation_node(name='点击登出确认')
    def logout_confirm(self) -> OperationRoundResult:
        return self.round_by_click_area('弹窗', '右选项', success_wait=1)

    @node_from(from_name='点击登出确认')
    @operation_node(name='进入游戏')
    def enter_game(self) -> OperationRoundResult:
        op = EnterGame(self.ctx)
        return self.round_by_op_result(op.execute())


def __debug():
    ctx = WContext()
    ctx.init_by_config()
    ctx.ocr.init_model()
    ctx.start_running()
    op = SwitchAccount(ctx)
    op.execute()


if __name__ == '__main__':
    __debug()
