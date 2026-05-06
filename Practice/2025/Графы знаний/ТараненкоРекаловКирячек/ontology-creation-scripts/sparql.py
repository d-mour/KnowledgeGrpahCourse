#!/usr/bin/env python3
"""
Скрипт для работы с онтологией World of Tanks и выполнения SPARQL запросов
"""

from rdflib import Graph, Namespace
from pathlib import Path
import argparse
import time


class OntologyQueryEngine:
    def __init__(self, ontology_file):
        """Инициализация движка запросов"""
        self.g = Graph()
        self.ontology_file = Path(ontology_file)

        # Namespace
        self.WOT = Namespace("http://www.semanticweb.org/ontology/wot#")
        self.g.bind("wot", self.WOT)

        print("=" * 60)
        print("WORLD OF TANKS ONTOLOGY QUERY ENGINE")
        print("=" * 60)

        # Загружаем онтологию
        print(f"\n📂 Loading ontology: {self.ontology_file.name}")
        start_time = time.time()

        try:
            self.g.parse(str(self.ontology_file), format='xml')
            load_time = time.time() - start_time

            print(f"✅ Loaded successfully in {load_time:.2f} seconds")
            print(f"📊 Total triples: {len(self.g):,}")

        except Exception as e:
            print(f"❌ Error loading ontology: {e}")
            raise

    def execute_query(self, query, description=None):
        """Выполняет SPARQL запрос"""
        if description:
            print(f"\n{'=' * 60}")
            print(f"🔍 {description}")
            print(f"{'=' * 60}")

        try:
            start_time = time.time()
            results = self.g.query(query)
            query_time = time.time() - start_time

            result_list = list(results)
            print(f"\n⏱️  Query executed in {query_time:.3f} seconds")
            print(f"📋 Results: {len(result_list)} rows\n")

            return result_list

        except Exception as e:
            print(f"❌ Query error: {e}")
            return []

    def print_results(self, results, limit=None):
        """Печатает результаты запроса"""
        if not results:
            print("No results found.")
            return

        # Определяем ширину колонок
        if results:
            headers = list(results[0].labels)
            col_widths = {h: len(str(h)) for h in headers}

            # Вычисляем максимальную ширину для каждой колонки
            for row in results[:100]:  # Проверяем первые 100 строк
                for header in headers:
                    value = row[header]
                    if value:
                        value_str = self.format_value(value)
                        col_widths[header] = max(col_widths[header], len(value_str))

            # Ограничиваем ширину колонок
            for header in headers:
                col_widths[header] = min(col_widths[header], 50)

        # Печатаем заголовки
        header_line = " | ".join([h.ljust(col_widths[h]) for h in headers])
        print(header_line)
        print("-" * len(header_line))

        # Печатаем строки
        display_results = results[:limit] if limit else results
        for row in display_results:
            row_values = []
            for header in headers:
                value = row[header]
                value_str = self.format_value(value) if value else ""
                row_values.append(value_str.ljust(col_widths[header]))
            print(" | ".join(row_values))

        if limit and len(results) > limit:
            print(f"\n... and {len(results) - limit} more rows")

    def format_value(self, value):
        """Форматирует значение для вывода"""
        value_str = str(value)

        # Убираем namespace из URI
        if "http://www.semanticweb.org/ontology/wot#" in value_str:
            value_str = value_str.split("#")[-1]

        # Форматируем числа
        if value_str.replace('.', '').replace('-', '').isdigit():
            try:
                num = float(value_str)
                if num.is_integer():
                    return str(int(num))
                else:
                    return f"{num:.2f}"
            except:
                pass

        # Ограничиваем длину строки
        if len(value_str) > 50:
            return value_str[:47] + "..."

        return value_str

    def get_statistics(self):
        """Получает статистику по онтологии"""
        print("\n" + "=" * 60)
        print("📊 ONTOLOGY STATISTICS")
        print("=" * 60)

        # Количество классов
        class_query = """
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        
        SELECT (COUNT(DISTINCT ?class) AS ?count)
        WHERE {
          ?class rdf:type owl:Class .
        }
        """

        # Количество инстансов по классам
        instances_query = """
        PREFIX wot: <http://www.semanticweb.org/ontology/wot#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        
        SELECT ?class (COUNT(?instance) AS ?count)
        WHERE {
          ?instance rdf:type ?class .
          FILTER(STRSTARTS(STR(?class), "http://www.semanticweb.org/ontology/wot#"))
        }
        GROUP BY ?class
        ORDER BY DESC(?count)
        """

        print("\n🎯 Instances by class:")
        results = self.execute_query(instances_query)
        self.print_results(results, limit=20)

    # ==================== ПРЕДОПРЕДЕЛЕННЫЕ ЗАПРОСЫ ====================

    def query_best_tanks_by_composite(self, limit=10, tier=None, exclude_premium=False, exclude_gift=False):
        """Лучшие танки по совокупному скору (без нормировки, взвешенная сумма метрик)"""
        # Опциональные фильтры
        premium_filters = ""
        if exclude_premium:
            premium_filters += """
      OPTIONAL { ?tank wot:isPremium ?isPrem . }
      FILTER( !BOUND(?isPrem) || ?isPrem = false )
    """
        if exclude_gift:
            premium_filters += """
      OPTIONAL { ?tank wot:isGift ?isGift . }
      FILTER( !BOUND(?isGift) || ?isGift = false )
    """

        tier_filter = f"\n  FILTER(?tier = {int(tier)})" if tier is not None else ""

        query = f"""
    PREFIX rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX xsd:  <http://www.w3.org/2001/XMLSchema#>
    PREFIX wot:  <http://www.semanticweb.org/ontology/wot#>

    SELECT ?tank ?label ?tier ?score ?dpmEff ?penF ?alphaF ?aimF ?speedF ?hpAny ?ptw
    WHERE {{
      ?tank a wot:Tank .
      OPTIONAL {{ ?tank wot:tankName  ?name . }}
      OPTIONAL {{ ?tank wot:shortName ?shortName . }}
      OPTIONAL {{ ?tank wot:tier      ?tier . }}
      BIND(COALESCE(?name, ?shortName) AS ?label)

      OPTIONAL {{
        ?tank wot:hasGun ?gun .
        OPTIONAL {{ ?gun wot:dpm            ?dpm        }}
        OPTIONAL {{ ?gun wot:avgDamage      ?avgDamage  }}
        OPTIONAL {{ ?gun wot:avgPenetration ?pen        }}
        OPTIONAL {{ ?gun wot:fireRate       ?fr         }}
        OPTIONAL {{ ?gun wot:aimTime        ?aim        }}
      }}

      OPTIONAL {{
        ?tank wot:hasCharacteristics ?ch .
        OPTIONAL {{ ?ch wot:speedForward ?topSpeed }}
        OPTIONAL {{ ?ch wot:hp           ?hpCh     }}
      }}
      OPTIONAL {{ ?tank wot:maxHP  ?hpMax  }}
      OPTIONAL {{ ?tank wot:weight ?weight }}

      OPTIONAL {{
        ?tank wot:hasEngine ?engine .
        OPTIONAL {{ ?engine wot:power ?power }}
      }}

      # Эффективный DPM (готовый или fireRate * avgDamage)
      BIND(
        COALESCE(
          xsd:decimal(?dpm),
          IF(BOUND(?fr) && BOUND(?avgDamage),
             xsd:decimal(?fr) * xsd:decimal(?avgDamage),
             xsd:decimal("0")
          )
        ) AS ?dpmEff
      )

      # Безопасные значения
      BIND(COALESCE(xsd:decimal(?pen),       xsd:decimal("0")) AS ?penF)
      BIND(COALESCE(xsd:decimal(?avgDamage), xsd:decimal("0")) AS ?alphaF)
      BIND(COALESCE(xsd:decimal(?aim),       xsd:decimal("3")) AS ?aimF)
      BIND(COALESCE(xsd:decimal(?topSpeed),  xsd:decimal("0")) AS ?speedF)
      BIND(COALESCE(xsd:decimal(?hpMax), xsd:decimal(?hpCh), xsd:decimal("0")) AS ?hpAny)

      # Удельная мощность
      BIND(
        IF(BOUND(?power) && BOUND(?weight) && xsd:decimal(?weight) > 0,
           xsd:decimal(?power) / xsd:decimal(?weight),
           xsd:decimal("0")
        ) AS ?ptw
      )

      # Веса (без нормировок)
      BIND(xsd:decimal("0.000075")   AS ?wDpm)   # DPM
      BIND(xsd:decimal("0.00050")    AS ?wPen)   # пробитие
      BIND(xsd:decimal("0.00013333") AS ?wAlpha) # альфа-урон
      BIND(xsd:decimal("0.00200")    AS ?wSpd)   # скорость вперед
      BIND(xsd:decimal("0.000050")   AS ?wHp)    # HP
      BIND(xsd:decimal("0.00400")    AS ?wPtw)   # уд. мощность
      BIND(xsd:decimal("0.01250")    AS ?wAim)   # штраф за aimTime

      # Итоговый скор (aimTime с минусом)
      BIND(
        (?wDpm  * ?dpmEff) +
        (?wPen  * ?penF)   +
        (?wAlpha* ?alphaF) +
        (?wSpd  * ?speedF) +
        (?wHp   * ?hpAny)  +
        (?wPtw  * ?ptw)    -
        (?wAim  * ?aimF)
        AS ?score
      )

      {premium_filters}
      {tier_filter}
    }}
    ORDER BY DESC(?score)
    LIMIT {limit}
    """
        desc = "Best Tanks by Composite Score"
        if tier is not None:
            desc += f" (tier {tier})"
        if exclude_premium or exclude_gift:
            flags = []
            if exclude_premium: flags.append("no-premium")
            if exclude_gift:    flags.append("no-gift")
            desc += " [" + ", ".join(flags) + "]"
        results = self.execute_query(query, desc)
        self.print_results(results, limit=limit)
        return results

    def query_best_nation_by_weighted_tanks(self, limit=10):
        """Какая нация имеет в среднем больше лучших танков: взвешенное среднее по композитному скору, вес = tier"""
        query = """
    PREFIX rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX xsd:  <http://www.w3.org/2001/XMLSchema#>
    PREFIX wot:  <http://www.semanticweb.org/ontology/wot#>

    SELECT ?nationName
           (AVG(?score) AS ?avgScore)
           ((SUM(?weightedScore) / SUM(?tierWeight)) AS ?weightedAvgScore)
           (COUNT(?tank) AS ?tankCount)
    WHERE {
      {
        SELECT ?tank ?nationName ?tier ?score
               (COALESCE(xsd:decimal(?tier), xsd:decimal("1")) AS ?tierWeight)
               ((?score * COALESCE(xsd:decimal(?tier), xsd:decimal("1"))) AS ?weightedScore)
        WHERE {
          ?tank a wot:Tank .
          ?tank wot:belongsToNation ?nation .
          ?nation wot:nationName ?nationName .
          OPTIONAL { ?tank wot:tier ?tier . }

          OPTIONAL {
            ?tank wot:hasGun ?gun .
            OPTIONAL { ?gun wot:dpm            ?dpm        }
            OPTIONAL { ?gun wot:avgDamage      ?avgDamage  }
            OPTIONAL { ?gun wot:avgPenetration ?pen        }
            OPTIONAL { ?gun wot:fireRate       ?fr         }
            OPTIONAL { ?gun wot:aimTime        ?aim        }
          }

          OPTIONAL {
            ?tank wot:hasCharacteristics ?ch .
            OPTIONAL { ?ch wot:speedForward ?topSpeed }
            OPTIONAL { ?ch wot:hp           ?hpCh     }
          }
          OPTIONAL { ?tank wot:maxHP  ?hpMax  }
          OPTIONAL { ?tank wot:weight ?weight }

          OPTIONAL {
            ?tank wot:hasEngine ?engine .
            OPTIONAL { ?engine wot:power ?power }
          }

          BIND(
            COALESCE(
              xsd:decimal(?dpm),
              IF(BOUND(?fr) && BOUND(?avgDamage),
                 xsd:decimal(?fr) * xsd:decimal(?avgDamage),
                 xsd:decimal("0")
              )
            ) AS ?dpmEff
          )

          BIND(COALESCE(xsd:decimal(?pen),       xsd:decimal("0")) AS ?penF)
          BIND(COALESCE(xsd:decimal(?avgDamage), xsd:decimal("0")) AS ?alphaF)
          BIND(COALESCE(xsd:decimal(?aim),       xsd:decimal("3")) AS ?aimF)
          BIND(COALESCE(xsd:decimal(?topSpeed),  xsd:decimal("0")) AS ?speedF)
          BIND(COALESCE(xsd:decimal(?hpMax), xsd:decimal(?hpCh), xsd:decimal("0")) AS ?hpAny)

          BIND(
            IF(BOUND(?power) && BOUND(?weight) && xsd:decimal(?weight) > 0,
               xsd:decimal(?power) / xsd:decimal(?weight),
               xsd:decimal("0")
            ) AS ?ptw
          )

          BIND(xsd:decimal("0.000075")   AS ?wDpm)
          BIND(xsd:decimal("0.00050")    AS ?wPen)
          BIND(xsd:decimal("0.00013333") AS ?wAlpha)
          BIND(xsd:decimal("0.00200")    AS ?wSpd)
          BIND(xsd:decimal("0.000050")   AS ?wHp)
          BIND(xsd:decimal("0.00400")    AS ?wPtw)
          BIND(xsd:decimal("0.01250")    AS ?wAim)

          BIND(
            (?wDpm  * ?dpmEff) +
            (?wPen  * ?penF)   +
            (?wAlpha* ?alphaF) +
            (?wSpd  * ?speedF) +
            (?wHp   * ?hpAny)  +
            (?wPtw  * ?ptw)    -
            (?wAim  * ?aimF)
            AS ?score
          )

          # Пример исключений (раскомментируйте при необходимости):
          # OPTIONAL { ?tank wot:isPremium ?isPrem . }
          # OPTIONAL { ?tank wot:isGift    ?isGift . }
          # FILTER( !BOUND(?isPrem) || ?isPrem = false )
          # FILTER( !BOUND(?isGift) || ?isGift = false )
        }
      }
    }
    GROUP BY ?nationName
    ORDER BY DESC(?weightedAvgScore)
    LIMIT 1
    """
        results = self.execute_query(query, "Best Nation by Weighted Average of 'Best' Tanks (weight = tier)")
        self.print_results(results, limit=limit)
        return results

    def query_tank_with_highest_avg_damage(self, min_battles=50, top_n=1):
        """Танк(и) с наибольшим средним уроном, рассчитанным по данным боёв"""

        query = f""" 
        PREFIX rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX xsd:  <http://www.w3.org/2001/XMLSchema#>
        PREFIX wot:  <http://www.semanticweb.org/ontology/wot#>

    
        SELECT ?tank ?tankName
               (AVG(xsd:decimal(?damage)) AS ?avgDamage)
               (COUNT(?perf) AS ?battles)
        WHERE {{
          ?perf wot:withTank ?tank .
          ?perf wot:damage   ?damage .
          ?tank wot:tankName ?tankName .
        }}
        GROUP BY ?tank ?tankName
        HAVING (COUNT(?perf) >= {min_battles})
        ORDER BY DESC(?avgDamage) DESC(?battles)
        LIMIT {top_n}
        """
        results = self.execute_query(
            query,
            f"Tank(s) with Highest Average Damage (min {min_battles} battles)"
        )
        self.print_results(results, limit=top_n)
        return results

    def query_worst_maps_for_tank(self, tank_name, min_battles=10, limit=2):
        """Топ худших карт для конкретного танка по win rate (при равенстве — по числу боёв, затем по урону)"""

        safe_name = str(tank_name).replace('"', '\\"')
        safe_name_lc = safe_name.lower()

        query = f"""
        PREFIX wot:  <http://www.semanticweb.org/ontology/wot#>
        PREFIX xsd:  <http://www.w3.org/2001/XMLSchema#>

        SELECT ?mapName
               ?battles
               ?winRate
               ?avgDamage
        WHERE {{
          {{
            SELECT (SAMPLE(?mapRaw) AS ?mapName)
                   (COUNT(?battle) AS ?battles)
                   ((SUM(IF(?won = true, 1, 0)) * 100.0 / COUNT(?battle)) AS ?winRate)
                   (AVG(COALESCE(xsd:decimal(?damage), xsd:decimal("0"))) AS ?avgDamage)
            WHERE {{
              # Находим нужный танк по имени/короткому имени (регистронезависимо)
              ?tank wot:tankName ?tName .
              OPTIONAL {{ ?tank wot:shortName ?sName . }}
              FILTER(LCASE(STR(?tName)) = "{safe_name_lc}" || LCASE(STR(?sName)) = "{safe_name_lc}")

              # Performance этого танка и связанные бои
              ?perf   wot:withTank ?tank .
              ?perf   wot:inBattle ?battle .
              ?battle wot:won ?won .
              ?battle wot:onMap ?mapRaw .
              OPTIONAL {{ ?perf wot:damage ?damage . }}

              # Нормализуем ключ карты по регистру, чтобы объединять 'Himmelsdorf' и 'himmelsdorf'
              BIND(LCASE(STR(?mapRaw)) AS ?mapKey)
            }}
            GROUP BY ?mapKey
            HAVING (COUNT(?battle) >= {int(min_battles)})
          }}
        }}
        ORDER BY ASC(?winRate) DESC(?battles) DESC(?avgDamage)
        LIMIT {int(limit)}
        """
        results = self.execute_query(
            query,
            f"Worst {limit} Maps for Tank '{tank_name}' (min {min_battles} battles per map)"
        )
        self.print_results(results, limit=limit)
        return results

    def query_maps_with_side_imbalance(self, threshold_pct=10.0, min_battles_per_side=20, limit=50):
        """Карты с перекосом по сторонам: одна сторона выигрывает на threshold_pct п.п. чаще другой.
           Счёт ведётся по боям (won/spawn — свойства Battle), onMap — строковое свойство."""
        query = f"""
        PREFIX wot:  <http://www.semanticweb.org/ontology/wot#>
        PREFIX xsd:  <http://www.w3.org/2001/XMLSchema#>

        SELECT
          ?mapName
          ?sideAdv ?winRateAdv ?battlesAdv
          ?sideOther ?winRateOther ?battlesOther
          (?winRateAdv - ?winRateOther AS ?winRateDiff)
        WHERE {{
          # Агрегаты по карте и стороне (первая выборка — A)
          {{
            SELECT
              ?mapKey
              (SAMPLE(?mapRaw) AS ?mapName)
              ?sideA
              (COUNT(?battle) AS ?battlesA)
              ((SUM(IF(?won, 1, 0)) * 100.0 / COUNT(?battle)) AS ?winRateA)
            WHERE {{
              ?battle wot:onMap ?mapRaw ;
                      wot:spawn ?sideA ;
                      wot:won   ?won .
              BIND(LCASE(STR(?mapRaw)) AS ?mapKey)
            }}
            GROUP BY ?mapKey ?sideA
            HAVING (COUNT(?battle) >= {int(min_battles_per_side)})
          }}

          # Агрегаты по карте и стороне (вторая выборка — B), связываем по той же карте
          {{
            SELECT
              ?mapKey
              ?sideB
              (COUNT(?battle) AS ?battlesB)
              ((SUM(IF(?won, 1, 0)) * 100.0 / COUNT(?battle)) AS ?winRateB)
            WHERE {{
              ?battle wot:onMap ?mapRaw ;
                      wot:spawn ?sideB ;
                      wot:won   ?won .
              BIND(LCASE(STR(?mapRaw)) AS ?mapKey)
            }}
            GROUP BY ?mapKey ?sideB
            HAVING (COUNT(?battle) >= {int(min_battles_per_side)})
          }}

          # Сравниваем разные стороны одной карты; < — чтобы не дублировать пары
          FILTER(?sideA != ?sideB)
          FILTER(?sideA <  ?sideB)

          # Определяем сторону с преимуществом
          BIND(IF(?winRateA >= ?winRateB, ?sideA, ?sideB) AS ?sideAdv)
          BIND(IF(?winRateA >= ?winRateB, ?winRateA, ?winRateB) AS ?winRateAdv)
          BIND(IF(?winRateA >= ?winRateB, ?battlesA, ?battlesB) AS ?battlesAdv)

          # И вторую сторону (с меньшим win rate)
          BIND(IF(?winRateA >= ?winRateB, ?sideB, ?sideA) AS ?sideOther)
          BIND(IF(?winRateA >= ?winRateB, ?winRateB, ?winRateA) AS ?winRateOther)
          BIND(IF(?winRateA >= ?winRateB, ?battlesB, ?battlesA) AS ?battlesOther)

          # Порог по разнице в процентах побед
          FILTER((?winRateAdv - ?winRateOther) >= {float(threshold_pct)})
        }}
        ORDER BY DESC(?winRateDiff) DESC(?battlesAdv) DESC(?battlesOther) ?mapName
        LIMIT {int(limit)}
        """
        results = self.execute_query(
            query,
            f"Maps with Side Imbalance (ΔWR ≥ {threshold_pct} pp; ≥ {min_battles_per_side} battles per side)"
        )
        self.print_results(results, limit=limit)
        return results

    def interactive_mode(self):
        """Интерактивный режим для выполнения произвольных запросов"""
        print("\n" + "=" * 60)
        print("🎮 INTERACTIVE MODE")
        print("=" * 60)
        print("\nEnter SPARQL query (type 'exit' to quit, 'help' for examples):\n")

        while True:
            try:
                print("\n" + ">" * 60)
                lines = []
                while True:
                    line = input()
                    if line.strip().lower() == 'exit':
                        return
                    if line.strip().lower() == 'help':
                        self.show_help()
                        break
                    lines.append(line)
                    if line.strip().endswith('}') or line.strip().endswith(';'):
                        break

                if lines:
                    query = '\n'.join(lines)
                    results = self.execute_query(query)
                    self.print_results(results, limit=50)

            except KeyboardInterrupt:
                print("\n\nExiting...")
                break
            except Exception as e:
                print(f"Error: {e}")

    def show_help(self):
        """Показывает примеры запросов"""
        print("\n" + "=" * 60)
        print("📚 QUERY EXAMPLES")
        print("=" * 60)

        examples = {
            "All tanks": """
PREFIX wot: <http://www.semanticweb.org/ontology/wot#>
SELECT ?tank ?name WHERE {
  ?tank wot:tankName ?name .
} LIMIT 10
            """,

            "Heavy tanks tier 10": """
PREFIX wot: <http://www.semanticweb.org/ontology/wot#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
SELECT ?name ?hp WHERE {
  ?tank rdf:type wot:HeavyTank .
  ?tank wot:tier 10 .
  ?tank wot:tankName ?name .
  OPTIONAL { ?tank wot:maxHP ?hp }
}
            """
        }

        for title, query in examples.items():
            print(f"\n### {title}:")
            print(query)


def main():
    parser = argparse.ArgumentParser(description='Query World of Tanks Ontology')
    parser.add_argument('--ontology', type=str,
                        default='ontology/wot_with_data.owl',
                        help='Path to ontology file')
    parser.add_argument('--query', type=str,
                        help='Predefined query to run')
    parser.add_argument('--interactive', action='store_true',
                        help='Start interactive mode')
    parser.add_argument('--stats', action='store_true',
                        help='Show ontology statistics')

    args = parser.parse_args()

    # Определяем путь к онтологии
    ontology_path = Path(__file__).parent.parent / args.ontology

    if not ontology_path.exists():
        print(f"❌ Ontology file not found: {ontology_path}")
        print("\nAvailable files:")
        ontology_dir = ontology_path.parent
        if ontology_dir.exists():
            for f in ontology_dir.glob("*.owl"):
                print(f"  - {f.name}")
        return

    # Создаем движок запросов
    engine = OntologyQueryEngine(ontology_path)

    # Статистика
    if args.stats:
        engine.get_statistics()
        return

    # Предопределенные запросы
    if args.query:
        query_map = {
            'best-tanks': lambda: engine.query_best_tanks_by_composite(limit=10),
            'best-nation': lambda: engine.query_best_nation_by_weighted_tanks(limit=10)
        }

        if args.query in query_map:
            query_map[args.query]()
        else:
            print(f"❌ Unknown query: {args.query}")
            print("\nAvailable queries:")
            for key in query_map.keys():
                print(f"  - {key}")
        return

    # Интерактивный режим
    if args.interactive:
        engine.interactive_mode()
        return

    # По умолчанию - показываем несколько запросов
    print("\n" + "=" * 60)
    print("🚀 RUNNING SAMPLE QUERIES")
    print("=" * 60)

    engine.query_best_tanks_by_composite(limit=10)
    engine.query_best_nation_by_weighted_tanks(limit=1)
    engine.query_tank_with_highest_avg_damage(min_battles=50, top_n=1)
    engine.query_worst_maps_for_tank("B-C 25 t", min_battles=1, limit=2)
    engine.query_maps_with_side_imbalance(threshold_pct=5.0, min_battles_per_side=4, limit=5)

    print("\n" + "=" * 60)
    print("💡 TIP: Use --query <name> or --interactive for more options")
    print("   Run with --help to see all options")
    print("=" * 60)


if __name__ == "__main__":
    main()
