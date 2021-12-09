from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler
from typing import Optional

from bs4 import BeautifulSoup

import database

profile_in_html: str


def init():
    global profile_in_html

    with open("website/profile.in.html", encoding="utf-8") as f:
        profile_in_html = f.read()


def read_userid_cookie(rqw: SimpleHTTPRequestHandler) -> Optional[int]:
    cookie: str = rqw.headers.get("Cookie")

    if not cookie or not cookie.startswith("userid="):
        rqw.send_response(HTTPStatus.TEMPORARY_REDIRECT)
        rqw.send_header("Location", "/login.html")
        rqw.end_headers()

        return None

    try:
        user_id = int(cookie[len("userid="):])
    except ValueError:
        rqw.send_response(HTTPStatus.TEMPORARY_REDIRECT)
        rqw.send_header("Location", "/login.html")
        rqw.send_error("Set-Cookie", "")
        rqw.end_headers()

        return None

    return user_id


def show_profile(_query_vars: dict[str, str], rqw: SimpleHTTPRequestHandler) -> Optional[str]:
    user_id = read_userid_cookie(rqw)
    if user_id is None:
        return None

    with database.conn.cursor() as cursor:
        cursor.execute("""\

SELECT nom, prenom, mail, rue, numero, complement, code_postal, tel FROM utilisateur, adresse
WHERE utilisateur.adresse=adresse.id
AND utilisateur.id=%s

        """, (user_id,))

        rs = cursor.fetchone()

    soup = BeautifulSoup(profile_in_html, features="html.parser")
    form = soup.find(id="profilebox")

    form.find("input", attrs={"name": "name"})["value"] = rs[0]
    form.find("input", attrs={"name": "surname"})["value"] = rs[1]
    form.find("input", attrs={"name": "mail"})["value"] = rs[2]
    form.find("input", attrs={"name": "street"})["value"] = rs[3]
    form.find("input", attrs={"name": "street_number"})["value"] = rs[4]
    form.find("input", attrs={"name": "additional_address"})["value"] = rs[5]
    form.find("input", attrs={"name": "postal_code"})["value"] = rs[6]
    form.find("input", attrs={"name": "tel"})["value"] = rs[7]

    return str(soup)
