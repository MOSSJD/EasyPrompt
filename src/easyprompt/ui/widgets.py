"""通用 UI 组件：灰白主题样式、状态计时器、报错输出、滚动区。"""

from __future__ import annotations

from enum import Enum

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import (
    QLabel,
    QScrollArea,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

# ---- 灰白主题色板 ----
COLOR_BG = "#F5F5F5"          # 窗口背景（浅灰白）
COLOR_PANEL = "#FFFFFF"       # 面板/输入区背景
COLOR_BORDER = "#D9D9D9"      # 边框
COLOR_TEXT = "#333333"        # 正文
COLOR_TITLE = "#1F1F1F"       # 标题
COLOR_MUTED = "#999999"       # 次要文字（默认"报错输出"）
COLOR_ACTIVE = "#5B7A9D"      # 激活高亮（灰蓝）
COLOR_HOVER = "#E8EEF5"       # 悬停背景
COLOR_ERROR = "#C0392B"       # 错误红

_TITLE_BOLD = "font-weight: bold;"


def title_style(size: int = 14) -> str:
    """标题字号 + 加粗样式。"""
    return f"font-size: {size}pt; {_TITLE_BOLD} color: {COLOR_TITLE};"


def body_style(size: int = 10) -> str:
    """正文字号样式。"""
    return f"font-size: {size}pt; color: {COLOR_TEXT};"


class StatusTimer(QWidget):
    """状态计时器：三态显示【等待 / 已发送 mm:ss / 错误 mm:ss】。"""

    class Status(Enum):
        WAITING = "等待"
        SENT = "已发送"
        ERROR = "错误"

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self._status = self.Status.WAITING
        self._elapsed = 0
        self._label = QLabel(self)
        self._label.setStyleSheet(body_style())
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.addWidget(self._label)
        self._timer = QTimer(self)
        self._timer.setInterval(1000)
        self._timer.timeout.connect(self._tick)
        self._render()

    # ---- 状态切换 ----
    def set_waiting(self) -> None:
        self._timer.stop()
        self._status = self.Status.WAITING
        self._elapsed = 0
        self._render()

    def set_sent(self) -> None:
        self._status = self.Status.SENT
        self._elapsed = 0
        self._render()
        self._timer.start()

    def set_error(self) -> None:
        self._timer.stop()
        self._status = self.Status.ERROR
        self._render()

    @property
    def status(self) -> "StatusTimer.Status":
        return self._status

    @property
    def elapsed(self) -> int:
        return self._elapsed

    def _tick(self) -> None:
        self._elapsed += 1
        self._render()

    def _render(self) -> None:
        if self._status is self.Status.WAITING:
            text = "等待"
            color = COLOR_MUTED
        else:
            mm, ss = divmod(self._elapsed, 60)
            text = f"{self._status.value} {mm:02d}:{ss:02d}"
            color = COLOR_ERROR if self._status is self.Status.ERROR else COLOR_ACTIVE
        self._label.setText(text)
        self._label.setStyleSheet(f"color: {color}; {body_style()}")


class ErrorLabel(QTextEdit):
    """报错输出（只读）：默认灰色"报错输出"，出错时显示简洁错误信息。"""

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setFrameShape(QTextEdit.NoFrame)
        self.setStyleSheet(
            f"background: {COLOR_PANEL}; color: {COLOR_MUTED};"
            f"border: 1px solid {COLOR_BORDER}; {body_style()}"
        )
        self.setPlaceholderText("")
        self.clear_error()

    def show_error(self, message: str) -> None:
        self.setPlainText(message)
        self.setStyleSheet(
            f"background: {COLOR_PANEL}; color: {COLOR_ERROR};"
            f"border: 1px solid {COLOR_BORDER}; {body_style()}"
        )

    def clear_error(self) -> None:
        self.setPlainText("报错输出")
        self.setStyleSheet(
            f"background: {COLOR_PANEL}; color: {COLOR_MUTED};"
            f"border: 1px solid {COLOR_BORDER}; {body_style()}"
        )


class ScrollArea(QScrollArea):
    """通用滚动区：内容自适应宽度，鼠标悬停时滚轮滚动（Qt 默认行为）。"""

    def __init__(self, content: QWidget, parent: QWidget | None = None):
        super().__init__(parent)
        self.setWidgetResizable(True)
        self.setFrameShape(QScrollArea.NoFrame)
        self.setStyleSheet(f"background: {COLOR_PANEL}; border: 1px solid {COLOR_BORDER};")
        self.setWidget(content)


def title_label(text: str, size: int = 14) -> QLabel:
    """创建标题 QLabel：加粗 + role=title（供字体主题规则匹配）。"""
    label = QLabel(text)
    label.setProperty("role", "title")
    label.setStyleSheet(title_style(size))
    return label


def apply_theme(widget: QWidget, fonts: dict[str, str] | None = None) -> None:
    """给窗口应用灰白主题基础样式（可按配置覆盖标题/正文字体）。"""
    title_font = fonts.get("title") if fonts else None
    body_font = fonts.get("body") if fonts else None
    qss = f"""
    QWidget {{ background: {COLOR_BG}; color: {COLOR_TEXT}; font-size: 10pt; }}
    QLabel {{ background: transparent; }}
    QTextEdit, QPlainTextEdit, QLineEdit {{
        background: {COLOR_PANEL};
        border: 1px solid {COLOR_BORDER};
        border-radius: 4px;
        padding: 4px;
        selection-background-color: {COLOR_HOVER};
    }}
    QTextEdit:focus, QPlainTextEdit:focus, QLineEdit:focus {{
        border: 1px solid {COLOR_ACTIVE};
    }}
    QPushButton {{
        background: {COLOR_PANEL};
        border: 1px solid {COLOR_BORDER};
        border-radius: 4px;
        padding: 4px 12px;
    }}
    QPushButton:hover {{ background: {COLOR_HOVER}; }}
    QPushButton:pressed {{ background: {COLOR_BORDER}; }}
    QToolButton {{ background: transparent; border: none; border-radius: 4px; }}
    QToolButton:hover {{ background: {COLOR_HOVER}; }}
    QComboBox, QSpinBox {{
        background: {COLOR_PANEL};
        border: 1px solid {COLOR_BORDER};
        border-radius: 4px;
        padding: 2px 8px;
    }}
    QScrollBar:vertical {{ background: transparent; width: 10px; }}
    QScrollBar::handle:vertical {{ background: {COLOR_BORDER}; border-radius: 5px;
        min-height: 24px; }}
    QScrollBar::handle:vertical:hover {{ background: {COLOR_ACTIVE}; }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
    """
    if body_font:
        qss += f"\nQWidget {{ font-family: \"{body_font}\"; }}"
    if title_font:
        qss += (
            f"\nQLabel[role=\"title\"] {{ font-family: \"{title_font}\"; {_TITLE_BOLD} }}"
        )
    widget.setStyleSheet(qss)
