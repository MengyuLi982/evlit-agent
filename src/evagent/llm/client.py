from __future__ import annotations

from typing import Any

try:
    from litellm import completion
except Exception:  # pragma: no cover - optional dependency fallback
    completion = None

from evagent.config import Settings


class LLMClient:
    def __init__(self, settings: Settings):
        self.settings = settings

    def chat(self, messages: list[dict[str, str]], temperature: float = 0.1, max_tokens: int = 700) -> str:
        api_key = self.settings.effective_api_key
        api_base = self.settings.effective_api_base

        if completion is None or not api_key:
            # Local fallback so the pipeline still runs without API credentials.
            joined = " ".join(m.get("content", "") for m in messages[-2:])
            return f"[fallback-no-llm] {joined[:500]}"

        model = self.settings.chat_model
        if api_base and "/" not in model:
            # For OpenAI-compatible gateways, LiteLLM works reliably with provider-prefixed model names.
            model = f"openai/{model}"

        resp = completion(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            api_key=api_key,
            api_base=api_base,
        )
        content = resp.choices[0].message.content
        return content if isinstance(content, str) else str(content)

    def summarize_evidence(self, query: str, evidence: list[dict[str, Any]]) -> str:
        if not evidence:
            return "No sufficient evidence found."

        bullets = []
        for item in evidence[:6]:
            title = item.get("title", "unknown")
            snippet = item.get("snippet", "")
            bullets.append(f"- {title}: {snippet[:220]}")

        prompt = [
            {
                "role": "system",
                "content": "You are a careful research assistant. Only answer with grounded claims.",
            },
            {
                "role": "user",
                "content": (
                    f"Question: {query}\n"
                    "Use the evidence below and produce a concise answer with caveats.\n"
                    "Evidence:\n" + "\n".join(bullets)
                ),
            },
        ]
        return self.chat(prompt)
