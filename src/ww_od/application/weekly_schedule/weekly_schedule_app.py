from typing import List

# 尝试删除from one_dragon.base.geometry.point import Point
# 尝试删除from one_dragon.base.operation.operation_edge import node_from
from one_dragon.base.operation.operation_node import operation_node
from one_dragon.base.operation.operation_round_result import OperationRoundResult
from one_dragon.utils.i18_utils import gt
from ww_od.application.ww_application import WApplication
from ww_od.context.ww_context import WContext
# 尝试删除from ww_od.operation.arcade.arcade_snake_suicide import ArcadeSnakeSuicide
from ww_od.operation.back_to_normal_world import BackToNormalWorld
# 尝试删除from ww_od.operation.sola_guide.sola_guide_choose_tab import SolaGuideChooseTab
from ww_od.operation.sola_guide.opens_sola_guide import OpenSolaGuide
# 尝试删除from ww_od.operation.eat_noodle import EatNoodle


class WeeklyScheduleApp(WApplication):

    def __init__(self, ctx: WContext):
        WApplication.__init__(
            self,
            ctx=ctx, app_id='weekly_schedule',
            op_name=gt('每周行程，无用', 'ui'),
            run_record=ctx.weekly_schedule_record,
            retry_in_od=True,  # 传送落地有可能会歪 重试
        )
        self.to_choose_list: List[str] = ['前往电玩店玩2局游戏', '享用1碗拉面']
        self.to_choose_idx: int = 0

    def handle_init(self) -> None:
        """
        执行前的初始化 由子类实现
        注意初始化要全面 方便一个指令重复使用
        """
        self.to_choose_idx: int = 0

    @operation_node(name='索拉指南', is_start_node=True)
    def open_compendium(self) -> OperationRoundResult:
        op = OpenSolaGuide(self.ctx)
        return self.round_by_op_result(op.execute())



    #@node_from(from_name='点击领取')
    @operation_node(name='完成后返回')
    def finish(self) -> OperationRoundResult:
        op = BackToNormalWorld(self.ctx)
        return self.round_by_op_result(op.execute())


def __debug():
    ctx = WContext()
    ctx.init_by_config()
    app = WeeklyScheduleApp(ctx)
    app.execute()


if __name__ == '__main__':
    __debug()