from time import time

import click
from rdflib import Graph, URIRef, RDF
from rdflib.plugins.sparql import prepareQuery

from GraphWrapper import GraphWrapper
from utils.etc import print_elapsed_time, stringify_marked_reviewable
from utils.files import get_yaml_files, read_yaml


@click.group()
def main():
    pass


@click.command()
@click.option('--input-dir', default='ontologies/resources/documents/annotations', type=str)
@click.option('--input-file', default='ontologies/resources/recommender.ttl', type=str)
@click.option('--output-file', default='ontologies/resources/augmented-recommender.ttl', type=str)
def parse(input_dir, input_file, output_file):
    graph = GraphWrapper(initial_ontology_path=input_file)
    for file in get_yaml_files(input_dir):
        graph.append_review(read_yaml(file))

    required_year = 2020
    print(f'Reviewables with reviews written at least in {required_year}:')
    print(f'{"Title":30s}{"User":20s}')
    for row in graph.graph.query(
            prepareQuery(
                f"""
                select ?title ?login where {{
                    ?review a :Review;
                        :year-of-production ?year;
                        :creator/person:login ?login;
                        :target/:english-title/:raw ?title.
                    filter (?year >= {required_year})
                }}
                """,
                initNs={
                    '': URIRef('http://zeio.nara/recommender/'),
                    'person':  URIRef('http://zeio.nara/recommender/person/')
                }
            )
    ):
        print(f'{row[0]:30s}{row[1]:30s}')

    graph.export(output_file)


@click.command()
@click.option('--path', default='ontologies/resources/recommender.ttl', type=str)
def trace(path):
    g.parse(path, format='ttl')

    print('Extrinsic marks for films extracted with help of rdflib API: ')

    start_time = time()
    for review_target, year_of_production, extrinsic_mark in [
        (review_target, year_of_production, extrinsic_mark)
        for review in g.subjects(RDF.type, article_type)
        for opinions in g.objects(review, opinions_property)
        for opinion in g.objects(opinions, content_property)
        for mood in g.objects(opinion, mood_property)
        for extrinsic_mark in g.objects(mood, extrinsic_mark_property)
        for review_target in g.objects(review, target_property)
        for year_of_production in g.objects(review_target, year_of_production_property)
    ]:
        print(stringify_marked_reviewable(review_target, year_of_production, extrinsic_mark))
    print_elapsed_time(start_time)

    print('Extrinsic marks for films extracted via SPARQL query: ')
    start_time = time()
    for row in g.query(
            prepareQuery(
                """
                select ?target ?year_of_production ?extrinsic_mark where {
                    ?review a :Article;
                        :opinions/:content/:mood/:extrinsic-mark ?extrinsic_mark;
                        :target ?target.
                    ?target :year-of-production ?year_of_production.
                }
                """,
                initNs={
                    '': URIRef('http://zeio.nara/recommender/')
                }
            )
    ):
        print(stringify_marked_reviewable(*row))
    print_elapsed_time(start_time)


if __name__ == "__main__":
    film_type = URIRef('http://zeio.nara/recommender/Film')
    review_type = URIRef('http://zeio.nara/recommender/Review')
    article_type = URIRef('http://zeio.nara/recommender/Article')

    opinions_property = URIRef('http://zeio.nara/recommender/opinions')
    content_property = URIRef('http://zeio.nara/recommender/content')
    mood_property = URIRef('http://zeio.nara/recommender/mood')
    target_property = URIRef('http://zeio.nara/recommender/target')
    original_title_property = URIRef('http://zeio.nara/recommender/original-title')
    year_of_production_property = URIRef('http://zeio.nara/recommender/year-of-production')
    extrinsic_mark_property = URIRef('http://zeio.nara/recommender/extrinsic-mark')

    g = Graph()
    main.add_command(trace)
    main.add_command(parse)
    main()
