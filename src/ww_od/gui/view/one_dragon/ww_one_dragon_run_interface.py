from one_dragon.base.operation.one_dragon_app import OneDragonApp
from one_dragon.gui.view.one_dragon.one_dragon_run_interface import OneDragonRunInterface
from ww_od.application.ww_one_dragon_app import WOneDragonApp
from ww_od.context.ww_context import WContext


class ZOneDragonRunInterface(OneDragonRunInterface):

    def __init__(self, ctx: WContext, parent=None):
        self.ctx: WContext = ctx
        OneDragonRunInterface.__init__(
            self,
            ctx=ctx,
            parent=parent,
            help_url='https://one-dragon.org/zzz/zh/docs/feat_one_dragon.html'
        )

    def get_one_dragon_app(self) -> OneDragonApp:
        return WOneDragonApp(self.ctx)
