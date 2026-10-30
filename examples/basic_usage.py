"""Basic offline-safe example; replace placeholders with securely loaded keys."""
from glitch_integrations import GlitchAIEngine, ProviderConfig, IntegrationError

engine = GlitchAIEngine([
    ProviderConfig("google", api_key="YOUR_GEMINI_KEY", enabled=False),
    ProviderConfig("openai", api_key="YOUR_OPENAI_KEY", enabled=False),
])

try:
    result = engine.generate_with_fallback(
        "Summarize the following information.",
        system="Be accurate and concise.",
        prefer_native_search=False,
    )
    print(result["text"])
except IntegrationError as exc:
    print(f"AI request failed: {exc}")
