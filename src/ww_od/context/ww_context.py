from typing import Optional

from one_dragon.base.operation.one_dragon_context import OneDragonContext
from one_dragon.utils import i18_utils
from ww_od.application.kill_nutao.kill_nutao_run_recrd import KillNutaoRunRecord
from ww_od.application.organize_check_strength.organize_check_strength_run_recrd import OrganizeCheckStrengthRunRecord
from ww_od.application.synthesis.synthesis_run_record import SynthesisRunRecord


class WContext(OneDragonContext):

    def __init__(self, for_installer: bool = False):
        """
        :param for_installer: 给安装器用的
        """
        OneDragonContext.__init__(self, for_installer=for_installer)

        # 其它上下文
        if for_installer:
            return

        # 尝试删除from ww_od.context.hollow_context import HollowContext
        # 尝试删除self.hollow: HollowContext = HollowContext(self)

        from ww_od.config.yolo_config import YoloConfig
        from ww_od.game_data.compendium import CompendiumService
        from ww_od.game_data.map_area import MapAreaService

        # 基础配置
        self.yolo_config: YoloConfig = YoloConfig()

        # 游戏数据
        self.map_service: MapAreaService = MapAreaService()
        self.compendium_service: CompendiumService = CompendiumService()

        # 实例独有的配置
        self.load_instance_config()

    def init_by_config(self) -> None:
        """
        根据配置进行初始化
        :return:
        """
        OneDragonContext.init_by_config(self)
        i18_utils.update_default_lang(self.game_config.game_language)

        from ww_od.config.game_config import GamePlatformEnum
        from ww_od.controller.ww_pc_controller import ZPcController
        if self.game_config.platform == GamePlatformEnum.PC.value.value:
            self.controller = ZPcController(
                game_config=self.game_config,
                win_title=self.game_config.win_title,
                standard_width=self.project_config.screen_standard_width,
                standard_height=self.project_config.screen_standard_height
            )

        # 尝试删除self.hollow.data_service.reload()
        # 尝试删除self.init_hollow_config()
    '''# 尝试删除
    def init_hollow_config(self) -> None:
        """
        对空洞配置进行初始化
        :return:
        """
        from ww_od.hollow_zero.hollow_zero_challenge_config import HollowZeroChallengeConfig
        challenge_config = self.hollow_zero_config.challenge_config
        if challenge_config is None:
            self.hollow_zero_challenge_config = HollowZeroChallengeConfig('', is_mock=True)
        else:
            self.hollow_zero_challenge_config = HollowZeroChallengeConfig(challenge_config)
    '''
    def load_instance_config(self) -> None:
        OneDragonContext.load_instance_config(self)

        #from ww_od.application.battle_assistant.battle_assistant_config import BattleAssistantConfig
        from ww_od.application.charge_plan.charge_plan_config import ChargePlanConfig
        from ww_od.application.charge_plan.charge_plan_run_record import ChargePlanRunRecord
        from ww_od.application.Arrange_radio.Arrange_radio_run_record import ArrangeRadioRunRecord
        # 尝试删除from ww_od.application.coffee.coffee_config import CoffeeConfig
        # 尝试删除from ww_od.application.coffee.coffee_run_record import CoffeeRunRecord
        from ww_od.application.devtools.screenshot_helper.screenshot_helper_config import ScreenshotHelperConfig
        from ww_od.application.take_a_echo.take_a_echo_run_record import TakeAEchoRunRecord
        from ww_od.application.email_app.email_run_record import EmailRunRecord
        from ww_od.application.engagement_reward.engagement_reward_run_record import EngagementRewardRunRecord
        # 尝试删除from ww_od.application.hollow_zero.hollow_zero_config import HollowZeroConfig
        # 尝试删除from ww_od.application.hollow_zero.hollow_zero_run_record import HollowZeroRunRecord
        # 尝试删除from ww_od.application.life_on_line.life_on_line_config import LifeOnLineConfig
        # 尝试删除from ww_od.application.life_on_line.life_on_line_run_record import LifeOnLineRunRecord
        from ww_od.application.notorious_hunt.notorious_hunt_config import NotoriousHuntConfig
        from ww_od.application.notorious_hunt.notorious_hunt_run_record import NotoriousHuntRunRecord
        # 尝试删除from ww_od.application.random_play.random_play_run_record import RandomPlayRunRecord
        # 尝试删除from ww_od.application.scratch_card.scratch_card_run_record import ScratchCardRunRecord
        from ww_od.config.game_config import GameConfig
        # 尝试删除from ww_od.hollow_zero.hollow_zero_challenge_config import HollowZeroChallengeConfig
        from ww_od.application.redemption_code.redemption_code_run_record import RedemptionCodeRunRecord
        # 尝试删除from ww_od.application.commission_assistant.commission_assistant_config import CommissionAssistantConfig
        self.game_config: GameConfig = GameConfig(self.current_instance_idx)

        # 应用配置
        self.screenshot_helper_config: ScreenshotHelperConfig = ScreenshotHelperConfig(self.current_instance_idx)
        #self.battle_assistant_config: BattleAssistantConfig = BattleAssistantConfig(self.current_instance_idx)
        self.notorious_hunt_config: NotoriousHuntConfig = NotoriousHuntConfig(self.current_instance_idx)
        self.charge_plan_config: ChargePlanConfig = ChargePlanConfig(self.current_instance_idx)
        # 尝试删除self.hollow_zero_config: HollowZeroConfig = HollowZeroConfig(self.current_instance_idx)
        # 尝试删除self.hollow_zero_challenge_config: Optional[HollowZeroChallengeConfig] = None
        # 尝试删除self.init_hollow_config()
        # 尝试删除self.coffee_config: CoffeeConfig = CoffeeConfig(self.current_instance_idx)
        # 尝试删除self.life_on_line_config: LifeOnLineConfig = LifeOnLineConfig(self.current_instance_idx)
        # 尝试删除self.commission_assistant_config: CommissionAssistantConfig = CommissionAssistantConfig(self.current_instance_idx)
        # 尝试删除from ww_od.application.random_play.random_play_config import RandomPlayConfig
        # 尝试删除self.random_play_config: RandomPlayConfig = RandomPlayConfig(self.current_instance_idx)

        # 运行记录
        game_refresh_hour_offset = self.game_config.game_refresh_hour_offset
        self.take_a_echo_run_record: TakeAEchoRunRecord = TakeAEchoRunRecord(self.current_instance_idx, game_refresh_hour_offset)
        self.take_a_echo_run_record.check_and_update_status()
        self.kill_nutao_run_record: KillNutaoRunRecord = KillNutaoRunRecord(self.current_instance_idx, game_refresh_hour_offset)
        self.kill_nutao_run_record.check_and_update_status()
        self.email_run_record: EmailRunRecord = EmailRunRecord(self.current_instance_idx, game_refresh_hour_offset)
        self.email_run_record.check_and_update_status()
        self.synthesis_run_record: SynthesisRunRecord = SynthesisRunRecord(self.current_instance_idx, game_refresh_hour_offset)
        self.synthesis_run_record.check_and_update_status()
        self.organize_check_strength_run_record: OrganizeCheckStrengthRunRecord = OrganizeCheckStrengthRunRecord(self.current_instance_idx, game_refresh_hour_offset)
        self.organize_check_strength_run_record.check_and_update_status()
        self.charge_plan_run_record: ChargePlanRunRecord = ChargePlanRunRecord(self.current_instance_idx, game_refresh_hour_offset)
        self.charge_plan_run_record.check_and_update_status()
        self.engagement_reward_run_record: EngagementRewardRunRecord = EngagementRewardRunRecord(self.current_instance_idx, game_refresh_hour_offset)
        self.engagement_reward_run_record.check_and_update_status()
        self.notorious_hunt_record: NotoriousHuntRunRecord = NotoriousHuntRunRecord(self.current_instance_idx, game_refresh_hour_offset)
        self.notorious_hunt_record.check_and_update_status()
        self.city_fund_record: ArrangeRadioRunRecord = ArrangeRadioRunRecord(self.current_instance_idx, game_refresh_hour_offset)
        self.city_fund_record.check_and_update_status()
        self.redemption_code_record: RedemptionCodeRunRecord = RedemptionCodeRunRecord(self.current_instance_idx, game_refresh_hour_offset)
        self.redemption_code_record.check_and_update_status()

        from ww_od.application.weekly_schedule.weekly_schedule_run_record import WeeklyScheduleRunRecord
        self.weekly_schedule_record: WeeklyScheduleRunRecord = WeeklyScheduleRunRecord(self.current_instance_idx, game_refresh_hour_offset)
        self.weekly_schedule_record.check_and_update_status()
