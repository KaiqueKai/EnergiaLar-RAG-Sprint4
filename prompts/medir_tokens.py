"""Conta tokens exatos das versões do prompt usando tiktoken."""
from pathlib import Path
import tiktoken
BASE = Path(__file__).resolve().parent
ENCODING = "cl100k_base"
if __name__ == "__main__":
    enc = tiktoken.get_encoding(ENCODING)
    for version in ("v1", "v2", "v3"):
        path = BASE / f"system_prompt_{version}.md"
        print(f"{path.name}: {len(enc.encode(path.read_text(encoding='utf-8')))} tokens ({ENCODING})")
