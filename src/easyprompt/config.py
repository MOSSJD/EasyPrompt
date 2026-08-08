"""配置管理：config.json 的读写与默认值兜底合并。

密钥（api.api_key）仅保存在本地 config.json 中，界面不做输入入口，
用户手动编辑文件即可。
"""

from __future__ import annotations

import copy
import json
import os
from typing import Any

# 默认配置（兜底值，缺失键自动补齐）
DEFAULTS: dict[str, Any] = {
    "api": {
        "base_url": "https://api.deepseek.com",
        "model": "deepseek-v4-flash",
        "api_key": "",
        "timeout": 60,
    },
    "ui": {
        "main_window_size": [1200, 800],
        "settings_window_size": [1000, 600],
        "main_title_font": "",
        "main_body_font": "",
        "settings_title_font": "",
        "settings_body_font": "",
    },
    "presets_dir": "./Presets",
}


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    """以 base 为底，用 override 递归覆盖，缺失键保留 base 的默认值。"""
    result = copy.deepcopy(base)
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


class ConfigManager:
    """config.json 配置管理器。

    用法：
        cfg = ConfigManager("config.json")
        cfg.api_key = "sk-xxx"   # 或直接编辑文件
        cfg.save()
    """

    def __init__(self, path: str = "config.json"):
        self.path = path
        self._data: dict[str, Any] = {}
        self.load()

    # ---- 读写 ----
    def load(self) -> None:
        """从磁盘加载配置并与默认值合并兜底；文件不存在/损坏时回退到默认值。"""
        data: dict[str, Any] = {}
        if os.path.exists(self.path):
            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                if isinstance(loaded, dict):
                    data = loaded
            except (json.JSONDecodeError, OSError):
                data = {}
        self._data = _deep_merge(DEFAULTS, data)

    def save(self) -> None:
        """将当前配置写回磁盘（UTF-8，保留密钥字段）。"""
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self._data, f, ensure_ascii=False, indent=2)

    def to_dict(self) -> dict[str, Any]:
        return copy.deepcopy(self._data)

    # ---- API ----
    @property
    def api_base_url(self) -> str:
        return str(self._data["api"]["base_url"])

    @api_base_url.setter
    def api_base_url(self, value: str) -> None:
        self._data["api"]["base_url"] = value

    @property
    def model(self) -> str:
        return str(self._data["api"]["model"])

    @model.setter
    def model(self, value: str) -> None:
        self._data["api"]["model"] = value

    @property
    def api_key(self) -> str:
        return str(self._data["api"]["api_key"])

    @api_key.setter
    def api_key(self, value: str) -> None:
        self._data["api"]["api_key"] = value

    @property
    def timeout(self) -> int:
        return int(self._data["api"]["timeout"])

    @timeout.setter
    def timeout(self, value: int) -> None:
        self._data["api"]["timeout"] = value

    # ---- UI ----
    @property
    def main_window_size(self) -> tuple[int, int]:
        size = self._data["ui"]["main_window_size"]
        return int(size[0]), int(size[1])

    @main_window_size.setter
    def main_window_size(self, value: tuple[int, int]) -> None:
        self._data["ui"]["main_window_size"] = [int(value[0]), int(value[1])]

    @property
    def settings_window_size(self) -> tuple[int, int]:
        size = self._data["ui"]["settings_window_size"]
        return int(size[0]), int(size[1])

    @settings_window_size.setter
    def settings_window_size(self, value: tuple[int, int]) -> None:
        self._data["ui"]["settings_window_size"] = [int(value[0]), int(value[1])]

    @property
    def main_title_font(self) -> str:
        return str(self._data["ui"]["main_title_font"])

    @main_title_font.setter
    def main_title_font(self, value: str) -> None:
        self._data["ui"]["main_title_font"] = value

    @property
    def main_body_font(self) -> str:
        return str(self._data["ui"]["main_body_font"])

    @main_body_font.setter
    def main_body_font(self, value: str) -> None:
        self._data["ui"]["main_body_font"] = value

    @property
    def settings_title_font(self) -> str:
        return str(self._data["ui"]["settings_title_font"])

    @settings_title_font.setter
    def settings_title_font(self, value: str) -> None:
        self._data["ui"]["settings_title_font"] = value

    @property
    def settings_body_font(self) -> str:
        return str(self._data["ui"]["settings_body_font"])

    @settings_body_font.setter
    def settings_body_font(self, value: str) -> None:
        self._data["ui"]["settings_body_font"] = value

    # ---- 预设 ----
    @property
    def presets_dir(self) -> str:
        return str(self._data["presets_dir"])

    @presets_dir.setter
    def presets_dir(self, value: str) -> None:
        self._data["presets_dir"] = value
