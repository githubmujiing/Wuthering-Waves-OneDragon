import time

from typing import Optional, ClassVar

from one_dragon.base.geometry.point import Point
from one_dragon.base.operation.operation_base import OperationResult
from one_dragon.base.operation.operation_edge import node_from
from one_dragon.base.operation.operation_node import operation_node
from one_dragon.base.operation.operation_round_result import OperationRoundResult
from one_dragon.utils import cv2_utils, str_utils
from one_dragon.utils.i18_utils import gt
from zzz_od.application.charge_plan.charge_plan_config import ChargePlanItem
from zzz_od.application.notorious_hunt.notorious_hunt_config import NotoriousHuntLevelEnum
# 尝试删除from zzz_od.auto_battle import auto_battle_utils
# 尝试删除from zzz_od.auto_battle.auto_battle_operator import AutoBattleOperator
from zzz_od.context.zzz_context import WContext
from zzz_od.operation.zzz_operation import WOperation


class NotoriousHunt(WOperation):

    STATUS_NO_LEFT_TIMES: ClassVar[str] = '没有剩余次数'

    def __init__(self, ctx: WContext, plan: ChargePlanItem,
                 ):
        """
        使用索拉指南传送后
        用这个进行挑战
        :param ctx:
        """
        WOperation.__init__(
            self, ctx,
            op_name='%s %s' % (
                gt('周本'),
                gt(plan.mission_type_name)
            )
        )

        self.plan: ChargePlanItem = plan
        # 尝试删除self.auto_op: Optional[AutoBattleOperator] = None

    def handle_init(self) -> None:
        """
        执行前的初始化 由子类实现
        注意初始化要全面 方便一个指令重复使用
        """
        self.charge_left: Optional[int] = None
        self.charge_need: Optional[int] = None

    @operation_node(name='等待入口加载', is_start_node=True, node_max_retry_times=60)
    def wait_entry_load(self) -> OperationRoundResult:
        screen = self.screenshot()
        r1 = self.round_by_find_area(screen, '周本', '当期剩余奖励次数')
        if r1.is_success:
            return self.round_success(r1.status)

        r2 = self.round_by_find_area(screen, '周本', '剩余奖励次数')
        if r2.is_success:
            self.round_by_click_area('菜单', '返回')
            return self.round_wait(r2.status, wait=1)

        return self.round_retry(r1.status, wait=1)

    '''
    @node_from(from_name='等待入口加载')
    @operation_node(name='识别剩余次数')
    def check_left_times(self) -> OperationRoundResult:
        screen = self.screenshot()
        area = self.ctx.screen_loader.get_area('周本', '剩余次数')
        part = cv2_utils.crop_image_only(screen, area.rect)

        ocr_result = self.ctx.ocr.run_ocr_single_line(part)
        left_times = str_utils.get_positive_digits(ocr_result, None)

        if left_times is None:
            return self.round_retry('未能识别剩余次数', wait_round_time=1)
        elif left_times == 0:
            self.ctx.notorious_hunt_record.left_times = 0
            return self.round_success(NotoriousHunt.STATUS_NO_LEFT_TIMES)
        else:
            self.ctx.notorious_hunt_record.left_times = left_times
            self.can_run_times = min(left_times, self.plan.plan_times - self.plan.run_times)
            return self.round_success()

    @node_from(from_name='识别剩余次数')
    @operation_node(name='选择副本')
    def choose_mission(self) -> OperationRoundResult:
        screen = self.screenshot()
        area = self.ctx.screen_loader.get_area('周本', '副本名称列表')
        part = cv2_utils.crop_image_only(screen, area.rect)

        ocr_result_map = self.ctx.ocr.run_ocr(part)
        for ocr_result, mrl in ocr_result_map.items():
            if str_utils.find_by_lcs(gt(self.plan.mission_type_name), ocr_result, percent=0.5):
                to_click = mrl.max.center + area.left_top + Point(0, 100)
                if self.ctx.controller.click(to_click):
                    return self.round_success(wait=2)

        return self.round_retry(f'未能识别{self.plan.mission_type_name}', wait_round_time=1)

    @node_from(from_name='选择副本')
    @operation_node(name='选择难度')
    def choose_level(self) -> OperationRoundResult:
        if self.plan.level == NotoriousHuntLevelEnum.DEFAULT.value.value:
            return self.round_success()

        self.round_by_click_area('周本', '难度选择入口')
        time.sleep(1)

        screen = self.screenshot()
        area = self.ctx.screen_loader.get_area('周本', '难度选择区域')
        result = self.round_by_ocr_and_click(screen, self.plan.level, area=area,
                                           success_wait=1)
        # 如果选择的是最高难度 那第一下有可能选中不到 多选一下兜底
        self.round_by_ocr_and_click(screen, self.plan.level, area=area,
                                    success_wait=1)
        if result.is_success:
            return result
        else:
            return self.round_retry(result.status, wait=1)

    @node_from(from_name='选择难度')
    @operation_node(name='下一步')
    def click_next(self) -> OperationRoundResult:
        screen = self.screenshot()
        return self.round_by_find_and_click_area(
            screen, '模拟领域', '下一步',
            success_wait=1, retry_wait_round=1
        )

    @node_from(from_name='下一步')
    @operation_node(name='出战')
    def click_start(self) -> OperationRoundResult:
        screen = self.screenshot()
        return self.round_by_find_and_click_area(
            screen, '模拟领域', '出战',
            success_wait=1, retry_wait_round=1
        )

    @node_from(from_name='出战')
    @node_from(from_name='重新开始-确认')
    @operation_node(name='加载自动战斗指令')
    def init_auto_battle(self) -> OperationRoundResult:
        return auto_battle_utils.load_auto_op(self, 'auto_battle', self.plan.auto_battle_config)

    @node_from(from_name='加载自动战斗指令')
    @operation_node(name='等待战斗画面加载', node_max_retry_times=60)
    def wait_battle_screen(self) -> OperationRoundResult:
        screen = self.screenshot()
        return self.round_by_find_area(screen, '战斗画面', '按键-普通攻击', retry_wait_round=1)

    @node_from(from_name='等待战斗画面加载')
    @operation_node(name='移动交互')
    def move_and_interact(self) -> OperationRoundResult:
        if self.node_retry_times == 0:  # 第一次移动较远距离
            self.ctx.controller.move_w(press=True, press_time=1.2, release=True)
        else:
            self.ctx.controller.move_w(press=True, press_time=0.2, release=True)
        time.sleep(1)

        screen = self.screenshot()
        area = self.ctx.screen_loader.get_area('周本', '鸣徽交互区域')
        result = self.round_by_ocr(screen, '鸣徽', area=area)
        if result.is_success:
            self.ctx.controller.interact(press=True, press_time=0.2, release=True)
            time.sleep(2)
            return self.round_success()
        else:
            return self.round_retry(result.status)

    @node_from(from_name='移动交互')
    @operation_node(name='选择')
    def choose_buff(self) -> OperationRoundResult:
        screen = self.screenshot()

        return self.round_by_find_and_click_area(screen, '周本', '选择',
                                                 success_wait=1, retry_wait_round=1)

    @node_from(from_name='选择')
    @operation_node(name='向前移动准备战斗')
    def move_to_battle(self) -> OperationRoundResult:
        self.ctx.controller.move_w(press=True, press_time=3, release=True)
        self.auto_op.start_running_async()
        return self.round_success()

    @node_from(from_name='向前移动准备战斗')
    @node_from(from_name='战斗失败', status='战斗结果-倒带')
    @operation_node(name='自动战斗')
    def auto_battle(self) -> OperationRoundResult:
        if self.auto_op.auto_battle_context.last_check_end_result is not None:
            auto_battle_utils.stop_running(self.auto_op)
            return self.round_success(status=self.auto_op.auto_battle_context.last_check_end_result)
        now = time.time()
        screen = self.screenshot()

        self.auto_op.auto_battle_context.check_battle_state(screen, now, check_battle_end_normal_result=True)

        return self.round_wait(wait=self.ctx.battle_assistant_config.screenshot_interval)

    @node_from(from_name='自动战斗', status='普通战斗-撤退')
    @operation_node(name='战斗失败')
    def battle_fail(self) -> OperationRoundResult:
        screen = self.screenshot()
        result = self.round_by_find_and_click_area(screen, '战斗画面', '战斗结果-倒带')

        if result.is_success:
            self.auto_op.auto_battle_context.last_check_end_result = None
            self.auto_op.start_running_async()
            return self.round_success(result.status, wait=1)

        result = self.round_by_find_and_click_area(screen, '战斗画面', '战斗结果-撤退')
        if result.is_success:
            return self.round_success(result.status, wait=1)

        return self.round_retry(result.status, wait=1)

    @node_from(from_name='战斗失败', status='战斗结果-撤退')
    @operation_node(name='战斗失败退出')
    def battle_fail_exit(self) -> OperationRoundResult:
        screen = self.screenshot()
        result = self.round_by_find_and_click_area(screen, '战斗画面', '战斗结果-退出')

        if result.is_success:  # 战斗失败 返回失败到外层 中断后续挑战
            return self.round_fail(result.status, wait=5)
        else:
            return self.round_retry(result.status, wait=1)

    @node_from(from_name='自动战斗')
    @operation_node(name='战斗结束')
    def after_battle(self) -> OperationRoundResult:
        self.can_run_times -= 1
        self.ctx.notorious_hunt_record.left_times = self.ctx.notorious_hunt_record.left_times - 1
        self.ctx.notorious_hunt_config.add_plan_run_times(self.plan)
        return self.round_success()

    @node_from(from_name='战斗结束')
    @operation_node(name='判断下一次')
    def check_next(self) -> OperationRoundResult:
        screen = self.screenshot()
        if self.can_run_times == 0:
            return self.round_by_find_and_click_area(screen, '战斗画面', '战斗结果-完成',
                                                     success_wait=5, retry_wait_round=1)
        else:
            return self.round_by_find_and_click_area(screen, '战斗画面', '战斗结果-再来一次',
                                                     success_wait=1, retry_wait_round=1)

    @node_from(from_name='判断下一次', status='战斗结果-再来一次')
    @operation_node(name='重新开始-确认')
    def restart_confirm(self) -> OperationRoundResult:
        screen = self.screenshot()
        return self.round_by_find_and_click_area(screen, '周本', '重新开始-确认',
                                                 success_wait=1, retry_wait_round=1)

    @node_from(from_name='判断下一次', status='战斗结果-完成')
    @operation_node(name='等待返回入口', node_max_retry_times=60)
    def wait_back_to_entry(self) -> OperationRoundResult:
        screen = self.screenshot()
        return self.round_by_find_area(
            screen, '周本', '剩余奖励次数',
            success_wait=1, retry_wait=1
        )
    '''

    def _on_pause(self, e=None):
        WOperation._on_pause(self, e)
        if self.auto_op is not None:
            self.auto_op.stop_running()

    def _on_resume(self, e=None):
        WOperation._on_resume(self, e)
        # 尝试删除auto_battle_utils.resume_running(self.auto_op)

    def after_operation_done(self, result: OperationResult):
        WOperation.after_operation_done(self, result)
        if self.auto_op is not None:
            self.auto_op.dispose()
            self.auto_op = None


def __debug():
    ctx = WContext()
    ctx.init_by_config()
    ctx.ocr.init_model()
    ctx.start_running()
    op = NotoriousHunt(ctx, ChargePlanItem(
        category_name='周本',
        mission_type_name='无序边境·余烬',
        level=NotoriousHuntLevelEnum.DEFAULT.value.value
    ))
    op.can_run_times = 1
    op.auto_op = None
    op.init_auto_battle()

    op.execute()


if __name__ == '__main__':
    __debug()
