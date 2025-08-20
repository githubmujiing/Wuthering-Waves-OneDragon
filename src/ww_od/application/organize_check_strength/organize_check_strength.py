from one_dragon.base.operation.operation_edge import node_from
from one_dragon.base.operation.operation_node import operation_node
from one_dragon.base.operation.operation_round_result import OperationRoundResult
from one_dragon.utils.i18_utils import gt
from ww_od.application.ww_application import WApplication
from ww_od.context.ww_context import WContext
from ww_od.operation.back_to_normal_world import BackToNormalWorld
from ww_od.operation.sola_guide.organize_check_strength import OrganizeCheckStrength as OrganizeCheck


class OrganizeCheckStrength(WApplication):

    def __init__(self, ctx: WContext):
        """
        使用结晶单质确保体力充足
        """
        WApplication.__init__(
            self,
            ctx=ctx, app_id='organize_check_strength',
            op_name=gt('使用结晶单质确保体力充足', 'ui'),
            run_record=ctx.organize_check_strength_run_record
        )

    def handle_init(self) -> None:
        """
        执行前的初始化 由子类实现
        注意初始化要全面 方便一个指令重复使用
        """
        pass

    @operation_node(name='整理与确定体力', is_start_node=True)
    def organize_check_strength(self) -> OperationRoundResult:
        op = OrganizeCheck(self.ctx)
        return self.round_by_op_result(op.execute())

    @node_from(from_name='整理与确定体力')
    @operation_node(name='返回大世界')
    def back_world(self) -> OperationRoundResult:
        op = BackToNormalWorld(self.ctx)
        op.execute()
        return self.round_success()


def __debug():
    ctx = WContext()
    ctx.init_by_config()
    ctx.ocr.init_model()
    ctx.start_running()
    op = OrganizeCheckStrength(ctx)
    op.execute()


if __name__ == '__main__':
    __debug()

