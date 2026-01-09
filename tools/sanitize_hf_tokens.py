import json
import re
import sys
from pathlib import Path

HF_TOKEN_RE = re.compile(r"hf_[A-Za-z0-9]{10,}")


def _sanitize_obj(obj):
    if isinstance(obj, str):
        return HF_TOKEN_RE.sub("hf_REDACTED", obj)
    if isinstance(obj, list):
        return [_sanitize_obj(x) for x in obj]
    if isinstance(obj, dict):
        return {k: _sanitize_obj(v) for k, v in obj.items()}
    return obj


def sanitize_file(path: Path) -> bool:
    raw = path.read_text(encoding="utf-8")
    data = json.loads(raw)
    sanitized = _sanitize_obj(data)
    out = json.dumps(sanitized, ensure_ascii=False, indent=2)
    changed = out != raw
    if changed:
        path.write_text(out, encoding="utf-8")
    return changed


def main(argv):
    if len(argv) < 2:
        print("Usage: python tools/sanitize_hf_tokens.py <file-or-dir> [...]")
        return 2

    any_changed = False
    for p in argv[1:]:
        path = Path(p)
        if path.is_dir():
            for nb in path.rglob("*.ipynb"):
                if sanitize_file(nb):
                    print(f"Sanitized: {nb}")
                    any_changed = True
        else:
            if sanitize_file(path):
                print(f"Sanitized: {path}")
                any_changed = True

    if not any_changed:
        print("No changes needed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
