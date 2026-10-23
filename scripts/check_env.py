"""Check configuration without ever printing the API key."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))


def main() -> int:
    try:
        from historybot.config import ConfigError, load_config, validate_models
    except ImportError:
        print("Error: dependencies are not installed. Install requirements.txt in the virtualenv.", file=sys.stderr)
        return 1
    try:
        config = load_config()
        print("GOOGLE_API_KEY: set (value hidden)")
        if not config.pdf_path.is_file():
            raise ConfigError(f"PDF missing: {config.pdf_path}")
        validate_models(config)
        print("PDF: present; configured Gemini models: available")
        return 0
    except ConfigError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
