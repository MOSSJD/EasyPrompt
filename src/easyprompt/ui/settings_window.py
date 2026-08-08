"""设置窗口：左侧类别树（界面/预设，界面可展开收起）+ 右侧设置表单。"""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QFontDatabase
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QStackedWidget,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from ..config import ConfigManager
from ..fonts import FontManager
from ..presets import PresetManager
from .widgets import ScrollArea, apply_theme, title_label


class _FontCombo(QComboBox):
    """字体下拉：首项"默认（系统字体）"，其余为系统/已导入字体，带字体预览。"""

    def fill(self, current: str) -> None:
        self.clear()
        self.addItem("默认（系统字体）", "")
        for family in FontManager.list_system_fonts():
            self.addItem(family, family)
        index = self.findData(current)
        self.setCurrentIndex(index if index >= 0 else 0)
        self._apply_preview()

    def _apply_preview(self) -> None:
        for i in range(self.count()):
            family = self.itemData(i) or self.itemText(i)
            self.setItemData(i, QFont(family, 12), Qt.FontRole)


class _SizeEditor(QWidget):
    """宽 x 高（px）编辑器。"""

    changed = Signal()

    def __init__(self, label: str, width: int, height: int, parent: QWidget | None = None):
        super().__init__(parent)
        self.width_spin = QSpinBox()
        self.height_spin = QSpinBox()
        for spin in (self.width_spin, self.height_spin):
            spin.setRange(600, 3840)
            spin.setSuffix(" px")
        self.width_spin.setValue(width)
        self.height_spin.setValue(height)
        self.width_spin.valueChanged.connect(self.changed.emit)
        self.height_spin.valueChanged.connect(self.changed.emit)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)
        layout.addWidget(QLabel(label), 0)
        layout.addWidget(self.width_spin, 1)
        layout.addWidget(QLabel("×"), 0)
        layout.addWidget(self.height_spin, 1)
        layout.addStretch(2)

    def value(self) -> tuple[int, int]:
        return self.width_spin.value(), self.height_spin.value()


class SettingsWindow(QWidget):
    """设置窗口（默认 1000x600）。

    左侧：类别树（界面[可展开：主页面/设置]、预设）；
    右侧：对应设置表单（尺寸、字体[含导入]、预设目录）。
    """

    settings_changed = Signal()

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
        self._building = False

        self.setWindowTitle("设置")
        self.resize(*config.settings_window_size)
        self._build_ui()
        self._load_values()
        apply_theme(self, fonts=self._theme_fonts())

    # ---- UI ----
    def _build_ui(self) -> None:
        # 左侧：类别树（1/4）
        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.setMinimumWidth(140)
        item_ui = QTreeWidgetItem(["界面"])
        self.item_main = QTreeWidgetItem(["主页面"])
        self.item_settings = QTreeWidgetItem(["设置"])
        item_ui.addChildren([self.item_main, self.item_settings])
        item_presets = QTreeWidgetItem(["预设"])
        self.tree.addTopLevelItems([item_ui, item_presets])
        self.tree.expandItem(item_ui)  # 默认展开"界面"
        self.tree.itemClicked.connect(self._on_tree_clicked)

        # 右侧：表单堆叠（3/4，超出可显示范围时滚动）
        self.stack = QStackedWidget()
        self.page_main = self._build_page_main()
        self.page_settings = self._build_page_settings()
        self.page_presets = self._build_page_presets()
        self.stack.addWidget(self.page_main)
        self.stack.addWidget(self.page_settings)
        self.stack.addWidget(self.page_presets)
        self.stack.setMinimumHeight(200)
        stack_scroll = ScrollArea(self.stack)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)
        layout.addWidget(self.tree, 1)
        layout.addWidget(stack_scroll, 3)

    def _build_page_main(self) -> QWidget:
        page = QWidget()
        title = title_label("主页面")
        self.main_size = _SizeEditor("主页面大小", *self._config.main_window_size)
        self.main_size.changed.connect(self._on_changed)
        self.main_title_font = _FontCombo()
        self.main_title_font.currentIndexChanged.connect(self._on_changed)
        self.main_body_font = _FontCombo()
        self.main_body_font.currentIndexChanged.connect(self._on_changed)
        import_btn = QPushButton("导入新字体…")
        import_btn.clicked.connect(lambda: self._import_font(self.main_title_font))

        layout = QVBoxLayout(page)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(10)
        layout.addWidget(title)
        layout.addWidget(self.main_size)
        layout.addWidget(self._font_row("标题字体", self.main_title_font, import_btn))
        layout.addWidget(self._font_row("正文字体", self.main_body_font, None))
        layout.addStretch(1)
        return page

    def _build_page_settings(self) -> QWidget:
        page = QWidget()
        title = title_label("设置")
        self.settings_size = _SizeEditor("设置窗口大小", *self._config.settings_window_size)
        self.settings_size.changed.connect(self._on_changed)
        self.settings_title_font = _FontCombo()
        self.settings_title_font.currentIndexChanged.connect(self._on_changed)
        self.settings_body_font = _FontCombo()
        self.settings_body_font.currentIndexChanged.connect(self._on_changed)
        import_btn = QPushButton("导入新字体…")
        import_btn.clicked.connect(lambda: self._import_font(self.settings_title_font))

        layout = QVBoxLayout(page)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(10)
        layout.addWidget(title)
        layout.addWidget(self.settings_size)
        layout.addWidget(self._font_row("标题字体", self.settings_title_font, import_btn))
        layout.addWidget(self._font_row("正文字体", self.settings_body_font, None))
        layout.addStretch(1)
        return page

    def _build_page_presets(self) -> QWidget:
        page = QWidget()
        title = title_label("预设")
        self.presets_dir_edit = QLineEdit(self._config.presets_dir)
        self.presets_dir_edit.editingFinished.connect(self._on_changed)
        browse_btn = QPushButton("浏览…")
        browse_btn.clicked.connect(self._browse_presets_dir)

        row = QHBoxLayout()
        row.addWidget(self.presets_dir_edit, 1)
        row.addWidget(browse_btn, 0)

        layout = QVBoxLayout(page)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(10)
        layout.addWidget(title)
        layout.addWidget(QLabel("预设存放目录"))
        layout.addLayout(row)
        layout.addStretch(1)
        return page

    @staticmethod
    def _font_row(label: str, combo: QComboBox, import_btn: QPushButton | None) -> QWidget:
        row = QWidget()
        layout = QHBoxLayout(row)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        layout.addWidget(QLabel(label), 0)
        layout.addWidget(combo, 1)
        if import_btn is not None:
            layout.addWidget(import_btn, 0)
        return row

    # ---- 树交互 ----
    def _on_tree_clicked(self, item: QTreeWidgetItem, _column: int) -> None:
        if item.parent() is None:
            # 顶层节点：点击"界面"切换展开/收起；点击"预设"显示表单
            if item.text(0) == "界面":
                self.tree.setItemExpanded(item, not item.isExpanded())
                if item.isExpanded():
                    self.tree.setCurrentItem(self.item_main)
                    self._show_page(0)
            else:
                self._show_page(2)
        elif item is self.item_main:
            self._show_page(0)
        elif item is self.item_settings:
            self._show_page(1)

    def _show_page(self, index: int) -> None:
        self.stack.setCurrentIndex(index)

    # ---- 数据加载 / 保存 ----
    def _load_values(self) -> None:
        self._building = True
        self.main_size.width_spin.setValue(self._config.main_window_size[0])
        self.main_size.height_spin.setValue(self._config.main_window_size[1])
        self.settings_size.width_spin.setValue(self._config.settings_window_size[0])
        self.settings_size.height_spin.setValue(self._config.settings_window_size[1])
        self.main_title_font.fill(self._config.main_title_font)
        self.main_body_font.fill(self._config.main_body_font)
        self.settings_title_font.fill(self._config.settings_title_font)
        self.settings_body_font.fill(self._config.settings_body_font)
        self.presets_dir_edit.setText(self._config.presets_dir)
        self._building = False

    def _on_changed(self, *_args) -> None:
        if self._building:
            return
        self._config.main_window_size = self.main_size.value()
        self._config.settings_window_size = self.settings_size.value()
        self._config.main_title_font = self.main_title_font.currentData() or ""
        self._config.main_body_font = self.main_body_font.currentData() or ""
        self._config.settings_title_font = self.settings_title_font.currentData() or ""
        self._config.settings_body_font = self.settings_body_font.currentData() or ""
        self._config.presets_dir = self.presets_dir_edit.text().strip() or "./Presets"
        self._config.save()
        apply_theme(self, fonts=self._theme_fonts())
        self.settings_changed.emit()

    def _theme_fonts(self) -> dict[str, str]:
        return {
            "title": self._config.settings_title_font,
            "body": self._config.settings_body_font,
        }

    # ---- 字体导入 / 目录浏览 ----
    def _import_font(self, combo: _FontCombo) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, "导入字体", "", "字体文件 (*.ttf *.otf *.ttc)"
        )
        if not path:
            return
        font_id = self._font_manager.import_font(path)
        if font_id == -1:
            QMessageBox.warning(self, "导入失败", "无法识别该字体文件。")
            return
        self._font_manager.persist_imported(path)
        families = QFontDatabase.applicationFontFamilies(font_id)
        family = families[0] if families else None
        combo.fill(combo.currentData() or "")
        if family:
            index = combo.findData(family)
            if index >= 0:
                combo.setCurrentIndex(index)
        self._on_changed()

    def _browse_presets_dir(self) -> None:
        directory = QFileDialog.getExistingDirectory(
            self, "选择预设目录", self.presets_dir_edit.text() or "."
        )
        if directory:
            self.presets_dir_edit.setText(directory)
            self._on_changed()
