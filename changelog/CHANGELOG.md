# Glitch Gaming Integration Updates

All notable integration-engine and provider-configuration changes are documented here.

## [2.0.1] - 2026-10-30

### Added
- General-purpose installation and integration instructions for third-party Python applications.
- Package metadata for standard and editable local installation.
- Offline unit tests for provider validation, enablement, fallback, and provider ordering.
- GitHub Actions workflow to run the test suite on Python 3.10–3.13.
- Contributor guidance and a basic usage example.

### Improved
- Reorganized documentation around the reusable Python package rather than only the game tracker.
- Exported the main engine classes and helpers from the package root.
- Clarified that native-search flags and separate search adapters are subject to provider/API availability.
- Clarified that local JSON settings are not encrypted credential storage.

### Validation
- Offline unit tests do not make live API requests. Provider credentials, live model access, and search entitlements still require separate testing.

## [2.0.0] - 2026-10-29

### Added
- Anthropic / Claude provider configuration.
- Perplexity provider configuration.
- DeepSeek provider configuration.
- Shared Python AI integration engine with provider-specific request adapters.
- User-controlled enable/disable and model selection for each provider.
- Ordered AI-provider fallback when a configured provider fails.
- Native-search capability metadata for supported provider families.
- Separate DeepSeek Search/Fetch adapter.
- Search fallback policy configuration.
- Provider and manifest JSON schemas.
- Example integration instructions for the Universal Game Update Tracker.
- Provider-level connectivity test helper.

### Improved
- Expanded the original Google Gemini, OpenAI / ChatGPT, and xAI / Grok configuration set.
- Centralized request handling, timeout handling, error reporting, and response extraction.
- Provider API keys are supplied at runtime and are not included in repository configuration.

### Security
- API keys are not stored in provider JSON files or the public manifest.
- Local settings helper writes only to a user-selected local path.
- Public configuration downloads should be HTTPS-only and schema-validated.
- SHA-256 hashes alone are not sufficient against a malicious manifest replacement; production
  auto-updates must verify a detached signature using a public key embedded in the application.
- Downloaded configuration must never be executed as code.

### Compatibility and limitations
- The integration engine uses Python's standard library and is intended for Python 3.10+.
- Default model IDs are starting defaults and may change or require account-specific access.
- Provider APIs and native search tools are provider/model/account dependent; live API access
  was not tested as part of packaging.
- DeepSeek Search/Fetch is included as an optional adapter, subject to account/API availability.
- Cloudflare and Parallel search are not wired into this release; the search manager interface
  can be extended when their exact account/API configuration is selected.
- The engine is synchronous. Tkinter callers must run requests in a background worker thread.
- This package is a reusable integration module, not a direct edit of the tracker GUI. The
  current tracker source file was not included in the uploaded ZIP, so its Settings screen,
  saved preferences, and patch-note call sites have not been modified.

## [1.0.0] - 2026-10-29

### Added
- Initial Google Gemini provider configuration.
- Initial OpenAI / ChatGPT provider configuration.
- Initial xAI / Grok provider configuration.
- Initial integration schema and changelog.
