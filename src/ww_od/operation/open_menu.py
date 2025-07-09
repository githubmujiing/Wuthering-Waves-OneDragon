from typing import ClassVar

from one_dragon.base.operation.operation_edge import node_from
from one_dragon.base.operation.operation_node import operation_node
from one_dragon.base.operation.operation_round_result import OperationRoundResult
from one_dragon.utils.i18_utils import gt
from ww_od.context.ww_context import WContext
from ww_od.operation.back_to_normal_world import BackToNormalWorld
from ww_od.operation.ww_operation import WOperation


class OpenMenu(WOperation):

    STATUS_NOT_IN_MENU: ClassVar[str] = '未在菜单页面'

    def __init__(self, ctx: WContext):
        """
        识别画面 打开菜单
        由于使用了返回大世界 应可保证在任何情况下使用
        :param ctx:
        """
        WOperation.__init__(self, ctx,
                            op_name=gt('打开菜单', 'ui')
                            )

    @node_from(from_name='点击菜单')
    @operation_node(name='画面识别', is_start_node=True)
    def check_menu(self) -> OperationRoundResult:
        """
        识别画面
        :return:
        """
        screen = self.screenshot()
        area = self.ctx.screen_loader.get_area('菜单', '中部列表')
        result = self.round_by_ocr(screen, '编队', area=area)
        if result.is_success:
            return self.round_success()

        return self.round_fail()

    @node_from(from_name='画面识别', success=False)
    @operation_node(name='返回大世界')
    def back_to_world(self) -> OperationRoundResult:
        op = BackToNormalWorld(self.ctx)
        return self.round_by_op_result(op.execute())

    @node_from(from_name='画面识别', status='多人游戏')
    @node_from(from_name='返回大世界')
    @operation_node(name='点击菜单')
    def click_menu(self) -> OperationRoundResult:
        """
        在大世界画面 点击菜单的按钮
        :return:
        """
        click = self.round_by_click_area('大世界', '菜单')
        if click.is_success:
            return self.round_success(wait=2)
        else:
            return self.round_retry(wait=1)


if __name__ == '__main__':
    ctx = WContext()
    op = OpenMenu(ctx)
    op._init_before_execute()
    pass