import jq
from rdflib import Literal, Namespace, Graph, URIRef
from rdflib.namespace import RDF, RDFS

JQ_SKILLS = r"""
map(select(.type != "enemyCollectionDetail") | .collectionNo as $servant | {servant: $servant} + .skills[]) | map({
        id, servant, name,
        detail: (.unmodifiedDetail | gsub(".0."; "Lv.") | gsub("\\[g..o."; "") | gsub("./o../g."; "")),
        slot: .num, version: .priority, cooldown: .coolDown[9],
        effects: (.functions | map(select(
                                                .funcTargetTeam == "playerAndEnemy" or
                                                .funcTargetTeam == "enemy" and (.funcTargetType == "enemy" or .funcTargetType == "enemyAll") or
                                                .funcTargetTeam == "player" and (.funcTargetType != "enemy" and .funcTargetType != "enemyAll")
                                        ) | {
                id: .funcId, type: .funcType, team: .funcTargetTeam, target: .funcTargetType, popup: .funcPopupText,
                targetTraits: .functvals, targetTraits2: .traitVals,
                value: .svals[9], level: (.svals[0] != .svals[9]),
                buff: (.buffs[0] | if . then {
                        id, name, detail, type, traits: .vals, targetTraits: .tvals, ourGameplayTrait: .ckSelfIndv, enemyGameplayTrait: .ckOpIndv
                } else null end)
        }))
})"""
# (.unmodifiedDetail | gsub(".0."; "Lv.") | gsub("\\[g..o."; "") | gsub("./o../g."; ""))

FGO = Namespace("http://kg@se.ifmo.ru/~s367583/fgo#")

TOTAL_EFFECTS = 0
COVERED_EFFECTS = 0

TOTAL_BUFFS = 0
COVERED_BUFFS = 0


def has(g: Graph, node: URIRef):
    return not not next(g.objects(node, RDF.type), None)


def func_label(func) -> str:
    if func.popup == "":
        return ""

    # TODO: add traits
    return f'{func.popup.replace("\n", " ")} ({func.target})'


def func_shortenSkill(g: Graph, node, effect) -> URIRef:
    if node:
        g.add((node, FGO.decreases, FGO["Skill_Cooldown"]))
    return value_Turns(g, effect.value["Value"])


def func_gainStar(g: Graph, node, effect) -> URIRef:
    if node:
        g.add((node, FGO.increases, FGO["C._Star_Count"]))
    return value_Stars(g, effect.value["Value"])


def func_lossStar(g: Graph, node, effect) -> URIRef:
    if node:
        g.add((node, FGO.decreases, FGO["C._Star_Count"]))
    return value_Stars(g, effect.value["Value"])


def func_gainNp(g: Graph, node, effect) -> URIRef:
    if node:
        g.add((node, FGO.increases, FGO["NP_Gauge"]))
    return value_Percent(g, effect.value["Value"] // 100)


func_gainNpBuffIndividualSum = func_gainNp


def func_gainNpFromTargets(g: Graph, node, effect) -> URIRef:
    if node:
        g.add((node, FGO.increases, FGO["NP_Gauge"]))
    return value_Percent(g, effect.value["DependFuncVals"]["Value"] // 100)


def func_lossNp(g: Graph, node, effect) -> URIRef:
    if node:
        g.add((node, FGO.decreases, FGO["NP_Gauge"]))
    return value_Percent(g, effect.value["Value"] // 100)


def func_gainHp(g: Graph, node, effect) -> URIRef:
    if node:
        g.add((node, FGO.increases, FGO["HP_Bar"]))
        effect.popup = "HP Gain"
        g.add((node, RDFS.label, Literal(func_label(effect))))
    return value_HP(g, effect.value["Value"])


def func_gainHpFromTargets(g: Graph, node, effect) -> URIRef:
    if node:
        g.add((node, FGO.increases, FGO["HP_Bar"]))
        effect.popup = "HP Gain"
        g.add((node, RDFS.label, Literal(func_label(effect))))
    return value_HP(g, effect.value["DependFuncVals"]["Value"])


def func_lossHpSafe(g: Graph, node, effect) -> URIRef:
    if node:
        g.add((node, FGO.decreases, FGO["HP_Bar"]))
    return value_HP(g, effect.value["Value"])


# def func_subState(g: Graph, node, effect) -> URIRef: ...


# These functions are both really special and rare, so we won't bother with
# trying to stuff them into our graph.
def func_moveState(*_): 
    # Van Gogh's Absorb Curse
    ...


def func_cardReset(*_): 
    # Altria (Ruler) Skill 2
    ...


def func_fixCommandcard(*_):
    # BB (Summer) Skill 3
    ...



def func_transformServant(*_): 
    # Melusine transformation
    ...


buffs_tsv = """
attackAfterFunction	Skill_{}
attackBeforeFunction	Skill_{}
commandattackAfterFunction	Skill_{}
commandattackBeforeFunction	Skill_{}
damageFunction	Skill_{}
deadFunction	Skill_{}
delayFunction	Skill_{}
selfturnendFunction	Skill_{}
gutsFunction	Skill_{}
npattackPrevBuff	Skill_{}
addIndividuality	Trait_{}
fieldIndividuality	Trait_{}
subIndividuality	Trait_{}
donotAct	-
donotNoble	-
donotSkill	-
addDamage	ATK
addMaxhp	HP
subMaxhp	HP
subSelfdamage	ATK
reduceHp	HP
regainHp	HP
regainNp	%
regainStar	C._Stars_{}
pierceDefence	-
pierceInvincible	-
invincible	-
avoidance	-
breakAvoidance	-
avoidInstantdeath	-
avoidState	-
guts	HP
downCriticalRateDamageTaken	%
downCriticalrate	%
downDefence	%
downDefencecommandall	%
downGainHp	%
downNpdamage	%
downNpturnval	Turns_{}
downTolerance	%
upAtk	%
upCommandall	%
upCriticaldamage	%
upCriticalpoint	%
upDamage	%
upDamageIndividuality	%
upDamageIndividualityActiveonly	%
upDamagedropnp	%
upDefence	%
upDropnp	%
upFuncHpReduce	%
upGainHp	%
upGivegainHp	%
upGrantInstantdeath	%
upGrantstate	%
upHate	%
upNonresistInstantdeath	%
upNpdamage	%
upResistInstantdeath	%
upStarweight	%
upTolerance	%
upToleranceSubstate	%
downAtk	%
downStarweight	%
"""

print(buffs_tsv.strip().split("\n"))

buffs = {
    k: (k, *v) 
    for line in buffs_tsv.strip().split("\n") 
    for k, *v in [line.split("\t")]
}
print(buffs)


"""
def buff_upDropnp(g: Graph, node: URIRef, buff, value) -> URIRef:
    if node:
        g.add((node, FGO.increases, FGO["Current_NP_Gain"]))
    return value_Percent(g, value["Value"] // 10)


def buff_downDropnp(g: Graph, node: URIRef, buff, value) -> URIRef:
    if node:
        g.add((node, FGO.decreases, FGO["Current_NP_Gain"]))
    return value_Percent(g, value["Value"] // 10)


def buff_upAtk(g: Graph, node: URIRef, buff, value) -> URIRef:
    if node:
        g.add((node, FGO.increases, FGO["Current_ATK"]))
    return value_Percent(g, value["Value"] // 10)


def buff_downAtk(g: Graph, node: URIRef, buff, value) -> URIRef:
    if node:
        g.add((node, FGO.decreases, FGO["Current_ATK"]))
    return value_Percent(g, value["Value"] // 10)


def buff_upNpdamage(g: Graph, node: URIRef, buff, value) -> URIRef:
    if node:
        g.add((node, FGO.increases, FGO["NP_Damage"]))
    return value_Percent(g, value["Value"] // 10)


def buff_downNpdamage(g: Graph, node: URIRef, buff, value) -> URIRef:
    if node:
        g.add((node, FGO.decreases, FGO["NP_Damage"]))
    return value_Percent(g, value["Value"] // 10)


def buff_upCommandall(g: Graph, node: URIRef, buff, value) -> URIRef:
    card_type = buff.ourGameplayTrait[0]["name"].removeprefix("card")
    if node:
        g.add((node, FGO.increases, FGO[f"{card_type}_Damage"]))
    return value_Percent(g, value["Value"] // 10)
"""

def init_buff(g: Graph, node: URIRef | None, buff, value) -> URIRef | None:
    global TOTAL_BUFFS, COVERED_BUFFS
    TOTAL_BUFFS += 1
    if node:
        g.add((node, RDF.type, FGO["Buff"]))
        g.add((node, FGO["id"], Literal(buff.id)))
        g.add((node, FGO.hasBuffType, FGO[f"BuffType_{buff.type}"]))
        g.add((node, RDFS.label, Literal(buff.name)))
        g.add((node, RDFS.comment, Literal(buff.detail)))

        for trait in buff.traits:
            g.add((node, FGO.hasBuffTrait, trait_Trait(g, trait)))

        for trait in buff.targetTraits:
            g.add((node, FGO.targetsTrait, trait_Trait(g, trait)))

        for trait in buff.ourGameplayTrait:
            g.add((node, FGO.requiresSelfTrait, trait_Trait(g, trait)))

        for trait in buff.enemyGameplayTrait:
            g.add((node, FGO.requiresEnemyTrait, trait_Trait(g, trait)))


    # if (serializer := globals().get(f"buff_{buff.type}")) is None:
    #     return

    # COVERED_BUFFS += 1

    # value_node = serializer(g, node, buff, value)

    if buff.type not in buffs:
        return None

    _, value_type = buffs[buff.type]
    if value_type == "%":
        value_node = value_Percent(g, value["Value"] // 10)
    elif value_type == "HP":
        value_node = value_HP(g, value["Value"])
    elif value_type == "ATK":
        value_node = value_ATK(g, value["Value"])
    elif value_type == "Trait_{}":
        # value_node = trait_Trait(g, value["Value"])
        value_node = FGO["Trait_{}".format(value["Value"])]
    elif value_type == "C._Stars_{}":
        value_node = value_Stars(g, value["Value"])
    elif value_type == "Turns_{}":
        value_node = value_Turns(g, value["Value"])
    else:
        value_node = None

    if value_node is not None:
        TOTAL_BUFFS += 1

    return value_node


def func_addState(g: Graph, func_node: URIRef, effect) -> URIRef | None:
    buff = effect.buff

    buff_node = FGO[f"Buff_{buff.id}"]
    value = init_buff(g, None if has(g, buff_node) else buff_node, buff, effect.value)

    if func_node is not None:
        g.add((func_node, FGO.grantsBuff, buff_node))

    return value


func_addStateShort = func_addState


def func_subState(g: Graph, node: URIRef, effect):
    if node:
        for trait in effect.targetTraits2:
            g.add((node, FGO.affectsBuffsWithTrait, trait_Trait(g, trait)))
    return None


class AttributeDict(dict):
    __slots__ = ()
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__


def trait_Trait(g: Graph, trait, cls="Buff_Trait") -> URIRef:
    id, name = trait["id"], trait["name"]
    node = FGO[f"Trait_{id}"]
    if not has(g, node):
        g.add((node, RDF.type, FGO[cls]))
        g.add((node, FGO["id"], Literal(id)))
        if name != "unknown":
            g.add((node, RDFS.label, Literal(name)))
    return node


def value_Turns(g: Graph, v: int) -> URIRef:
    node = FGO[f"Turns_{v}"]
    if not has(g, node):
        g.add((node, RDF.type, FGO["Turns"]))
        g.add((node, RDFS.label, Literal(f"{v} Turns")))
        g.add((node, FGO.value, Literal(v)))
    return node


def value_Times(g: Graph, v: int) -> URIRef:
    node = FGO[f"Times_{v}"]
    if not has(g, node):
        g.add((node, RDF.type, FGO["Times"]))
        g.add((node, RDFS.label, Literal(f"{v} Times")))
        g.add((node, FGO.value, Literal(v)))
    return node


def value_Target(g: Graph, target: str) -> URIRef:
    node = FGO[f"Target_{target}"]
    if not has(g, node):
        g.add((node, RDF.type, FGO["Target"]))
    # TODO: add label
    return node


def value_Percent(g: Graph, v: int) -> URIRef:
    node = FGO[f"{v}_Percent"]
    if not has(g, node):
        g.add((node, RDF.type, FGO["Percent"]))
        g.add((node, RDFS.label, Literal(f"{v}%")))
        g.add((node, FGO.value, Literal(v)))
    return node


def value_Stars(g: Graph, v: int) -> URIRef:
    node = FGO[f"C._Stars_{v}"]
    if not has(g, node):
        g.add((node, RDF.type, FGO["C._Stars"]))
        g.add((node, RDFS.label, Literal(f"{v} C. Stars")))

        g.add((node, FGO.value, Literal(v)))
    return node


def value_HP(g: Graph, v: int) -> URIRef:
    node = FGO[f"HP_{v}"]
    if not has(g, node):
        g.add((node, RDF.type, FGO["HP"]))
        g.add((node, RDFS.label, Literal(f"{v} HP")))
        g.add((node, FGO.value, Literal(v)))
    return node


def value_ATK(g: Graph, v: int) -> URIRef:
    node = FGO[f"ATK_{v}"]
    if not has(g, node):
        g.add((node, RDF.type, FGO["ATK"]))
        g.add((node, RDFS.label, Literal(f"{v} ATK")))
        g.add((node, FGO.value, Literal(v)))
    return node


def value_Skill_Priority(g: Graph, priority: int) -> URIRef:
    node = FGO[f"Skill_Priority_{priority}"]
    if not has(g, node):
        g.add((node, RDF.type, FGO["Skill_Priority"]))
        g.add((node, RDFS.label, Literal(f"Priority {priority}")))
    return node


def skills_to_rdf(data_json_path: str, rating_json_path: str, in_rdf: str, out_rdf: str):
    global TOTAL_EFFECTS, COVERED_EFFECTS

    with open(data_json_path) as f:
        skills = jq.compile(JQ_SKILLS).input_text(f.read()).first()

    with open(rating_json_path) as f:
        ratings = jq.compile("map(.analysis.skill_priority) | add").input_text(f.read()).first()

    skills = list(map(AttributeDict, skills))
    for skill in skills:
        skill.effects = list(map(AttributeDict, skill.effects))
        for effect in skill.effects:
            if effect.buff is not None:
                effect.buff = AttributeDict(effect.buff)

        # skills = json.loads(skills_filtered)

    g = Graph()
    g.parse(in_rdf)

    for cd_value in set(s.cooldown for s in skills):
        cd_node = FGO[f"Turns_{cd_value}"]
        g.add((cd_node, RDF.type, FGO["Turns"]))
        g.add((cd_node, RDFS.label, Literal(f"{cd_value} Turns")))

    for skill in skills:
        skill_node = FGO[f"Skill_{skill.id}"]

        g.add((skill_node, RDF.type, FGO["Skill"]))

        # Basic skill properties
        g.add((skill_node, RDFS.label, Literal(skill.name)))
        g.add((skill_node, RDFS.comment, Literal(skill.detail)))
        g.add((skill_node, FGO["id"], Literal(skill.id)))

        g.add((FGO[f"Servant_{skill.servant}"], FGO[f"hasSkill{skill.slot}"], skill_node))
        g.add((FGO[f"Servant_{skill.servant}"], FGO[f"hasSkill"], skill_node))

        if skill.name in ratings:
            g.add((skill_node, FGO.hasPriority, value_Skill_Priority(g, ratings[skill.name])))

        # Cooldown is a node
        g.add((skill_node, FGO.hasCooldown, FGO[f"Turns_{skill.cooldown}"]))

        # Effects are tricky
        for no, effect in enumerate(skill.effects):
            # Each effect is described in terms of:
            # *Function*, which has id, type, target traits, affects traits, and a buff granted.
            # *Value*, which is percentage, times, and other things.

            TOTAL_EFFECTS += 1
            effect_node = FGO[f"Skill_{skill.id}/Effect_{no}"]
            g.add((effect_node, RDF.type, FGO["Skill_Effect"]))
            g.add((skill_node, FGO.hasEffect, effect_node))

            func = FGO[f"Function_{effect.id}"]
            func_existed = has(g, func)

            g.add((effect_node, FGO.hasFunction, func))

            if not func_existed:
                g.add((func, RDF.type, FGO["Function"]))
                g.add((func, FGO["id"], Literal(effect.id)))
                g.add((func, FGO.hasFuncType, FGO[f"FuncType_{effect.type}"]))

                if effect.popup != "":
                    g.add((func, RDFS.label, Literal(func_label(effect))))

                g.add((func, FGO.targets, value_Target(g, effect.target)))

                for trait in effect.targetTraits:
                    g.add((func, FGO.targetsTrait, trait_Trait(g, trait)))

                # if effect.targetTraits2 is not None:
                #     for trait in effect.targetTraits2:
                #         g.add((effect_node, FGO.affectsTrait, trait_Trait(g, trait)))

            if (turns := effect.value.get("Turn", -1)) != -1:
                g.add((effect_node, FGO.hasDuration, value_Turns(g, turns)))

            if (times := effect.value.get("Count", -1)) != -1:
                g.add((effect_node, FGO.hasDuration, value_Times(g, times)))

            if (serializer := globals().get(f"func_{effect.type}")) is None:
                continue
            COVERED_EFFECTS += 1

            value = serializer(g, (None if func_existed else func), effect)
            if value is not None:
                g.add((effect_node, FGO.hasValue, value))

    g.serialize(destination=out_rdf)


if __name__ == "__main__":
    import sys

    skills_json, analysis_json, in_rdf, out_rdf = sys.argv[1:]
    skills_to_rdf(skills_json, analysis_json, in_rdf, out_rdf)

    print(
        f"fx:\ttotal = {TOTAL_EFFECTS:4}, covered = {COVERED_EFFECTS:4}, % = {COVERED_EFFECTS / TOTAL_EFFECTS * 100:.04f}"
    )
    print(
        f"buffs:\ttotal = {TOTAL_BUFFS:4}, covered = {COVERED_BUFFS:4}, % = {COVERED_BUFFS/ TOTAL_BUFFS * 100:.04f}"
    )
