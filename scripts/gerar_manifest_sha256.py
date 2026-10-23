"""Gera o manifesto SHA-256 de fontes/documentos do projeto sem incluir segredos/cache."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "MANIFEST_SHA256.json"
EXCLUDED_DIRS = {".git", ".venv", "venv", "env", "__pycache__", ".pytest_cache"}
EXCLUDED_NAMES = {".env", "secrets.toml", OUTPUT.name}
EXCLUDED_PARTS = {"storage/chroma"}
EXCLUDED_SUFFIXES = {".pyc", ".pyo"}


def should_include(path: Path) -> bool:
    relative = path.relative_to(ROOT).as_posix()
    if path.name in EXCLUDED_NAMES or path.suffix.lower() in EXCLUDED_SUFFIXES:
        return False
    if any(part in EXCLUDED_DIRS for part in path.relative_to(ROOT).parts):
        return False
    if any(relative == part or relative.startswith(part + "/") for part in EXCLUDED_PARTS):
        return False
    if relative.startswith("storage/"):
        return False
    return path.is_file()


def main() -> None:
    records = []
    for path in sorted(ROOT.rglob("*")):
        if not should_include(path):
            continue
        data = path.read_bytes()
        records.append({
            "path": path.relative_to(ROOT).as_posix(),
            "bytes": len(data),
            "sha256": hashlib.sha256(data).hexdigest(),
        })
    OUTPUT.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Manifesto atualizado: {OUTPUT.name} ({len(records)} arquivos). Arquivo .env, caches e índice Chroma excluídos.")


if __name__ == "__main__":
    main()
