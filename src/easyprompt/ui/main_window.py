"""主窗口：左侧边栏（1/8）+ 右侧当前界面（7/8），含设置窗口联动。"""

from __future__ import annotations

from PySide6.QtWidgets import QHBoxLayout, QStackedWidget, QWidget

from ..api_client import DeepSeekClient
from ..config import ConfigManager
from ..fonts import FontManager
from ..presets import Preset, PresetManager
from .chat_page import ChatPage
from .presets_page import PresetsPage
from .settings_window import SettingsWindow
from .sidebar import SidebarWidget
from .widgets import apply_theme


class MainWindow(QWidget):
    """Easy Prompt 主窗口。"""

    def __init__(
        self,
        config: ConfigManager,
        preset_manager: PresetManager,
        font_manager: FontManager,
        parent: QWidget | None = None,
    ):
        super().__init__(parent)
        self._config = config
        self._preset_manager = preset_manager
        self._font_manager = font_manager
        self._settings_window: SettingsWindow | None = None

        self._api_client = DeepSeekClient(
            api_key=config.api_key,
            base_url=config.api_base_url,
            model=config.model,
            timeout=config.timeout,
        )

        self.setWindowTitle("Easy Prompt")
        self.resize(*config.main_window_size)
        apply_theme(self, fonts=self._theme_fonts())

        # 边栏 + 界面堆叠（1:7）
        self.sidebar = SidebarWidget()
        self.chat_page = ChatPage(config, self._api_client)
        self.presets_page = PresetsPage(preset_manager)

        self.stack = QStackedWidget()
        self.stack.addWidget(self.chat_page)      # PAGE_CHAT
        self.stack.addWidget(self.presets_page)   # PAGE_PRESETS

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.sidebar, 1)
        layout.addWidget(self.stack, 7)

        # 信号连接
        self.sidebar.page_changed.connect(self.stack.setCurrentIndex)
        self.sidebar.settings_requested.connect(self.open_settings)
        self.presets_page.preset_selected.connect(self._on_preset_selected)

    # ---- 预设联动 ----
    def _on_preset_selected(self, preset: Preset) -> None:
        """切换预设后，将其 System Prompt 填充到主功能界面。"""
        self.chat_page.set_system_prompt(preset.system_prompt)

    # ---- 设置窗口 ----
    def open_settings(self) -> None:
        if self._settings_window is None:
            self._settings_window = SettingsWindow(
                self._config, self._preset_manager, self._font_manager
            )
            self._settings_window.settings_changed.connect(self._apply_settings)
        self._settings_window.show()
        self._settings_window.raise_()
        self._settings_window.activateWindow()

    def _apply_settings(self) -> None:
        self.resize(*self._config.main_window_size)
        apply_theme(self, fonts=self._theme_fonts())

    def _theme_fonts(self) -> dict[str, str]:
        return {
            "title": self._config.main_title_font,
            "body": self._config.main_body_font,
        }
