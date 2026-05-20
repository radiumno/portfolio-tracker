"""LLM 客户端 — 基于 httpx 的 OpenAI 兼容接口"""

from typing import Optional
import json
import httpx
from config.settings import settings


class LLMClient:
    """DeepSeek / OpenAI 兼容 LLM 客户端

    支持 DeepSeek、OpenAI 以及其他 OpenAI 兼容 API。
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        timeout: int = 60,
    ):
        self.api_key = settings.deepseek_api_key if api_key is None else (api_key or "")
        self.base_url = (base_url or settings.deepseek_base_url).rstrip("/")
        self.model = model or settings.deepseek_model
        self.timeout = timeout

    @property
    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def chat(
        self,
        messages: list[dict],
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> str:
        """调用 LLM 聊天补全接口

        参数:
            messages: OpenAI 格式消息列表 [{"role":..., "content":...}]
            temperature: 采样温度
            max_tokens: 最大生成长度
        返回:
            模型回复文本
        """
        if not self.api_key:
            return "未配置 API Key，无法调用 LLM。"

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        try:
            with httpx.Client(timeout=self.timeout) as client:
                resp = client.post(
                    f"{self.base_url}/v1/chat/completions",
                    headers=self._headers,
                    json=payload,
                )
                resp.raise_for_status()
                data = resp.json()
                return data["choices"][0]["message"]["content"]
        except httpx.HTTPStatusError as e:
            return f"API 请求失败 (HTTP {e.response.status_code}): {e.response.text[:200]}"
        except httpx.TimeoutException:
            return "API 请求超时，请检查网络连接"
        except Exception as e:
            return f"API 调用异常: {e}"

    def chat_json(
        self,
        messages: list[dict],
        temperature: float = 0.3,
        max_tokens: int = 2048,
    ) -> dict:
        """调用 LLM 并解析 JSON 格式回复"""
        result = self.chat(
            messages=[
                *messages,
                {"role": "system", "content": "你必须以 JSON 格式回复，不要包含 markdown 代码块标记。"},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        # 尝试提取 JSON
        result = result.strip()
        if result.startswith("```"):
            result = result.split("\n", 1)[-1]
            result = result.rsplit("```", 1)[0]
        result = result.strip()

        try:
            return json.loads(result)
        except json.JSONDecodeError:
            return {"error": "LLM 返回非 JSON 格式", "raw": result[:500]}
