# Easy Prompt

一个运行在 Windows 10/11 64 位的 DeepSeek API 桌面小工具：输入 user prompt 与 system prompt，调用 DeepSeek 大模型并将输出展示在输出框。

## 环境要求

- Python 3.13+
- Windows 10 64 位（开发环境）

## 快速开始

```bash
# 1. 创建虚拟环境并安装依赖
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements-dev.txt

# 2. 配置 API 密钥（本地保存，不入库）
copy config.example.json config.json
# 编辑 config.json，在 api.api_key 中填入你的 DeepSeek API Key

# 3. 运行
python -m easyprompt.main
```

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

- 分支：`main`（最新 release）、`feature/<功能>`、`develop/<数字>`（默认开发分支）、`fix/<功能>-<说明>`、`release/<版本号>`
- 版本号：语义化版本扩展格式 `vX.Y.Z-stage.N`（dev / alpha / beta / rc），正式版为 `vX.Y.Z`
- 版本发布：必须使用 Annotated Tag（`git tag -a`），Tag 名称与版本号一致
- CI/CD：GitHub Actions（`.github/workflows/ci.yml`），lint + 单元测试 + PyInstaller 打包

## 测试

```bash
pytest
```
