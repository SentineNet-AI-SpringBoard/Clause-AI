import argparse
import json
import re
from pathlib import Path


PCSK_RE = re.compile(r"pcsk_[A-Za-z0-9_-]{10,}")
HF_RE = re.compile(r"hf_[A-Za-z0-9_-]{10,}")


def _redact_string(s: str) -> str:
    s = PCSK_RE.sub("pcsk_REDACTED", s)
    s = HF_RE.sub("hf_REDACTED", s)
    return s


def _redact_obj(obj):
    if isinstance(obj, str):
        return _redact_string(obj)
    if isinstance(obj, list):
        return [_redact_obj(x) for x in obj]
    if isinstance(obj, dict):
        return {k: _redact_obj(v) for k, v in obj.items()}
    return obj


def sanitize_notebook(path: Path) -> bool:
    raw = path.read_text(encoding="utf-8")
    nb = json.loads(raw)

    changed = False

    # Replace hardcoded Pinecone API key assignment in code cell sources.
    for cell in nb.get("cells", []):
        if cell.get("cell_type") != "code":
            continue
        src = cell.get("source")
        if not isinstance(src, list):
            continue

        new_src = []
        for line in src:
            if isinstance(line, str) and "PINECONE_API_KEY" in line and "pcsk_" in line:
                new_src.append('PINECONE_API_KEY = (os.getenv("PINECONE_API_KEY") or "").strip()\n')
                new_src.append('if not PINECONE_API_KEY:\n')
                new_src.append('    raise ValueError("Missing PINECONE_API_KEY. Set it as an environment variable.")\n')
                changed = True
                continue

            if isinstance(line, str):
                redacted = _redact_string(line)
                if redacted != line:
                    changed = True
                new_src.append(redacted)
            else:
                new_src.append(line)

        cell["source"] = new_src

    # Redact tokens anywhere else (metadata/outputs, etc.)
    nb2 = _redact_obj(nb)
    if nb2 != nb:
        changed = True

    if changed:
        path.write_text(json.dumps(nb2, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

    return changed


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "path",
        nargs="?",
        default=str(Path("milestone2") / "Milestone2_Pinecone_VectorDB.ipynb"),
        help="Path to .ipynb to sanitize",
    )
    args = parser.parse_args()

    path = Path(args.path)
    if not path.exists():
        raise SystemExit(f"Not found: {path}")

    changed = sanitize_notebook(path)
    print(f"Sanitized: {path}" if changed else f"No changes needed: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
