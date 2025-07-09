from one_dragon.base.operation.operation_edge import node_from
from one_dragon.base.operation.operation_node import operation_node
from one_dragon.base.operation.operation_round_result import OperationRoundResult
from one_dragon.utils.i18_utils import gt
from ww_od.context.zzz_context import WContext
from ww_od.operation.back_to_normal_world import BackToNormalWorld
from ww_od.operation.sola_guide.sola_guide_choose_category import SolaGuideChooseCategory
from ww_od.operation.sola_guide.sola_guide_choose_mission_type import SolaGuideChooseMissionType
from ww_od.operation.sola_guide.sola_guide_choose_tab import SolaGuideChooseTab
from ww_od.operation.sola_guide.opens_sola_guide import OpenSolaGuide
from ww_od.operation.zzz_operation import WOperation


class TransportBySolaGuide(WOperation):

    def __init__(self, ctx: WContext, tab_name: str, category_name: str, mission_type_name: str):
        """
        使用索拉指南传送 最后会等待加载完毕
        :param ctx:
        tab_name: str:副本类型
        category_name: str:副本名称
        mission_type_name: str:
        """
        WOperation.__init__(
            self, ctx,
            op_name='%s %s %s-%s-%s' % (
                gt('传送'),
                gt('索拉指南'),
                gt(tab_name), gt(category_name), gt(mission_type_name)
            )
        )

        self.tab_name: str = tab_name
        self.category_name: str = category_name
        self.mission_type_name: str = mission_type_name

        if self.mission_type_name == '自定义模板':  # 没法直接传送到自定义
            self.mission_type_name: str = '模拟领域'

    @operation_node(name='索拉指南', is_start_node=True)
    def open_sola_guide(self) -> OperationRoundResult:
        op = OpenSolaGuide(self.ctx)
        return self.round_by_op_result(op.execute())

    @node_from(from_name='索拉指南')
    @operation_node(name='选择TAB')
    def choose_tab(self) -> OperationRoundResult:
        op = SolaGuideChooseTab(self.ctx, self.tab_name)
        return self.round_by_op_result(op.execute())

    @node_from(from_name='选择TAB')
    @operation_node(name='选择分类')
    def choose_category(self) -> OperationRoundResult:
        op = SolaGuideChooseCategory(self.ctx, self.category_name)
        return self.round_by_op_result(op.execute())

    @node_from(from_name='选择分类')
    @operation_node(name='选择副本分类')
    def choose_mission_type(self) -> OperationRoundResult:
        op = SolaGuideChooseMissionType(self.ctx, self.mission_type_name)
        return self.round_by_op_result(op.execute())

    @node_from(from_name='选择副本分类')
    @operation_node(name='等待传送加载完毕', node_max_retry_times=60)
    def wait_for_tp_complete(self) -> OperationRoundResult:
        op = BackToNormalWorld(self.ctx)
        self.round_by_op_result(op.execute())
        screen = self.screenshot()
        result = self.round_by_find_area(screen, '大世界', '多人游戏', retry_wait_round=1)
        if result.is_success:
            return result
        else:
            return self.round_retry()



def __debug():
    ctx = WContext()
    ctx.init_by_config()
    ctx.ocr.init_model()
    ctx.start_running()
    op = TransportBySolaGuide(ctx, '周期挑战', '无音清剿', '虎口山脉无音区')
    op.execute()


if __name__ == '__main__':
    __debug()
