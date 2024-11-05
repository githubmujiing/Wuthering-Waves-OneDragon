import time
from datetime import datetime, timedelta

from one_dragon.base.operation.operation_node import operation_node
from one_dragon.base.operation.operation_round_result import OperationRoundResult
from zzz_od.context.zzz_context import WContext
from zzz_od.operation.zzz_operation import WOperation
from one_dragon.utils.i18_utils import gt


class MonitorBottleBySuccess(WOperation):


    def __init__(self, ctx: WContext):
        """
        监控战斗是否结束 不断锁定
        :param ctx:
        """
        WOperation.__init__(self, ctx,
                            op_name=gt('监控自动战斗by挑战成功', 'ui')
                            )

    #有 挑战达成和挑战成功

    @operation_node(name='监控', is_start_node=True)
    def monitor_bottle_by_success(self) -> OperationRoundResult:
        time.sleep(2)
        screen = self.screenshot()
        area = self.ctx.screen_loader.get_area('战斗', '挑战成功')
        result = self.round_by_ocr(screen, '挑战', area=area)
        print('一段识别')
        lock = 0
        start_time = datetime.now()
        while not result.is_success:
            current_time = datetime.now()
            # 计算当前时间与开始时间的差值
            if current_time - start_time >= timedelta(minutes=5):
                print('超时')
                break
            screen = self.screenshot()
            result = self.round_by_ocr(screen, '挑战成功', area=area, retry_wait=0.1)
            area_fail = self.ctx.screen_loader.get_area('战斗', '领取后选择')
            result_fail = self.round_by_ocr_and_click(screen, '退出副本', area=area_fail, success_wait=1)
            if result_fail.is_success:
                return self.round_success(status='全员死亡')
            result_fail = self.round_by_ocr_and_click(screen, '复苏', area=area_fail, success_wait=1)
            if result_fail.is_success:
                return self.round_success(status='全员死亡')
            lock += 1
            if lock % 40 == 0:
                self.ctx.controller.lock()
                #print('执行锁定')
            if result.is_success:
                print('挑战成功识别')
                return result
        return result




def __debug_op():
    ctx = WContext()
    ctx.init_by_config()
    ctx.ocr.init_model()
    op = MonitorBottleBySuccess(ctx)
    ctx.start_running()
    op.execute()


if __name__ == '__main__':
    __debug_op()