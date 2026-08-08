"""Easy Prompt 程序入口。

用法：python -m easyprompt.main
"""

from __future__ import annotations

import sys
from pathlib import Path

# 项目根目录（src/easyprompt/main.py -> 项目根）
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# 确保 src 可导入（直接运行脚本时）
if str(BASE_DIR / "src") not in sys.path:
    sys.path.insert(0, str(BASE_DIR / "src"))


def _resolve(root_dir: Path, value: str) -> str:
    """将配置中的相对路径解析为相对项目根目录的绝对路径。"""
    path = Path(value)
    if path.is_absolute():
        return str(path)
    return str((root_dir / path).resolve())


def main() -> int:
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import QApplication

    from easyprompt import __version__
    from easyprompt.config import ConfigManager
    from easyprompt.fonts import FontManager
    from easyprompt.presets import PresetManager
    from easyprompt.ui.main_window import MainWindow

    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    app = QApplication(sys.argv)
    app.setApplicationName("Easy Prompt")
    app.setApplicationVersion(__version__)

    config = ConfigManager(str(BASE_DIR / "config.json"))

    font_manager = FontManager(imported_dir=str(BASE_DIR / "fonts"))
    font_manager.load_imported()  # 加载历史导入字体

    preset_manager = PresetManager(_resolve(BASE_DIR, config.presets_dir))

    window = MainWindow(config, preset_manager, font_manager)
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
