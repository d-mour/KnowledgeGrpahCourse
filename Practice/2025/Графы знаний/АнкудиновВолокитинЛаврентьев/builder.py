import logging
from typing import List

from rdflib import OWL, RDF, RDFS, XSD, Graph, Literal, Namespace, URIRef

from kg.scraper.dota.types import (
    Ability,
    AbilityStats,
    AbilityType,
    Buffs,
    DotaItem,
    GenericItem,
    NeutralItem,
)
from kg.scraper.scrapers.base_scraper import ScrapeResult
from kg.utils import normalize_name, snake_case_to_camel_case

logger = logging.getLogger(__name__)


class DotaKgBuilder:
    ONTO_NAME = "kg-dota"
    ONTO_BASE = f"http://www.semanticweb.org/lavrent/ontologies/2025/9/{ONTO_NAME}#"
    ONTO_CLASSES = [
        "Ability",
        "PassiveAbility",
        "ActiveAbility",
        "NoTargetActiveAbility",
        "PointTargetActiveAbility",
        "UnitTargetActiveAbility",
        "AuraAbility",
        "ToggleAbility",
        "Item",
        "NeutralItem",
        "DotaItem",
        "BuildSchema",
        "BuildSchemaSlot",
        "ItemRole",
        "AbilityEffect",
    ]
    _schema_built = False

    def __init__(self) -> None:
        self.KG = Namespace(self.ONTO_BASE)

        self.graph = Graph()
        self.graph.bind("kg-dota", self.KG)

    def build_generic_item(self, item: GenericItem, item_uri: URIRef) -> None:
        name = normalize_name(item.name)

        # Create item individual
        if isinstance(item, NeutralItem):
            self.graph.add((item_uri, RDF.type, self.KG.NeutralItem))
        elif isinstance(item, DotaItem):
            self.graph.add((item_uri, RDF.type, self.KG.DotaItem))
        else:
            self.graph.add((item_uri, RDF.type, self.KG.Item))
        self.graph.add((item_uri, self.KG.name, Literal(item.name)))
        self.graph.add((item_uri, self.KG.imageUrl, Literal(item.image)))
        self.graph.add((item_uri, self.KG.wikiUrl, Literal(item.url)))

        # abilities
        if item.abilities:
            self.build_abilities(item.abilities, item_uri, name)

        # buffs
        if item.buffs:
            self.build_buffs(item.buffs, item_uri, name)

        # roles
        if item.roles:
            for role in item.roles:
                role_uri = self.KG[f"Role_{role.name}"]
                self.graph.add((role_uri, RDF.type, self.KG.ItemRole))
                self.graph.add((item_uri, self.KG.hasRole, role_uri))

    def build_buffs(self, buffs: Buffs, item_uri: URIRef, name: str) -> None:
        for k, val in buffs.asdict().items():
            if not val:
                continue
            logger.debug(f"adding buff {k}={val} to item {name}")
            buff = snake_case_to_camel_case(k)
            prop = self.KG[buff]
            self.graph.add((item_uri, prop, Literal(val, datatype=XSD.decimal)))

    def build_abilities(
        self, abilities: List[Ability], item_uri: URIRef, name: str
    ) -> None:
        for ability in abilities:
            logger.debug(f"adding ability {ability} to item {name}")
            ability_name = name + "_" + ability.name.replace(" ", "_").replace("'", "")
            ability_uri = self.KG[ability_name]

            ability_type = self.KG.Ability
            if ability.ability_type == AbilityType.PASSIVE:
                ability_type = self.KG.PassiveAbility
            elif ability.ability_type == AbilityType.NO_TARGET:
                ability_type = self.KG.NoTargetActiveAbility
            elif ability.ability_type == AbilityType.POINT_TARGET:
                ability_type = self.KG.PointTargetActiveAbility
            elif ability.ability_type == AbilityType.UNIT_TARGET:
                ability_type = self.KG.UnitTargetActiveAbility
            elif ability.ability_type == AbilityType.AURA:
                ability_type = self.KG.AuraAbility
            elif ability.ability_type == AbilityType.TOGGLE:
                ability_type = self.KG.ToggleAbility

            self.graph.add((ability_uri, RDF.type, ability_type))
            self.graph.add((ability_uri, self.KG.name, Literal(ability.name)))
            self.graph.add(
                (ability_uri, self.KG.description, Literal(ability.description))
            )

            if ability.cooldown is not None:
                self.graph.add(
                    (
                        ability_uri,
                        self.KG.cooldown,
                        Literal(ability.cooldown, datatype=XSD.integer),
                    )
                )
            if ability.mana_cost is not None:
                self.graph.add(
                    (
                        ability_uri,
                        self.KG.manaCost,
                        Literal(ability.mana_cost, datatype=XSD.integer),
                    )
                )

            if ability.stats:
                for stat_name, stat_value in ability.stats.asdict().items():
                    if stat_name == "additional_stats":
                        continue
                    logger.debug(
                        f"adding ability stat {stat_name}={stat_value} for ability {ability.name}"
                    )
                    stat_prop = self.KG[snake_case_to_camel_case(stat_name)]
                    self.graph.add(
                        (
                            ability_uri,
                            stat_prop,
                            Literal(stat_value, datatype=XSD.decimal),
                        )
                    )

            if ability.effects:
                for effect in ability.effects:
                    effect_uri = self.KG[f"AbilityEffect_{effect.name}"]
                    self.graph.add((effect_uri, RDF.type, self.KG.AbilityEffect))
                    self.graph.add((ability_uri, self.KG.hasEffect, effect_uri))

            # Link ability to item
            self.graph.add((item_uri, self.KG.hasAbility, ability_uri))

    def build_dota_item(self, item: DotaItem) -> None:
        name = item.name.replace(" ", "_").replace("'", "")
        item_uri = self.KG[name]

        self.build_generic_item(item, item_uri)

        # cost
        self.graph.add(
            (item_uri, self.KG.cost, Literal(item.cost, datatype=XSD.integer))
        )

        # Build schema
        if item.recipe:
            schema_uri = self.KG[f"{name}_BS"]
            self.graph.add((schema_uri, RDF.type, self.KG.BuildSchema))
            self.graph.add((item_uri, self.KG.hasBuildSchema, schema_uri))

            used = set()
            for comp in item.recipe:
                normalized_name = normalize_name(comp)
                qty = item.recipe.count(comp)

                if normalized_name not in used:
                    used.add(normalized_name)

                    if qty == 1:
                        slot_ref = self.KG[normalized_name]
                    else:
                        slot_id = f"{normalized_name}_{qty}x"
                        slot_ref = self.KG[slot_id]
                        self.graph.add((slot_ref, RDF.type, self.KG.BuildSchemaSlot))
                        self.graph.add(
                            (slot_ref, self.KG.hasItem, self.KG[normalized_name])
                        )
                        self.graph.add(
                            (
                                slot_ref,
                                self.KG.hasQuantity,
                                Literal(qty, datatype=XSD.integer),
                            )
                        )

                    self.graph.add((schema_uri, self.KG.hasSlot, slot_ref))

        # Buffs
        if item.buffs:
            self.build_buffs(item.buffs, item_uri, name)

        # Abilities
        if item.abilities:
            self.build_abilities(item.abilities, item_uri, name)

    def build_neutral_item(self, item: NeutralItem) -> None:
        name = normalize_name(item.name)
        item_uri = self.KG[name]

        self.build_generic_item(item, item_uri)

        # tier
        self.graph.add(
            (item_uri, self.KG.tier, Literal(item.tier, datatype=XSD.integer))
        )

        # Abilities
        if item.abilities:
            self.build_abilities(item.abilities, item_uri, name)

    def build_schema(self) -> None:
        # Classes
        for c in self.ONTO_CLASSES:
            self.graph.add((self.KG[c], RDF.type, OWL.Class))

        # Class inheritance
        inheritance = [
            (self.KG["PassiveAbility"], self.KG["Ability"]),
            (self.KG["ActiveAbility"], self.KG["Ability"]),
            (self.KG["NoTargetActiveAbility"], self.KG["ActiveAbility"]),
            (self.KG["PointTargetActiveAbility"], self.KG["ActiveAbility"]),
            (self.KG["UnitTargetActiveAbility"], self.KG["ActiveAbility"]),
            (self.KG["AuraAbility"], self.KG["Ability"]),
            (self.KG["ToggleAbility"], self.KG["Ability"]),
            (self.KG["NeutralItem"], self.KG["Item"]),
            (self.KG["DotaItem"], self.KG["Item"]),
        ]
        for subclass, superclass in inheritance:
            self.graph.add((subclass, RDFS.subClassOf, superclass))

        # Object properties
        self.graph.add((self.KG.hasBuildSchema, RDF.type, OWL.ObjectProperty))
        self.graph.add((self.KG.hasBuildSchema, RDFS.domain, self.KG.DotaItem))
        self.graph.add((self.KG.hasBuildSchema, RDFS.range, self.KG.BuildSchema))

        self.graph.add((self.KG.hasSlot, RDF.type, OWL.ObjectProperty))
        self.graph.add((self.KG.hasSlot, RDFS.domain, self.KG.BuildSchema))
        self.graph.add((self.KG.hasSlot, RDFS.range, self.KG.BuildSchemaSlot))
        self.graph.add(
            (self.KG.hasSlot, RDFS.range, self.KG.DotaItem)
        )  # for slots with qty=1

        self.graph.add((self.KG.hasAbility, RDF.type, OWL.ObjectProperty))
        self.graph.add((self.KG.hasAbility, RDFS.domain, self.KG.Item))
        self.graph.add((self.KG.hasAbility, RDFS.range, self.KG.Ability))

        self.graph.add((self.KG.hasItem, RDF.type, OWL.ObjectProperty))
        self.graph.add((self.KG.hasItem, RDFS.domain, self.KG.BuildSchemaSlot))
        self.graph.add((self.KG.hasItem, RDFS.range, self.KG.DotaItem))

        self.graph.add((self.KG.hasQuantity, RDF.type, OWL.DatatypeProperty))
        self.graph.add((self.KG.hasQuantity, RDFS.domain, self.KG.BuildSchemaSlot))
        self.graph.add((self.KG.hasQuantity, RDFS.range, XSD.integer))

        self.graph.add((self.KG.hasRole, RDF.type, OWL.ObjectProperty))
        self.graph.add((self.KG.hasRole, RDFS.domain, self.KG.Item))
        self.graph.add((self.KG.hasRole, RDFS.range, self.KG.ItemRole))

        self.graph.add((self.KG.hasEffect, RDF.type, OWL.ObjectProperty))
        self.graph.add((self.KG.hasEffect, RDFS.domain, self.KG.Ability))
        self.graph.add((self.KG.hasEffect, RDFS.range, self.KG.AbilityEffect))

        # Datatype properties: buffs
        for k in Buffs.__annotations__:
            buff_name = snake_case_to_camel_case(k)
            self.graph.add((self.KG[buff_name], RDF.type, OWL.DatatypeProperty))
            self.graph.add((self.KG[buff_name], RDFS.domain, self.KG.Item))

        # initialize ability stats data properties
        for k in list(AbilityStats.__annotations__.keys()) + ["mana_cost", "cooldown"]:
            if k == "additional_stats":
                continue
            stat_name = snake_case_to_camel_case(k)
            self.graph.add((self.KG[stat_name], RDF.type, OWL.DatatypeProperty))
            self.graph.add((self.KG[stat_name], RDFS.domain, self.KG.Ability))
            self.graph.add((self.KG[stat_name], RDFS.range, XSD.integer))

        # Other datatype properties
        # dota item cost
        self.graph.add((self.KG.cost, RDF.type, OWL.DatatypeProperty))
        self.graph.add((self.KG.cost, RDFS.domain, self.KG.DotaItem))
        self.graph.add((self.KG.cost, RDFS.range, XSD.integer))

        # neutral item tier
        self.graph.add((self.KG.tier, RDF.type, OWL.DatatypeProperty))
        self.graph.add((self.KG.tier, RDFS.domain, self.KG.NeutralItem))
        self.graph.add((self.KG.tier, RDFS.range, XSD.integer))

        self._schema_built = True

    def build(self, data: ScrapeResult) -> None:
        if not self._schema_built:
            logger.info("schema not yet built, building...")
            self.build_schema()
            logger.info("schema built")

        # build individuals
        if data.dota_items:
            for dota_item in data.dota_items.values():
                self.build_dota_item(dota_item)

        if data.neutral_items:
            for neutral_item in data.neutral_items.values():
                self.build_neutral_item(neutral_item)

    def load_from_file(self, path: str) -> None:
        """
        loads ontology from .rdf
        """
        self.graph.parse(path, format="xml")

    def save_to_file(self, output_path: str) -> None:
        self.graph.serialize(destination=output_path, format="xml")
