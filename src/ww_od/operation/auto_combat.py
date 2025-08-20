
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


        '''
        #使用exec
        if not os.path.isfile(relative_path):
            print(f"脚本文件不存在: {relative_path}")
            return

        # 读取脚本内容
        with open(relative_path, 'r', encoding='utf-8') as f:
            script_content = f.read()

        # 使用 exec 执行脚本内容
        exec(script_content)
        '''
        '''
        # ,三，还是不行
        # 启动子进程
        process = subprocess.Popen(
            ['python', relative_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,  # 设置为 1 可以逐行读取输出
            encoding='utf-8',  # 指定输出编码
            cwd=cwd
        )
        time.sleep(5)

        try:
            # 启动线程分别读取 stdout 和 stderr
            stdout_thread = threading.Thread(target=self.read_output, args=(process.stdout, 'stdout'))
            stderr_thread = threading.Thread(target=self.read_output, args=(process.stderr, 'stderr'))

            stdout_thread.start()
            stderr_thread.start()

            stdout_thread.join()
            stderr_thread.join()

            # 等待进程结束并获取返回值
            return_code = process.wait()
            print(f"进程结束，返回码：{return_code}")

        except KeyboardInterrupt:
            print("手动停止进程...")
            process.terminate()
    '''
        '''
        # # 处理日志方法二，依然没有后续输出
        # 启动子进程
        process = subprocess.Popen(
            ['python', relative_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,  # 设置为 1 可以逐行读取输出
            encoding='utf-8'  # 指定输出编码
        )
        time.sleep(5)

        try:
            # 读取第一行
            first_line = process.stdout.readline()
            if first_line:
                # 处理第一行过长的问题
                wrapped_first_line = textwrap.fill(first_line.strip(), width=80)  # 将第一行每行限制为80个字符
                print("第一行输出（已处理）：")
                print(wrapped_first_line)

            # 继续逐行读取后续的输出
            while True:
                output = process.stdout.readline()

                # 如果输出为空，说明进程结束
                if output == '' and process.poll() is not None:
                    break

                # 检查是否包含特定的日志信息
                if "INFO TaskExecutor CombatCheck:out of combat start double check" in output:
                    print("检测到日志信息，正在停止代码...")
                    # process.terminate()  # 停止子进程
                    # break

                # 打印后续输出
                if output:
                    print(output.strip())

            # 等待进程结束并获取返回值
            return_code = process.wait()
            print(f"进程结束，返回码：{return_code}")

        except KeyboardInterrupt:
            print("手动停止进程...")
            process.terminate()

        finally:
            process.stdout.close()
            process.stderr.close()
        '''
        '''
        # 处理日志方法一，第一行过长无法处理
        # 启动子进程
        process = subprocess.Popen(
            ['python', relative_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,  # 设置为 1 可以逐行读取输出
            #encoding='utf-8',  # 指定输出编码
            #cwd=cwd
        )

        try:
            while True:
                # 逐行读取输出
                output = process.stdout.readline()

                # 如果输出为空，说明进程结束
                if output == '' and process.poll() is not None:
                    break

                # 检查是否包含特定的日志信息
                if "INFO TaskExecutor CombatCheck:out of combat start double check" in output:
                    print("检测到日志信息，正在停止代码...")
                    # process.terminate()  # 停止子进程
                    # break

                # 打印输出
                if output:
                    print(output.strip())
                    pass
            # 等待进程结束并获取返回值
            return_code = process.wait()
            print(f"进程结束，返回码：{return_code}")

        except KeyboardInterrupt:
            print("手动停止进程...")
            process.terminate()
            sys.exit()

        finally:
            process.stdout.close()
            process.stderr.close()
        '''
        '''
        result = CheckOkLog(process)
        if result:
            process.terminate()
            return self.round_success()
        '''
        '''
        iteration = 0
        lock = 0
        while iteration < 300:
            # 执行 AAAB 的顺序
            for _ in range(5):
                time.sleep(1)
                screen = self.screenshot()
                d_result = self.round_by_find_area(screen,'战斗', '锁定框')
                if not d_result.is_success:
                    lock = 0
                    print('锁定框识别失败')
                    break
                l_result = self.round_by_find_area(screen, '战斗', '锁定状态')
                # 检查 B 的返回结果
                if l_result.is_success:
                    lock = 0
                    print('lock = 0')
                else:
                    lock += 1
                    print('lock += 1')
                if lock > 5:
                    break
                    print('lock > 5')
            if lock > 5:
                break
            iteration += 1
            # 等待 N 秒
            time.sleep(3)
    '''


        time.sleep(2)
        screen = self.screenshot()
        area = self.ctx.screen_loader.get_area('战斗', '挑战成功')
        result = self.round_by_ocr(screen, '挑战成功', area=area)
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
            lock += 1
            if lock % 40 == 0:
                self.ctx.controller.lock()
                #print('执行锁定')
            if result.is_success:
                process.terminate()
                print('挑战成功识别')
        # 终止进程
        process.terminate()  # 或者使用 process.kill() 强制终止
        #process.wait()        # 可选：等待进程结束并获取返回码
        return self.round_success()
        #return '战斗失败'
        #return '战斗胜利'



def __debug_op():
    ctx = WContext()
    ctx.init_by_config()
    ctx.ocr.init_model()
    op = AutomaticCombat(ctx)
    ctx.start_running()
    op.execute()


if __name__ == '__main__':
    __debug_op()