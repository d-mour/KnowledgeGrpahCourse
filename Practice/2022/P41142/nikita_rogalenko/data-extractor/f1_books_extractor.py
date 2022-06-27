import urllib.request as urllib_request
import bs4 as bs
from datetime import datetime
import dateutil.parser as dparser
import json
from sense_extractor import get_what_creation_is_about


BASE_URL = "https://www.goodreads.com/"


def get_date_from_string(text):
    try:
        text = text.splitlines()[2].strip()
        publication_date = dparser.parse(text, fuzzy=True)
        return publication_date.strftime("%d.%m.%Y")
    except dparser.ParserError:
        return None


def save_json_to_file(json_data, file_path):
    data_to_write = json.dumps(json_data, indent=4)
    file = open(file_path, 'w+')
    file.write(data_to_write)
    file.close()


def get_page_html(url):
    req = urllib_request.Request(url)
    page = urllib_request.urlopen(req)
    html_bytes = page.read()
    html = html_bytes.decode("utf-8")
    return html


def get_book_pages_links():
    book_pages_links = []
    books_list_url = 'https://www.goodreads.com/list/show/111690.Best_Formula_1_Racing_Books_?page='
    for i in range(1, 3):
        books_list_page_html = get_page_html(books_list_url + str(i))
        soup = bs.BeautifulSoup(books_list_page_html, features="html.parser")
        book_pages_links.extend(
            [link.get("href") for link in soup.findAll("a", class_="bookTitle")]
        )
    return book_pages_links


def get_book_data(book_pages_list):
    books_list = []
    for book_page_url in book_pages_list:
        print(book_page_url)
        book_page_html = get_page_html(BASE_URL + book_page_url)
        soup = bs.BeautifulSoup(book_page_html, features="html.parser")
        try:
            genres_list = [genre.text for genre in soup.findAll("a", class_="bookPageGenreLink")]
        except AttributeError:
            genres_list = None
        try:
            description = soup.find("div", id="description").findAll("span")[1].text
        except IndexError:
            description = soup.find("div", id="description").find("span").text
        except AttributeError:
            print(f"Not enough data about the book with url {BASE_URL + book_page_url}")
            description = None
        try:
            date = get_date_from_string(soup.find("div", id="details").findAll("div", class_="row")[1].text)
        except IndexError:
            date = None
        try:
            pages_num = soup.find("span", itemprop="numberOfPages").text.split(" ")[0].strip()
        except AttributeError:
            pages_num = None
        books_list.append(
            {
                "title": soup.find("h1", id="bookTitle").text.replace("\n", "").strip(),
                "date": date,
                "genres": list(set(genres_list)),
                "description": description,
                "rating": soup.find("span", itemprop="ratingValue").text.replace("\n", "").strip(),
                "ratings_num": [int(s) for s in soup.find("meta", itemprop="ratingCount").parent.getText()
                    .replace(",", "").split() if s.isdigit()][0],
                "reviews_num":  [int(s) for s in soup.find("meta", itemprop="reviewCount").parent.getText().split()
                                 if s.isdigit()][0],
                "author": soup.find("div", class_="bookAuthorProfile__name").find("a").text.replace("\n", "").strip(),
                "number_of_pages": pages_num,
                'isAbout': get_what_creation_is_about(soup.find("h1", id="bookTitle").text.replace("\n", "").strip(),
                                                      description, None)
            }
        )

    print(books_list)
    return books_list


def get_f1_books_data(results_dir_path):
    books_pages_list = get_book_pages_links()
    print(books_pages_list)
    save_json_to_file(get_book_data(books_pages_list), results_dir_path + 'f1-books.json')
