"""ConfigManager 单元测试。"""

from __future__ import annotations

import json

from easyprompt.config import ConfigManager


def test_defaults_when_file_missing(tmp_path):
    cfg = ConfigManager(str(tmp_path / "missing.json"))
    assert cfg.api_base_url == "https://api.deepseek.com"
    assert cfg.model == "deepseek-v4-flash"
    assert cfg.api_key == ""
    assert cfg.timeout == 60
    assert cfg.main_window_size == (1200, 800)
    assert cfg.settings_window_size == (1000, 600)
    assert cfg.presets_dir == "./Presets"
    for font_attr in ("main_title_font", "main_body_font",
                      "settings_title_font", "settings_body_font"):
        assert getattr(cfg, font_attr) == ""


def test_roundtrip_save_load(tmp_path):
    path = tmp_path / "config.json"
    cfg = ConfigManager(str(path))
    cfg.api_key = "sk-test-key"
    cfg.model = "deepseek-v4-flash"
    cfg.main_window_size = (1400, 900)
    cfg.save()

    cfg2 = ConfigManager(str(path))
    assert cfg2.api_key == "sk-test-key"
    assert cfg2.main_window_size == (1400, 900)


def test_partial_config_merges_defaults(tmp_path):
    path = tmp_path / "config.json"
    path.write_text(json.dumps({"api": {"api_key": "sk-partial"}}), encoding="utf-8")
    cfg = ConfigManager(str(path))
    assert cfg.api_key == "sk-partial"
    assert cfg.api_base_url == "https://api.deepseek.com"  # 缺失键兜底
    assert cfg.timeout == 60


def test_corrupt_file_falls_back_to_defaults(tmp_path):
    path = tmp_path / "config.json"
    path.write_text("{ not valid json", encoding="utf-8")
    cfg = ConfigManager(str(path))
    assert cfg.model == "deepseek-v4-flash"
    assert cfg.timeout == 60


def test_timeout_setter_and_type(tmp_path):
    cfg = ConfigManager(str(tmp_path / "c.json"))
    cfg.timeout = 120
    assert cfg.timeout == 120
    cfg.save()


def test_presets_dir_setter(tmp_path):
    cfg = ConfigManager(str(tmp_path / "c.json"))
    cfg.presets_dir = "./MyPresets"
    assert cfg.presets_dir == "./MyPresets"
