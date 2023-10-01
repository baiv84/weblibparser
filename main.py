import os
import re
import time
import logging
import argparse
import requests
from environs import Env
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from urllib.parse import urljoin, urlparse, unquote
from parser_exceptions import RedirectException
from parser_exceptions import BookTextDownloadException
from parser_exceptions import StartIdStopIdException


def download_txt(url, filename, folder='books/'):
    '''Download book file as a text'''
    main_page_url = 'https://tululu.org/'
    folder = sanitize_filename(folder)
    filename = sanitize_filename(filename)
    book_fullpath = os.path.join(folder, filename)
    os.makedirs(folder, exist_ok=True)

    response = requests.get(url)
    response.raise_for_status()

    if response.url == main_page_url:
        raise BookTextDownloadException

    with open(book_fullpath, 'wb') as file:
        file.write(response.content)

    return book_fullpath


def download_image(url, filename, folder='images/'):
    '''Download book image to the folder'''
    folder = sanitize_filename(folder)
    filename = sanitize_filename(filename)
    image_fullpath = os.path.join(folder, filename)
    os.makedirs(folder, exist_ok=True)

    response = requests.get(url)
    response.raise_for_status()

    with open(image_fullpath, 'wb') as file:
        file.write(response.content)

    return image_fullpath


def parse_book_page(url,
                    txt_folder='books',
                    img_folder='images'
                    ):
    '''Parse book page for fields'''
    main_page_url = 'https://tululu.org/'
    book_txt_link = 'https://tululu.org/txt.php'
    response = requests.get(url)
    response.raise_for_status()

    if response.url == main_page_url:
        raise RedirectException

    html = response.text
    soup = BeautifulSoup(html, 'lxml')
    book = soup.select_one('div[id=content] h1').text
    book_title, book_author = book.split('::')

    book_title = book_title.lstrip().rstrip()
    book_author = book_author.lstrip().rstrip()

    result = re.search(r'b(\d+)/$', url)
    book_id = result.group(1)

    book_img_relative_url = soup.select_one('div.bookimage a img')['src']
    img_fname = unquote(urlparse(book_img_relative_url).path.split("/")[-1])

    comments = soup.select('div.texts span.black')
    comments = list(map(lambda comment: comment.text, comments))

    book_genres = soup.select('span.d_book a')
    book_genres = list(map(lambda genre: genre.text, book_genres))

    return {
        'title': book_title,
        'author': book_author,
        'img_src': os.path.join(img_folder, img_fname),
        'book_path': os.path.join(txt_folder, f'{book_title}.txt'),
        'comments': comments,
        'genres': book_genres,
        'image_filename': img_fname,
        'txt_filename': f'{book_title}.txt',
        'book_txt_link': urljoin(book_txt_link, f'?id={book_id}'),
        'book_img_link': urljoin(url, book_img_relative_url),
    }


def main():
    '''Program entry point'''
    env = Env()
    env.read_env()
    book_txt_folder = env('BOOK_TXT_FOLDER', 'books/')
    book_image_folder = env('BOOK_IMAGE_FOLDER', 'images/')
    delay_interval = env.int('DELAY_INTERVAL', 5)
    main_page_url = 'https://tululu.org/'

    parser = argparse.ArgumentParser(prog='python3 main.py',
                                     description=f'Parse books and images '
                                                 f'from on-line library: '
                                                 f'{main_page_url}')
    parser.add_argument('--start_id',
                        default=1,
                        type=int,
                        help='Determine the first book index to parse. '
                             'Default index value: %(default)s')
    parser.add_argument('--stop_id',
                        default=10,
                        type=int,
                        help='Determine the last book index to parse. '
                             'Default index value: %(default)s')
    args = parser.parse_args()
    start_id = args.start_id
    stop_id = args.stop_id

    if stop_id < start_id:
        raise StartIdStopIdException

    for book_id in range(start_id, stop_id+1):
        try:
            book_page_url = urljoin(main_page_url, f'b{book_id}/')
            print(book_page_url)

            book = parse_book_page(book_page_url)
            txt_url = book['book_txt_link']
            img_url = book['book_img_link']
            txt_filename = book['txt_filename']
            img_filename = book['image_filename']

            saved_txt_filepath = download_txt(txt_url,
                                              txt_filename,
                                              )
            saved_img_filepath = download_image(img_url,
                                                img_filename,
                                                )
        except RedirectException as err:
            logging.info(f'Redirect exception - there is no book with URL: '
                         f'{book_page_url}')
        except requests.exceptions.ConnectionError as err:
            print(f'Network connection error, you should just pray. '
                  f'Sleep for {delay_interval} seconds...')
            logging.info(f'Network connection error, you should just pray. '
                         f'Sleep for {delay_interval} seconds...')
            time.sleep(delay_interval)
        except requests.exceptions.Timeout as err:
            print(f'Connection timeout, you should just pray. '
                  f'Sleep for {delay_interval} seconds...')
            logging.info(f'Connection timeout, you should just pray. '
                         f'Sleep for {delay_interval} seconds...')
            time.sleep(delay_interval)
        except requests.exceptions.HTTPError as err:
            logging.info(f'HTTP protocol error '
                         f'{book_page_url} is unavailable')


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO,
                        filename='parser.log',
                        filemode='w',
                        format="%(asctime)s %(levelname)s %(message)s")
    try:
        main()
    except StartIdStopIdException:
        print('Parameters exception: stop_id lower then start_id!')
        logging.info('Parameters exception: stop_id lower then start_id!')
