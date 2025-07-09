from one_dragon.base.operation.operation_edge import node_from
from one_dragon.base.operation.operation_node import operation_node
from one_dragon.base.operation.operation_round_result import OperationRoundResult
from one_dragon.utils.i18_utils import gt
from zzz_od.application.zzz_application import WApplication
from zzz_od.context.zzz_context import WContext
from zzz_od.operation.back_to_normal_world import BackToNormalWorld
from zzz_od.operation.open_menu import OpenMenu


class ArrangeRadioApp(WApplication):

    def __init__(self, ctx: WContext):
        WApplication.__init__(
            self,
            ctx=ctx, app_id='Arrange_radio',
            op_name=gt('先约电台', 'ui'),
            run_record=ctx.city_fund_record
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
    @operation_node(name='点击先约电台')
    def click_fund(self) -> OperationRoundResult:
        screen = self.screenshot()
        area = self.ctx.screen_loader.get_area('菜单', '中部列表')
        return self.round_by_ocr_and_click(screen, '先约电台', area=area, success_wait=2, retry_wait=1)

    @node_from(from_name='点击先约电台')
    @operation_node(name='点击电台任务')
    def click_task(self) -> OperationRoundResult:
        return self.round_by_click_area('先约电台', '电台任务', success_wait=1, retry_wait=1)

    @node_from(from_name='点击电台任务')
    @operation_node(name='任务一键领取')
    def click_task_claim(self) -> OperationRoundResult:
        return self.round_by_click_area('先约电台', '一键领取', success_wait=3, retry_wait=1)

    @node_from(from_name='任务一键领取')
    @operation_node(name='点击内先约电台')
    def click_level(self) -> OperationRoundResult:
        self.round_by_click_area('先约电台', '先约电台', success_wait=1, retry_wait=1)
        return self.round_by_click_area('先约电台', '先约电台', success_wait=1, retry_wait=1)

    @node_from(from_name='点击内先约电台')
    @operation_node(name='点击一键领取')
    def click_level_claim(self) -> OperationRoundResult:
        self.round_by_click_area('先约电台', '一键领取', success_wait=2, retry_wait=1)
        self.round_by_click_area('先约电台', '一键领取', success_wait=2, retry_wait=1)
        return self.round_by_click_area('先约电台', '一键领取', success_wait=1, retry_wait=1)

    @node_from(from_name='点击一键领取')
    @node_from(from_name='点击一键领取', success=False)
    @operation_node(name='返回大世界')
    def back_to_world(self) -> OperationRoundResult:
        op = BackToNormalWorld(self.ctx)
        return self.round_by_op_result(op.execute())


def __debug():
    ctx = WContext()
    ctx.init_by_config()
    app = ArrangeRadioApp(ctx)
    app.execute()


if __name__ == '__main__':
    __debug()