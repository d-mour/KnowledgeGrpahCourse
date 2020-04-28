# Ontologies
Contains ontologies made during the respective course at the ITMO University.
[Visualization](http://www.visualdataweb.de/webvowl/#iri=https://se.ifmo.ru/~s207602/ontologies/recommender.owl)
[Visualization (short link)](http://bit.ly/recommender-ontology)
## Usage
To load ontology pre-constructed via protege and augment it with data from annotations written in `.yaml` files:
```shell script
python -m ontologies parse --input-dir ontologies/resources/documents/annotations --input-file ontologies/resources/recommender.ttl --output-file ontologies/resources/augmented-recommender.ttl
```
