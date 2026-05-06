from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class Ontology:
    """
    Ontology class that holds the ontology properties and classes.

    properties: dict
        Dictionary of properties with their types. Examples:
            - {"by": {"type": "DatatypeProperty", "domain": "Artist"}}
            - {"name": {"type": "ObjectProperty"}}
    classes: List[str]
        List of classes in the ontology. Examples:
            - ["Song", "Artist"]
    """

    properties: dict
    classes: List[str]


