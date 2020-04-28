from nltk.stem import PorterStemmer
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import RegexpTokenizer
from rdflib import Graph, BNode, URIRef, Literal

# common
from utils.datetime import parse_time
from utils.files import read, read_binary, write

#
# Nodes
#

READABLE = URIRef("http://zeio.nara/recommender/Readable")
AUDIO = URIRef("http://zeio.nara/recommender/Audio")
VIDEO = URIRef("http://zeio.nara/recommender/Video")
TEXT = URIRef("http://zeio.nara/recommender/Text")

# review
REVIEW = URIRef("http://zeio.nara/recommender/Review")
ARTICLE = URIRef("http://zeio.nara/recommender/Article")
CLIP = URIRef("http://zeio.nara/recommender/Clip")
PODCAST = URIRef("http://zeio.nara/recommender/Podcast")

# aspect
ASPECT = URIRef("http://zeio.nara/recommender/Aspect")

# mood
MOOD = URIRef("http://zeio.nara/recommender/Mood")

# segment
AUDIO_SEGMENT = URIRef("http://zeio.nara/recommender/AudioSegment")
READABLE_SEGMENT = URIRef("http://zeio.nara/recommender/ReadableSegment")
VIDEO_SEGMENT = URIRef("http://zeio.nara/recommender/VideoSegment")

# reviewable
ENGLISH_TITLE = "http://zeio.nara/recommender/{title}"
REVIEWABLE = URIRef("http://zeio.nara/recommender/Reviewable")
SONG = URIRef("http://zeio.nara/recommender/Song")
TRACK = URIRef("http://zeio.nara/recommender/Track")
MOVIE = URIRef("http://zeio.nara/recommender/Movie")
FILM = URIRef("http://zeio.nara/recommender/Film")
BOOK = URIRef("http://zeio.nara/recommender/Book")

# platform
PLATFORM = "http://zeio.nara/recommender/{platform}"

# person
MALE = URIRef("http://zeio.nara/recommender/Male")
FEMALE = URIRef("http://zeio.nara/recommender/Female")
PERSON = URIRef("http://zeio.nara/recommender/person/Person")
LOGIN = "http://zeio.nara/recommender/person/{login}"
PERSON_NAME = URIRef("http://zeio.nara/recommender/person/Name")

#
# Properties
#

# common
RDF_TYPE_ = URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type")

# platform
PLATFORM_ITEM_ = URIRef("http://zeio.nara/recommender/platform-item")

# item
PLATFORM_ = URIRef("http://zeio.nara/recommender/platform")
RAW_ = URIRef("http://zeio.nara/recommender/raw")
YEAR_OF_PRODUCTION_ = URIRef("http://zeio.nara/recommender/year-of-production")
READABLE_CONTENT_ = URIRef("http://zeio.nara/recommender/readable-content")
AUDIO_DATA_ = URIRef("http://zeio.nara/recommender/audio-data")
VIDEO_DATA_ = URIRef("http://zeio.nara/recommender/video-data")
CREATOR_ = URIRef("http://zeio.nara/recommender/creator")

# review
REVIEW_TARGET_ = URIRef("http://zeio.nara/recommender/target")
OPINIONS_ = URIRef("http://zeio.nara/recommender/opinions")
SOURCE_SEGMENT_ = URIRef("http://zeio.nara/recommender/source-segment")
TARGET_SEGMENT_ = URIRef("http://zeio.nara/recommender/target-segment")

# opinion
ASPECT_ = URIRef("http://zeio.nara/recommender/aspect")
MOOD_ = URIRef("http://zeio.nara/recommender/mood")
ASPECT_NAME_ = URIRef("http://zeio.nara/recommender/aspect-name")
ASPECT_DESCRIPTION_ = URIRef("http://zeio.nara/recommender/aspect-description")

# mood
EXTRINSIC_MARK_ = URIRef("http://zeio.nara/recommender/extrinsic-mark")
MOOD_POSITIVENESS_ = URIRef("http://zeio.nara/recommender/mood-positiveness")
MOOD_INTENSITY_ = URIRef("http://zeio.nara/recommender/mood-intensity")

# aspect
ASPECT_HOLDER_ = URIRef("http://zeio.nara/recommender/aspect-holder")

# segment
START_INDEX_ = URIRef("http://zeio.nara/recommender/start-index")
END_INDEX_ = URIRef("http://zeio.nara/recommender/end-index")
START_TIME_ = URIRef("http://zeio.nara/recommender/start-time")
END_TIME_ = URIRef("http://zeio.nara/recommender/end-time")

# reviewable
ORIGINAL_TITLE_ = URIRef("http://zeio.nara/recommender/original-title")
ENGLISH_TITLE_ = URIRef("http://zeio.nara/recommender/english-title")

# text
LEMMAS_ = URIRef("http://zeio.nara/recommender/lemmas")
STEMS_ = URIRef("http://zeio.nara/recommender/stems")
TOKENS_ = URIRef("http://zeio.nara/recommender/tokens")

# list
CONTENT_ = URIRef("http://zeio.nara/recommender/content")
NEXT_ = URIRef("http://zeio.nara/recommender/next")

# person
NAME_ = URIRef("http://zeio.nara/recommender/person/name")
FIRST_ = URIRef("http://zeio.nara/recommender/person/name/first")
LAST_ = URIRef("http://zeio.nara/recommender/person/name/last")
LOGIN_ = URIRef("http://zeio.nara/recommender/person/login")
AGE_ = URIRef("http://zeio.nara/recommender/age")
GENDER_ = URIRef("http://zeio.nara/recommender/gender")


class GraphWrapper:
    def __init__(self, initial_ontology_path: str = None):
        self.graph = Graph()
        if initial_ontology_path:
            self.graph.parse(initial_ontology_path, format='ttl')
        self.tokenizer = RegexpTokenizer('\w+|\$[\d\.]+|\S+')
        self.stemmer = PorterStemmer()
        self.lemmatizer = WordNetLemmatizer()

    def _add_mirror_properties(self, forward_property: URIRef, backward_property: URIRef, subject: URIRef, object_: URIRef):
        self.graph.add((subject, forward_property, object_))
        self.graph.add((object_, backward_property, subject))

    def _try_insert_year_of_production(self, node: URIRef, data: dict, second_key: str):
        if 'year-of-production' in data and second_key in data['year-of-production']:
            self.graph.add((node, YEAR_OF_PRODUCTION_, Literal(data['year-of-production'][second_key])))

    def _try_insert_platform(self, node: URIRef, data: dict, second_key: str):
        if 'platform' in data and second_key in data['platform']:
            self._add_mirror_properties(
                PLATFORM_,
                PLATFORM_ITEM_,
                node,
                URIRef(PLATFORM.format(platform=data['platform'][second_key]))
            )

    def _insert_list_item(self, content):
        node = BNode()
        self.graph.add((node, CONTENT_, content))
        return node

    def _insert_list(self, node: URIRef, predicate: URIRef, items: iter):
        previous_node = self._insert_list_item(next(items))

        self.graph.add((node, predicate, previous_node))

        for item in items:
            next_node = self._insert_list_item(item)
            self.graph.add((previous_node, NEXT_, next_node))
            previous_node = next_node

    def _insert_text(self, node: URIRef, predicate: URIRef, text: str):
        text_node = BNode()

        # Add node type
        self.graph.add((text_node, RDF_TYPE_, TEXT))

        # Add raw content
        self.graph.add((text_node, RAW_, Literal(text)))

        tokens = self.tokenizer.tokenize(text)

        # Add tokens
        self._insert_list(text_node, TOKENS_, map(Literal, tokens))

        # Add lemmas
        self._insert_list(text_node, LEMMAS_, map(lambda token: Literal(self.lemmatizer.lemmatize(token)), tokens))

        # Add stems
        self._insert_list(text_node, STEMS_, map(lambda token: Literal(self.stemmer.stem(token)), tokens))

        # Connect to the given node via provided predicate
        self.graph.add((node, predicate, text_node))

    def _add_segment(self, segment: dict, kind: str):
        segment_node = BNode()

        if kind in {'song', 'podcast', 'film', 'movie', 'clip'}:
            self.graph.add((segment_node, START_TIME_, Literal(parse_time(segment['start-time']))))
            self.graph.add((segment_node, END_TIME_, Literal(parse_time(segment['end-time']))))
        elif kind in {'book', 'text', 'article'}:
            self.graph.add((segment_node, START_INDEX_, Literal(segment['start-index'])))
            self.graph.add((segment_node, END_TIME_, Literal(segment['end-index'])))
        else:
            raise ValueError(f'Incorrect kind of item: "{kind}"')

        if kind in {'song', 'podcast'}:
            self.graph.add((segment_node, RDF_TYPE_, AUDIO_SEGMENT))
        elif kind in {'film', 'movie', 'clip'}:
            self.graph.add((segment_node, RDF_TYPE_, VIDEO_SEGMENT))
        elif kind in {'book', 'text', 'article'}:
            self.graph.add((segment_node, RDF_TYPE_, READABLE_SEGMENT))
        else:
            raise ValueError(f'Incorrect kind of item: "{kind}"')

        return segment_node

    def _add_aspect(self, opinion_node: URIRef, aspect: dict):
        aspect_node = BNode()

        suitable_aspects = [
            aspect_
            for aspect_ in self.graph.subjects(RDF_TYPE_, ASPECT)
            for aspect_name in self.graph.objects(aspect_, ASPECT_NAME_)
            if aspect_name == aspect['name']
        ]

        if len(suitable_aspects) > 0:
            aspect_node = suitable_aspects[0]
        else:
            # Add node type
            self.graph.add((aspect_node, RDF_TYPE_, ASPECT))

            # Connect aspect to opinion and vice versa
            self._add_mirror_properties(
                ASPECT_,
                ASPECT_HOLDER_,
                opinion_node,
                aspect_node
            )

            # Add aspect name
            self.graph.add((aspect_node, ASPECT_NAME_, Literal(aspect['name'])))

            # Add aspect description
            self.graph.add((aspect_node, ASPECT_DESCRIPTION_, Literal(aspect['description'])))

    def _add_mood(self, mood: dict):
        mood_node = BNode()

        # Add node type
        self.graph.add((mood_node, RDF_TYPE_, MOOD))

        if 'intensity' in mood:
            # Add mood intensity
            self.graph.add((mood_node, MOOD_INTENSITY_, Literal(mood['intensity'])))

        if 'positiveness' in mood:
            # Add mood positiveness
            self.graph.add((mood_node, MOOD_INTENSITY_, Literal(mood['positiveness'])))

        if 'extrinsic-mark' in mood:
            # Add extrinsic mark
            self.graph.add((mood_node, EXTRINSIC_MARK_, Literal(mood['extrinsic-mark'])))

        return mood_node

    def _add_opinion(self, opinion: dict, target_kind: str, source_kind: str):
        opinion_node = BNode()

        # Add source segment
        self.graph.add((opinion_node, SOURCE_SEGMENT_, self._add_segment(opinion['source-segment'], source_kind)))

        # Add target segment
        self.graph.add((opinion_node, TARGET_SEGMENT_, self._add_segment(opinion['target-segment'], target_kind)))

        # Add aspect
        self._add_aspect(opinion_node, opinion['aspect'])

        # Add mood
        self.graph.add((opinion_node, MOOD_, self._add_mood(opinion['mood'])))

        return opinion_node

    def _add_review(self, review: dict, reviewer: URIRef, reviewable: URIRef, second_key: str = 'source', alternative_second_key: str = 'target'):
        node = BNode()

        self.graph.add((node, RDF_TYPE_, REVIEW))
        self.graph.add((node, RDF_TYPE_, REVIEWABLE))

        if review['kind'][second_key] == 'text':
            self.graph.add((node, RDF_TYPE_, ARTICLE))
            self.graph.add((node, RDF_TYPE_, READABLE))
            self._insert_text(node, READABLE_CONTENT_, read(review['path'][second_key]))
        elif review['kind'][second_key] == 'clip':
            self.graph.add((node, RDF_TYPE_, CLIP))
            self.graph.add((node, RDF_TYPE_, VIDEO))
            self.graph.add((node, VIDEO_DATA_, Literal(read_binary(review['path'][second_key]))))
        elif review['kind'][second_key] == 'podcast':
            self.graph.add((node, RDF_TYPE_, PODCAST))
            self.graph.add((node, RDF_TYPE_, AUDIO))
            self.graph.add((node, AUDIO_DATA_, Literal(read_binary(review['path'][second_key]))))

        # Add a year of production
        self._try_insert_year_of_production(node, review, second_key)

        # Add platform
        self._try_insert_platform(node, review, second_key)

        # Connect reviewable to the review
        self.graph.add((node, REVIEW_TARGET_, reviewable))

        # Add opinions
        self._insert_list(
            node, OPINIONS_, map(
                lambda opinion: self._add_opinion(
                    opinion,
                    source_kind=review['kind'][second_key],
                    target_kind=review['kind'][alternative_second_key]
                ), review['opinions']
            )
        )

        # Connect reviewer to the review
        self.graph.add((node, CREATOR_, reviewer))

    def _add_reviewable(self, review: dict, second_key: str = 'target'):
        node = URIRef(ENGLISH_TITLE.format(title=review['english-title'].lower().replace(' ', '-')))

        if len(tuple(self.graph[node])) == 0:
            self.graph.add((node, RDF_TYPE_, REVIEWABLE))

            if review['kind'][second_key] == 'song':
                self.graph.add((node, RDF_TYPE_, SONG))
                self.graph.add((node, RDF_TYPE_, TRACK))
                self.graph.add((node, RDF_TYPE_, AUDIO))
                self.graph.add((node, AUDIO_DATA_, Literal(read_binary(review['path'][second_key]))))
            elif review['kind'][second_key] == 'book':
                self.graph.add((node, RDF_TYPE_, BOOK))
                self.graph.add((node, RDF_TYPE_, READABLE))
                self._insert_text(node, READABLE_CONTENT_, read(review['path'][second_key]))
            elif review['kind'][second_key] == 'film':
                self.graph.add((node, RDF_TYPE_, MOVIE))
                self.graph.add((node, RDF_TYPE_, FILM))
                self.graph.add((node, RDF_TYPE_, VIDEO))
                self.graph.add((node, VIDEO_DATA_, Literal(read_binary(review['path'][second_key]))))

            # Add a year of production
            self._try_insert_year_of_production(node, review, second_key)

            # Add a platform
            self._try_insert_platform(node, review, second_key)

            # Add english title
            self._insert_text(node, ENGLISH_TITLE_, review['english-title'])

            # Add original title
            self.graph.add((node, ORIGINAL_TITLE_, Literal(review['original-title'])))

        return node

    def _add_name(self, person_node: URIRef, review: dict):
        # Make name node
        name_node = BNode()

        # Add node type
        self.graph.add((person_node, RDF_TYPE_, PERSON_NAME))

        # Add first name
        self.graph.add((name_node, FIRST_, Literal(review['reviewer']['name']['first'])))

        # Add last name
        self.graph.add((name_node, LAST_, Literal(review['reviewer']['name']['last'])))

        # Connect name node to the person node
        self.graph.add((person_node, NAME_, name_node))

    def _add_gender(self, person_node: URIRef, review: dict):
        if review['reviewer']['gender'] == 'male':
            self.graph.add((person_node, GENDER_, MALE))
        elif review['reviewer']['gender'] == 'female':
            self.graph.add((person_node, GENDER_, FEMALE))
        else:
            raise ValueError(f"Don't know such gender: {review['reviewer']['gender']}")

    def _add_reviewer(self, review: dict):
        person_node = URIRef(LOGIN.format(login=review['reviewer']['login']))

        if len(tuple(self.graph[person_node])) == 0:
            # Add node type
            self.graph.add((person_node, RDF_TYPE_, PERSON))

            # Add name
            self._add_name(person_node, review)

            # Add login
            self.graph.add((person_node, LOGIN_, Literal(review['reviewer']['login'])))

            # Add age
            self.graph.add((person_node, AGE_, Literal(review['reviewer']['age'])))

            # Add gender
            self._add_gender(person_node, review)

        return person_node

    def export(self, filename):
        write(filename, self.graph.serialize(format='ttl').decode('utf-8'))

    def append_review(self, review: dict):
        self._add_review(
            review,
            reviewer=self._add_reviewer(review),
            reviewable=self._add_reviewable(review)
        )
