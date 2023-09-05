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


def check_for_redirect(response):
    '''Check for redirect URL'''
    if response.url == 'https://tululu.org/':
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
    check_for_redirect(response)

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
    check_for_redirect(response)

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

    image_url = soup.find('div', class_="bookimage") \
                    .find('a').find('img')['src']

    comments = soup.find_all('div', class_='texts')
    comments_txt = [comment.find('span').text for comment in comments]

    genres = soup.find('span', class_='d_book').find_all('a')
    genres = [genre.text for genre in genres]

    return {
        'book_name': book_name,
        'book_author': book_author,
        'book_comments': '\n'.join(comments_txt),
        'book_genres': genres,
        'book_filename': f'{book_name}.txt',
        'book_image_url': image_url,
    }


def main():
    '''Program entry point'''
    env = Env()
    env.read_env()
    book_folder = env('BOOK_FOLDER', 'books/')
    image_folder = env('IMAGE_FOLDER', 'images/')
    base_url = env('BASE_URL', 'https://tululu.org')
    delay_interval = env.int('DELAY_INTERVAL', 5)

    parser = argparse.ArgumentParser(prog='python3 main.py',
                                     description='Parse books and images '
                                                 'from on-line library: '
                                                 'https://tululu.org/')
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
            book_url = urljoin(base_url, f'b{book_id}')
            response = requests.get(book_url)
            response.raise_for_status()
            check_for_redirect(response)

            book = parse_book_page(response.text)
            book_image_url = book['book_image_url']
            book_image_url = urljoin(base_url, book_image_url)

            book_name = book['book_name']
            book_author = book['book_author']
            book_filename = f"{book_id}. {book['book_filename']}"

            book_comments = book['book_comments']
            book_genres = book['book_genres']

            image_filename = unquote(urlparse(book_image_url).path.split("/")[-1])
            image_filepath = download_image(book_image_url,
                                            image_filename,
                                            folder=image_folder)
            book_filepath = download_txt(book_id,
                                         book_filename,
                                         folder=book_folder)

            print(f'\nНазвание: {book_name}')
            print(f'Автор: {book_author}')
        except RedirectException as err:
            logging.info(f'Redirect exception - there is no book with URL: {book_url}')
        except requests.exceptions.ConnectionError as err:
            print(f'Network connection error, you should just pray. Sleep for {delay_interval} seconds...')
            logging.info(f'Network connection error, you should just pray. Sleep for {delay_interval} seconds...')
            time.sleep(delay_interval)
        except requests.exceptions.Timeout as err:
            print(f'Connection timeout, you should just pray. Sleep for {delay_interval} seconds...')
            logging.info(f'Connection timeout, you should just pray. Sleep for {delay_interval} seconds...')
            time.sleep(delay_interval)
        except requests.exceptions.HTTPError as err:
            logging.info(f'HTTP protocol error - {book_url} is unavailable')


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
