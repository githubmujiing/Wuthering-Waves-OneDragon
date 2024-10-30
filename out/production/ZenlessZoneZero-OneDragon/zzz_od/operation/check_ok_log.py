import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def CheckOkLog(log_message):
    if "CombatCheck:out of combat start double check" in log_message:
        print("检测到 'CombatCheck:out of combat start double check' 信息，正在进行反应。")
        return True

# 示例日志信息
log_messages = [
    "2024-10-22 16:17:38,630 INFO TaskExecutor TaskExecutor:wait_until timeout <bound method CombatCheck.find_target_enemy ...",
    "2024-10-22 16:17:41,438 INFO TaskExecutor AutoPickTask:found Pick Up White List [吸收_1.00]",
    "2024-10-22 16:17:40,618 INFO TaskExecutor CombatCheck:out of combat start double check",
]

# 检查每条日志信息
for message in log_messages:
    CheckOkLog(message)
