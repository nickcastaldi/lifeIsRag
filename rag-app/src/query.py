"""Interactive CLI for OWASP RAG."""
from owaspRag import OWASPRagApp


def main():
    rag = OWASPRagApp()

    print("=" * 60)
    print("OWASP Security Assistant (Local Llama 3.2)")
    print("=" * 60)
    print("Ask any OWASP-related question. Type 'exit' to quit.\n")

    while True:
        try:
            query = input("Question: ").strip()
            if not query:
                continue
            if query.lower() in ["exit", "quit", "q"]:
                break

            print("\nThinking...\n")
            result = rag.answer(query)

            print(f"Answer:\n{result['answer']}\n")
            print("Sources:")
            for src in result['sources'][:5]:
                src_path = src.get('source', 'unknown')
                repo = src.get('repo', 'unknown')
                print(f"  - [{repo}] {src_path}")
            print()
        except KeyboardInterrupt:
            print("\n")
            break
        except Exception as e:
            print(f"\nError: {e}\n")

    print("Goodbye!")


if __name__ == "__main__":
    main()
