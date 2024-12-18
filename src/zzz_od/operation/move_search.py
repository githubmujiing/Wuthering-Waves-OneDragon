import random
import time

from one_dragon.base.operation.operation_edge import node_from
from one_dragon.base.operation.operation_node import operation_node
from one_dragon.base.operation.operation_round_result import OperationRoundResult
from one_dragon.utils.i18_utils import gt
from zzz_od.context.zzz_context import WContext
from zzz_od.operation.zzz_operation import WOperation


class MoveSearch(WOperation):

    def __init__(self, ctx: WContext, find_text: str = '领取'):
        WOperation.__init__(self, ctx, op_name=gt('移动寻找并领取奖励', 'ui'))
        self.target_y = None
        self.target_x = None
        self.find_text = find_text
        self.fail_count = 0

    @node_from(from_name='四处找找')
    @node_from(from_name='移动')
    @operation_node(name='画面识别', is_start_node=True)
    def start(self) -> OperationRoundResult:
        screen = self.screenshot()
        area = self.ctx.screen_loader.get_area('大世界', '交互框')
        result = self.round_by_ocr_and_click(screen, self.find_text, area)
        if result.is_success:
            return self.round_success()
        else:
            return self.round_success(status='无交互框')

    @node_from(from_name='画面识别', status='无交互框')
    @operation_node(name='识别奖励方位')
    def search_reward(self) -> OperationRoundResult:
        screen = self.screenshot()
        find_result = self.round_find_area_position(screen, "大世界", '奖励')
        print(f'结果是 {find_result.status}')

        # 提取坐标
        start_index = find_result.status.find('(')  # 查找 '(' 的位置
        end_index = find_result.status.find(')')  # 查找 ')' 的位置
        if start_index != -1 and end_index != -1:
            # 提取括号中的部分
            coordinates_str = find_result.status[start_index + 1:end_index]
            # 以逗号分隔并提取x和y的值
            x_str, y_str = coordinates_str.split(',')
            # 去掉可能的空格并转换为整数
            self.target_x = int(x_str.strip())
            self.target_y = int(y_str.strip())
        else:
            return self.round_success(status='无奖励无交互')
        print(f'target_x: {self.target_x},target_y: {self.target_y}')
        return self.round_success()

    @node_from(from_name='识别奖励方位', success=True)
    @operation_node(name='移动')
    def move(self) -> OperationRoundResult:
        if self.target_x < 986:
            self.ctx.controller.move_a(press=True, press_time=1.5)
        elif self.target_x > 1642:
            self.ctx.controller.move_d(press=True, press_time=1.5)
        elif self.target_y > 1100 or self.target_y < 620:
            self.ctx.controller.move_s(press=True, press_time=0.1, release=True)
            time.sleep(0.5)
            self.ctx.controller.lock(press=True, press_time=1, release=True)
            time.sleep(1)
        else:
            self.ctx.controller.move_w(press=True, press_time=1.5)
        time.sleep(2)
        return self.round_success()

    @node_from(from_name='识别奖励方位', status='无奖励无交互')
    @operation_node(name='四处找找')
    def random_move(self) -> OperationRoundResult:
        if self.fail_count > 10:
            return self.round_fail()
        self.ctx.controller.lock(press=True, press_time=1, release=True)
        time.sleep(1)
        random_number = random.randint(1, 4)
        if random_number == 1:
            self.ctx.controller.move_a(press=True, press_time=0.5)
        elif random_number == 2:
            self.ctx.controller.move_d(press=True, press_time=0.5)
        elif random_number == 3:
            self.ctx.controller.move_w(press=True, press_time=0.5)
        elif random_number == 4:
            self.ctx.controller.move_s(press=True, press_time=0.5)
        time.sleep(2)
        self.fail_count += 1
        return self.round_success()




def __debug_op():
    ctx = WContext()
    ctx.init_by_config()
    ctx.ocr.init_model()
    op = MoveSearch(ctx, '领取')
    ctx.start_running()
    op.execute()


if __name__ == '__main__':
    __debug_op()