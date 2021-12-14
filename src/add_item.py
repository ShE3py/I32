from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler
from typing import Optional
import time
import base64

import database
from profile import read_userid_cookie


def read_item(query_vars: dict[str, str], rqw: SimpleHTTPRequestHandler) -> Optional[tuple]:
    if not all(var in query_vars for var in ("categorie", "model", "series", "brand", "description", "price")):
        rqw.send_error(HTTPStatus.BAD_REQUEST, None, "The query string isn't valid")

        return None

    categorie = query_vars["categorie"].strip()
    model = query_vars["model"].strip()
    series = query_vars["series"].strip()
    brand = query_vars["brand"].strip()
    description = query_vars["description"].strip()
    price = query_vars["price"].strip()

    if any(not var for var in (categorie, model, series, brand, description, price)):
        rqw.send_error(HTTPStatus.BAD_REQUEST, None, "A parameter isn't valid")

        return None

    try:
        categorie = int(categorie)
        price = float(price)
    except ValueError:
        rqw.send_error(HTTPStatus.BAD_REQUEST, None, "A parameter isn't valid")

        return None

    return categorie, model, series, brand, description, price


def do_add_item(query_vars: dict[str, str], rqw: SimpleHTTPRequestHandler) -> Optional[str]:
    user_id = read_userid_cookie(rqw)
    ri = read_item(query_vars, rqw)

    if user_id is None or ri is None:
        return None

    categorie, model, series, brand, description, price = ri
    ref = "item-" + hex(time.time_ns())[2:]

    with database.conn.cursor() as cursor:
        cursor.execute("INSERT INTO article VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", (ref, categorie, user_id, price, description, brand, series, model))

    database.conn.commit()

    rqw.send_response(HTTPStatus.SEE_OTHER)
    rqw.send_header("Set-Cookie", "userid=%d;" % user_id)
    rqw.send_header("Location", "/item.html?ref=%s" % ref)
    rqw.end_headers()

    return None
