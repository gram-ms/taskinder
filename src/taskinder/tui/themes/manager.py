import json
from dataclasses import fields
from pathlib import Path
from typing import List, Optional

import platformdirs
from textual.theme import Theme

from taskinder.tui.themes.defaults import BUILT_IN_THEMES


class ThemeManager:
    def __init__(self) -> None:
        self.config_dir = Path(platformdirs.user_config_dir("taskinder"))
        self.themes_dir = self.config_dir / "themes"
        self.config_file = self.config_dir / "config.json"
        self.themes_dir.mkdir(parents=True, exist_ok=True)

    def _load_config(self) -> dict:
        if self.config_file.exists():
            try:
                return json.loads(self.config_file.read_text())
            except json.JSONDecodeError:
                pass
        return {"active_theme": "catppuccin"}

    def _save_config(self, config: dict) -> None:
        self.config_file.write_text(json.dumps(config, indent=2))

    def get_active_theme_name(self) -> str:
        return self._load_config().get("active_theme", "catppuccin")

    def set_active_theme(self, name: str) -> None:
        available = self.list_themes()
        if name not in available:
            raise ValueError(
                f"Theme '{name}' not found. Available: {', '.join(available)}"
            )
        config = self._load_config()
        config["active_theme"] = name
        self._save_config(config)

    def list_themes(self) -> List[str]:
        built_in = [t.name for t in BUILT_IN_THEMES]
        user = [f.stem for f in self.themes_dir.glob("*.json")]
        return sorted(set(built_in + user))

    def get_all_themes(self) -> List[Theme]:
        themes: List[Theme] = list(BUILT_IN_THEMES)
        for json_file in sorted(self.themes_dir.glob("*.json")):
            try:
                data = json.loads(json_file.read_text())
                themes.append(self._dict_to_theme(data))
            except (json.JSONDecodeError, TypeError, ValueError):
                pass
        return themes

    def get_theme_by_name(self, name: str) -> Optional[Theme]:
        for theme in self.get_all_themes():
            if theme.name == name:
                return theme
        return None

    def add_user_theme(self, name: str, theme_data: dict) -> None:
        theme_data = dict(theme_data)
        theme_data["name"] = name
        path = self.themes_dir / f"{name}.json"
        path.write_text(json.dumps(theme_data, indent=2))

    def remove_user_theme(self, name: str) -> None:
        path = self.themes_dir / f"{name}.json"
        if not path.exists():
            built_in_names = [t.name for t in BUILT_IN_THEMES]
            if name in built_in_names:
                raise ValueError(f"Cannot remove built-in theme '{name}'.")
            raise ValueError(f"User theme '{name}' not found.")
        path.unlink()

    def export_theme(self, name: str) -> dict:
        theme = self.get_theme_by_name(name)
        if not theme:
            raise ValueError(f"Theme '{name}' not found.")
        return self._theme_to_dict(theme)

    @staticmethod
    def _dict_to_theme(data: dict) -> Theme:
        valid = {f.name for f in fields(Theme)}
        return Theme(**{k: v for k, v in data.items() if k in valid})

    @staticmethod
    def _theme_to_dict(theme: Theme) -> dict:
        return {
            f.name: getattr(theme, f.name)
            for f in fields(Theme)
            if getattr(theme, f.name) is not None
        }
