import numpy as np
import pandas as pd
from rdflib import Graph, Namespace, Literal, RDF, RDFS, OWL, XSD

def clean_numeric_value(value):
    if pd.isna(value):
        return None
    try:
        if isinstance(value, str):
            value = value.replace('%', '').replace(',', '').strip()
        return float(value)
    except:
        return None

def safe_name(x: str) -> str:
    s = str(x).strip()
    if not s:
        return ""
    for ch in [" ", "/", "\\", "#", "?", "&", ":", ";", ",", "\"", "'"]:
        s = s.replace(ch, "_")
    s = s.strip("_")
    if not s:
        return ""
    if s[0].isdigit():
        s = f"n_{s}"
    return s

def parse_teams_field(teams_value):
    if pd.isna(teams_value):
        return []
    s = str(teams_value).strip()
    if not s or s.lower() in ("nan", "none"):
        return []
    for sep in [";", ",", "|"]:
        if sep in s:
            parts = [p.strip() for p in s.split(sep)]
            return [p for p in parts if p and p.lower() not in ("nan", "none")]
    return [s]

def make_qcut(series: pd.Series, q=3, name="col"):
    s = pd.to_numeric(series, errors="coerce")
    try:
        codes, edges = pd.qcut(s, q=q, labels=False, retbins=True, duplicates="drop")
        k = len(edges) - 1
        if k <= 1:
            return pd.Series([pd.NA]*len(s), index=s.index)
        labels = []
        for i in range(k):
            if i == 0:
                labels.append(f"{name}_low")
            elif i == k-1:
                labels.append(f"{name}_high")
            else:
                labels.append(f"{name}_mid" if k == 3 else f"{name}_{i}")
        return codes.map(lambda x: labels[int(x)] if pd.notna(x) else pd.NA)
    except Exception:
        return pd.Series([pd.NA]*len(s), index=s.index)

def add_archetype_5(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    kill_cols = ["rifle_kills","sniper_kills","smg_kills","pistol_kills","grenade_kills","other_kills"]
    for c in kill_cols:
        if c not in df.columns:
            df[c] = 0

    total = df[kill_cols].sum(axis=1).replace(0, np.nan)
    df["sniper_share"] = df["sniper_kills"] / total

    q_sniper = df["sniper_share"].quantile(0.80)
    q_open   = df["opening_kill_ratio"].quantile(0.80) if "opening_kill_ratio" in df.columns else None
    q_ast    = df["assists_per_round"].quantile(0.80) if "assists_per_round" in df.columns else None
    q_gr     = df["grenade_dmg_per_round"].quantile(0.80) if "grenade_dmg_per_round" in df.columns else None
    q_deathL = df["deaths_per_round"].quantile(0.20) if "deaths_per_round" in df.columns else None

    arche = []
    for _, r in df.iterrows():
        if pd.notna(r["sniper_share"]) and r["sniper_share"] >= q_sniper:
            arche.append("Sniper"); continue
        if q_open is not None and pd.notna(r.get("opening_kill_ratio")) and r["opening_kill_ratio"] >= q_open:
            arche.append("Entry"); continue

        support_flag = False
        if q_ast is not None and pd.notna(r.get("assists_per_round")) and r["assists_per_round"] >= q_ast:
            support_flag = True
        if q_gr is not None and pd.notna(r.get("grenade_dmg_per_round")) and r["grenade_dmg_per_round"] >= q_gr:
            support_flag = True
        if support_flag:
            arche.append("Support"); continue

        if q_deathL is not None and pd.notna(r.get("deaths_per_round")) and r["deaths_per_round"] <= q_deathL:
            arche.append("Anchor"); continue

        arche.append("Rifler")

    df["archetype_5"] = arche
    return df

def add_main_weapon(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    cols = ["rifle_kills","sniper_kills","smg_kills","pistol_kills"]
    for c in cols:
        df[c] = pd.to_numeric(df.get(c), errors="coerce").fillna(0)
    df["main_weapon"] = df[cols].idxmax(axis=1).str.replace("_kills", "", regex=False)
    return df

def load_cs2_data(csv_file,output_file,
    output_format = "turtle",n = 3,
    include_numeric_literals = False, add_archetypes = True
):
    g = Graph()
    CS2 = Namespace("http://example.org/cs2#")
    FOAF = Namespace("http://xmlns.com/foaf/0.1/")

    g.bind("cs2", CS2)
    g.bind("foaf", FOAF)

    df = pd.read_csv(csv_file)

    df = df.dropna(subset=["player_id"]).copy()
    df["player_id"] = df["player_id"].apply(clean_numeric_value).astype(int)

    df = add_main_weapon(df)
    if add_archetypes:
        df = add_archetype_5(df)

    for cls in ["Player","Team","Country","Weapon","Bucket","Archetype"]:
        g.add((CS2[cls], RDF.type, OWL.Class))

    def add_objprop(name, domain, range_):
        g.add((CS2[name], RDF.type, OWL.ObjectProperty))
        g.add((CS2[name], RDFS.domain, CS2[domain]))
        g.add((CS2[name], RDFS.range, CS2[range_]))

    add_objprop("fromCountry", "Player", "Country")
    add_objprop("playsFor", "Player", "Team")
    add_objprop("playedFor", "Player", "Team")
    add_objprop("hasMainWeapon", "Player", "Weapon")
    add_objprop("hasArchetype", "Player", "Archetype")

    cols = [
        "rating",
        "deaths_per_round",
        "assists_per_round",
        "opening_kill_ratio",
    ]
    cols = [c for c in cols if c in df.columns]

    for col in cols:
        df[col + "_level"] = make_qcut(df[col], q=n, name=col)

        prop = f"has_{col}_level"
        add_objprop(prop, "Player", "Bucket")

    if include_numeric_literals:
        for col in cols:
            g.add((CS2[col], RDF.type, OWL.DatatypeProperty))
            g.add((CS2[col], RDFS.domain, CS2["Player"]))
            g.add((CS2[col], RDFS.range, XSD.float))

    for _, row in df.iterrows():
        pid = int(row["player_id"])
        player_uri = CS2[f"player_{pid}"]
        g.add((player_uri, RDF.type, CS2.Player))

        if pd.notna(row.get("nickname")):
            nick = str(row["nickname"]).strip()
            if nick and nick.lower() != "nan":
                g.add((player_uri, FOAF.nick, Literal(nick)))
        if pd.notna(row.get("real_name")):
            rn = str(row["real_name"]).strip()
            if rn and rn.lower() != "nan":
                g.add((player_uri, FOAF.name, Literal(rn)))

        if pd.notna(row.get("country")):
            c_name = str(row["country"]).strip()
            if c_name and c_name.lower() not in ("nan","none",""):
                country_uri = CS2[f"country_{safe_name(c_name)}"]
                g.add((country_uri, RDF.type, CS2.Country))
                g.add((player_uri, CS2.fromCountry, country_uri))

        if pd.notna(row.get("current_team")):
            t_name = str(row["current_team"]).strip()
            if t_name and t_name.lower() not in ("nan","none",""):
                team_uri = CS2[f"team_{safe_name(t_name)}"]
                g.add((team_uri, RDF.type, CS2.Team))
                g.add((player_uri, CS2.playsFor, team_uri))

        for t in parse_teams_field(row.get("teams")):
            team_uri = CS2[f"team_{safe_name(t)}"]
            g.add((team_uri, RDF.type, CS2.Team))
            g.add((player_uri, CS2.playedFor, team_uri))

        if pd.notna(row.get("main_weapon")):
            w = str(row["main_weapon"]).strip()
            if w and w.lower() not in ("nan","none",""):
                w_uri = CS2[f"weapon_{safe_name(w)}"]
                g.add((w_uri, RDF.type, CS2.Weapon))
                g.add((player_uri, CS2.hasMainWeapon, w_uri))

        if "archetype_5" in df.columns and pd.notna(row.get("archetype_5")):
            a = str(row["archetype_5"]).strip()
            a_uri = CS2[f"archetype_{safe_name(a)}"]
            g.add((a_uri, RDF.type, CS2.Archetype))
            g.add((player_uri, CS2.hasArchetype, a_uri))

        for col in cols:
            lvl = row.get(col + "_level")
            if pd.notna(lvl):
                lvl_uri = CS2[f"{safe_name(lvl)}"]
                g.add((lvl_uri, RDF.type, CS2.Bucket))
                g.add((player_uri, CS2[f"has_{col}_level"], lvl_uri))

            if include_numeric_literals:
                val = clean_numeric_value(row.get(col))
                if val is not None:
                    g.add((player_uri, CS2[col], Literal(float(val), datatype=XSD.float)))

    g.serialize(destination=output_file, format=output_format)

    stats = {
        "rows": len(df),
        "triples": len(g),
        "output_file": output_file,
        "format": output_format,
    }
    return stats


if __name__ == "__main__":
    stats = load_cs2_data(
        csv_file="cs2_players.csv",
        output_file="cs2_ontology.ttl",
        output_format="turtle",
    )
    print(stats)
