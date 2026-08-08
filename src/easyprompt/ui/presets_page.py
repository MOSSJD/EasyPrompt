"""预设切换界面：左侧预设列表（1/8）+ 右侧预设展示（7/8）。"""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from ..presets import PresetManager
from .widgets import COLOR_MUTED, title_label


class PresetsPage(QWidget):
    """预设列表点选切换，展示标题 / 模型 / System Prompt。"""

    preset_selected = Signal(object)  # Preset

    def __init__(self, preset_manager: PresetManager, parent: QWidget | None = None):
        super().__init__(parent)
        self._preset_manager = preset_manager
        self._build_ui()
        self.refresh_list()

    def _build_ui(self) -> None:
        # 左 1/8：预设列表
        self.list_widget = QListWidget()
        self.list_widget.currentItemChanged.connect(self._on_select)

        # 右 7/8：预设展示
        self.title_label = title_label("—")
        self.model_label = QLabel("")
        self.model_label.setStyleSheet(f"color: {COLOR_MUTED}; font-size: 10pt;")
        self.system_prompt_view = QTextEdit()
        self.system_prompt_view.setReadOnly(True)

        display_layout = QVBoxLayout()
        display_layout.setSpacing(6)
        display_layout.addWidget(self.title_label, 0)
        display_layout.addWidget(self.model_label, 0)
        display_layout.addWidget(self.system_prompt_view, 1)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)
        layout.addWidget(self.list_widget, 1)
        layout.addLayout(display_layout, 7)

    def refresh_list(self) -> None:
        """重新扫描预设目录并刷新列表（保持当前选中项）。"""
        current_name = self.current_name()
        self.list_widget.blockSignals(True)
        self.list_widget.clear()
        for name in self._preset_manager.list_names():
            preset = self._preset_manager.load(name)
            item = QListWidgetItem(preset.title if preset and preset.title else name)
            item.setData(Qt.UserRole, name)
            self.list_widget.addItem(item)
        self.list_widget.blockSignals(False)

        index = self._index_of_name(current_name)
        self.list_widget.setCurrentRow(index if index >= 0 else 0)
        if self.list_widget.currentRow() >= 0:
            self._show(self.list_widget.currentItem())

    def current_name(self) -> str | None:
        item = self.list_widget.currentItem()
        if item is None:
            return None
        return item.data(Qt.UserRole)

    def _index_of_name(self, name: str | None) -> int:
        if not name:
            return 0
        for i in range(self.list_widget.count()):
            if self.list_widget.item(i).data(Qt.UserRole) == name:
                return i
        return -1

    def _on_select(self, current: QListWidgetItem, _previous) -> None:
        if current is not None:
            self._show(current)

    def _show(self, item: QListWidgetItem) -> None:
        name = item.data(Qt.UserRole)
        preset = self._preset_manager.load(name)
        if preset is None:
            return
        self.title_label.setText(preset.title or preset.name)
        self.model_label.setText(f"模型：{preset.model}（暂不可修改）")
        self.system_prompt_view.setPlainText(preset.system_prompt)
        self.preset_selected.emit(preset)
