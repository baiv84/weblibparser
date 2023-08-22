import requests
from bs4 import BeautifulSoup


def post_webparser(url):
    '''Post webparser implementation'''
    response = requests.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'lxml')
    title_tag = soup.find('main').find('header').find('h1')
    post_title = title_tag.text

    post_url = soup.find('img', class_='attachment-post-image')['src']

    post_text_div = soup.find('div', class_='entry-content')
    paragraphs = post_text_div.find_all('p')
    paragraphs = [p.text for p in paragraphs]
    post_text = '\n'.join(paragraphs)

    return (post_title, post_url, post_text,)


if __name__ == '__main__':
    url = 'https://www.franksonnenbergonline.com/blog/are-you-grateful/'
    post_title, post_url, post_text = post_webparser(url)
    print(f'{post_title}',
          f'\n{post_url}',
          f'\n\n{post_text}')
