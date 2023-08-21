import os
import requests
from environs import Env


def check_for_redirect(response):
    '''Check for redirect URL'''
    if response.url == 'https://tululu.org/':
        raise requests.HTTPError


def download_book(url, storage_folder, book_filename):
    '''Download file as a text'''
    response = requests.get(url)
    response.raise_for_status() 
    check_for_redirect(response)

    book_fullpath = f'{storage_folder}/{book_filename}'
    print(f'Save to file - {book_fullpath}')
    with open(book_fullpath, 'wb') as file:
        file.write(response.content)
    return response.status_code


def main():
    '''Program entry point'''
    env = Env()
    env.read_env()
    storage_folder = env('STORAGE_FOLDER')

    if not os.path.exists(storage_folder):
        os.makedirs(storage_folder)

    for i in range(11):
        url = f'https://tululu.org/txt.php?id={i}'
        book_filename = f'id{i}.txt'
        try:
            response = download_book(url=url, \
                                     storage_folder=storage_folder, \
                                     book_filename=book_filename)
        except requests.exceptions.HTTPError as err:
            print('Main page redirect')


if __name__=='__main__':
    main()
