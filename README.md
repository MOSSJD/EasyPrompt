# Easy Prompt

一个运行在 Windows 10/11 64 位或 Ubuntu 的 DeepSeek API 桌面小工具：输入 user prompt 与 system prompt，调用 DeepSeek 大模型并将输出展示在输出框。

## 环境要求

- Python 3.12+
- 平台：Windows 10/11 64 位，或 Ubuntu 24.04+（Linux）

## 快速开始（Windows）

```cmd
# 1. 创建虚拟环境并安装依赖
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements-dev.txt

# 2. 配置 API 密钥（本地保存，不入库）
copy config.example.json config.json
# 编辑 config.json，在 api.api_key 中填入你的 DeepSeek API Key

# 3. 运行（必须使用虚拟环境启动，未激活时使用完整路径）
.venv\Scripts\python.exe src/easyprompt/main.py
```

> 注意：运行必须使用虚拟环境中的 Python（依赖只安装在 `.venv` 内）。已执行 `activate` 后可直接运行 `python src/easyprompt/main.py`；未激活时请使用 `.venv\Scripts\python.exe`，不要使用系统 Python。

## 快速开始（Ubuntu / Linux）

```bash
# 0. 安装 Qt 系统依赖（PySide6 运行所需；python3-venv 用于创建虚拟环境）
sudo apt-get update
sudo apt-get install -y libegl1 libgl1 libxkbcommon-x11-0 libdbus-1-3 libfontconfig1 python3-venv

# 1. 创建虚拟环境并安装依赖
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt

# 2. 配置 API 密钥（本地保存，不入库）
cp config.example.json config.json
# 编辑 config.json，在 api.api_key 中填入你的 DeepSeek API Key

# 3. 运行（必须使用虚拟环境启动，未激活时使用完整路径）
.venv/bin/python src/easyprompt/main.py
```

> 注意：运行必须使用虚拟环境中的 Python（依赖只安装在 `.venv` 内）。已执行 `source .venv/bin/activate` 后可直接运行 `python src/easyprompt/main.py`；未激活时请使用 `.venv/bin/python`。
>
> 无显示器的无头环境（如纯 SSH 服务器）无法弹出窗口，请在有桌面环境的 Ubuntu 上运行；测试可在无头环境下进行（见下文「测试」）。

## 功能

- **主功能界面**：user prompt / system prompt 输入、请求状态计时（等待 / 已发送 / 错误）、报错输出、模型输出框
- **预设切换界面**：通过 `./Presets/<name>.json` 管理预设（标题、模型、System Prompt），点选切换
- **设置窗口**：主页面 / 设置窗口尺寸与字体（支持系统字体选择与 ttf/otf 字体导入）、预设存放目录
- 默认模型 `deepseek-v4-flash`，API 地址、模型名、超时时间均可在 `config.json` 修改

## 配置文件

`config.json`（首次运行前从 `config.example.json` 复制）：

```json
{
  "api": { "base_url": "https://api.deepseek.com", "model": "deepseek-v4-flash",
           "api_key": "", "timeout": 60 },
  "ui": { "main_window_size": [1200, 800], "settings_window_size": [1000, 600],
          "main_title_font": "", "main_body_font": "",
          "settings_title_font": "", "settings_body_font": "" },
  "presets_dir": "./Presets"
}
```

## 开发规范

- 分支：`main`（最新 release）、`feature/<功能>`、`develop/<数字>`（默认开发分支）、`fix/<功能>-<说明>`、`ci/<数字>`（CI/CD 修复分支，验证通过后合并回 develop）、`release/<版本号>`
- 版本号：语义化版本扩展格式 `vX.Y.Z-stage.N`（dev / alpha / beta / rc），正式版为 `vX.Y.Z`
- 版本发布：必须使用 Annotated Tag（`git tag -a`），Tag 名称与版本号一致
- CI/CD：GitHub Actions（`.github/workflows/ci.yml`），lint + 单元测试 + PyInstaller 打包

## 测试

需先激活虚拟环境（或使用 `.venv` 内的解释器）。

```bash
# Windows（已激活 .venv）
pytest

# Ubuntu / Linux（已激活 .venv）
pytest

# Ubuntu 无头环境（无显示器时）
QT_QPA_PLATFORM=offscreen pytest
```
