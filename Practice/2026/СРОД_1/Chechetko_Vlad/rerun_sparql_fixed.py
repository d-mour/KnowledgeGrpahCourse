from pathlib import Path
import csv
from rdflib import Graph

PROJECT_DIR = Path(__file__).resolve().parent
SPARQL_DIR = PROJECT_DIR / "exports" / "sparql"
RDF_FILE = PROJECT_DIR / "exports" / "rdf" / "medical_kg.ttl"

print("[1/2] Loading RDF graph...")
g = Graph()
g.parse(str(RDF_FILE), format="turtle")
print("RDF triples:", len(g))

print("[2/2] Running SPARQL queries...")
for rq_file in sorted(SPARQL_DIR.glob("*.rq")):
    query_name = rq_file.stem
    query_text = (
        rq_file.read_text(encoding="utf-8-sig")
        .replace("\\n", "\n")
        .lstrip("\ufeff")
        .strip()
    )
    out_csv = SPARQL_DIR / f"{query_name}_result.csv"
    try:
        rows = list(g.query(query_text))
        var_names = [str(v) for v in rows.vars] if hasattr(rows, "vars") else []
        with out_csv.open("w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            if var_names:
                writer.writerow(var_names)
                for row in rows:
                    writer.writerow([str(row.get(v, "")) for v in rows.vars])
            else:
                writer.writerow(["result"])
                for row in rows:
                    writer.writerow([str(row)])
        print(f"[OK] {query_name}: {len(rows)} rows")
    except Exception as e:
        with out_csv.open("w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow(["error"])
            writer.writerow([str(e)])
        print(f"[ERROR] {query_name}: {e}")
