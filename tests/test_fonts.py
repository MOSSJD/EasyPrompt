"""FontManager 单元测试（需要 QApplication，见 conftest.py）。"""

from __future__ import annotations

import os

from easyprompt.fonts import FontManager


def test_list_system_fonts_returns_sorted_list(qapp):
    fonts = FontManager.list_system_fonts()
    assert isinstance(fonts, list)
    assert fonts == sorted(fonts)
    # 注意：offscreen 平台（如 Windows CI）可能不加载系统字体，
    # 因此不断言非空，仅验证接口契约与排序。


def test_persist_imported_copies_file(tmp_path, qapp):
    src = tmp_path / "MyFont.ttf"
    src.write_bytes(b"fake-font-bytes")
    mgr = FontManager(imported_dir=str(tmp_path / "fonts"))
    dest = mgr.persist_imported(str(src))
    assert dest is not None
    assert os.path.exists(dest)
    with open(dest, "rb") as f:
        assert f.read() == b"fake-font-bytes"


def test_persist_imported_skips_existing(tmp_path, qapp):
    fonts_dir = tmp_path / "fonts"
    fonts_dir.mkdir()
    dest = fonts_dir / "MyFont.ttf"
    dest.write_bytes(b"existing")
    src = tmp_path / "MyFont.ttf"
    src.write_bytes(b"new-bytes")

    mgr = FontManager(imported_dir=str(fonts_dir))
    result = mgr.persist_imported(str(src))
    assert result == str(dest)
    with open(dest, "rb") as f:
        assert f.read() == b"existing"  # 未被覆盖


def test_load_imported_only_font_files(tmp_path, qapp):
    fonts_dir = tmp_path / "fonts"
    fonts_dir.mkdir()
    (fonts_dir / "a.ttf").write_bytes(b"x")
    (fonts_dir / "b.otf").write_bytes(b"x")
    (fonts_dir / "note.txt").write_text("hello", encoding="utf-8")

    mgr = FontManager(imported_dir=str(fonts_dir))
    loaded = mgr.load_imported()
    # 无效字体字节可能导致注册失败，但至少不会返回 txt 文件
    assert all(p.endswith((".ttf", ".otf")) for p in loaded)
