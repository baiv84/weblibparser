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


MAIN_PAGE_URL = 'https://tululu.org/'
BOOKS_PER_PAGE = 25

def check_for_tululu_redirect(response):
    '''Check for redirection to the tululu.org main page'''
    if response.url == MAIN_PAGE_URL:
        raise RedirectException    


def get_genre_bookpage_url(genre_id=55, book_page_num=1):
    '''Get genre page URL. Default genre - science fiction with id=55'''
    category_page_url = urljoin(MAIN_PAGE_URL, f'l{genre_id}/')
    return urljoin(category_page_url, f'{book_page_num}/')


def get_first_book_url(soup):
    '''Get first book URL on the book page'''
    first_book_card = soup.find('table', class_='d_book')
    _, book_url_section, _, _, _, _ = first_book_card.find_all('tr') 
    book_url = book_url_section.find('a')['href']
    book_url = urljoin(MAIN_PAGE_URL, f'{book_url}')
    return book_url
    

def get_all_book_urls(soup):
    '''Get all books URLs from the page'''
    book_urls = []
    book_cards = soup.find_all('table', class_='d_book')
    
    for book_card in book_cards:
        book_rows = book_card.find_all('tr')
        _, book_url_section, _, _, _, _ = book_rows
        book_url = book_url_section.find('a')['href']
        book_url = urljoin(MAIN_PAGE_URL, f'{book_url}')
        book_urls.append(book_url)
    return {'book_urls': book_urls,
            'books_number': len(book_urls)}


if __name__ == '__main__':
    page_num = 1
    genre_url_page = get_genre_bookpage_url(book_page_num=page_num)
    response = requests.get(genre_url_page)
    response.raise_for_status()
    check_for_tululu_redirect(response)
    html = response.text
    soup = BeautifulSoup(html, 'lxml')
    print(get_first_book_url(soup))

    # while True: 
    #     genre_url_page = get_genre_bookpage_url(book_page_num=page_num)
    #     response = requests.get(genre_url_page)
    #     response.raise_for_status()
    #     check_for_tululu_redirect(response)
    #     html = response.text
    #     soup = BeautifulSoup(html, 'lxml')

    #     print(get_first_book_url(soup))
    #     print('*************************')
    #     genre_book_urls = get_all_book_urls(soup)
    #     all_genre_books = genre_book_urls['book_urls']  
    #     genre_books_number = genre_book_urls['books_number']
    #     print(all_genre_books)
    #     if genre_books_number < BOOKS_PER_PAGE:
    #         break
    #     page_num +=1
    