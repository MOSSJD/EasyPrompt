"""DeepSeek API 客户端（OpenAI 兼容 REST，非流式）与后台 Worker。"""

from __future__ import annotations

import threading

import requests
from PySide6.QtCore import QObject, Signal, Slot


class DeepSeekError(Exception):
    """DeepSeek API 调用异常。"""


class DeepSeekClient:
    """封装 DeepSeek Chat Completions 接口（OpenAI 兼容格式）。"""

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.deepseek.com",
        model: str = "deepseek-v4-flash",
        timeout: int = 60,
    ):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout

    def chat(self, user_prompt: str, system_prompt: str = "") -> str:
        """发送一次非流式对话请求，返回模型回复文本。

        抛出的异常：DeepSeekError（网络/HTTP/业务错误）、ValueError（未配置密钥）。
        """
        if not self.api_key:
            raise ValueError("未配置 API Key，请在 config.json 中填写 api.api_key。")
        if not user_prompt.strip():
            raise ValueError("user prompt 不能为空。")

        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        messages = []
        if system_prompt.strip():
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": user_prompt})
        payload = {"model": self.model, "messages": messages, "stream": False}

        try:
            resp = requests.post(
                url,
                headers=headers,
                json=payload,
                timeout=(min(10, self.timeout), self.timeout),  # (连接, 读取)
            )
        except requests.Timeout as exc:
            raise DeepSeekError(f"请求超时（{self.timeout}s）。") from exc
        except requests.ConnectionError as exc:
            raise DeepSeekError("无法连接 API 服务器，请检查网络或 API 地址。") from exc
        except requests.RequestException as exc:
            raise DeepSeekError(f"请求失败：{exc}") from exc

        if resp.status_code != 200:
            reason = self._extract_error(resp)
            raise DeepSeekError(f"API 错误（HTTP {resp.status_code}）：{reason}")

        try:
            data = resp.json()
            return str(data["choices"][0]["message"]["content"])
        except (KeyError, IndexError, ValueError) as exc:
            raise DeepSeekError("API 响应格式异常，无法解析模型输出。") from exc

    @staticmethod
    def _extract_error(resp: requests.Response) -> str:
        try:
            body = resp.json()
            if isinstance(body, dict):
                err = body.get("error")
                if isinstance(err, dict):
                    return str(err.get("message", err))
                if err:
                    return str(err)
                msg = body.get("message")
                if msg:
                    return str(msg)
        except ValueError:
            pass
        return resp.text[:200] or f"HTTP {resp.status_code}"


class ApiWorker(QObject):
    """后台 API 调用器（Python threading 实现）。

    通过 Qt 信号跨线程回传结果：从子线程 emit 信号会自动排队，
    finished(str) / failed(str) 槽在主线程（UI 线程）执行，线程安全。
    """

    finished = Signal(str)
    failed = Signal(str)

    def __init__(self, client: DeepSeekClient, parent: QObject | None = None):
        super().__init__(parent)
        self._client = client
        self._cancelled = threading.Event()
        self._thread: threading.Thread | None = None

    @Slot(str, str)
    def run(self, user_prompt: str, system_prompt: str) -> None:
        """启动后台线程执行 API 调用（可重复调用，互不阻塞）。"""
        if self._thread is not None and self._thread.is_alive():
            return
        self._thread = threading.Thread(
            target=self._target,
            args=(user_prompt, system_prompt),
            name="api-worker",
            daemon=True,
        )
        self._thread.start()

    def _target(self, user_prompt: str, system_prompt: str) -> None:
        try:
            text = self._client.chat(user_prompt, system_prompt)
            if not self._cancelled.is_set():
                self.finished.emit(text)
        except Exception as exc:  # noqa: BLE001 - 所有异常统一转错误信号
            if not self._cancelled.is_set():
                self.failed.emit(str(exc))

    def cancel(self) -> None:
        """标记取消：请求结束后不再回传结果（任意线程可调用）。"""
        self._cancelled.set()

    def reset(self) -> None:
        """清除取消标记（下次请求前调用）。"""
        self._cancelled.clear()

    def is_busy(self) -> bool:
        return self._thread is not None and self._thread.is_alive()
