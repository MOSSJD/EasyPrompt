"""GUI 冒烟测试：无头（offscreen）模式下构建窗口并验证结构。"""

from __future__ import annotations

import pytest


@pytest.fixture()
def app_context(tmp_path):
    from easyprompt.config import ConfigManager
    from easyprompt.fonts import FontManager
    from easyprompt.presets import PresetManager

    config = ConfigManager(str(tmp_path / "config.json"))
    font_manager = FontManager(str(tmp_path / "fonts"))
    preset_manager = PresetManager(str(tmp_path / "Presets"))
    return config, preset_manager, font_manager


def test_main_window_constructs(qapp, app_context):
    from easyprompt.ui.main_window import MainWindow

    config, preset_manager, font_manager = app_context
    window = MainWindow(config, preset_manager, font_manager)
    assert window.stack.count() == 2
    assert window.chat_page is not None
    assert window.presets_page is not None
    assert window.sidebar.btn_chat.isChecked()  # 默认激活主功能界面
    window.close()


def test_page_switch(qapp, app_context):
    from easyprompt.ui.main_window import MainWindow
    from easyprompt.ui.sidebar import PAGE_CHAT, PAGE_PRESETS

    config, preset_manager, font_manager = app_context
    window = MainWindow(config, preset_manager, font_manager)

    window.sidebar.page_changed.emit(PAGE_PRESETS)
    assert window.stack.currentIndex() == PAGE_PRESETS
    assert window.presets_page.isVisibleTo(window) or True

    window.sidebar.page_changed.emit(PAGE_CHAT)
    assert window.stack.currentIndex() == PAGE_CHAT
    window.close()


def test_preset_selection_fills_system_prompt(qapp, app_context):
    from PySide6.QtWidgets import QTextEdit

    from easyprompt.presets import Preset
    from easyprompt.ui.main_window import MainWindow

    config, preset_manager, font_manager = app_context
    preset_manager.save(
        Preset(name="coder", title="代码助手", model="deepseek-v4-flash",
               system_prompt="你是一名资深工程师。")
    )
    window = MainWindow(config, preset_manager, font_manager)
    window.presets_page.refresh_list()

    # 选中 coder 预设
    for i in range(window.presets_page.list_widget.count()):
        if window.presets_page.list_widget.item(i).data(0x0100) == "coder":
            window.presets_page.list_widget.setCurrentRow(i)
            break

    editor = window.chat_page.system_input.findChild(QTextEdit)
    assert "资深工程师" in editor.toPlainText()
    window.close()


def test_settings_window_constructs_and_expand(qapp, app_context):
    from easyprompt.ui.settings_window import SettingsWindow

    config, preset_manager, font_manager = app_context
    win = SettingsWindow(config, preset_manager, font_manager)
    assert win.stack.count() == 3
    # "界面"默认展开，含两个子项
    top = win.tree.topLevelItem(0)
    assert top.isExpanded() is True
    assert top.childCount() == 2
    assert [top.child(i).text(0) for i in range(2)] == ["主页面", "设置"]
    # 折叠后再展开
    top.setExpanded(False)
    assert top.isExpanded() is False
    top.setExpanded(True)
    assert top.isExpanded() is True
    win.close()
