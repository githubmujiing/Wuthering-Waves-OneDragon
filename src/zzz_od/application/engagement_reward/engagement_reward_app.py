from typing import ClassVar

from one_dragon.base.operation.operation_edge import node_from
from one_dragon.base.operation.operation_node import operation_node
from one_dragon.base.operation.operation_round_result import OperationRoundResult
from one_dragon.utils import cv2_utils, str_utils
from one_dragon.utils.i18_utils import gt
from zzz_od.application.zzz_application import WApplication
from zzz_od.context.zzz_context import WContext
from zzz_od.operation.back_to_normal_world import BackToNormalWorld
from zzz_od.operation.report_message.report_message import report_activity
from zzz_od.operation.sola_guide.sola_guide_choose_tab import SolaGuideChooseTab
from zzz_od.operation.sola_guide.opens_sola_guide import OpenSolaGuide


class EngagementRewardApp(WApplication):

    STATUS_NO_REWARD: ClassVar[str] = '无奖励可领取'

    def __init__(self, ctx: WContext):
        """
        每天自动接收邮件奖励
        """
        WApplication.__init__(
            self,
            ctx=ctx, app_id='engagement_reward',
            op_name=gt('活跃度奖励', 'ui'),
            run_record=ctx.engagement_reward_run_record
        )
        self.liveness = None

    def handle_init(self) -> None:
        """
        执行前的初始化 由子类实现
        注意初始化要全面 方便一个指令重复使用
        """
        self.idx: int = 4

    @operation_node(name='索拉指南', is_start_node=True)
    def open_compendium(self) -> OperationRoundResult:
        op = OpenSolaGuide(self.ctx)
        return self.round_by_op_result(op.execute())

    @node_from(from_name='索拉指南')
    @operation_node(name='点击活跃度')
    def choose_train(self) -> OperationRoundResult:
        op = SolaGuideChooseTab(self.ctx, '活跃度')
        return self.round_by_op_result(op.execute(), wait=1)

    @node_from(from_name='点击活跃度')
    @operation_node(name='领取活跃度')
    def click_liveness(self) -> OperationRoundResult:
        reward_fail = 0
        screen = self.screenshot()
        area = self.ctx.screen_loader.get_area('活跃度', '领取活跃度')
        result = self.round_by_ocr(screen, '领取', area, success_wait=1, retry_wait=1)
        while reward_fail < 3:
            while result.is_success:
                screen = self.screenshot()
                area = self.ctx.screen_loader.get_area('活跃度', '领取活跃度')
                self.round_by_click_area('索拉指南tab', '活跃度', success_wait=1, retry_wait=1)
                self.round_by_ocr_and_click(screen, '领取', area, success_wait=1, retry_wait=1)
                result = self.round_by_ocr(screen, '领取', area, success_wait=1, retry_wait=1)
            else:
                result = self.round_by_ocr(screen, '领取', area, success_wait=1, retry_wait=1)
                reward_fail += 1
        return self.round_success()

    @node_from(from_name='领取奖励', status='识别活跃度失败')
    @node_from(from_name='领取活跃度')
    @operation_node(name='领取奖励')
    def check_reward(self) -> OperationRoundResult:
        screen = self.screenshot()
        area = self.ctx.screen_loader.get_area('活跃度', '活跃度')
        part = cv2_utils.crop_image_only(screen, area.rect)
        ocr_result = self.ctx.ocr.run_ocr_single_line(part)
        self.liveness = str_utils.get_positive_digits(ocr_result, None)
        if self.liveness is None:
            return self.round_retry(status='识别活跃度失败', wait=1)
        if self.liveness >= 100:
            self.round_by_click_area('活跃度', '领取每日100', success_wait=1)
        elif self.liveness >= 80:
            self.round_by_click_area('活跃度', '领取每日80', success_wait=1)
        elif self.liveness >= 60:
            self.round_by_click_area('活跃度', '领取每日60', success_wait=1)
        elif self.liveness >= 40:
            self.round_by_click_area('活跃度', '领取每日40', success_wait=1)
        elif self.liveness >= 20:
            self.round_by_click_area('活跃度', '领取每日20', success_wait=1)
        return self.round_success()

    @node_from(from_name='领取奖励')
    @operation_node(name='发送消息')
    def report_activity(self) -> OperationRoundResult:
        account = self.ctx.current_instance_idx
        report_activity(account, self.ctx.game_config.wechat_notification, self.liveness)
        return self.round_success()

    @node_from(from_name='发送消息')
    @operation_node(name='完成后返回大世界')
    def back_afterwards(self) -> OperationRoundResult:
        op = BackToNormalWorld(self.ctx)
        return self.round_by_op_result(op.execute())
    '''    
    @node_from(from_name='领取奖励')
    @operation_node(name='查看奖励结果')
    def check_reward(self) -> OperationRoundResult:
        screen = self.screenshot()
        return self.round_by_find_and_click_area(screen, '索拉指南', '活跃度奖励-确认', success_wait=1, retry_wait=1)

    @node_from(from_name='查看奖励结果', success=False)
    @node_from(from_name='识别活跃度', status=STATUS_NO_REWARD)
    @operation_node(name='完成后返回大世界')
    def back_afterwards(self) -> OperationRoundResult:
        op = BackToNormalWorld(self.ctx)
        return self.round_by_op_result(op.execute())
        
        '''


def __debug():
    ctx = WContext()
    ctx.init_by_config()
    ctx.ocr.init_model()
    ctx.start_running()
    op = EngagementRewardApp(ctx)
    op.execute()


if __name__ == '__main__':
    __debug()
