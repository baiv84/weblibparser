import os
import requests
from environs import Env
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from urllib.parse import urljoin, urlparse, unquote


def check_for_redirect(response):
    '''Check for redirect URL'''
    if response.url == 'https://tululu.org/':
        raise requests.HTTPError


def serialize_book(book_id):
    '''Serialize book with particular book_id'''
    base_url = 'https://tululu.org'
    book_url = urljoin(base_url, f'b{book_id}')

    response = requests.get(book_url)
    response.raise_for_status()
    check_for_redirect(response)

    soup = BeautifulSoup(response.text, 'lxml')
    book = soup.find('div', id='content').find('h1').text
    book_name, book_author = book.split('::')

    book_name = book_name.lstrip().rstrip()
    book_author = book_author.lstrip().rstrip()

    image_url = soup.find('div', class_="bookimage") \
                    .find('a').find('img')['src']
    image_url = urljoin(base_url, image_url)

    return {
        'id': book_id,
        'url': f'http://tululu.org/txt.php?id={book_id}',
        'image_url': image_url,
        'name': f'{book_name}.txt',
        'author': book_author,
    }


def download_txt(url, filename, folder='books/'):
    '''Download file as a text'''
    folder = sanitize_filename(folder)
    filename = sanitize_filename(filename)
    book_fullpath = os.path.join(folder, filename)

    if not os.path.exists(folder):
        os.makedirs(folder)

    response = requests.get(url)
    response.raise_for_status()
    check_for_redirect(response)

    with open(book_fullpath, 'wb') as file:
        file.write(response.content)

    return book_fullpath


def download_image(url, filename, folder='images/'):
    '''Download image to the folder'''
    folder = sanitize_filename(folder)
    filename = sanitize_filename(filename)
    image_fullpath = os.path.join(folder, filename)

    if not os.path.exists(folder):
        os.makedirs(folder)

    response = requests.get(url)
    response.raise_for_status()
    check_for_redirect(response)

    with open(image_fullpath, 'wb') as file:
        file.write(response.content)

    return image_fullpath


def main():
    '''Program entry point'''
    env = Env()
    env.read_env()
    book_folder = env('BOOK_FOLDER')
    image_folder = env('IMAGE_FOLDER')

    for book_id in range(100):
        try:
            book = serialize_book(book_id)
            book_url = book['url']
            image_url = book['image_url']
            book_name = f"{book['id']}. {book['name']}"
            image_name = unquote(urlparse(image_url).path.split("/")[-1])

            image_filepath = download_image(image_url, image_name,
                                            folder=image_folder)
            book_filepath = download_txt(book_url, book_name,
                                         folder=book_folder)

            print(image_filepath)
            print(book_filepath)
        except requests.exceptions.HTTPError as err:
            pass


if __name__ == '__main__':
    main()
