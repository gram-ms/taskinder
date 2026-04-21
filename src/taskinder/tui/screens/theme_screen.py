from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Footer, Label, ListItem, ListView


class ThemeScreen(ModalScreen[bool]):
    BINDINGS = [
        Binding("escape", "cancel", "Voltar"),
        Binding("j", "cursor_down", "Baixo", show=False),
        Binding("k", "cursor_up", "Cima", show=False),
        Binding("enter", "select_theme", "Aplicar"),
    ]

    DEFAULT_CSS = """
    ThemeScreen {
        align: center middle;
        background: $background 70%;
    }
    #theme-dialog {
        width: 44;
        height: auto;
        max-height: 36;
        background: $surface;
        border: heavy $primary;
        padding: 1 2;
    }
    #theme-heading {
        text-style: bold;
        color: $primary;
        text-align: center;
        margin-bottom: 1;
    }
    #theme-list {
        height: auto;
        max-height: 20;
        background: $surface;
        border: none;
    }
    #theme-hint {
        color: $text-muted;
        text-style: dim;
        text-align: center;
        margin-top: 1;
    }
    """

    def compose(self) -> ComposeResult:
        mgr = self.app.theme_manager  # type: ignore[attr-defined]
        themes = mgr.list_themes()
        active = mgr.get_active_theme_name()

        with Vertical(id="theme-dialog"):
            yield Label("  Temas", id="theme-heading")
            with ListView(id="theme-list"):
                for name in themes:
                    marker = "  ●" if name == active else "   "
                    yield ListItem(Label(f"{marker}  {name}"), id=f"t-{name}")
            yield Label("enter: aplicar · esc: voltar", id="theme-hint")
        yield Footer()

    def on_mount(self) -> None:
        mgr = self.app.theme_manager  # type: ignore[attr-defined]
        active = mgr.get_active_theme_name()
        lv = self.query_one("#theme-list", ListView)
        themes = mgr.list_themes()
        try:
            idx = themes.index(active)
            lv.index = idx
        except ValueError:
            pass

    def action_cursor_down(self) -> None:
        self.query_one("#theme-list", ListView).action_cursor_down()

    def action_cursor_up(self) -> None:
        self.query_one("#theme-list", ListView).action_cursor_up()

    def action_select_theme(self) -> None:
        lv = self.query_one("#theme-list", ListView)
        item = lv.highlighted_child
        if item and item.id:
            name = item.id.removeprefix("t-")
            mgr = self.app.theme_manager  # type: ignore[attr-defined]
            mgr.set_active_theme(name)
            try:
                self.app.theme = name
            except Exception:
                pass
            self.app.notify(f"Tema aplicado: {name}")
        self.dismiss(True)

    def action_cancel(self) -> None:
        self.dismiss(False)

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        self.action_select_theme()
