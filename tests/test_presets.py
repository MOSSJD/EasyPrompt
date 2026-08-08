"""PresetManager 单元测试。"""

from __future__ import annotations

import json

from easyprompt.presets import DEFAULT_PRESET_NAME, Preset, PresetManager


def test_init_creates_default_preset(tmp_path):
    mgr = PresetManager(str(tmp_path / "Presets"))
    assert DEFAULT_PRESET_NAME in mgr.list_names()
    default = mgr.get_default()
    assert default.name == "default"
    assert default.model == "deepseek-v4-flash"
    assert default.system_prompt == ""


def test_save_and_load_custom_preset(tmp_path):
    mgr = PresetManager(str(tmp_path / "Presets"))
    preset = Preset(name="coder", title="代码助手", model="deepseek-v4-flash",
                    system_prompt="你是一名资深 Python 工程师。")
    mgr.save(preset)
    assert "coder" in mgr.list_names()

    loaded = mgr.load("coder")
    assert loaded is not None
    assert loaded.title == "代码助手"
    assert "Python" in loaded.system_prompt


def test_load_missing_returns_none(tmp_path):
    mgr = PresetManager(str(tmp_path / "Presets"))
    assert mgr.load("not-exist") is None


def test_load_corrupt_returns_none(tmp_path):
    presets_dir = tmp_path / "Presets"
    mgr = PresetManager(str(presets_dir))
    (presets_dir / "broken.json").write_text("{oops", encoding="utf-8")
    assert mgr.load("broken") is None


def test_list_names_sorted_and_only_json(tmp_path):
    presets_dir = tmp_path / "Presets"
    mgr = PresetManager(str(presets_dir))
    (presets_dir / "b.json").write_text(json.dumps({"name": "b"}), encoding="utf-8")
    (presets_dir / "a.json").write_text(json.dumps({"name": "a"}), encoding="utf-8")
    (presets_dir / "note.txt").write_text("x", encoding="utf-8")
    assert mgr.list_names() == ["a", "b", "default"]


def test_preset_to_dict_roundtrip():
    preset = Preset(name="n", title="t", model="m", system_prompt="s")
    restored = Preset.from_dict(preset.to_dict())
    assert restored == preset
