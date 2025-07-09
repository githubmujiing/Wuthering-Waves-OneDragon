from one_dragon.base.operation.operation_edge import node_from
from one_dragon.base.operation.operation_node import operation_node
from one_dragon.base.operation.operation_round_result import OperationRoundResult
from one_dragon.utils.i18_utils import gt
from ww_od.context.zzz_context import WContext
from ww_od.operation.open_menu import OpenMenu
from ww_od.operation.zzz_operation import WOperation


class OpenSolaGuide(WOperation):

    def __init__(self, ctx: WContext):
        """
        打开索拉指南
        使用了打开菜单 会包含返回大世界的操作
        """
        WOperation.__init__(
            self,
            ctx=ctx,
            op_name=gt('打开索拉指南', 'ui'),
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
    @operation_node(name='点击索拉指南')
    def click_sola_guide(self) -> OperationRoundResult:
        """
        点击更多
        """
        screen = self.screenshot()
        area = self.ctx.screen_loader.get_area('菜单', '中部列表')
        return self.round_by_ocr_and_click(screen, '索拉指南', area=area,
                                           success_wait=2, retry_wait=1)
