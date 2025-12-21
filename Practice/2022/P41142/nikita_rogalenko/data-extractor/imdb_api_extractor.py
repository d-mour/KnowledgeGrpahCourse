import urllib.request as urllib_request
import re
import json
from sense_extractor import get_what_creation_is_about


API_KEY = ""
KEYWORD = "formula-1"
COUNT = 250
URL = f'https://imdb-api.com/API/AdvancedSearch/{API_KEY}?keywords={KEYWORD}&count={COUNT}'


def get_json_data_by_request(data_url):
    req = urllib_request.Request(data_url)
    req.add_header('User-Agent',
                   'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11')
    req.add_header('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8')
    req.add_header('Accept-Charset', 'ISO-8859-1,utf-8;q=0.7,*;q=0.3')
    req.add_header('Accept-Encoding', 'none')
    req.add_header('Accept-Language', 'en-US,en;q=0.8')
    req.add_header('Connection', 'keep-alive')
    data_response = urllib_request.urlopen(req)
    data = json.load(data_response)
    return data


def save_json_to_file(json_data, file_path):
    data_to_write = json.dumps(json_data, indent=4)
    file = open(file_path, 'w+')
    file.write(data_to_write)
    file.close()


def parse_f1_movies(json_data):
    movies_array = []
    imdb_movies_array = json_data['results']
    for imdb_movie in imdb_movies_array:
        movie = {
            'title': imdb_movie['title'],
            'date': re.sub("[^\d-]", "", imdb_movie['description']),
            'genres': imdb_movie['genres'],
            'description': imdb_movie['plot'],
            'runtime': imdb_movie['runtimeStr'],
            'stars': imdb_movie['stars'],
            'contentRating': imdb_movie['contentRating'],
            'imDbRating': imdb_movie['imDbRating'],
            'imDbRatingVotes': imdb_movie['imDbRatingVotes'],
            'metacriticRating': imdb_movie['metacriticRating'],
            'isAbout': get_what_creation_is_about(imdb_movie['title'], imdb_movie['plot'], imdb_movie['stars'])
        }
        movies_array.append(movie)
    return movies_array


# process f1 data from ergast api
# arg - dir with output files
def process_f1_imdb_movies(results_dir_path):
    f1_movies_data_json = get_json_data_by_request(URL)
    f1_movies_data = parse_f1_movies(f1_movies_data_json)
    save_json_to_file(f1_movies_data, results_dir_path + 'f1-movies.json')
