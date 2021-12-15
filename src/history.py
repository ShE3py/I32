import urllib.parse
from http.server import SimpleHTTPRequestHandler
from typing import Optional

from bs4 import BeautifulSoup

import database
from profile import read_userid_cookie

history_in_html: str
history_purchase_card_in_html: str
history_selling_card_in_html: str
history_currenlty_selling_card_in_html: str


def init():
    global history_in_html, history_purchase_card_in_html, history_selling_card_in_html, history_currenlty_selling_card_in_html

    with open("website/history.in.html", encoding="utf-8") as f:
        history_in_html = f.read()

    with open("website/history.purchase_card.in.html", encoding="utf-8") as f:
        history_purchase_card_in_html = f.read()

    with open("website/history.selling_card.in.html", encoding="utf-8") as f:
        history_selling_card_in_html = f.read()

    with open("website/history.currently_selling_card.in.html", encoding="utf-8") as f:
        history_currenlty_selling_card_in_html = f.read()


def show_history(_query_vars: dict[str, str], rqw: SimpleHTTPRequestHandler) -> Optional[str]:
    user_id = read_userid_cookie(rqw)
    if user_id is None:
        return None

    soup = BeautifulSoup(history_in_html, features="html.parser")

    purchase_inner_html = ""
    selling_inner_html = ""
    currently_selling_inner_html = ""
    with database.conn.cursor() as cursor:
        cursor.execute("SELECT * FROM historique_achat(%s)", (user_id,))

        for record in cursor:
            purchase_inner_html += history_purchase_card_in_html.format(ref=urllib.parse.quote(record[0]), model=record[1], price=record[2], seller_surname=record[3], seller_name=record[4])

        cursor.execute("SELECT * FROM historique_vente(%s)", (user_id,))

        for record in cursor:
            selling_inner_html += history_selling_card_in_html.format(ref=urllib.parse.quote(record[0]), model=record[1], price=record[2], buyer_surname=record[3], buyer_name=record[4])

        cursor.execute("SELECT * FROM articles_vendus_par(%s)", (user_id,))

        for record in cursor:
            currently_selling_inner_html += history_currenlty_selling_card_in_html.format(ref=urllib.parse.quote(record[0]), model=record[1], price=record[2])

    if not purchase_inner_html:
        purchase_inner_html = "<h5>Néant.</h5>"

    if not selling_inner_html:
        selling_inner_html = "<h5>Néant.</h5>"

    if not currently_selling_inner_html:
        currently_selling_inner_html = "<h5>Néant.</h5>"

    soup.find(id="__python_generate_0").append(BeautifulSoup(purchase_inner_html, features="html.parser"))
    soup.find(id="__python_generate_1").append(BeautifulSoup(selling_inner_html, features="html.parser"))
    soup.find(id="__python_generate_2").append(BeautifulSoup(currently_selling_inner_html, features="html.parser"))

    return str(soup)
