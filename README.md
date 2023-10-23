# Description

Script parses book texts and images from on-line library: https://tululu.org/ and puts it to the folders, determined by the user.

# Install tools

## python3-venv
```bash
apt update && apt install -y python3-venv

cd weblibparser
```

## Create & activate virtual environment
```bash
python3 -m venv venv

source venv/bin/activate
```

## Install dependencies

```bash
pip3 install -r requirements.txt
```

## Prepare .env file

Available variables are:

- BOOKS_GENRE  (define book genre to parse)

In case of `.env` file absence, script will parse books of science fiction genre over on-line library.

Default parameters to parse on-line library are:

- BOOKS_GENRE = 55    (science fictions genre)


# Run script

To run on-line library parsing, you can just execute command:

```bash
python3 parse_tululu_category.py
```

In this way, script will parse all science fictions books, parse text fragments, images and generate `JSON` file and store all of these stuff in a current folder.


## Script options

- --start_page

Determine first page of book category to start parsing.

Default value = 1 (first page of books category list)

- --end_page

Determine last page of book category to stop parsing.

Default value =  last page of books category list

Be careful with script parameters: `--end_page` must be larger then `start_page`.

- --skip_imgs

Skip images downloading

- --skip_txt

Skip book descriptions downloading

- --dest_folder

Setup folder name to store text descriptions, images and `JSON` file.

In case of absence, all files will be stored in current folder.

In case of exceptions, all error events will be handled and files will be stored in the current folder as well.


## Run script with parameters

```bash
python3 parse_tululu_category.py  --start_page=2 --end_page=3 --skip_txt --dest_folder=/User/apollo84/ 
```

In this case, script will parse 2 and 3 page of science fiction category, skip text descriptions downloading and try store all files to the folder with name `/User/apollo84/`

## Parsing results

Script saves parsing results in `JSON` file with name `books.json`, file structure shown below:


```json
[
    {
        "title": "Программируемый мальчик (педагогическая фантастика)",
        "author": "Тюрин Александр Владимирович",
        "img_src": "/Users/admin/code/weblibparser/images/nopic.gif",
        "book_path": "",
        "comments": [],
        "genres": [
            "Детская фантастика",
            "Киберпанк",
            "Научная фантастика"
        ]
    },
    {
        "title": "Войны Сорока Островов (Часть первая)",
        "author": "Лукьяненко Сергей Васильевич",
        "img_src": "/Users/admin/code/weblibparser/images/nopic.gif",
        "book_path": "",
        "comments": [
            "В последних словах объясняющих книгу в целом, я просто остановился и думал..., а ведь правда всё именно так. ",
            "Понравилось, жду продолжения!!!",
            "Если вы еще не читали Лукьяненко, советую начинать с этой книги. Она, как простая но забойная песня в концерте, покажет вам, ваш ли это автор. (Мне ОЧЕНЬ нравтися)."
        ],
        "genres": [
            "Детская фантастика",
            "Научная фантастика"
        ]
    } 
] 
```

## Result log file

Script writes log file `parser.log` with errors and collisions events. It allows you to figure out and fix occurred issues. 

# Projects goals

Script was written as a study project for Python web development course [Devman](https://dvmn.org)
