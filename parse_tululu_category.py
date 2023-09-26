import os
import time
import logging
import argparse
import requests
from environs import Env
from bs4 import BeautifulSoup
from constants import MAIN_PAGE_URL as MAIN_PAGE_URL
from pathvalidate import sanitize_filename
from urllib.parse import urljoin, urlparse, unquote
from parser_exceptions import RedirectException
from parser_exceptions import StartIdStopIdException


def check_for_tululu_redirect(response):
    '''Check for redirection to the tululu.org main page'''
    if response.url == MAIN_PAGE_URL:
        raise RedirectException


def get_genre_bookpage_url(genre_id, book_page_num=1):
    '''Get genre page URL. Default genre - science fiction with id=55'''
    category_page_url = urljoin(MAIN_PAGE_URL, f'l{genre_id}/')
    return urljoin(category_page_url, f'{book_page_num}/')


def get_first_book_url(html):
    '''Get first book URL on the book page'''
    soup = BeautifulSoup(html, 'lxml')
    first_book_card = soup.find('table', class_='d_book')
    _, book_url_section, _, _, _, _ = first_book_card.find_all('tr')
    book_url = book_url_section.find('a')['href']
    book_url = urljoin(MAIN_PAGE_URL, f'{book_url}')
    return book_url


def get_page_book_urls(html):
    '''Get all books URLs from the page'''
    page_books_urls = []
    soup = BeautifulSoup(html, 'lxml')
    book_cards = soup.find_all('table', class_='d_book')

    for book_card in book_cards:
        book_rows = book_card.find_all('tr')
        _, book_url_section, _, _, _, _ = book_rows
        book_url = book_url_section.find('a')['href']
        book_url = urljoin(MAIN_PAGE_URL, f'{book_url}')
        page_books_urls.append(book_url)
    return {'page_books_urls': page_books_urls,
            'page_books_number': len(page_books_urls)}


def main():
    env = Env()
    env.read_env()
    genre_id = env.int('BOOKS_GENRE', 55)

    for page_id in range(1, 11):
        genre_url_page = get_genre_bookpage_url(genre_id=genre_id,
                                                book_page_num=page_id)
        response = requests.get(genre_url_page)
        response.raise_for_status()
        check_for_tululu_redirect(response)
        html = response.text

        page_books_urls = get_page_book_urls(html=html)['page_books_urls']
        for book_url in page_books_urls:
            print(book_url)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO,
                        filename='parser.log',
                        filemode='w',
                        format="%(asctime)s %(levelname)s %(message)s")
    try:
        main()
    except RedirectException as err:
        print('Redirect to the main page exception!')
        logging.info('Redirect to the main page exception!')
    except requests.exceptions.HTTPError as err:
        print(f'HTTP protocol error!')
        logging.info(f'HTTP protocol error!')
