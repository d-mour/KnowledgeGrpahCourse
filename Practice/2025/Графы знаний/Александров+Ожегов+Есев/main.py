#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
StackKG demo (rdflib + SPARQL):
- load Turtle file (stackkg_large.ttl)
- (optional) add demo Project via rdflib (filling)
- run 6 SPARQL queries (CQ -> query -> results)
- pretty-print using rdfs:label (not raw IRIs)
- save updated graph to output .ttl

Run:
  python main.py --input stackkg_large.ttl
  python main.py --input stackkg_large.ttl --add-demo --output stackkg_updated.ttl
  python main.py --input stackkg_large.ttl --only Q1
"""

import argparse
from typing import Dict, List, Tuple

from rdflib import Graph, Namespace, RDF, RDFS, Literal
from rdflib.namespace import XSD

EX = Namespace("https://stackknowledge.org/stackkg#")

# ---------------------------------------------------------------------
# Competency Questions (CQ) mapping to query IDs
# ---------------------------------------------------------------------
CQ_MAP: List[Tuple[str, str]] = [
    ("CQ1: Подобрать стеки для realtime-чата при LOW cost и LOW DevOps complexity", "Q1"),
    ("CQ2: Найти стеки под LOW_LATENCY + HIGH_AVAILABILITY при DevOps complexity <= MEDIUM", "Q2"),
    ("CQ3: Топ технологий для CRUD по поддержке сообщества (githubStars)", "Q3"),
    ("CQ4: Какие технологии обычно используются вместе со SPRING_BOOT", "Q4"),
    ("CQ5: Стеки для команды без DevOps: LOW ops + CLOUD + (MONOLITH | MODULAR_MONOLITH)", "Q5"),
    ("CQ6: Объяснимость: для PROJECT_CHAT_MVP показать рекомендованный стек и его технологии", "Q6"),
    ("CQ7: Стеки под HIGH_AVAILABILITY, отсортированы по стоимости (LOW→HIGH)", "Q7"),
    ("CQ8: Технологии, часто используемые вместе с REACT (двунаправленно)", "Q8"),
    ("CQ9: Стеки с высокой масштабируемостью (HIGH) и облачным деплоем", "Q9"),
    ("CQ10: Для каждого стека показать архитектуру и стратегию тестирования", "Q10"),
    ("CQ11: Java‑ориентированные технологии (usesLanguage JAVA), сорт по звёздам", "Q11"),
    ("CQ12: Объяснимость: требования PROJECT_FINTECH_API, стек и его технологии", "Q12"),
    ("CQ13: Сравнить стоимость и DevOps‑сложность стеков для REALTIME_CHAT", "Q13"),
    ("CQ14: Стеки, включающие MONGODB, и поддерживаемые типы деплоя", "Q14"),
    ("CQ15: Технологии с HIGH community support и LOW maturity", "Q15"),
]

# ---------------------------------------------------------------------
# SPARQL Queries (labels everywhere)
# ---------------------------------------------------------------------
QUERIES: Dict[str, str] = {
    # Q1: stacks for realtime chat with low cost and low DevOps complexity
    "Q1": r"""
PREFIX ex: <https://stackknowledge.org/stackkg#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?stack ?stackLabel WHERE {
  ?stack a ex:Stack ;
         ex:recommendedForScenario ex:REALTIME_CHAT ;
         ex:hasCostTier ex:LOW ;
         ex:hasDevopsComplexityTier ex:LOW .
  OPTIONAL { ?stack rdfs:label ?stackLabel }
}
ORDER BY ?stackLabel ?stack
""",

    # Q2: LOW_LATENCY + HIGH_AVAILABILITY stacks with DevOps complexity <= MEDIUM
    "Q2": r"""
PREFIX ex: <https://stackknowledge.org/stackkg#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT DISTINCT ?stack ?stackLabel ?opsTier ?opsTierLabel WHERE {
  ?stack a ex:Stack ;
         ex:fitsRequirement ex:LOW_LATENCY ;
         ex:fitsRequirement ex:HIGH_AVAILABILITY ;
         ex:hasDevopsComplexityTier ?opsTier .
  FILTER (?opsTier IN (ex:LOW, ex:MEDIUM))

  OPTIONAL { ?stack rdfs:label ?stackLabel }
  OPTIONAL { ?opsTier rdfs:label ?opsTierLabel }
}
ORDER BY ?opsTierLabel ?stackLabel ?stack
""",

    # Q3: top technologies by GitHub stars that support CRUD_WEB_SERVICE scenario
    "Q3": r"""
PREFIX ex: <https://stackknowledge.org/stackkg#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?tech ?techLabel ?stars ?type ?typeLabel WHERE {
  ?tech a ex:Technology ;
        ex:supportsScenario ex:CRUD_WEB_SERVICE ;
        ex:githubStars ?stars .
  OPTIONAL { ?tech rdfs:label ?techLabel }

  OPTIONAL {
    ?tech a ?type .
    FILTER(?type != ex:Technology)
  }
  OPTIONAL { ?type rdfs:label ?typeLabel }
}
ORDER BY DESC(?stars)
LIMIT 10
""",

    # Q4: what is often used together with Spring Boot (neighbors)
    "Q4": r"""
PREFIX ex: <https://stackknowledge.org/stackkg#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT DISTINCT ?other ?otherLabel WHERE {
  ex:SPRING_BOOT ex:oftenUsedWith ?other .
  OPTIONAL { ?other rdfs:label ?otherLabel }
}
ORDER BY ?otherLabel ?other
""",

    # Q5: stacks friendly for low-DevOps teams: low ops + cloud + monolith/modular monolith
    "Q5": r"""
PREFIX ex: <https://stackknowledge.org/stackkg#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT DISTINCT ?stack ?stackLabel ?arch ?archLabel ?dep ?depLabel WHERE {
  ?stack a ex:Stack ;
         ex:hasDevopsComplexityTier ex:LOW ;
         ex:supportsDeployment ?dep ;
         ex:usesArchitecture ?arch .
  FILTER(?dep = ex:CLOUD)
  FILTER(?arch IN (ex:MONOLITH, ex:MODULAR_MONOLITH))

  OPTIONAL { ?stack rdfs:label ?stackLabel }
  OPTIONAL { ?arch rdfs:label ?archLabel }
  OPTIONAL { ?dep rdfs:label ?depLabel }
}
ORDER BY ?stackLabel ?stack
""",

    # Q6: for a concrete project: show recommended stack and its included technologies
    "Q6": r"""
PREFIX ex: <https://stackknowledge.org/stackkg#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?project ?projectLabel ?stack ?stackLabel ?tech ?techLabel WHERE {
  VALUES ?project { ex:PROJECT_CHAT_MVP }
  OPTIONAL { ?project rdfs:label ?projectLabel }

  ?project ex:recommendedStack ?stack .
  OPTIONAL { ?stack rdfs:label ?stackLabel }

  ?stack ex:includesTechnology ?tech .
  OPTIONAL { ?tech rdfs:label ?techLabel }
}
ORDER BY ?stackLabel ?techLabel ?tech
""",

    # Q7: stacks for HIGH_AVAILABILITY ordered by cost tier LOW->MEDIUM->HIGH
    "Q7": r"""
PREFIX ex: <https://stackknowledge.org/stackkg#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT DISTINCT ?stack ?stackLabel ?cost ?costLabel WHERE {
  ?stack a ex:Stack ;
         ex:fitsRequirement ex:HIGH_AVAILABILITY ;
         ex:hasCostTier ?cost .
  VALUES (?cost ?rank) { (ex:LOW 1) (ex:MEDIUM 2) (ex:HIGH 3) }
  OPTIONAL { ?stack rdfs:label ?stackLabel }
  OPTIONAL { ?cost rdfs:label ?costLabel }
}
ORDER BY ?rank ?stackLabel ?stack
""",

    # Q8: technologies often used with REACT (both directions)
    "Q8": r"""
PREFIX ex: <https://stackknowledge.org/stackkg#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT DISTINCT ?other ?otherLabel WHERE {
  { ex:REACT ex:oftenUsedWith ?other }
  UNION
  { ?other ex:oftenUsedWith ex:REACT }
  OPTIONAL { ?other rdfs:label ?otherLabel }
}
ORDER BY ?otherLabel ?other
""",

    # Q9: stacks with HIGH scalability that support CLOUD deployment
    "Q9": r"""
PREFIX ex: <https://stackknowledge.org/stackkg#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT DISTINCT ?stack ?stackLabel WHERE {
  ?stack a ex:Stack ;
         ex:hasScalabilityTier ex:HIGH ;
         ex:supportsDeployment ex:CLOUD .
  OPTIONAL { ?stack rdfs:label ?stackLabel }
}
ORDER BY ?stackLabel ?stack
""",

    # Q10: for each stack, show architecture and testing strategy
    "Q10": r"""
PREFIX ex: <https://stackknowledge.org/stackkg#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT DISTINCT ?stack ?stackLabel ?arch ?archLabel ?ts ?tsLabel WHERE {
  ?stack a ex:Stack ;
         ex:usesArchitecture ?arch ;
         ex:usesTestingStrategy ?ts .
  OPTIONAL { ?stack rdfs:label ?stackLabel }
  OPTIONAL { ?arch rdfs:label ?archLabel }
  OPTIONAL { ?ts rdfs:label ?tsLabel }
}
ORDER BY ?stackLabel ?archLabel ?tsLabel
""",

    # Q11: JAVA-based technologies ordered by GitHub stars
    "Q11": r"""
PREFIX ex: <https://stackknowledge.org/stackkg#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT DISTINCT ?tech ?techLabel ?type ?typeLabel ?stars WHERE {
  ?tech a ex:Technology ;
        ex:usesLanguage ex:JAVA ;
        ex:githubStars ?stars .
  OPTIONAL { ?tech rdfs:label ?techLabel }
  OPTIONAL {
    ?tech a ?type .
    FILTER(?type != ex:Technology)
  }
  OPTIONAL { ?type rdfs:label ?typeLabel }
}
ORDER BY DESC(?stars)
LIMIT 20
""",

    # Q12: explainability for PROJECT_FINTECH_API: list requirements, stack and its technologies
    "Q12": r"""
PREFIX ex: <https://stackknowledge.org/stackkg#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?project ?projectLabel ?req ?reqLabel ?stack ?stackLabel ?tech ?techLabel WHERE {
  VALUES ?project { ex:PROJECT_FINTECH_API }
  OPTIONAL { ?project rdfs:label ?projectLabel }

  OPTIONAL { ?project ex:hasRequirement ?req . OPTIONAL { ?req rdfs:label ?reqLabel } }

  ?project ex:recommendedStack ?stack .
  OPTIONAL { ?stack rdfs:label ?stackLabel }

  ?stack ex:includesTechnology ?tech .
  OPTIONAL { ?tech rdfs:label ?techLabel }
}
ORDER BY ?stackLabel ?techLabel ?reqLabel
""",

    # Q13: compare cost and DevOps complexity for stacks recommended for REALTIME_CHAT
    "Q13": r"""
PREFIX ex: <https://stackknowledge.org/stackkg#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT DISTINCT ?stack ?stackLabel ?cost ?costLabel ?ops ?opsLabel WHERE {
  ?stack a ex:Stack ;
         ex:recommendedForScenario ex:REALTIME_CHAT ;
         ex:hasCostTier ?cost ;
         ex:hasDevopsComplexityTier ?ops .
  OPTIONAL { ?stack rdfs:label ?stackLabel }
  OPTIONAL { ?cost rdfs:label ?costLabel }
  OPTIONAL { ?ops rdfs:label ?opsLabel }
}
ORDER BY ?stackLabel
""",

    # Q14: stacks that include MONGODB and their deployment types
    "Q14": r"""
PREFIX ex: <https://stackknowledge.org/stackkg#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT DISTINCT ?stack ?stackLabel ?dep ?depLabel WHERE {
  ?stack a ex:Stack ;
         ex:includesTechnology ex:MONGODB ;
         ex:supportsDeployment ?dep .
  OPTIONAL { ?stack rdfs:label ?stackLabel }
  OPTIONAL { ?dep rdfs:label ?depLabel }
}
ORDER BY ?stackLabel ?depLabel
""",

    # Q15: technologies with HIGH community support and LOW maturity
    "Q15": r"""
PREFIX ex: <https://stackknowledge.org/stackkg#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT DISTINCT ?tech ?techLabel ?type ?typeLabel ?stars WHERE {
  ?tech a ex:Technology ;
        ex:hasCommunitySupportTier ex:HIGH ;
        ex:hasMaturityTier ex:LOW .
  OPTIONAL { ?tech rdfs:label ?techLabel }
  OPTIONAL {
    ?tech a ?type .
    FILTER(?type != ex:Technology)
  }
  OPTIONAL { ?type rdfs:label ?typeLabel }
  OPTIONAL { ?tech ex:githubStars ?stars }
}
ORDER BY DESC(?stars) ?techLabel
LIMIT 50
""",
}

# ---------------------------------------------------------------------
# rdflib "filling" demo: add a new project + recommendation
# ---------------------------------------------------------------------
def add_demo_project(g: Graph):
    """
    Adds a new Project instance to demonstrate 'filling via rdflib'.
    После запуска с --add-demo в Protégé появится PROJECT_DEMO_JUNIOR_CHAT.
    """
    project = EX.PROJECT_DEMO_JUNIOR_CHAT
    team = EX.TEAM_SMALL_JUNIOR
    scenario = EX.REALTIME_CHAT

    g.add((project, RDF.type, EX.Project))
    g.add((project, RDFS.label, Literal("PROJECT_DEMO_JUNIOR_CHAT")))

    g.add((project, EX.hasScenario, scenario))
    g.add((project, EX.hasTeam, team))

    g.add((project, EX.hasBudgetTier, EX.LOW))
    g.add((project, EX.hasTimeToMarketTier, EX.HIGH))
    g.add((project, EX.expectedLoadRps, Literal(150, datatype=XSD.integer)))
    g.add((project, EX.expectedUsers, Literal(8000, datatype=XSD.integer)))

    g.add((project, EX.hasArchitecture, EX.MONOLITH))
    g.add((project, EX.hasDeployment, EX.CLOUD))
    g.add((project, EX.hasTestingStrategy, EX.BALANCED))

    g.add((project, EX.hasRequirement, EX.LOW_LATENCY))
    g.add((project, EX.hasRequirement, EX.FAST_DELIVERY))
    g.add((project, EX.hasRequirement, EX.LOW_OPS))

    # Recommend an existing stack from the ontology
    g.add((project, EX.recommendedStack, EX.STACK_CHAT_NODE_SOCKETIO_MONGO))
    return project


# ---------------------------------------------------------------------
# Printing utilities
# ---------------------------------------------------------------------
def shrink_iri(value: str) -> str:
    # Make output readable if some labels missing: keep fragment after '#'
    if "#" in value:
        return value.split("#", 1)[1]
    return value

def cell_to_str(cell) -> str:
    if cell is None:
        return ""
    if isinstance(cell, Literal):
        return str(cell)
    s = str(cell)
    return shrink_iri(s)

def print_table(headers: List[str], rows: List[List[str]], max_rows: int = 50):
    if not rows:
        print("(no rows)")
        return

    widths = [len(h) for h in headers]
    for r in rows[:max_rows]:
        for i, v in enumerate(r):
            widths[i] = max(widths[i], len(v))

    def fmt_row(r: List[str]) -> str:
        return " | ".join(v.ljust(widths[i]) for i, v in enumerate(r))

    print(fmt_row(headers))
    print("-" * (sum(widths) + 3 * (len(widths) - 1)))

    for r in rows[:max_rows]:
        print(fmt_row(r))

    if len(rows) > max_rows:
        print(f"... ({len(rows) - max_rows} more rows)")

def run_query(g: Graph, qid: str):
    q = QUERIES[qid]
    res = g.query(q)

    headers = [str(v) for v in res.vars]
    rows: List[List[str]] = []
    for row in res:
        rows.append([cell_to_str(cell) for cell in row])

    print_table(headers, rows)

def print_cq_banner():
    print("\n=== Competency Questions -> SPARQL demo ===\n")
    for cq, qid in CQ_MAP:
        print(f"- {cq}  ->  {qid}")
    print("")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default="stackkg_large.ttl", help="Path to input Turtle file")
    ap.add_argument("--output", default="stackkg_updated.ttl", help="Path to output Turtle file")
    ap.add_argument("--add-demo", action="store_true", help="Add demo Project via rdflib")
    ap.add_argument("--only", choices=list(QUERIES.keys()), help="Run only one query (Q1..Q15)")
    args = ap.parse_args()

    g = Graph()
    g.parse(args.input, format="turtle")

    if args.add_demo:
        p = add_demo_project(g)
        print(f"Added demo project: {shrink_iri(str(p))}\n")

    print_cq_banner()

    if args.only:
        print("=" * 90)
        print(args.only)
        print("-" * 90)
        run_query(g, args.only)
    else:
        for qid in QUERIES.keys():
            print("\n" + "=" * 90)
            print(qid)
            print("-" * 90)
            run_query(g, qid)

    g.serialize(destination=args.output, format="turtle")
    print(f"\nSaved updated graph to: {args.output}")

if __name__ == "__main__":
    main()
