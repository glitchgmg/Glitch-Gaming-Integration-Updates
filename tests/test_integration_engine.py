import unittest
from unittest.mock import patch

from glitch_integrations.integration_engine import (
    GlitchAIEngine, ProviderConfig, IntegrationError
)


class IntegrationEngineTests(unittest.TestCase):
    def test_unknown_provider_is_rejected(self):
        with self.assertRaises(ValueError):
            GlitchAIEngine([ProviderConfig("not-a-provider", api_key="x", enabled=True)])

    def test_disabled_or_keyless_provider_is_not_enabled(self):
        engine = GlitchAIEngine([
            ProviderConfig("google", api_key="", enabled=True),
            ProviderConfig("openai", api_key="secret", enabled=False),
        ])
        self.assertEqual(engine.enabled_providers(), [])
        with self.assertRaises(IntegrationError):
            engine.generate_with_fallback("hello")

    def test_fallback_uses_next_provider_after_failure(self):
        engine = GlitchAIEngine([
            ProviderConfig("google", api_key="g-key", enabled=True),
            ProviderConfig("openai", api_key="o-key", enabled=True),
        ])
        def fake_request(cfg, prompt, system, use_search):
            if cfg.provider == "google":
                raise IntegrationError("simulated failure")
            return "successful response"
        with patch.object(engine, "_request_provider", side_effect=fake_request):
            result = engine.generate_with_fallback("hello", prefer_native_search=False)
        self.assertEqual(result["provider"], "openai")
        self.assertEqual(result["text"], "successful response")
        self.assertIn("google", result["errors"])

    def test_provider_order_is_respected(self):
        engine = GlitchAIEngine([
            ProviderConfig("google", api_key="g-key", enabled=True),
            ProviderConfig("openai", api_key="o-key", enabled=True),
        ])
        with patch.object(engine, "_request_provider", return_value="ok") as mocked:
            result = engine.generate_with_fallback(
                "hello", prefer_native_search=False, provider_order=["openai", "google"]
            )
        self.assertEqual(result["provider"], "openai")
        self.assertEqual(mocked.call_args.args[0].provider, "openai")


if __name__ == "__main__":
    unittest.main()
