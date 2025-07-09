import requests

from datetime import datetime, timedelta
from ww_od.context.zzz_context import WContext
from ww_od.operation.zzz_operation import WOperation
from one_dragon.utils.i18_utils import gt


def report_activity(account, webhook, activity):
    activity_value = int(activity)  # 将 activity 转换为整数类型
    if activity_value < 100:
        Printxt = f"{account}。\n取得活跃度{activity}。\n⚠⚠⚠每日任务未完成"  # 活跃度不足 100 时，添加提醒信息
    else:
        Printxt = f"{account}。\n取得活跃度{activity}"  # 活跃度达到或超过 100 时，仅显示完成信息
    URL = webhook
    mHeader = {'Content-Type': 'application/json; charset=UTF-8'}
    mBody = {
        "msgtype": "text",
        "text": {
            "content": Printxt
        }
    }
    # 注意：json=mBody  必须用json
    requests.post(url=URL, json=mBody, headers=mHeader)


def state_of_charge(account, webhook, charge):
    # 体力上限
    max_charge = 240
    # 每小时恢复体力
    charge_per_hour = 10
    # 剩余体力和总量的字符串
    remaining_text = f"体力剩余 {charge}/{max_charge}"
    # 计算回满所需时间（小时）
    hours_needed = (max_charge - charge) / charge_per_hour
    # 当前时间
    now = datetime.now()
    # 预计回满时间
    full_charge_time = now + timedelta(hours=hours_needed)
    # 格式化预计回满时间的字符串
    if full_charge_time.date() == now.date():
        full_charge_text = f"预计今天 {full_charge_time.strftime('%H点%M分')} 回满"
    else:
        full_charge_text = f"预计明天 {full_charge_time.strftime('%H点%M分')} 回满"
    # 构造发送内容
    Printxt = f"{account}。\n{remaining_text}\n{full_charge_text}"
    URL = webhook
    mHeader = {'Content-Type': 'application/json; charset=UTF-8'}
    mBody = {
        "msgtype": "text",
        "text": {
            "content": Printxt
        }
    }
    # 发送请求
    requests.post(url=URL, json=mBody, headers=mHeader)


def test_webhook(webhook):
    # 测试消息内容
    test_message = "这是一条来自鸣潮一条龙的测试消息"
    # 构造发送内容
    mHeader = {'Content-Type': 'application/json; charset=UTF-8'}
    mBody = {
        "msgtype": "text",
        "text": {
            "content": test_message
        }
    }
    # 发送请求
    response = requests.post(url=webhook, json=mBody, headers=mHeader)
    # 检查响应状态码
    if response.status_code == 200:
        print("测试消息已成功发送，Webhook 地址正确。")
    else:
        print(f"发送失败，状态码：{response.status_code}。请检查 Webhook 地址。")



def __debug():
    ctx = WContext()
    ctx.init_by_config()
    ctx.start_running()
    ctx.ocr.init_model()
    report_activity('账号', 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=5619540f-48ed-4a21-883a-d0121c4002e2',
                    activity=10)
    state_of_charge('账号', 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=5619540f-48ed-4a21-883a-d0121c4002e2',
                    charge=20)
    test_webhook('https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=5619540f-48ed-4a21-883a-d0121c4002e2')


if __name__ == '__main__':
    __debug()
