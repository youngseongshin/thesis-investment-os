# Contributing

Contributions are welcome if they keep Thesis OS explicit, auditable, and safe.

## Good Contributions

- Schema improvements
- Public sample adapters
- Better vault templates
- Better feedback metrics
- Documentation that clarifies agent boundaries
- Tests for judgment objects and runtime behavior

## Do Not Contribute

- Real account data
- API keys
- Cookies or OAuth sessions
- Private Telegram channel IDs
- Paid raw data
- Private company documents
- Unlicensed scraped data

## Development Setup

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e .
python -m thesis_os lint --root .
python -m thesis_os demo --out /tmp/thesis-os-demo
python -m unittest discover -s tests
```

To regenerate README visual assets:

```bash
python -m pip install -e ".[assets]"
python scripts/render_assets.py
```

## Design Standard

New features should answer:

1. Which agent owns this?
2. What object does it create or update?
3. What evidence does it require?
4. What is the public/private data boundary?
5. How can the output be checked later?
