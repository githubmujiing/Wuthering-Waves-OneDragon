from one_dragon.base.operation.operation_edge import node_from
from one_dragon.base.operation.operation_node import operation_node
from one_dragon.base.operation.operation_round_result import OperationRoundResult
from one_dragon.utils.i18_utils import gt
from ww_od.application.zzz_application import WApplication
from ww_od.context.zzz_context import WContext
from ww_od.operation.open_menu import OpenMenu


class SynthesisApp(WApplication):

    def __init__(self, ctx: WContext):
        """
        每天自动接收邮件奖励
        """
        WApplication.__init__(
            self,
            ctx=ctx, app_id='synthesis',
            op_name=gt('合成', 'ui'),
            run_record=ctx.synthesis_run_record
        )

    def handle_init(self) -> None:
        """
        执行前的初始化 由子类实现
        注意初始化要全面 方便一个指令重复使用
        """
        pass

    @operation_node(name='打开菜单', is_start_node=True)
    def open_menu(self) -> OperationRoundResult:
        op = OpenMenu(self.ctx)
        return self.round_by_op_result(op.execute())

    @node_from(from_name='打开菜单')
    @operation_node(name='点击合成')
    def click_synthesis(self) -> OperationRoundResult:
        screen = self.screenshot()
        area = self.ctx.screen_loader.get_area('菜单', '中部列表')
        return self.round_by_ocr_and_click(screen, '合成', area, success_wait=2)

    @node_from(from_name='点击合成')
    @operation_node(name='合成')
    def synthesis(self) -> OperationRoundResult:
        screen = self.screenshot()
        self.round_by_click_area('合成', '纯化', success_wait=1)
        self.round_by_click_area('合成', '第一个', success_wait=1)
        self.round_by_click_area('合成', '合成', success_wait=1)
        return self.round_success()

    @node_from(from_name='合成')
    @operation_node(name='返回菜单')
    def back_to_menu(self) -> OperationRoundResult:
        op = OpenMenu(self.ctx)
        return self.round_by_op_result(op.execute())
