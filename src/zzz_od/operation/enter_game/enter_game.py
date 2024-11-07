import time

from one_dragon.base.operation.operation_edge import node_from
from one_dragon.base.operation.operation_node import operation_node
from one_dragon.base.operation.operation_round_result import OperationRoundResult
from one_dragon.utils.i18_utils import gt
from zzz_od.context.zzz_context import WContext
from zzz_od.operation.back_to_normal_world import BackToNormalWorld
from zzz_od.operation.zzz_operation import WOperation


class EnterGame(WOperation):

    def __init__(self, ctx: WContext):
        WOperation.__init__(self, ctx,
                            op_name=gt('进入游戏', 'ui')
                            )

    @node_from(from_name='选择账号登陆')
    @operation_node(name='画面识别', is_start_node=True, node_max_retry_times=60)
    def check_screen(self) -> OperationRoundResult:
        screen = self.screenshot()
        area = self.ctx.screen_loader.get_area('打开游戏', '点击连接')
        result = self.round_by_ocr(screen, '点击连接', area)
        if result.is_success:
            return self.round_success(result.status, wait=1)
        screen = self.screenshot()
        area = self.ctx.screen_loader.get_area('打开游戏', '登录')
        result = self.round_by_ocr_and_click(screen, '登录', area)
        area_fail = self.ctx.screen_loader.get_area('弹窗', '整体')
        result_fail1 = self.round_by_ocr(screen, '重新启动', area_fail)
        if result_fail1.is_success:
            return self.round_success(status='重新启动', wait=1)
        result_fail2 = self.round_by_ocr(screen, '网络异常', area_fail)
        if result_fail2.is_success:
            return self.round_success(status='重新启动', wait=1)

        if result.is_success:
            return self.round_retry(wait=1)
        return self.round_retry(wait=1)


    @node_from(from_name='画面识别', status='点击连接')
    @operation_node(name='选择账号登陆')
    def input_account_password(self) -> OperationRoundResult:
        if self.ctx.game_config.password == '':
            return self.round_fail('未配置手机号')

        self.round_by_click_area('打开游戏', '切换账号', success_wait=1)
        self.round_by_click_area('弹窗', '右选项', success_wait=6)
        self.round_by_click_area('打开游戏', '登入')
        time.sleep(1)
        self.round_by_click_area('打开游戏', '切换手机号')
        time.sleep(2)
        screen = self.screenshot()
        area = self.ctx.screen_loader.get_area('打开游戏', '选择手机号')
        print(self.ctx.game_config.password)
        result = self.round_by_ocr_and_click(screen, self.ctx.game_config.password, area, success_wait=2)
        print(result.status)
        if not result.is_success:
            return self.round_fail('找不到手机号')
        self.round_by_click_area('打开游戏', '登入')
        self.round_by_click_area('打开游戏', '登录', success_wait=8)
        screen = self.screenshot()
        return self.round_by_find_and_click_area(screen, '打开游戏', '点击连接',
                                                 success_wait=5, retry_wait=1)

    @node_from(from_name='选择账号登陆', status='点击连接')
    @operation_node(name='等待画面加载,进入大世界')
    def wait_game(self) -> OperationRoundResult:
        op = BackToNormalWorld(self.ctx)
        return self.round_by_op_result(op.execute())


def __debug():
    ctx = WContext()
    ctx.init_by_config()
    ctx.start_running()
    ctx.ocr.init_model()
    op = EnterGame(ctx)
    op.execute()


if __name__ == '__main__':
    __debug()
