"""主功能界面：输入栏（user/system prompt）、提示栏（状态计时 + 报错输出）、模型输出框。"""

from __future__ import annotations

from PySide6.QtCore import Qt, QThread, QTimer, Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from ..api_client import ApiWorker
from .widgets import (
    COLOR_MUTED,
    ErrorLabel,
    StatusTimer,
    title_label,
)


class ChatPage(QWidget):
    """主功能界面：输入 → 调用 API → 输出展示。"""

    # 跨线程触发 worker（Qt 自动队列连接至子线程）
    request_signal = Signal(str, str)

    def __init__(self, config, api_client, parent: QWidget | None = None):
        super().__init__(parent)
        self._config = config
        self._api_client = api_client
        self._busy = False
        self._build_ui()

        # API 子线程（常驻）
        self._thread = QThread(self)
        self._worker = ApiWorker(api_client)
        self._worker.moveToThread(self._thread)
        self._thread.start()
        self.request_signal.connect(self._worker.run)
        self._worker.finished.connect(self._on_finished)
        self._worker.failed.connect(self._on_failed)

        # 超时兜底（requests 超时之外的第二道保险）
        self._watchdog = QTimer(self)
        self._watchdog.setSingleShot(True)
        self._watchdog.timeout.connect(self._on_watchdog_timeout)

    # ---- UI 构建 ----
    def _build_ui(self) -> None:
        # 输入栏：左右 2:1
        self.user_input = self._make_input("user prompt")
        self.system_input = self._make_input("system prompt")
        input_row = QHBoxLayout()
        input_row.addWidget(self.user_input, 2)
        input_row.addWidget(self.system_input, 1)

        # 提示栏：状态计时器 1/4 + 报错输出 3/4
        self.status_timer = StatusTimer()
        self.error_label = ErrorLabel()
        status_row = QHBoxLayout()
        status_row.addWidget(self.status_timer, 1)
        status_row.addWidget(self.error_label, 3)

        # 模型输出框
        output_title = title_label("输出")
        self.output_box = QTextEdit()
        self.output_box.setReadOnly(True)

        # 发送按钮
        self.send_button = QPushButton("发送")
        self.send_button.setFixedWidth(96)
        self.send_button.setShortcut(Qt.Key_Return | Qt.KeyboardModifier.ControlModifier)
        self.send_button.clicked.connect(self.on_send)
        button_row = QHBoxLayout()
        button_row.addStretch(1)
        button_row.addWidget(self.send_button)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)
        layout.addLayout(input_row, 2)
        layout.addLayout(status_row, 0)
        layout.addWidget(output_title, 0)
        layout.addWidget(self.output_box, 3)
        layout.addLayout(button_row, 0)

    @staticmethod
    def _make_input(title: str) -> QWidget:
        container = QWidget()
        label = QLabel(title)
        label.setStyleSheet(f"color: {COLOR_MUTED}; font-size: 9pt;")
        editor = QTextEdit()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        layout.addWidget(label, 0)
        layout.addWidget(editor, 1)
        return container

    # ---- 发送流程 ----
    def on_send(self) -> None:
        if self._busy:
            self.error_label.show_error("上一条请求尚未完成，请稍候。")
            self.status_timer.set_error()
            return
        user_prompt = self.user_input.findChild(QTextEdit).toPlainText().strip()
        if not user_prompt:
            self.error_label.show_error("user prompt 不能为空。")
            self.status_timer.set_error()
            return
        if not self._config.api_key:
            self.error_label.show_error("未配置 API Key，请在 config.json 中填写 api.api_key。")
            self.status_timer.set_error()
            return

        system_prompt = self.system_input.findChild(QTextEdit).toPlainText()
        self.error_label.clear_error()
        self.status_timer.set_sent()
        self.send_button.setEnabled(False)
        self._busy = True

        # 启动超时兜底（超时 = 配置值 + 10s 缓冲）
        self._watchdog.start((self._config.timeout + 10) * 1000)

        self._worker.reset()
        self.request_signal.emit(user_prompt, system_prompt)

    def _on_finished(self, text: str) -> None:
        self._watchdog.stop()
        self.output_box.setPlainText(text)
        self.status_timer.set_waiting()
        self.send_button.setEnabled(True)
        self._busy = False

    def _on_failed(self, message: str) -> None:
        self._watchdog.stop()
        self.error_label.show_error(message)
        self.status_timer.set_error()
        self.send_button.setEnabled(True)
        self._busy = False

    def _on_watchdog_timeout(self) -> None:
        self._worker.cancel()
        self.error_label.show_error("等待响应超时，请求已取消。")
        self.status_timer.set_error()
        self.send_button.setEnabled(True)
        self._busy = False

    # ---- 预设联动 ----
    def set_system_prompt(self, text: str) -> None:
        """切换预设时填充 system prompt 输入框。"""
        self.system_input.findChild(QTextEdit).setPlainText(text)

    def closeEvent(self, event) -> None:  # noqa: N802 (Qt 命名)
        self._thread.quit()
        self._thread.wait(2000)
        super().closeEvent(event)
