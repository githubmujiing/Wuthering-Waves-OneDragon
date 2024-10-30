from typing import ClassVar

from one_dragon.base.operation.operation_edge import node_from
from one_dragon.base.operation.operation_node import operation_node
import threading
from one_dragon.utils.i18_utils import gt
from zzz_od.context.zzz_context import WContext
from zzz_od.operation.zzz_operation import WOperation
import time


class SearchInteract(WOperation):

    def __init__(self, ctx: WContext, find_text: str = '启动', circles: int = 5):
        WOperation.__init__(self, ctx, op_name=gt('寻找并交互', 'ui'))
        self.find_text = find_text
        self.circles = circles

    @operation_node(name='画面识别', is_start_node=True)
    def start(self):
        stop_event = threading.Event()
        # 启动方法A的线程
        thread_a = threading.Thread(target=self.search, args=(stop_event,))
        thread_a.start()
        screen = self.screenshot()
        area = self.ctx.screen_loader.get_area('大世界', '交互框')
        result = self.round_by_ocr_and_click(screen, self.find_text, area)
        while not result.is_success:
            screen = self.screenshot()
            area = self.ctx.screen_loader.get_area('大世界', '交互框')
            result = self.round_by_ocr_and_click(screen, self.find_text, area)
        stop_event.set()  # 设置停止事件
        thread_a.join()  # 等待线程A结束
        if result.is_success:
            return self.round_success()


    # 转圈
    def search(self, stop_event):
        length = 1  # 初始步长
        for i in range(self.circles):
            # 每圈走四个方向，顺时针顺序
            self.ctx.controller.move_d(press=True, press_time=length, release=True)
            if stop_event.is_set():
                return  # 如果已设置停止标志，则返回
            self.ctx.controller.move_w(press=True, press_time=length, release=True)
            if stop_event.is_set():
                return  # 如果已设置停止标志，则返回
            length += 1  # 每圈步长增加
            self.ctx.controller.move_a(press=True, press_time=length, release=True)
            if stop_event.is_set():
                return  # 如果已设置停止标志，则返回
            self.ctx.controller.move_s(press=True, press_time=length, release=True)
            if stop_event.is_set():
                return  # 如果已设置停止标志，则返回
            length += 1  # 每圈步长增加
        return '找不到'



'''
    # 定义线程停止的标志
    stop_Search = threading.Event()
    stop_loop = False  # 用于退出循环的标志

    @operation_node(name='画面识别', is_start_node=True)
    def start(self):
        while not stop_loop:
            # 启动线程Search和interact
            thread_Search = threading.Thread(target=self.Search)
            thread_interact = threading.Thread(target=self.interact)

            thread_Search.start()
            thread_interact.start()

            # 等待线程interact结束
            thread_interact.join()

            # 确保Search线程也停止
            self.stop_Search.set()
            thread_Search.join()

        print("流程结束")

    # 转圈
    def Search(self, circles):
        length = 1  # 初始步长
        for i in range(circles):
            # 每圈走四个方向，顺时针顺序
            self.ctx.controller.move_d(press=True, press_time=length, release=True)
            self.ctx.controller.move_w(press=True, press_time=length, release=True)
            length += 1  # 每圈步长增加
            self.ctx.controller.move_a(press=True, press_time=length, release=True)
            self.ctx.controller.move_s(press=True, press_time=length, release=True)
            length += 1  # 每圈步长增加

    # 领取奖励
    def interact(self):
        global stop_loop
        while not stop_loop:
            print("执行领取奖励中...")
            screen = self.screenshot()
            area = self.ctx.screen_loader.get_area('大世界', '交互框')
            i_result = self.round_by_ocr(screen, self.find_text, area)
            if i_result.is_success:
                print("检测交互成功，停止寻找，执行点击")
                self.stop_Search.set()  # 停止Search线程
                success_C = self.round_by_ocr_and_click(screen, self.find_text, area)
                if success_C.is_success:
                    print("点击成功，退出循环")
                    stop_loop = True
                else:
                    print("操作C失败，重新执行Search和interact")
                    self.stop_Search.clear()  # 重新允许Search运行
            else:
                print("操作interact检测失败，重新执行Search和interact")
                self.stop_Search.clear()  # 重新允许Search运行
        '''




def __debug_op():
    ctx = WContext()
    ctx.init_by_config()
    ctx.ocr.init_model()
    op = SearchInteract(ctx, '激活', 4)
    ctx.start_running()
    op.execute()


if __name__ == '__main__':
    __debug_op()