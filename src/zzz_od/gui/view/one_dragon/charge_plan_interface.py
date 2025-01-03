from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget
from qfluentwidgets import PrimaryPushButton, FluentIcon, ComboBox, CaptionLabel, LineEdit, ToolButton
from typing import Optional

from one_dragon.gui.component.column_widget import ColumnWidget
from one_dragon.gui.component.interface.vertical_scroll_interface import VerticalScrollInterface
from one_dragon.gui.component.setting_card.multi_push_setting_card import MultiPushSettingCard, MultiLineSettingCard
from one_dragon.gui.component.setting_card.switch_setting_card import SwitchSettingCard
# 尝试删除from zzz_od.application.battle_assistant.auto_battle_config import get_auto_battle_op_config_list
from zzz_od.application.charge_plan.charge_plan_config import ChargePlanItem, TeamEnum # 尝试删除CardNumEnum,
from zzz_od.context.zzz_context import WContext

# 多线设置卡
class ChargePlanCard(MultiLineSettingCard):

    changed = Signal(int, ChargePlanItem)
    delete = Signal(int)
    move_up = Signal(int)

    def __init__(self, ctx: WContext,
                 idx: int, plan: ChargePlanItem):
        self.ctx: WContext = ctx
        self.idx: int = idx
        self.plan: ChargePlanItem = plan

        self.category_combo_box = ComboBox()
        self._init_category_combo_box()

        self.mission_type_combo_box = ComboBox()
        self._init_mission_type_combo_box()

        self.mission_combo_box = ComboBox()
        self._init_mission_combo_box()

        # 尝试删除self.card_num_box = ComboBox()
        # 尝试删除self._init_card_num_box()

        self.team_box = ComboBox()
        self._init_team_box()

        # 尝试删除self.auto_battle_combo_box = ComboBox()
        # 尝试删除self._init_auto_battle_box()

        run_times_label = CaptionLabel(text='已运行次数')
        self.run_times_input = LineEdit()
        self.run_times_input.setText(str(self.plan.run_times))
        self.run_times_input.textChanged.connect(self._on_run_times_changed)

        plan_times_label = CaptionLabel(text='计划次数')
        self.plan_times_input = LineEdit()
        self.plan_times_input.setText(str(self.plan.plan_times))
        self.plan_times_input.textChanged.connect(self._on_plan_times_changed)

        self.move_up_btn = ToolButton(FluentIcon.UP, None)
        self.move_up_btn.clicked.connect(self._on_move_up_clicked)
        self.del_btn = ToolButton(FluentIcon.DELETE, None)
        self.del_btn.clicked.connect(self._on_del_clicked)

        MultiLineSettingCard.__init__(
            self,
            icon=FluentIcon.CALENDAR,
            title='',
            line_list=[
                [
                    self.category_combo_box,
                    self.mission_type_combo_box,
                    self.mission_combo_box,
                    # 尝试删除self.card_num_box,
                    # 尝试删除self.auto_battle_combo_box,
                    self.team_box,
                ],
                [run_times_label,
                 self.run_times_input,
                 plan_times_label,
                 self.plan_times_input,
                 self.move_up_btn,
                 self.del_btn,
                 ]
            ]
        )

    def _init_category_combo_box(self) -> None:
        try:
            self.category_combo_box.currentIndexChanged.disconnect(self._on_category_changed)
        except Exception:
            pass

        category_list = self.ctx.compendium_service.get_charge_plan_category_list()
        self.category_combo_box.clear()
        target_category_text: Optional[str] = None
        for category in category_list:
            self.category_combo_box.addItem(text=category.ui_text, userData=category.value)
            if category.value == self.plan.category_name:
                target_category_text = category.ui_text

        # 添加自定义标签
        # self.category_combo_box.addItem("讨伐强敌和无音清剿需要在中心点放置借位信标", userData="custom_category")
        # 设置当前项为目标项（若存在），否则保持默认
        if target_category_text:
            self.category_combo_box.setCurrentText(target_category_text)
        self.category_combo_box.currentIndexChanged.connect(self._on_category_changed)
        # 原来的代码
        # self.category_combo_box.setCurrentText(target_category_text)
        # self.category_combo_box.currentIndexChanged.connect(self._on_category_changed)

    def _init_mission_type_combo_box(self) -> None:
        try:
            self.mission_type_combo_box.currentIndexChanged.disconnect(self._on_mission_type_changed)
        except Exception:
            pass

        config_list = self.ctx.compendium_service.get_charge_plan_mission_type_list(self.plan.category_name)
        self.mission_type_combo_box.clear()

        target_text: Optional[str] = None
        for config in config_list:
            self.mission_type_combo_box.addItem(text=config.ui_text, userData=config.value)
            if config.value == self.plan.mission_type_name:
                target_text = config.ui_text

        if target_text is None:
            self.mission_type_combo_box.setCurrentIndex(0)
            self.plan.mission_type_name = self.mission_type_combo_box.itemData(0)
        else:
            self.mission_type_combo_box.setCurrentText(target_text)

        self.mission_type_combo_box.currentIndexChanged.connect(self._on_mission_type_changed)

    def _init_mission_combo_box(self) -> None:
        try:
            self.mission_combo_box.currentIndexChanged.disconnect(self._on_mission_changed)
        except Exception:
            pass

        config_list = self.ctx.compendium_service.get_charge_plan_mission_list(
            self.plan.category_name, self.plan.mission_type_name)
        self.mission_combo_box.clear()

        target_text: Optional[str] = None
        for config in config_list:
            self.mission_combo_box.addItem(text=config.ui_text, userData=config.value)
            if config.value == self.plan.mission_name:
                target_text = config.ui_text

        if target_text is None:
            self.mission_combo_box.setCurrentIndex(0)
            self.plan.mission_name = self.mission_combo_box.itemData(0)
        else:
            self.mission_combo_box.setCurrentText(target_text)

        self.mission_combo_box.setVisible(self.plan.category_name == '模拟领域')
        self.mission_combo_box.currentIndexChanged.connect(self._on_mission_changed)

    '''# 尝试删除
    def _init_card_num_box(self) -> None:
        try:
            self.card_num_box.currentIndexChanged.disconnect(self._on_card_num_changed)
        except Exception:
            pass

        self.card_num_box.clear()

        target_text: Optional[str] = None
        for config_enum in CardNumEnum:
            config = config_enum.value
            self.card_num_box.addItem(text=config.ui_text, userData=config.value)
            if config.value == self.plan.card_num:
                target_text = config.ui_text

        if target_text is None:
            self.card_num_box.setCurrentIndex(0)
            self.plan.card_num = self.card_num_box.itemData(0)
        else:
            self.card_num_box.setCurrentText(target_text)

        self.card_num_box.setVisible(self.plan.category_name == '模拟领域')
        self.card_num_box.currentIndexChanged.connect(self._on_card_num_changed)
    '''

    def _init_team_box(self) -> None:
        try:
            self.team_box.currentIndexChanged.disconnect(self._on_team_changed)
        except Exception:
            pass

        self.team_box.clear()

        target_text: Optional[str] = None
        for config_enum in TeamEnum:
            config = config_enum.value
            self.team_box.addItem(text=config.ui_text, userData=config.value)
            if config.value == self.plan.team:
                target_text = config.ui_text

        if target_text is None:
            self.team_box.setCurrentIndex(0)
            self.plan.team = self.team_box.itemData(0)
        else:
            self.team_box.setCurrentText(target_text)

        # self.team_box.setVisible(self.plan.category_name == '模拟领域')#不设置可见性
        self.team_box.currentIndexChanged.connect(self._on_team_changed)

    '''# 尝试删除
    def _init_auto_battle_box(self) -> None:
        try:
            self.auto_battle_combo_box.currentIndexChanged.disconnect(self._on_auto_battle_changed)
        except Exception:
            pass

        # 尝试删除config_list = get_auto_battle_op_config_list(sub_dir='auto_battle')
        self.auto_battle_combo_box.clear()

        target_text: Optional[str] = None
        for config in config_list:
            self.auto_battle_combo_box.addItem(text=config.ui_text, userData=config.value)
            if config.value == self.plan.auto_battle_config:
                target_text = config.ui_text

        if target_text is None:
            self.auto_battle_combo_box.setCurrentIndex(0)
            self.plan.auto_battle_config = self.auto_battle_combo_box.itemData(0)
        else:
            self.auto_battle_combo_box.setCurrentText(target_text)

        self.auto_battle_combo_box.currentIndexChanged.connect(self._on_auto_battle_changed)
    '''
    def _on_category_changed(self, idx: int) -> None:
        category_name = self.category_combo_box.itemData(idx)
        self.plan.category_name = category_name

        self._init_mission_type_combo_box()
        self._init_mission_combo_box()
        # 尝试删除self._init_card_num_box()
        self._init_team_box()

        self._emit_value()

    def _on_mission_type_changed(self, idx: int) -> None:
        mission_type_name = self.mission_type_combo_box.itemData(idx)
        self.plan.mission_type_name = mission_type_name

        self._init_mission_combo_box()

        self._emit_value()

    def _on_mission_changed(self, idx: int) -> None:
        mission_name = self.mission_combo_box.itemData(idx)
        self.plan.mission_name = mission_name

        self._emit_value()

        # 尝试删除def _on_card_num_changed(self, idx: int) -> None:
        # 尝试删除self.plan.card_num = self.card_num_box.itemData(idx)
        # 尝试删除self._emit_value()

    '''# 尝试删除
    def _on_auto_battle_changed(self, idx: int) -> None:
        auto_battle = self.auto_battle_combo_box.itemData(idx)
        self.plan.auto_battle_config = auto_battle

        self._emit_value()
    '''

    def _on_team_changed(self, idx: int) -> None:
        self.plan.team = self.team_box.itemData(idx)
        self._emit_value()

    def _on_run_times_changed(self) -> None:
        self.plan.run_times = int(self.run_times_input.text())
        self._emit_value()

    def _on_plan_times_changed(self) -> None:
        self.plan.plan_times = int(self.plan_times_input.text())
        self._emit_value()

    def _emit_value(self) -> None:
        self.changed.emit(self.idx, self.plan)

    def _on_move_up_clicked(self) -> None:
        self.move_up.emit(self.idx)

    def _on_del_clicked(self) -> None:
        self.delete.emit(self.idx)


# 垂直滚动界面
class ChargePlanInterface(VerticalScrollInterface):

    def __init__(self, ctx: WContext, parent=None):
        self.ctx: WContext = ctx

        VerticalScrollInterface.__init__(
            self,
            object_name='zzz_charge_plan_interface',
            content_widget=None, parent=parent,
            nav_text_cn='体力计划'
        )

    def get_content_widget(self) -> QWidget:
        self.content_widget = ColumnWidget()

        self.plus_btn = PrimaryPushButton(text='新增')
        self.plus_btn.clicked.connect(self._on_add_clicked)
        self.content_widget.add_widget(self.plus_btn)

        return self.content_widget

    def update_plan_list_display(self):
        self.content_widget.clear_widgets()

        self.loop_opt = SwitchSettingCard(icon=FluentIcon.SYNC, title='循环执行', content='开启时 会循环执行到体力用尽')
        self.loop_opt.setValue(self.ctx.charge_plan_config.loop)
        self.loop_opt.value_changed.connect(self._on_loop_changed)
        self.content_widget.add_widget(self.loop_opt)

        for idx, plan_item in enumerate(self.ctx.charge_plan_config.plan_list):
            card = ChargePlanCard(self.ctx, idx, plan_item)
            card.changed.connect(self._on_plan_item_changed)
            card.delete.connect(self._on_plan_item_deleted)
            card.move_up.connect(self._on_plan_item_move_up)
            self.content_widget.add_widget(card)

        self.plus_btn = PrimaryPushButton(text='新增')
        self.plus_btn.clicked.connect(self._on_add_clicked)
        self.content_widget.add_widget(self.plus_btn)

        self.content_widget.add_stretch(1)

    def on_interface_shown(self) -> None:
        VerticalScrollInterface.on_interface_shown(self)
        self.update_plan_list_display()

    def on_interface_hidden(self) -> None:
        VerticalScrollInterface.on_interface_hidden(self)

    def _on_add_clicked(self) -> None:
        self.ctx.charge_plan_config.add_plan()
        self.update_plan_list_display()

    def _on_plan_item_changed(self, idx: int, plan: ChargePlanItem) -> None:
        self.ctx.charge_plan_config.update_plan(idx, plan)

    def _on_plan_item_deleted(self, idx: int) -> None:
        self.ctx.charge_plan_config.delete_plan(idx)
        self.update_plan_list_display()

    def _on_plan_item_move_up(self, idx: int) -> None:
        self.ctx.charge_plan_config.move_up(idx)
        self.update_plan_list_display()

    def _on_loop_changed(self, new_value: bool) -> None:
        self.ctx.charge_plan_config.loop = new_value