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
    book_folder = env('BOOK_FOLDER')
    image_folder = env('IMAGE_FOLDER')
    base_url = env('BASE_URL')

    start_id = 1
    end_id = 50

    for book_id in range(start_id, end_id+1):
        try:
            book_url = urljoin(base_url, f'b{book_id}')
            response = requests.get(book_url)
            response.raise_for_status()
            check_for_redirect(response)

            book = parse_book_page(response.text)
            book_txt_url = f'http://tululu.org/txt.php?id={book_id}'

            book_image_url = book['book_image_url']
            book_image_url = urljoin(base_url, book_image_url)

            book_comments = book['book_comments']
            book_genres = book['book_genres']
            book_name = f"{book_id}. {book['book_filename']}"

            image_filename = unquote(urlparse(book_image_url).path.split("/")[-1])
            image_filepath = download_image(book_image_url, image_filename,
                                            folder=image_folder)
            book_filepath = download_txt(book_txt_url, book_name,
                                         folder=book_folder)

            print('\n****************')
            print(book_filepath)
            print(book_genres)
        except requests.exceptions.HTTPError as err:
            pass


if __name__ == '__main__':
    main()
