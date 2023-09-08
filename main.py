import os
import time
import logging
import argparse
import requests
from environs import Env
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from urllib.parse import urljoin, urlparse, unquote
from parser_exceptions import RedirectException
from parser_exceptions import StartIdStopIdException


def check_for_tululu_redirect(response):
    '''Check for redirection to the tululu.org main page'''
    main_page_url = 'https://tululu.org/'
    if response.url == main_page_url:
        raise RedirectException


def download_txt(book_id, filename, folder='books/'):
    '''Download book file as a text'''
    folder = sanitize_filename(folder)
    filename = sanitize_filename(filename)
    book_fullpath = os.path.join(folder, filename)
    os.makedirs(folder, exist_ok=True)

    payload = {'id': book_id}
    response = requests.get('http://tululu.org/txt.php', params=payload)
    response.raise_for_status()
    check_for_tululu_redirect(response)

    with open(book_fullpath, 'wb') as file:
        file.write(response.content)

    return book_fullpath


def download_image(url, filename, folder='images/'):
    '''Download book image to the folder'''
    if filename == 'nopic.gif':
        return None

    folder = sanitize_filename(folder)
    filename = sanitize_filename(filename)
    image_fullpath = os.path.join(folder, filename)
    os.makedirs(folder, exist_ok=True)

    response = requests.get(url)
    response.raise_for_status()
    check_for_tululu_redirect(response)

    with open(image_fullpath, 'wb') as file:
        file.write(response.content)

    return image_fullpath


def parse_book_page(html):
    '''Parse book page for fields'''
    soup = BeautifulSoup(html, 'lxml')
    book = soup.find('div', id='content').find('h1').text
    book_name, book_author = book.split('::')

    book_name = book_name.lstrip().rstrip()
    book_author = book_author.lstrip().rstrip()

    book_image_relative_url = soup.find('div', class_="bookimage") \
                                  .find('a').find('img')['src']

    comments = soup.find_all('div', class_='texts')
    comments_txt = [comment.find('span').text for comment in comments]

    book_genres = soup.find('span', class_='d_book').find_all('a')
    book_genres = [genre.text for genre in book_genres]

    return {
        'book_name': book_name,
        'book_author': book_author,
        'book_comments': '\n'.join(comments_txt),
        'book_genres': book_genres,
        'book_filename': f'{book_name}.txt',
        'book_image_relative_url': book_image_relative_url,
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
            book_page_url = urljoin(main_page_url, f'b{book_id}')
            response = requests.get(book_page_url)
            response.raise_for_status()
            check_for_tululu_redirect(response)

            book_html = response.text
            book = parse_book_page(book_html)

            book_image_relative_url = book['book_image_relative_url']
            book_image_url = urljoin(book_page_url, book_image_relative_url)

            book_name = book['book_name']
            book_author = book['book_author']
            book_filename = f"{book_id}. {book['book_filename']}"

            image_fname = unquote(urlparse(book_image_url).path.split("/")[-1])
            saved_image_filepath = download_image(book_image_url,
                                                  image_fname,
                                                  folder=book_image_folder)
            if not saved_image_filepath:
                logging.info(f"Book '{book_name}' has no avatar picture. "
                             f"Book URL - {book_page_url}")

            saved_txt_filepath = download_txt(book_id,
                                              book_filename,
                                              folder=book_txt_folder)

            print(f'\nНазвание: {book_name}')
            print(f'Автор: {book_author}')
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
