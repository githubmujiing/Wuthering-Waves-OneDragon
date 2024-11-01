from PySide6.QtWidgets import QWidget
from qfluentwidgets import FluentIcon

from one_dragon.gui.component.column_widget import ColumnWidget
from one_dragon.gui.component.interface.vertical_scroll_interface import VerticalScrollInterface
from one_dragon.gui.component.setting_card.combo_box_setting_card import ComboBoxSettingCard
from zzz_od.application.battle_assistant.auto_battle_config import get_auto_battle_op_config_list
from zzz_od.application.coffee.coffee_config import CoffeeChooseWay, CoffeeChallengeWay, CoffeeCardNumEnum
from zzz_od.context.zzz_context import WContext


class CoffeePlanInterface(VerticalScrollInterface):

    def __init__(self, ctx: WContext, parent=None):
        self.ctx: WContext = ctx

        VerticalScrollInterface.__init__(
            self,
            object_name='zzz_coffee_plan_interface',
            content_widget=None, parent=parent,
            nav_text_cn='咖啡计划'
        )

    def get_content_widget(self) -> QWidget:
        content_widget = ColumnWidget()

        self.choose_way_opt = ComboBoxSettingCard(icon=FluentIcon.CALENDAR, title='咖啡选择', options_enum=CoffeeChooseWay,
                                                  show_config_desc=True)
        content_widget.add_widget(self.choose_way_opt)

        self.challenge_way_opt = ComboBoxSettingCard(icon=FluentIcon.GAME, title='喝后挑战', options_enum=CoffeeChallengeWay)
        content_widget.add_widget(self.challenge_way_opt)

        self.card_num_opt = ComboBoxSettingCard(icon=FluentIcon.GAME, title='体力计划外的数量', options_enum=CoffeeCardNumEnum,
                                                show_config_desc=True)
        content_widget.add_widget(self.card_num_opt)

        self.auto_battle_opt = ComboBoxSettingCard(icon=FluentIcon.GAME, title='自动战斗')
        content_widget.add_widget(self.auto_battle_opt)

        self.day_opt_1 = ComboBoxSettingCard(icon=FluentIcon.CALENDAR, title='星期一',
                                             options_list=self.ctx.compendium_service.get_coffee_config_list_by_day(1))
        content_widget.add_widget(self.day_opt_1)

        self.day_opt_2 = ComboBoxSettingCard(icon=FluentIcon.CALENDAR, title='星期二',
                                             options_list=self.ctx.compendium_service.get_coffee_config_list_by_day(2))
        content_widget.add_widget(self.day_opt_2)

        self.day_opt_3 = ComboBoxSettingCard(icon=FluentIcon.CALENDAR, title='星期三',
                                             options_list=self.ctx.compendium_service.get_coffee_config_list_by_day(3))
        content_widget.add_widget(self.day_opt_3)

        self.day_opt_4 = ComboBoxSettingCard(icon=FluentIcon.CALENDAR, title='星期四',
                                             options_list=self.ctx.compendium_service.get_coffee_config_list_by_day(4))
        content_widget.add_widget(self.day_opt_4)

        self.day_opt_5 = ComboBoxSettingCard(icon=FluentIcon.CALENDAR, title='星期五',
                                             options_list=self.ctx.compendium_service.get_coffee_config_list_by_day(5))
        content_widget.add_widget(self.day_opt_5)

        self.day_opt_6 = ComboBoxSettingCard(icon=FluentIcon.CALENDAR, title='星期六',
                                             options_list=self.ctx.compendium_service.get_coffee_config_list_by_day(6))
        content_widget.add_widget(self.day_opt_6)

        self.day_opt_7 = ComboBoxSettingCard(icon=FluentIcon.CALENDAR, title='星期日',
                                             options_list=self.ctx.compendium_service.get_coffee_config_list_by_day(7))
        content_widget.add_widget(self.day_opt_7)

        content_widget.add_stretch(1)

        return content_widget

    def on_interface_shown(self) -> None:
        VerticalScrollInterface.on_interface_shown(self)

        self.choose_way_opt.setValue(self.ctx.coffee_config.choose_way)
        self.challenge_way_opt.setValue(self.ctx.coffee_config.challenge_way)
        self.card_num_opt.setValue(self.ctx.coffee_config.card_num)
        self.auto_battle_opt.set_options_by_list(get_auto_battle_op_config_list('auto_battle'))
        self.auto_battle_opt.setValue(self.ctx.coffee_config.auto_battle)
        self.day_opt_1.setValue(self.ctx.coffee_config.day_coffee_1)
        self.day_opt_2.setValue(self.ctx.coffee_config.day_coffee_2)
        self.day_opt_3.setValue(self.ctx.coffee_config.day_coffee_3)
        self.day_opt_4.setValue(self.ctx.coffee_config.day_coffee_4)
        self.day_opt_5.setValue(self.ctx.coffee_config.day_coffee_5)
        self.day_opt_6.setValue(self.ctx.coffee_config.day_coffee_6)
        self.day_opt_7.setValue(self.ctx.coffee_config.day_coffee_7)

        # self._update_day_list_display()

        self.choose_way_opt.value_changed.connect(self._on_choose_way_changed)
        self.challenge_way_opt.value_changed.connect(self._on_challenge_way_changed)
        self.card_num_opt.value_changed.connect(self._on_card_num_changed)
        self.auto_battle_opt.value_changed.connect(self._on_auto_battle_changed)
        self.day_opt_1.value_changed.connect(self._on_day_1_changed)
        self.day_opt_2.value_changed.connect(self._on_day_2_changed)
        self.day_opt_3.value_changed.connect(self._on_day_3_changed)
        self.day_opt_4.value_changed.connect(self._on_day_4_changed)
        self.day_opt_5.value_changed.connect(self._on_day_5_changed)
        self.day_opt_6.value_changed.connect(self._on_day_6_changed)
        self.day_opt_7.value_changed.connect(self._on_day_7_changed)

    def on_interface_hidden(self) -> None:
        VerticalScrollInterface.on_interface_hidden(self)

        self.choose_way_opt.value_changed.disconnect(self._on_choose_way_changed)
        self.challenge_way_opt.value_changed.disconnect(self._on_challenge_way_changed)
        self.card_num_opt.value_changed.disconnect(self._on_card_num_changed)
        self.auto_battle_opt.value_changed.disconnect(self._on_auto_battle_changed)
        self.day_opt_1.value_changed.disconnect(self._on_day_1_changed)
        self.day_opt_2.value_changed.disconnect(self._on_day_2_changed)
        self.day_opt_3.value_changed.disconnect(self._on_day_3_changed)
        self.day_opt_4.value_changed.disconnect(self._on_day_4_changed)
        self.day_opt_5.value_changed.disconnect(self._on_day_5_changed)
        self.day_opt_6.value_changed.disconnect(self._on_day_6_changed)
        self.day_opt_7.value_changed.disconnect(self._on_day_7_changed)

    def _update_day_list_display(self) -> None:
        show_day_opt = self.ctx.coffee_config.choose_way == CoffeeChooseWay.CUSTOM.value.value
        self.day_opt_1.setVisible(show_day_opt)
        self.day_opt_2.setVisible(show_day_opt)
        self.day_opt_3.setVisible(show_day_opt)
        self.day_opt_4.setVisible(show_day_opt)
        self.day_opt_5.setVisible(show_day_opt)
        self.day_opt_6.setVisible(show_day_opt)
        self.day_opt_7.setVisible(show_day_opt)

    def _on_choose_way_changed(self, idx: int, value: str) -> None:
        self.ctx.coffee_config.choose_way = value
        self._update_day_list_display()

    def _on_challenge_way_changed(self, idx: int, value: str) -> None:
        self.ctx.coffee_config.challenge_way = value

    def _on_card_num_changed(self, idx: int, value: str) -> None:
        self.ctx.coffee_config.card_num = value

    def _on_auto_battle_changed(self, idx: int, value: str) -> None:
        self.ctx.coffee_config.auto_battle = value

    def _on_day_1_changed(self, idx: int, value: str) -> None:
        self.ctx.coffee_config.day_coffee_1 = value

    def _on_day_2_changed(self, idx: int, value: str) -> None:
        self.ctx.coffee_config.day_coffee_2 = value

    def _on_day_3_changed(self, idx: int, value: str) -> None:
        self.ctx.coffee_config.day_coffee_3 = value

    def _on_day_4_changed(self, idx: int, value: str) -> None:
        self.ctx.coffee_config.day_coffee_4 = value

    def _on_day_5_changed(self, idx: int, value: str) -> None:
        self.ctx.coffee_config.day_coffee_5 = value

    def _on_day_6_changed(self, idx: int, value: str) -> None:
        self.ctx.coffee_config.day_coffee_6 = value

    def _on_day_7_changed(self, idx: int, value: str) -> None:
        self.ctx.coffee_config.day_coffee_7 = value
