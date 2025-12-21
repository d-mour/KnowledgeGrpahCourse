from pathlib import Path
import re
from rdflib import Graph


def extract_queries(text: str):
    lines = text.splitlines()
    blocks = []
    capturing = False
    cur = []
    for line in lines:
        if re.match(r"^\s*[0-9]+\.", line):
            # Numbered heading marks boundary between queries
            if capturing and cur:
                blocks.append("\n".join(cur).strip())
                cur = []
                capturing = False
            continue
        if re.match(r"^\s*PREFIX\s*:\s*<[^>]+>\s*$", line):
            if capturing and cur:
                blocks.append("\n".join(cur).strip())
                cur = []
            capturing = True
            cur.append(line)
            continue
        if capturing:
            cur.append(line)
    if capturing and cur:
        blocks.append("\n".join(cur).strip())

    cleaned = []
    for b in blocks:
        if not b or "SELECT" not in b.upper():
            continue
        if "PREFIX rdf:" not in b:
            b = "PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>\n" + b
        cleaned.append(b)
    return cleaned


def main():
    ttl_path = Path("dota.ttl")
    queries_path = Path("sparql_requests.txt")

    if not ttl_path.exists():
        raise SystemExit("dota.ttl not found; generate ontology first.")

    g = Graph()
    g.parse(ttl_path.as_posix(), format="turtle")
    print(f"Graph loaded: {len(g)} triples")

    queries_text = queries_path.read_text(encoding="utf-8")
    queries = extract_queries(queries_text)
    print(f"Found {len(queries)} SPARQL queries in sparql_requests.txt")

    for i, q in enumerate(queries, 1):
        print("\n--- Query", i, "---")
        try:
            res = g.query(q)
            rows = list(res)
            print(f"Rows: {len(rows)}")
            for row in rows[:5]:
                print(tuple(str(x) for x in row))
        except Exception as e:
            print(f"Query {i} failed: {e}")


if __name__ == "__main__":
    main()
