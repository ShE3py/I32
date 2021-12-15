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

        if search_input:
            search_input = search_input.replace("%", "\\\\%").replace("_", "\\\\_")  # escape patterns in search input
            search_input = "%" + search_input + "%"
        else:
            search_input = None
    else:
        search_input = None

    categorie: Optional[int] = None
    if 'categorie' in query_vars:
        cat = query_vars['categorie'].strip()

        if cat:
            categorie = int(cat)

    price_min: float = float(0)
    if 'price_min' in query_vars:
        pmin = query_vars['price_min'].strip()

        if pmin:
            price_min = float(pmin)

    price_max: float = "Infinity"
    if 'price_max' in query_vars:
        pmax = query_vars['price_max'].strip()

        if pmax:
            price_max = float(pmax)

    ordering: int = 0
    if 'ordering' in query_vars:
        _ord = query_vars['ordering'].strip()

        if _ord:
            ordering = int(_ord)

    soup = BeautifulSoup(search_in_html, features="html.parser")

    inner_html = ""
    with database.conn.cursor() as cursor:
        cursor.execute("SELECT * FROM recherche(%s, %s, %s, %s, %s)", (search_input, categorie, price_min, price_max, ordering))

        for record in cursor:
            inner_html += search_item_card_in_html.format(ref=urllib.parse.quote(record[0]), model=record[1], price=record[2], seller_surname=record[3], seller_name=record[4])

    if not inner_html:
        inner_html += "<h3>Aucun résultat.</h3>"

    soup.find(id="__python_generate").append(BeautifulSoup(inner_html, features="html.parser"))

    return str(soup)
