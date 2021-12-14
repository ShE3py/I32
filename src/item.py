from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler
from typing import Optional

from bs4 import BeautifulSoup

import database

item_in_html: str


def init():
    global item_in_html

    with open("website/item.in.html", encoding="utf-8") as f:
        item_in_html = f.read()


def show_item(query_vars: dict[str, str], rqw: SimpleHTTPRequestHandler) -> Optional[str]:
    if "ref" not in query_vars:
        rqw.send_error(HTTPStatus.BAD_REQUEST, None, "The query string isn't valid")

        return None

    ref = query_vars["ref"].strip()

    if not ref:
        rqw.send_error(HTTPStatus.BAD_REQUEST, None, "A parameter isn't valid")

        return None

    with database.conn.cursor() as cursor:
        cursor.execute("SELECT prix, modele, description, nom, prenom, modele, serie, marque, code_postal FROM article, utilisateur, adresse WHERE article.vendeur=utilisateur.id AND utilisateur.adresse=adresse.id AND article.reference=%s", (ref,))
        rs = cursor.fetchone()

        if rs is None:
            rqw.send_error(HTTPStatus.NOT_FOUND, None, "There are no items referenced by `%s`" % ref)

            return None

    soup = BeautifulSoup(item_in_html, features="html.parser")
    el = soup.find(id="__python_generate")

    el.find(id="__python_generate_0").append("Prix: {:.2f} €".format(rs[0]))  # prix
    el.find(id="__python_generate_1").append(rs[1])  # modèle

    if rs[2] is None:
        text = ""
    else:
        text = rs[2] + "<br /><br />"

    text += "<b>Vendeur:</b> " + rs[3] + " " + rs[4] + "<br />"
    text += "<b>Code postal:</b> " + rs[8] + "<br />"
    text += "<b>Modèle:</b> " + rs[5] + "<br />"
    text += "<b>Série:</b> " + rs[6] + "<br />"
    text += "<b>Marque:</b> " + rs[7] + "<br />"

    el.find(id="__python_generate_2").append(BeautifulSoup(text, features="html.parser"))

    return str(soup)
