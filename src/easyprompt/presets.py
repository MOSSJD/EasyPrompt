"""预设管理：Presets/<name>.json 的读取与默认预设保障。

预设文件格式：
    {"name": "default", "title": "default",
     "model": "deepseek-v4-flash", "system_prompt": ""}
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Optional

DEFAULT_PRESET_NAME = "default"
DEFAULT_MODEL = "deepseek-v4-flash"


@dataclass
class Preset:
    """单个预设：名称（文件名）、标题、模型、System Prompt。"""

    name: str
    title: str
    model: str = DEFAULT_MODEL
    system_prompt: str = ""

    @classmethod
    def from_dict(cls, data: dict) -> "Preset":
        return cls(
            name=str(data.get("name", "")),
            title=str(data.get("title", "")),
            model=str(data.get("model", DEFAULT_MODEL)),
            system_prompt=str(data.get("system_prompt", "")),
        )

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "title": self.title,
            "model": self.model,
            "system_prompt": self.system_prompt,
        }


class PresetManager:
    """扫描/加载/保存 Presets 目录下的预设 JSON 文件。"""

    def __init__(self, presets_dir: str = "./Presets"):
        self.presets_dir = presets_dir
        self.ensure_default()

    def _path(self, name: str) -> str:
        if not name.endswith(".json"):
            name = f"{name}.json"
        return os.path.join(self.presets_dir, name)

    def ensure_default(self) -> None:
        """确保预设目录存在，且默认预设 default.json 存在。"""
        os.makedirs(self.presets_dir, exist_ok=True)
        default_path = self._path(DEFAULT_PRESET_NAME)
        if not os.path.exists(default_path):
            preset = Preset(
                name=DEFAULT_PRESET_NAME,
                title=DEFAULT_PRESET_NAME,
                model=DEFAULT_MODEL,
                system_prompt="",
            )
            self.save(preset)

    def list_names(self) -> list[str]:
        """列出全部预设名称（按文件名排序，不含扩展名）。"""
        names: list[str] = []
        if not os.path.isdir(self.presets_dir):
            return names
        for fname in sorted(os.listdir(self.presets_dir)):
            if fname.endswith(".json"):
                names.append(fname[: -len(".json")])
        return names

    def load(self, name: str) -> Optional[Preset]:
        """加载指定预设；文件缺失或损坏返回 None。"""
        path = self._path(name)
        if not os.path.exists(path):
            return None
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if not isinstance(data, dict):
                return None
            preset = Preset.from_dict(data)
            if not preset.name:
                preset.name = name
            return preset
        except (json.JSONDecodeError, OSError):
            return None

    def get_default(self) -> Preset:
        """获取默认预设；异常时返回内存中的 default 兜底。"""
        preset = self.load(DEFAULT_PRESET_NAME)
        if preset is not None:
            return preset
        return Preset(
            name=DEFAULT_PRESET_NAME,
            title=DEFAULT_PRESET_NAME,
            model=DEFAULT_MODEL,
            system_prompt="",
        )

    def save(self, preset: Preset) -> None:
        """将预设写为 <name>.json。"""
        os.makedirs(self.presets_dir, exist_ok=True)
        path = self._path(preset.name)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(preset.to_dict(), f, ensure_ascii=False, indent=2)
