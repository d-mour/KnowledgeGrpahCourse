from knowledge_graph.ontologies import Ontology
from knowledge_graph.graphs import GraphGenerator

ontology = Ontology(
    properties={
        "by": {"type": "DatatypeProperty", "domain": "Artist"},
        "inAlbum": {"type": "DatatypeProperty", "domain": "Album"},
        "inGenre": {"type": "DatatypeProperty", "domain": "Genre"},
        "playsGenre": {"type": "DatatypeProperty", "domain": "Genre"},
        "inPlaylist": {"type": "DatatypeProperty", "domain": "Playlist"},
    },
    classes=["Song", "Artist", "Album", "Genre", "Playlist"],
)

generator = GraphGenerator(ontology, "music:")
generator.add_individual("song1", [("by", "artist1"), ("inAlbum", "album1"), ("inGenre", "genre1")], "Song")

generator.load_dataset("data/yandex.csv", "song", ["by", "inAlbum", "inGenre", "inPlaylist"])
generator.load_dataset("data/artist.csv", "artist", ["playsGenre"])
generator.serialize("music2.owl", format="xml")
generator.save_triplets("triplets2.csv")
