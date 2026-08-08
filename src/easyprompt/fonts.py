"""字体管理：系统字体读取、ttf/otf 导入与持久化。

说明：QFontDatabase.addApplicationFont 仅在当前进程有效，
导入的字体文件会被复制到应用 fonts/ 目录，下次启动时重新加载，
以保证跨会话生效。
"""

from __future__ import annotations

import os
import shutil
from typing import Optional

from PySide6.QtGui import QFontDatabase

FONT_EXTENSIONS = (".ttf", ".otf", ".ttc")

# Windows 3.x 时代遗留的字体族名：仅有注册名、没有真实字体文件，
# DirectWrite 无法加载，枚举时会产生大量 qt.qpa.fonts 警告，直接过滤。
_LEGACY_FONT_FAMILIES = {
    "script",
    "system",
    "terminal",
    "fixedsys",
    "modern",
    "roman",
}


class FontManager:
    """系统字体列表查询与字体导入。"""

    def __init__(self, imported_dir: str = "fonts"):
        self.imported_dir = imported_dir

    # ---- 系统字体 ----
    @staticmethod
    def list_system_fonts() -> list[str]:
        """返回按字母排序的系统可用字体族名（已过滤 Windows 遗留旧字体）。"""
        return sorted(
            family
            for family in QFontDatabase.families()
            if family.lower() not in _LEGACY_FONT_FAMILIES
        )

    # ---- 导入 ----
    @staticmethod
    def import_font(path: str) -> int:
        """将字体文件注册到当前进程，返回字体 ID（失败返回 -1）。"""
        return QFontDatabase.addApplicationFont(path)

    def persist_imported(self, src_path: str) -> Optional[str]:
        """将字体文件复制到 fonts/ 目录持久化，返回目标路径。

        若目标已存在则跳过复制（避免重复导入同名字体）。
        """
        if not os.path.isfile(src_path):
            return None
        os.makedirs(self.imported_dir, exist_ok=True)
        dest = os.path.join(self.imported_dir, os.path.basename(src_path))
        if not os.path.exists(dest):
            shutil.copy2(src_path, dest)
        return dest

    def load_imported(self) -> list[str]:
        """启动时加载 fonts/ 目录下全部字体文件，返回加载成功的文件路径。"""
        loaded: list[str] = []
        if not os.path.isdir(self.imported_dir):
            return loaded
        for fname in sorted(os.listdir(self.imported_dir)):
            if fname.lower().endswith(FONT_EXTENSIONS):
                path = os.path.join(self.imported_dir, fname)
                if self.import_font(path) != -1:
                    loaded.append(path)
        return loaded
