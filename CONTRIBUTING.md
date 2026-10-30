# Contributing

Contributions are welcome. Please keep the integration engine provider-neutral and avoid adding application-specific GUI code to this repository.

## Before opening a pull request

1. Open an issue describing the provider, bug, or enhancement.
2. Keep API keys, tokens, personal settings, and real user data out of commits and tests.
3. Add or update offline unit tests. Tests must not require live API credentials.
4. Update the README and `changelog/CHANGELOG.md` when behavior or public interfaces change.
5. Run `py -m unittest discover -s tests -v`.

## Adding a provider

A provider addition generally requires:

1. A provider entry in `DEFAULTS` in `glitch_integrations/integration_engine.py`.
2. A request/response adapter in `_request_provider` (or a well-isolated helper).
3. A metadata file under `glitch_integrations/providers/`.
4. Schema and manifest updates where appropriate.
5. Mocked tests for successful response parsing, errors, and fallback behavior.
6. Documentation describing model/API limitations and any search capability.

Do not mark a provider's search capability as supported merely because text generation works. Verify the provider's current API documentation and keep account/model restrictions explicit.

## Pull request checklist

- [ ] Tests pass locally.
- [ ] No credentials or secrets are included.
- [ ] Documentation and changelog are updated.
- [ ] New network behavior has timeout and error handling.
- [ ] Compatibility with Python 3.10+ is maintained.
