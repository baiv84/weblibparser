import os
import requests
from environs import Env


def check_for_redirect(response):
    '''Check for redirect URL'''
    if response.url == 'https://tululu.org/':
        raise requests.HTTPError


def download_book_by_url(url, \
                  book_filename, \
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


def download_bunch_of_books(id_start=1, \
                            id_stop=100, \
                            storage_folder='books'):
    '''Download books with id in range [id_start, id_stop]'''

    if not os.path.exists(storage_folder):
        os.makedirs(storage_folder)

    for id in range(id_start, id_stop+1):
        url = f'https://tululu.org/txt.php?id={id}'
        book_filename = f'id{id}.txt'

        try:
            response = download_book_by_url(url=url, \
                                            storage_folder=storage_folder, \
                                            book_filename=book_filename)
        except requests.exceptions.HTTPError as err:
            print(f'Main page redirect - {book_filename}')


def main():
    '''Program entry point'''
    env = Env()
    env.read_env()
    storage_folder = env('STORAGE_FOLDER')

    #-----Download Arthur Clark book-----
    print('Download book - Arthur Clark The sands of Mars')
    book_id = 32168
    url = f'https://tululu.org/txt.php?id={book_id}'
    book_filename = f'id{book_id}.txt'

    try:
        response = download_book_by_url(url=url, \
                                        storage_folder=storage_folder, \
                                        book_filename=book_filename)
    except requests.exceptions.HTTPError as err:
        print(f'Main page redirect - {book_filename}')


    #-----Download set of books-----
    download_bunch_of_books(id_start=1, id_stop=10, storage_folder=storage_folder)


if __name__=='__main__':
    main()
