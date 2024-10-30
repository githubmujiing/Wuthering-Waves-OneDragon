import time
from datetime import datetime, timedelta

from one_dragon.base.operation.operation_node import operation_node
from one_dragon.base.operation.operation_round_result import OperationRoundResult
from zzz_od.context.zzz_context import WContext
from zzz_od.operation.zzz_operation import WOperation
from one_dragon.utils.i18_utils import gt


class MonitorBottleByBoss(WOperation):


    def __init__(self, ctx: WContext, boss:str = '云闪之鳞'):
        """
        监控战斗是否结束 不断锁定
        :param ctx:
        """
        WOperation.__init__(self, ctx,
                            op_name=gt('监控自动战斗by boss名', 'ui')
                            )
        self.boss = boss

    @operation_node(name='监控', is_start_node=True)
    def monitor_bottle_by_boss(self) -> OperationRoundResult:
        time.sleep(2)

        count = 0
        start_time = datetime.now()
        while count < 20:
            current_time = datetime.now()
            if current_time - start_time >= timedelta(minutes=5):
                print('超时')
                break
            screen = self.screenshot()
            area = self.ctx.screen_loader.get_area('战斗', 'boss名')
            result = self.round_by_ocr(screen, self.boss, area=area, success_wait=0.5, retry_wait=0.5)
            if result.is_success:
                count = 0
            else:
                count += 1
            print(count)

        return self.round_success()




def __debug_op():
    ctx = WContext()
    ctx.init_by_config()
    ctx.ocr.init_model()
    op = MonitorBottleByBoss(ctx, boss='云闪之鳞')
    ctx.start_running()
    op.execute()


if __name__ == '__main__':
    __debug_op()