import os
import sys
from glitch_integrations.integration_engine import IntegrationEngine

def run_provider_tests():
    print("==================================================")
    print(" Glitch Gaming AI Integration Tester (6 Providers)")
    print("==================================================")

    providers = [
        ("Google Gemini", "GEMINI_API_KEY"),
        ("OpenAI / ChatGPT", "OPENAI_API_KEY"),
        ("xAI / Grok", "XAI_API_KEY"),
        ("Anthropic / Claude", "ANTHROPIC_API_KEY"),
        ("Perplexity", "PERPLEXITY_API_KEY"),
        ("DeepSeek", "DEEPSEEK_API_KEY"),
    ]

    engine = IntegrationEngine()

    for name, env_var in providers:
        key = os.getenv(env_var)
        if not key:
            print(f"[SKIP] {name}: '{env_var}' not set in environment.")
            continue

        print(f"\n[TESTING] Connecting to {name}...")
        try:
            response = engine.generate_response(
                prompt="Hello! Respond with 'Ready' if you are receiving this.",
                provider_override=name
            )
            print(f"[PASS] {name} Response: {response.strip()}")
        except Exception as e:
            print(f"[FAIL] {name} Error: {e}")

    print("\n==================================================")
    print(" Testing Fallback Engine...")
    print("==================================================")
    try:
        fallback_res = engine.generate_response_with_fallback(
            prompt="Testing fallback chain."
        )
        print(f"[PASS] Engine Fallback Output: {fallback_res.strip()}")
    except Exception as e:
        print(f"[FAIL] Fallback Execution Error: {e}")

if __name__ == "__main__":
    run_provider_tests()
