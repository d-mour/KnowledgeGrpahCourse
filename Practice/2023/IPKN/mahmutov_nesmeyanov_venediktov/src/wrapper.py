from SPARQLWrapper import JSON, SPARQLWrapper


class Wrapper:
    def __init__(self):
        self.dbpedia = SPARQLWrapper("http://dbpedia.org/sparql")
        self.dbpedia.addDefaultGraph("http://dbpedia.org")
        self.wikidata = SPARQLWrapper("https://query.wikidata.org/sparql")

    def set_query(self, engine: str, query: str):
        """
        engine in ['wikidata', 'dbpedia']
        """

        assert engine in [
            "wikidata",
            "dbpedia",
        ], "engine could be 'wikidata', 'dbpedia'"

        if engine == "dbpedia":
            engine = self.dbpedia
        elif engine == "wikidata":
            engine = self.wikidata

        engine.setQuery(query)

        def wrapper_generator(results):
            vars_ = results["head"]["vars"]
            for val in results["results"]["bindings"]:
                wrapper_dict = {}
                for var in vars_:
                    wrapper_dict[var] = (
                        val[var]["value"].replace(" ", "_").replace('"', "")
                    )
                yield wrapper_dict

        try:
            engine.setReturnFormat(JSON)
            results = engine.query().convert()
        except Exception as e:
            print(e)

        return wrapper_generator(results)
