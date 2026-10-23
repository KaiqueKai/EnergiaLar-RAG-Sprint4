"""Constrói o índice persistente da base de conhecimento."""
import argparse
from .vector_store import build_or_load_vector_store


def main():
    parser = argparse.ArgumentParser(description="Cria ou atualiza o índice persistente ChromaDB do EnergiaLar.")
    parser.add_argument("--force", action="store_true", help="recria o índice, mesmo que não tenha mudado")
    args = parser.parse_args()
    store = build_or_load_vector_store(force_rebuild=args.force)
    try:
        count = store._collection.count()
    except Exception:
        count = "indisponível"
    print(f"Índice Chroma pronto. Registros/chunks: {count}")


if __name__ == "__main__":
    main()
