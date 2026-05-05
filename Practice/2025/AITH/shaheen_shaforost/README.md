# Project Overview

This project involves generating RDF graphs from a dataset using an ontology. The main components of the project are the
data, the ontology class, and the graph generator.

## Data

The data used in this project is typically stored in CSV files. Each row in the CSV file represents an individual, and
the columns represent the properties of these individuals. The data is loaded into the graph generator, which then
processes it to create RDF triples.

## Ontology Class

The `Ontology` class defines the structure of the data in terms of classes and properties. It includes:

- **Classes**: These represent the different types of entities in the data (e.g., `Artist`, `Album`).
- **Properties**: These define the relationships between the classes (e.g., `hasAlbum`, `hasArtist`).

The ontology is used by the graph generator to ensure that the data is structured correctly in the RDF graph.

## Graph Generator

The `GraphGenerator` class is responsible for creating the RDF graph from the data and ontology. It includes methods to:

- **Load Data**: Read data from CSV files.
- **Generate IDs**: Create unique IDs for each individual.
- **Add Individuals**: Add individuals and their properties to the RDF graph.
- **Serialize Graph**: Save the RDF graph to a file in various formats (e.g., Turtle).

The graph generator ensures that the data is correctly represented in the RDF format, adhering to the structure defined
by the ontology.