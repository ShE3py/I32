from http import HTTPStatus
from typing import Union

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


def do_search(query_vars: dict[str, str]) -> Union[str, tuple]:
    if 'what' not in query_vars:
        return HTTPStatus.BAD_REQUEST, None, "The query string isn't valid"

    search_input = query_vars['what']

    soup = BeautifulSoup(search_in_html, features="html.parser")

    inner_html = ""
    with database.conn.cursor() as cursor:
        cursor.execute("SELECT * FROM recherche(%s)", ('%' + search_input + '%',))

        for record in cursor:
            inner_html += search_item_card_in_html.format(model=record[0], categorie=record[1], price=record[2], seller_name=record[3], seller_surname=record[4])

    if not inner_html:
        inner_html += "<h3>Aucun résultat.</h3>"

    soup.find(id="__python_generate").append(BeautifulSoup(inner_html, features="html.parser"))

    return str(soup)
