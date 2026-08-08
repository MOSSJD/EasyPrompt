"""边栏组件：上对齐的可操作界面图标栏 + 下对齐的设置齿轮图标，背景透明。"""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QButtonGroup, QToolButton, QVBoxLayout, QWidget

from .widgets import COLOR_ACTIVE, COLOR_HOVER, COLOR_TEXT

# 页面索引常量（与 QStackedWidget 页序一致）
PAGE_CHAT = 0
PAGE_PRESETS = 1

# 图标字符（Windows Segoe UI 符号支持）
ICON_CHAT = "\u270E"    # ✎ 主功能界面
ICON_PRESETS = "\u25A4"  # ▤ 预设切换
ICON_SETTINGS = "\u2699"  # ⚙ 设置（齿轮）


class SidebarButton(QToolButton):
    """边栏图标按钮：背景透明，激活态高亮，悬停浅色。"""

    def __init__(self, text: str, tooltip: str, parent: QWidget | None = None):
        super().__init__(parent)
        self.setText(text)
        self.setToolTip(tooltip)
        self.setFixedSize(44, 44)
        self.setFont(self.font())
        self.setCursor(Qt.PointingHandCursor)
        self.setCheckable(True)
        self.setAutoRaise(True)
        self._refresh()

    def _refresh(self) -> None:
        if self.isChecked():
            self.setStyleSheet(
                f"QToolButton {{ background: {COLOR_HOVER}; color: {COLOR_ACTIVE};"
                f"font-size: 18pt; font-weight: bold; border-radius: 6px; }}"
            )
        else:
            self.setStyleSheet(
                f"QToolButton {{ background: transparent; color: {COLOR_TEXT};"
                f"font-size: 16pt; border-radius: 6px; }}"
                f"QToolButton:hover {{ background: {COLOR_HOVER}; }}"
            )

    def setChecked(self, checked: bool) -> None:
        super().setChecked(checked)
        self._refresh()


class SidebarWidget(QWidget):
    """左侧边栏（占主窗口 1/8）：上图标栏（主功能/预设）+ 下齿轮设置。"""

    page_changed = Signal(int)      # 切换页面（PAGE_CHAT / PAGE_PRESETS）
    settings_requested = Signal()   # 打开设置窗口

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setObjectName("sidebar")
        self.setStyleSheet(f"background: {COLOR_HOVER}; border-right: 1px solid #D9D9D9;")
        self.setMinimumWidth(48)

        # 上：可操作界面图标栏（上对齐）
        self.btn_chat = SidebarButton(ICON_CHAT, "主功能界面")
        self.btn_presets = SidebarButton(ICON_PRESETS, "预设切换")
        self.btn_chat.setChecked(True)  # 默认激活主功能界面

        self._group = QButtonGroup(self)
        self._group.setExclusive(True)
        self._group.addButton(self.btn_chat, PAGE_CHAT)
        self._group.addButton(self.btn_presets, PAGE_PRESETS)
        self._group.buttonClicked.connect(self._on_page_button)

        top_layout = QVBoxLayout()
        top_layout.setSpacing(4)
        top_layout.addWidget(self.btn_chat)
        top_layout.addWidget(self.btn_presets)
        top_layout.addStretch(1)

        # 下：设置齿轮（下对齐）
        self.btn_settings = SidebarButton(ICON_SETTINGS, "设置")
        self.btn_settings.setCheckable(False)
        self.btn_settings.clicked.connect(self.settings_requested.emit)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(2, 8, 2, 8)
        layout.addLayout(top_layout, 1)
        layout.addWidget(self.btn_settings, 0, Qt.AlignBottom)

    def _on_page_button(self, button: QToolButton) -> None:
        self.page_changed.emit(self._group.id(button))

    def set_active_page(self, page_index: int) -> None:
        if button := self._group.button(page_index):
            button.setChecked(True)
