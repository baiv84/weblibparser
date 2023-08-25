import os
import requests
from environs import Env
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename


def check_for_redirect(response):
    '''Check for redirect URL'''
    if response.url == 'https://tululu.org/':
        raise requests.HTTPError


def download_book_by_url(url,
                         book_filename,
                         storage_folder='books'):
    '''Download file as a text'''
    if not os.path.exists(storage_folder):
        os.makedirs(storage_folder)

    response = requests.get(url)
    response.raise_for_status()
    check_for_redirect(response)

    book_fullpath = f'{storage_folder}/{book_filename}'
    print(f'Save to file - {book_fullpath}')

    with open(book_fullpath, 'wb') as file:
        file.write(response.content)
    return response.status_code


def download_bunch_of_books(id_start=1,
                            id_stop=100,
                            storage_folder='books'):
    '''Download books with id in range [id_start, id_stop]'''
    if not os.path.exists(storage_folder):
        os.makedirs(storage_folder)

    for id in range(id_start, id_stop+1):
        url = f'https://tululu.org/txt.php?id={id}'
        book_filename = f'id{id}.txt'

        try:
            response = download_book_by_url(url=url,
                                            storage_folder=storage_folder,
                                            book_filename=book_filename)
        except requests.exceptions.HTTPError as err:
            print(f'Main page redirect - {book_filename}')


def extract_book_name_author(id):
    '''Extract book name and author'''
    url = f'https://tululu.org/b{id}/'
    response = requests.get(url)
    response.raise_for_status()
    check_for_redirect(response)

    soup = BeautifulSoup(response.text, 'lxml')
    book = soup.find('div', id='content').find('h1').text
    book_name, book_author = book.split('::')

    book_name = book_name.lstrip().rstrip()
    book_author = book_author.lstrip().rstrip()

    return {
        'id': id,
        'url': f'http://tululu.org/txt.php?id={id}',
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


def main():
    '''Program entry point'''
    env = Env()
    env.read_env()
    storage_folder = env('STORAGE_FOLDER')

    for book_id in range(100):
        try:
            book = extract_book_name_author(book_id)
            book_url = book['url']
            book_name = book['name']
            filepath = download_txt(book_url, book_name, folder=storage_folder)
            print(filepath)
        except requests.exceptions.HTTPError as err:
            pass


if __name__ == '__main__':
    main()
