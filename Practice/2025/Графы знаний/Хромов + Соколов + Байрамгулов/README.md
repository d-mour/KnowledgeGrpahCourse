# Knowledge Graph Project: Brawl Stars

**Student:**  Khromov Daniel, Bayramgulov Munir, Sokolov Artem 

## Project Overview

This project implements a knowledge graph for **Brawl Stars**, a popular mobile game. The work includes ontology design, knowledge graph population, semantic data processing with RDFlib/OWLReady, and embedding generation for entities.

The project follows the course requirements with all six required components:

| Component | File | Description |
|-----------|------|-------------|
| Ontology | [`brawl_ontology.ttl`](/brawl_ontology.ttl) | TTL representation of the Brawl Stars ontology |
| Knowledge Graph | [`brawl_graph.ttl`](/brawl_graph.ttl) | Populated knowledge graph with all entities |
| RDFlib/OWLReady Code | [`graph_rdflib.ipynb`](/graph_rdflib.ipynb) | Interactive notebook with graph operations |
| Embeddings Training | [`train_embeddings.py`](/train_embeddings.py) | Python script for learning entity embeddings |
| Presentation | [`Graf-znanij-Brawl-Stars.pdf`](/Graf-znanij-Brawl-Stars.pdf) | Project presentation in PDF format |

## Ontology Design ([`brawl_ontology.ttl`](/brawl_ontology.ttl))

The Brawl Stars ontology defines the core concepts and relationships:

**Main Classes:**
- **Brawler** - Playable characters with attributes (rarity, health, damage)
- **Gamemode** - Game modes (Gem Grab, Brawl Ball, etc.)
- **Map** - Battle arenas with terrain features
- **Ability** - Special attacks and star powers

**Properties:**
- `hasRarity`, `hasHealth`, `hasDamage` (data properties)
- `playsIn`, `hasAbility`, `locatedOn` (object properties)

## Knowledge Graph ([`brawl_graph.ttl`](/brawl_graph.ttl))

The populated knowledge graph contains:

- **50+ Brawler instances** (Shelly, Colt, Jessie, etc.) with attributes
- **10+ Game mode instances** with rules and objectives
- **30+ Map instances** with terrain characteristics
- **Relationships** connecting brawlers to their abilities and preferred game modes

**Example Triple:**
```
<BrawlStars/Shelly> rdf:type <Ontology/Brawler> .
<BrawlStars/Shelly> <Ontology/hasRarity> "Common" .
<BrawlStars/Shelly> <Ontology/hasAbility> <BrawlStars/Shell_Shock> .
```

## Results and Findings

**Key Insights:**
1. Brawlers cluster by rarity and role in embedding space
2. Similar abilities have close vector representations
3. Game mode preferences can be predicted from embeddings
4. The knowledge graph enables complex queries not possible in the original game data

**Applications:**
- Brawler recommendation system
- Game balance analysis
- New character design suggestions
- Matchmaking optimization

## Future Work

1. **Expand Ontology** - Add items, skins, and player statistics
2. **Improve Embeddings** - Experiment with ComplEx, RotatE models
3. **Real-time Updates** - Connect to Brawl Stars API for live data

## References

1. Brawl Stars Official Documentation
2. RDFlib Documentation
3. TransE: Translating Embeddings for Modeling Multi-relational Data (Bordes et al., 2013)
4. Course materials on Knowledge Graph construction
