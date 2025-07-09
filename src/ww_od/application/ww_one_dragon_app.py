from typing import List

from one_dragon.base.operation.one_dragon_app import OneDragonApp
from ww_od.application.charge_plan.charge_plan_app import ChargePlanApp
from ww_od.application.Arrange_radio.Arrange_radio_app import ArrangeRadioApp
# 尝试删除from ww_od.application.coffee.coffee_app import CoffeeApp
from ww_od.application.email_app.email_app import EmailApp
from ww_od.application.engagement_reward.engagement_reward_app import EngagementRewardApp
from ww_od.application.kill_nutao.kill_nutao import KillNutao
# 尝试删除from ww_od.application.hollow_zero.hollow_zero_app import HollowZeroApp
# 尝试删除from ww_od.application.life_on_line.life_on_line_app import LifeOnLineApp
from ww_od.application.notorious_hunt.notorious_hunt_app import NotoriousHuntApp
# 尝试删除from ww_od.application.random_play.random_play_app import RandomPlayApp
from ww_od.application.redemption_code.redemption_code_app import RedemptionCodeApp
from ww_od.application.synthesis.synthesis_app import SynthesisApp
from ww_od.application.take_a_echo.take_a_echo import TakeAEcho
# 尝试删除from ww_od.application.scratch_card.scratch_card_app import ScratchCardApp
from ww_od.application.weekly_schedule.weekly_schedule_app import WeeklyScheduleApp
from ww_od.application.ww_application import WApplication
from ww_od.context.ww_context import WContext
from ww_od.operation.enter_game.open_and_enter_game import OpenAndEnterGame
from ww_od.operation.enter_game.switch_account import SwitchAccount


class WOneDragonApp(OneDragonApp, WApplication):

    def __init__(self, ctx: WContext):
        app_id = 'ww_one_dragon'
        op_to_enter_game = OpenAndEnterGame(ctx)
        op_to_switch_account = SwitchAccount(ctx)

        WApplication.__init__(self, ctx, app_id)
        OneDragonApp.__init__(self, ctx, app_id,
                              op_to_enter_game=op_to_enter_game,
                              op_to_switch_account=op_to_switch_account)

    def get_app_list(self) -> List[WApplication]:
        return [
            RedemptionCodeApp(self.ctx),
            WeeklyScheduleApp(self.ctx),
            TakeAEcho(self.ctx),
            KillNutao(self.ctx),
            EmailApp(self.ctx),
            SynthesisApp(self.ctx),
            # 尝试删除RandomPlayApp(self.ctx),
            # 尝试删除ScratchCardApp(self.ctx),
            # 尝试删除CoffeeApp(self.ctx),
            NotoriousHuntApp(self.ctx),
            ChargePlanApp(self.ctx),
            EngagementRewardApp(self.ctx),
            # 尝试删除HollowZeroApp(self.ctx),
            ArrangeRadioApp(self.ctx),
            # 尝试删除LifeOnLineApp(self.ctx),
        ]


def __debug():
    ctx = WContext()
    ctx.init_by_config()

    if ctx.env_config.auto_update:
        from one_dragon.utils.log_utils import log
        log.info('开始自动更新...')
        ctx.git_service.fetch_latest_code()

    app = WOneDragonApp(ctx)
    app.execute()

    from one_dragon.base.config.one_dragon_config import AfterDoneOpEnum
    if ctx.one_dragon_config.after_done == AfterDoneOpEnum.SHUTDOWN.value.value:
        from one_dragon.utils import cmd_utils
        cmd_utils.shutdown_sys(60)
    elif ctx.one_dragon_config.after_done == AfterDoneOpEnum.CLOSE_GAME.value.value:
        ctx.controller.close_game()


if __name__ == '__main__':
    __debug()