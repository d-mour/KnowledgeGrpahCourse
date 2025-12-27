import os
from rdflib import Graph
import rdflib.plugins.sparql


def load_graph(path: str) -> Graph:
    g = Graph()
    g.parse(path, format="xml")
    print(f"Загружено триплов: {len(g)}")
    return g


def load_query(filename: str) -> str:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    queries_dir = os.path.join(base_dir, "queries")
    full_path = os.path.join(queries_dir, filename)

    with open(full_path, "r", encoding="utf-8") as f:
        return f.read()


def run_and_print(g: Graph, title: str, query: str, log_path: str | None = None):
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)

    qr = g.query(query)
    res = list(qr)

    print(f"Строк в результате: {len(res)}")

    var_names = [str(v) for v in qr.vars]

    if len(res) > 0:
        print(" | ".join(var_names))
        print("-" * 80)

    rows_str_lines: list[str] = []

    for row in res:
        values = []
        for var in qr.vars:
            val = row[var]
            values.append("" if val is None else str(val))
        line = " | ".join(values)
        print(line)
        rows_str_lines.append(line)

    if log_path:
        with open(log_path, "a", encoding="utf-8") as f:
            f.write("\n" + "=" * 80 + "\n")
            f.write(title + "\n")
            f.write("=" * 80 + "\n\n")

            f.write("SPARQL-запрос:\n")
            f.write(query)
            f.write("\n\n")

            f.write("Переменные:\n")
            if var_names:
                f.write(" | ".join(var_names) + "\n")
                f.write("-" * 80 + "\n")
            else:
                f.write("(нет переменных)\n")

            if rows_str_lines:
                f.write("\n".join(rows_str_lines) + "\n")
            else:
                f.write("Результат: 0 строк.\n")

            f.write(f"\nВсего строк: {len(res)}\n")


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    ontology_path = os.path.join(base_dir, "output.rdf")
    log_path = os.path.join(base_dir, "queries.log")

    print(f"Читаю онтологию из: {ontology_path}")
    print(f"Лог этого запуска: {log_path}")

    g = load_graph(ontology_path)

    with open(log_path, "w", encoding="utf-8") as f:
        f.write("Лог SPARQL-запросов за один запуск main()\n")


    q_the_knave = load_query("the_knave_teams.rq")
    q_anemo_teams = load_query("anemo_teams.rq")
    q_azhdaha_best_artifact = load_query("azhdaha_best_artifact.rq")
    q_staff_homa = load_query("staff_of_homa_cryo_chars.rq")
    q_emperor_team = load_query("emperor_team_2x4_2x5.rq")



    run_and_print(g, "1) Команды против The Knave", q_the_knave, log_path)
    run_and_print(g, "2) Команды с anemo-персонажами против anemo-уязвимых боссов", q_anemo_teams, log_path)
    run_and_print(g, "3) Лучший сет артефактов против azhdaha", q_azhdaha_best_artifact, log_path)
    run_and_print(g, "4) Крио-персонажи, которым подходит Staff of Homa", q_staff_homa, log_path)
    run_and_print(g, "5) Команды 2×4★ + 2×5★ против Emperor of Fire and Iron", q_emperor_team, log_path)



if __name__ == "__main__":
    main()
