"""
Glitch Gaming Shared AI Integration Engine
Python 3.10+; standard library only.

This module is intentionally separate from the Tkinter application. Import it,
configure enabled providers with API keys, then call generate_with_fallback().
No credentials are read from or written to the public GitHub configuration repo.
"""
from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Optional


DEFAULTS = {
    "google": {
        "name": "Google Gemini",
        "endpoint": "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
        "model": "gemini-2.5-flash",
        "format": "gemini",
        "native_search": True,
    },
    "openai": {
        "name": "OpenAI / ChatGPT",
        "endpoint": "https://api.openai.com/v1/responses",
        "model": "gpt-4.1-mini",
        "format": "responses",
        "native_search": True,
    },
    "xai": {
        "name": "xAI / Grok",
        "endpoint": "https://api.x.ai/v1/responses",
        "model": "grok-3-latest",
        "format": "responses",
        "native_search": True,
    },
    "anthropic": {
        "name": "Anthropic / Claude",
        "endpoint": "https://api.anthropic.com/v1/messages",
        "model": "claude-sonnet-4-20250514",
        "format": "anthropic",
        "native_search": True,
    },
    "perplexity": {
        "name": "Perplexity",
        "endpoint": "https://api.perplexity.ai/chat/completions",
        "model": "sonar",
        "format": "chat_completions",
        "native_search": True,
    },
    "deepseek": {
        "name": "DeepSeek",
        "endpoint": "https://api.deepseek.com/chat/completions",
        "model": "deepseek-chat",
        "format": "chat_completions",
        "native_search": False,
    },
}


class IntegrationError(RuntimeError):
    pass


@dataclass
class ProviderConfig:
    provider: str
    api_key: str = ""
    enabled: bool = False
    model: str = ""
    endpoint: str = ""
    native_search: Optional[bool] = None
    timeout: int = 45
    extra: Dict[str, Any] = field(default_factory=dict)


class GlitchAIEngine:
    """Optional provider manager with ordered AI fallback."""

    def __init__(self, providers: Optional[Iterable[ProviderConfig]] = None):
        self.providers: Dict[str, ProviderConfig] = {}
        self.last_errors: Dict[str, str] = {}
        for cfg in providers or []:
            self.configure(cfg)

    def configure(self, config: ProviderConfig) -> None:
        key = config.provider.lower().strip()
        if key not in DEFAULTS:
            raise ValueError(f"Unsupported AI provider: {key}")
        config.provider = key
        if not config.model:
            config.model = DEFAULTS[key]["model"]
        if not config.endpoint:
            config.endpoint = DEFAULTS[key]["endpoint"]
        self.providers[key] = config

    def set_provider(self, provider: str, *, api_key: str,
                     enabled: bool = True, model: str = "") -> None:
        self.configure(ProviderConfig(provider=provider, api_key=api_key,
                                      enabled=enabled, model=model))

    def enabled_providers(self) -> List[ProviderConfig]:
        return [p for p in self.providers.values()
                if p.enabled and p.api_key.strip()]

    @staticmethod
    def _post(url: str, headers: Dict[str, str], payload: Dict[str, Any],
              timeout: int) -> Dict[str, Any]:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=timeout) as response:
                raw = response.read().decode("utf-8", errors="replace")
                parsed = json.loads(raw) if raw else {}
                if response.status >= 400:
                    raise IntegrationError(f"HTTP {response.status}: {raw[:500]}")
                return parsed
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            raise IntegrationError(f"HTTP {exc.code}: {body[:700]}") from exc
        except (urllib.error.URLError, TimeoutError) as exc:
            raise IntegrationError(str(exc)) from exc
        except json.JSONDecodeError as exc:
            raise IntegrationError("Provider returned invalid JSON.") from exc

    def _request_provider(self, cfg: ProviderConfig, prompt: str,
                          system: str, use_native_search: bool) -> str:
        provider = cfg.provider
        defaults = DEFAULTS[provider]
        model = cfg.model or defaults["model"]
        endpoint = cfg.endpoint or defaults["endpoint"]
        headers = {"Content-Type": "application/json"}
        fmt = defaults["format"]

        if provider == "google":
            url = endpoint.format(model=model) + "?key=" + cfg.api_key
            body: Dict[str, Any] = {
                "systemInstruction": {"parts": [{"text": system}]},
                "contents": [{"role": "user", "parts": [{"text": prompt}]}],
                "generationConfig": {"temperature": 0.2},
            }
            if use_native_search:
                body["tools"] = [{"google_search": {}}]
            result = self._post(url, headers, body, cfg.timeout)
            try:
                return "".join(p.get("text", "") for p in
                               result["candidates"][0]["content"]["parts"]).strip()
            except (KeyError, IndexError, TypeError):
                raise IntegrationError(f"Gemini returned no text: {str(result)[:500]}")

        headers["Authorization"] = f"Bearer {cfg.api_key}"
        if provider == "openai" or provider == "xai":
            body = {"model": model, "input": [
                {"role": "system", "content": [{"type": "input_text", "text": system}]},
                {"role": "user", "content": [{"type": "input_text", "text": prompt}]}
            ]}
            if use_native_search:
                body["tools"] = [{"type": "web_search"}]
            result = self._post(endpoint, headers, body, cfg.timeout)
            if result.get("output_text"):
                return result["output_text"].strip()
            chunks = []
            for item in result.get("output", []):
                for part in item.get("content", []):
                    if part.get("type") in ("output_text", "text"):
                        chunks.append(part.get("text", ""))
            if chunks:
                return "\n".join(chunks).strip()
            raise IntegrationError(f"{defaults['name']} returned no text: {str(result)[:500]}")

        if provider == "anthropic":
            headers.update({"x-api-key": cfg.api_key, "anthropic-version": "2023-06-01"})
            headers.pop("Authorization", None)
            body = {"model": model, "max_tokens": 1800, "system": system,
                    "messages": [{"role": "user", "content": prompt}]}
            if use_native_search:
                body["tools"] = [{"type": "web_search_20250305", "name": "web_search",
                                  "max_uses": 5}]
            result = self._post(endpoint, headers, body, cfg.timeout)
            text_parts = [x.get("text", "") for x in result.get("content", [])
                          if x.get("type") == "text"]
            if not text_parts:
                raise IntegrationError(f"Claude returned no text: {str(result)[:500]}")
            return "\n".join(text_parts).strip()

        if provider in ("perplexity", "deepseek"):
            body = {"model": model, "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": prompt}
            ], "temperature": 0.2}
            result = self._post(endpoint, headers, body, cfg.timeout)
            try:
                return result["choices"][0]["message"]["content"].strip()
            except (KeyError, IndexError, AttributeError, TypeError):
                raise IntegrationError(f"{defaults['name']} returned no text: {str(result)[:500]}")

        raise IntegrationError(f"No request adapter for {provider}")

    def generate_with_fallback(self, prompt: str, system: str = (
        "You are the Glitch Gaming research assistant. Be accurate, concise, "
        "distinguish confirmed facts from uncertainty, and include source URLs "
        "when available."
    ), *, prefer_native_search: bool = True,
       provider_order: Optional[List[str]] = None) -> Dict[str, Any]:
        """Return {provider, model, text, used_native_search, errors}."""
        enabled = {p.provider: p for p in self.enabled_providers()}
        order = provider_order or list(DEFAULTS.keys())
        order = [name for name in order if name in enabled]
        if not order:
            raise IntegrationError("No enabled AI provider has an API key configured.")

        errors: Dict[str, str] = {}
        for name in order:
            cfg = enabled[name]
            native_supported = DEFAULTS[name]["native_search"]
            if cfg.native_search is not None:
                native_supported = cfg.native_search
            use_search = bool(prefer_native_search and native_supported)
            try:
                answer = self._request_provider(cfg, prompt, system, use_search)
                self.last_errors = errors
                return {"provider": name, "display_name": DEFAULTS[name]["name"],
                        "model": cfg.model, "text": answer,
                        "used_native_search": use_search, "errors": errors}
            except Exception as exc:
                errors[name] = str(exc)
        self.last_errors = errors
        raise IntegrationError("All enabled AI providers failed: " +
                               " | ".join(f"{k}: {v}" for k, v in errors.items()))

    def test_provider(self, provider: str) -> Dict[str, Any]:
        """Perform a small live test; requires an enabled provider and a valid key."""
        result = self.generate_with_fallback(
            "Reply with exactly: Glitch Gaming connection successful.",
            system="You are performing a connectivity test. Follow the user instruction exactly.",
            prefer_native_search=False, provider_order=[provider.lower()])
        return result


class DeepSeekSearch:
    """Optional separate DeepSeek Search/Fetch adapter.

    Enable only if your DeepSeek account/API key has access to these endpoints.
    """

    def __init__(self, api_key: str, timeout: int = 30,
                 search_url: str = "https://api.deepseek.com/v1/tools/search",
                 fetch_url: str = "https://api.deepseek.com/v1/tools/fetch"):
        self.api_key = api_key
        self.timeout = timeout
        self.search_url = search_url
        self.fetch_url = fetch_url

    def _call(self, url: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        return GlitchAIEngine._post(
            url, {"Content-Type": "application/json",
                  "Authorization": f"Bearer {self.api_key}"},
            payload, self.timeout)

    def search(self, query: str) -> Dict[str, Any]:
        return self._call(self.search_url, {"query": query})

    def fetch(self, url: str) -> Dict[str, Any]:
        return self._call(self.fetch_url, {"url": url})


def load_local_settings(path: str) -> Dict[str, Any]:
    """Load local settings. Protect this file with Windows user permissions."""
    if not os.path.exists(path):
        return {"providers": {}, "search": {}}
    with open(path, "r", encoding="utf-8") as stream:
        return json.load(stream)


def save_local_settings(path: str, settings: Dict[str, Any]) -> None:
    """Save local settings; never upload this file to GitHub."""
    folder = os.path.dirname(os.path.abspath(path))
    os.makedirs(folder, exist_ok=True)
    temp_path = path + ".tmp"
    with open(temp_path, "w", encoding="utf-8") as stream:
        json.dump(settings, stream, indent=2)
    os.replace(temp_path, path)


def engine_from_settings(settings: Dict[str, Any]) -> GlitchAIEngine:
    engine = GlitchAIEngine()
    for name, item in settings.get("providers", {}).items():
        engine.set_provider(name, api_key=item.get("api_key", ""),
                            enabled=bool(item.get("enabled", False)),
                            model=item.get("model", ""))
    return engine
