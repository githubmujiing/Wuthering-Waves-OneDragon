
from datetime import datetime, timedelta
import time
from typing import ClassVar
import os

from one_dragon.base.operation.operation_node import operation_node
from one_dragon.base.operation.operation_round_result import OperationRoundResult
from ww_od.context.ww_context import WContext
from one_dragon.utils.i18_utils import gt
from ww_od.operation.ww_operation import WOperation

import subprocess


class AutomaticCombat(WOperation):

    STATUS_NOT_IN_MENU: ClassVar[str] = '未在菜单页面'

    def __init__(self, ctx: WContext):
        """
        识别画面 打开菜单
        由于使用了返回大世界 应可保证在任何情况下使用
        :param ctx:
        """
        WOperation.__init__(self, ctx,
                            op_name=gt('自动战斗', 'ui')
                            )



    @operation_node(name='启动战斗', is_start_node=True)
    def run_3rdparty(self) -> OperationRoundResult:
        # 启动 main.py
        relative_path = os.path.join('..', '..', '..', '3rdparty', 'ok-wuthering-waves', 'main.py')
        cwd = os.path.join('..', '..', '..', '3rdparty', 'ok-wuthering-waves')
        process = subprocess.run(['python', relative_path])
        #process = subprocess.Popen(['python', relative_path])
        return self.round_success()



def __debug_op():
    ctx = WContext()
    ctx.init_by_config()
    ctx.ocr.init_model()
    op = AutomaticCombat(ctx)
    ctx.start_running()
    op.execute()


if __name__ == '__main__':
    __debug_op()