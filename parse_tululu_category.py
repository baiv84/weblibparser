import json
import logging
import requests
from environs import Env
from bs4 import BeautifulSoup
from main import download_txt
from main import download_image
from main import parse_book_page
from urllib.parse import urljoin
from parser_exceptions import BookTextDownloadException
from constants import MAIN_PAGE_URL as MAIN_PAGE_URL
from constants import SCIENCE_FICTION_GENRE_ID as SCIENCE_FICTION_GENRE_ID


def get_genre_bookpage_url(genre_id, book_page_num=1):
    '''Get genre page URL. Default genre - science fiction with id=55'''
    category_page_url = urljoin(MAIN_PAGE_URL, f'l{genre_id}/')
    return urljoin(category_page_url, f'{book_page_num}/')


def get_page_book_urls(url):
    '''Get all books URLs from the page'''
    page_books_urls = []

    response = requests.get(url)
    response.raise_for_status()
    html = response.text

    soup = BeautifulSoup(html, 'lxml')
    book_cards = soup.select('table.d_book')

    for book_card in book_cards:
        book_rows = book_card.select('tr')
        _, book_url_section, _, _, _, _ = book_rows
        book_url = book_url_section.select_one('a')['href']
        book_url = urljoin(MAIN_PAGE_URL, f'{book_url}')
        page_books_urls.append(book_url)

    return {'books_url': page_books_urls,
            'books_number': len(page_books_urls)}


def main():
    env = Env()
    env.read_env()
    genre_id = env.int('BOOKS_GENRE', SCIENCE_FICTION_GENRE_ID)
    txt_folder = env('BOOK_TXT_FOLDER', 'books')
    img_folder = env('BOOK_IMAGE_FOLDER', 'images')

    books_serialized = []
    for page_id in range(1, 5):
        genre_url_page = get_genre_bookpage_url(genre_id=genre_id,
                                                book_page_num=page_id
                                                )
        page_books = get_page_book_urls(genre_url_page)
        page_books_urls = page_books['books_url']

        for book_url in page_books_urls:
            book = parse_book_page(book_url,
                                   txt_folder=txt_folder,
                                   img_folder=img_folder)
            title = book['title']
            print(f'Get book - {title}, URL - {book_url}')

            txt_url = book['book_txt_link']
            img_url = book['book_img_link']

            txt_filename = book['txt_filename']
            img_filename = book['image_filename']

            try:
                download_txt(txt_url, txt_filename, folder=txt_folder)
            except BookTextDownloadException:
                print(f'+++++{book_url} -> Book does not contain text file...')
                logging.info(f'+++++{book_url} ->'
                             'Book does not contain text file...')
                continue

            print('--->>>continue grab IMG')
            download_image(img_url, img_filename, folder=img_folder)

            # Clean book dictionary
            for key in ('image_filename', 'txt_filename',
                        'book_txt_link', 'book_img_link',
                        ):
                book.pop(key)

            # Store book dict item
            print('*****->>>continue append JSON')
            books_serialized.append(book)

    print('Store JSON data...')
    books_in_json = json.dumps(books_serialized,
                               indent=4,
                               ensure_ascii=False
                               )
    with open('books.json', 'w') as books_json:
        books_json.write(books_in_json)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO,
                        filename='parser.log',
                        filemode='w',
                        format="%(asctime)s %(levelname)s %(message)s")
    main()
