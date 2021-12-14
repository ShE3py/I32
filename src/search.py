import urllib.parse
from http.server import SimpleHTTPRequestHandler
from typing import Optional

from bs4 import BeautifulSoup

import database

search_in_html: str
search_item_card_in_html: str


def init():
    global search_in_html, search_item_card_in_html

    with open("website/search.in.html", encoding="utf-8") as f:
        search_in_html = f.read()

    with open("website/search.item_card.in.html", encoding="utf-8") as f:
        search_item_card_in_html = f.read()


def do_search(query_vars: dict[str, str], _rqw: SimpleHTTPRequestHandler) -> Optional[str]:
    if 'what' in query_vars:
        search_input: Optional[str] = query_vars['what'].strip()
        search_input = search_input.replace("%", "\\\\%").replace("_", "\\\\_")  # escape patterns in search input
        search_input = "%" + search_input + "%"
    else:
        search_input = None

    if 'categorie' in query_vars:
        categorie = int(query_vars['categorie'])
    else:
        categorie = None

    soup = BeautifulSoup(search_in_html, features="html.parser")

    inner_html = ""
    with database.conn.cursor() as cursor:
        cursor.execute("SELECT * FROM recherche(%s, %s, 0)", (search_input, categorie))

        for record in cursor:
            inner_html += search_item_card_in_html.format(ref=urllib.parse.quote(record[0]), model=record[1], price=record[2], seller_name=record[3], seller_surname=record[4])

    if not inner_html:
        inner_html += "<h3>Aucun résultat.</h3>"

    soup.find(id="__python_generate").append(BeautifulSoup(inner_html, features="html.parser"))

    return str(soup)
