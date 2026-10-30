# Glitch Gaming AI Integrations

A reusable, modular Python integration layer for connecting applications to multiple AI providers through one consistent interface.

## Overview

Glitch Gaming AI Integrations brings six optional providers together behind a common Python API: Google Gemini, OpenAI / ChatGPT, xAI / Grok, Anthropic / Claude, Perplexity, and DeepSeek. Applications choose which providers to enable, supply their own credentials, select models, and optionally use ordered provider fallback when a request fails.

The project is designed for the Glitch Gaming ecosystem and third-party Python applications alike. It can support AI-powered summarization, research assistance, content analysis, troubleshooting, and other application-defined workflows. It is an integration layer—not a finished chatbot, user interface, search engine, or language-independent SDK.

**Goal:** One integration engine. Multiple AI providers. Smarter applications.

## Features

- Common Python interface for six optional AI providers.
- Per-provider enablement, API key, model, endpoint, and timeout configuration.
- Ordered fallback across enabled providers.
- Provider-specific request and response handling.
- Optional native-search request flags where represented by the provider adapter.
- Separate DeepSeek Search/Fetch adapter (availability must be verified with the provider).
- Local settings helpers and JSON configuration schemas.
- Standard-library implementation; no third-party runtime dependencies.

## Repository layout

```text
Glitch-Gaming-Integration-Updates/
├── README.md
├── CONTRIBUTING.md
├── LICENSE
├── pyproject.toml
├── .gitignore
├── .github/
│   └── workflows/tests.yml
├── changelog/
│   └── CHANGELOG.md
├── examples/
│   └── basic_usage.py
├── tests/
│   └── test_integration_engine.py
└── glitch_integrations/
    ├── __init__.py
    ├── integration_engine.py
    ├── manifest.json
    ├── providers/
    ├── search/
    └── schemas/
```

## Requirements

- Python 3.10 or newer.
- An API key and account access for each provider you choose to use.
- Internet access for live provider requests.

The package uses Python's standard library at runtime. No `requirements.txt` is necessary.

## Installation

### Option A: Install from a cloned repository

```bash
git clone https://github.com/glitchgmg/Glitch-Gaming-Integration-Updates.git
cd Glitch-Gaming-Integration-Updates
py -m pip install .
```

### Option B: Copy into an existing Python project

Copy the complete `glitch_integrations` directory into your project. Keep its internal folder structure intact. Your application can then import `glitch_integrations` from its project root.

### Option C: Editable development install

```bash
py -m pip install -e .
```

## Quick start

```python
from glitch_integrations import GlitchAIEngine, ProviderConfig

engine = GlitchAIEngine([
    ProviderConfig("google", api_key="YOUR_GEMINI_KEY", enabled=True),
    ProviderConfig("openai", api_key="YOUR_OPENAI_KEY", enabled=True),
    ProviderConfig("xai", api_key="YOUR_XAI_KEY", enabled=False),
    ProviderConfig("anthropic", api_key="YOUR_ANTHROPIC_KEY", enabled=False),
    ProviderConfig("perplexity", api_key="YOUR_PERPLEXITY_KEY", enabled=False),
    ProviderConfig("deepseek", api_key="YOUR_DEEPSEEK_KEY", enabled=False),
])

result = engine.generate_with_fallback(
    "Summarize this information for the user.",
    system="Be accurate and concise.",
    prefer_native_search=False,
)

print(result["text"])
print("Provider:", result["display_name"])
print("Model:", result["model"])
```

The example uses placeholder credentials. Replace them with values loaded securely at runtime. Do not hardcode real keys in source code.

## Integrating with any Python application

The engine does not depend on a particular GUI or application framework. A developer can call it from a desktop app, command-line utility, web backend, automation script, or another Python service. The host application is responsible for: (1) collecting provider preferences, (2) securely storing credentials, (3) constructing `ProviderConfig` objects, (4) calling the engine, and (5) displaying or otherwise using the returned result.

Typical integration sequence:

1. Add/install the `glitch_integrations` package.
2. Read the user's enabled providers, model choices, and API keys from the host application's settings.
3. Create one `ProviderConfig` for each provider. Disabled providers or providers without keys are skipped.
4. Initialize `GlitchAIEngine` and call `generate_with_fallback(...)`.
5. Use the returned `text`, `provider`, `display_name`, `model`, `used_native_search`, and `errors` fields as appropriate.
6. Handle `IntegrationError` when no provider is enabled or all enabled providers fail.

For Tkinter or other event-driven desktop interfaces, run network calls in a worker thread and marshal results back to the UI thread. The engine is synchronous and does not manage UI state.

### Example application use cases

- Desktop applications: explanations, summaries, assistants, and analysis features.
- Game utilities: patch-note summaries, update research, and game information analysis.
- Research tools: summarize retrieved sources and compare information.
- Automation: classify, transform, or summarize text within existing workflows.
- Web backends: provide a common AI-provider layer behind application endpoints.
- Developer tools: documentation assistance, code explanations, and troubleshooting.

These are examples of how an application may use the library; they are not standalone features automatically supplied by the package.

## Search behavior and limitations

`prefer_native_search=True` asks the selected provider adapter to include its configured native-search option when that adapter supports it. This does not guarantee that the selected model, account, endpoint, or API plan permits search. Provider API behavior and model identifiers change; verify current provider documentation and test the exact model/account combination.

If search is unavailable or fails, the engine's provider fallback is not a general-purpose external search fallback. The host application must integrate a separate search service, retrieve source material, and pass relevant excerpts and URLs to the AI model. The included DeepSeek Search/Fetch adapter is optional and its endpoint/account availability must be confirmed before relying on it. Other search policy JSON files are configuration references, not fully implemented search-service clients.

Treat retrieved pages and model responses as untrusted input. Prefer official sources for factual claims and retain source URLs.

## Credentials and security

- Supply API keys at runtime. Never commit real credentials to GitHub.
- Prefer Windows Credential Manager, another OS credential store, or a managed secrets service. Environment variables can be suitable for development/deployment.
- The local settings helpers write JSON to a path chosen by the host application; protect that file with appropriate OS permissions. They are not an encrypted vault.
- Avoid logging API keys, authorization headers, or sensitive prompts.
- Validate downloaded configuration and use HTTPS. Never execute downloaded configuration as code.
- SHA-256 hashes in an unsigned manifest do not authenticate the manifest. Production auto-updaters should verify a detached digital signature using a trusted public key embedded in the application.

## Tests

Run the offline unit tests (no API keys or network calls required):

```bash
py -m unittest discover -s tests -v
```

The tests cover basic configuration and fallback behavior using mocked provider responses. They do not establish that live provider APIs, model IDs, or search entitlements are currently available. Live connectivity tests require valid provider credentials and should be run separately.

## Compatibility

- Python 3.10+
- Runtime dependencies: Python standard library only
- Synchronous HTTP requests
- Provider endpoints, model IDs, request formats, and search entitlements may change

## License

See [LICENSE](LICENSE).
