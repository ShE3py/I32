from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler
from typing import Optional

import database
from profile import read_userid_cookie


# Reads an user's data from the query string's variables
def read_user(query_vars: dict[str, str], rqw: SimpleHTTPRequestHandler) -> Optional[tuple]:
    if not all(var in query_vars for var in ("name", "surname", "mail", "street", "street_number", "additional_address", "postal_code", "country", "tel")):
        rqw.send_error(HTTPStatus.BAD_REQUEST, None, "The query string isn't valid")

        return None

    name = query_vars["name"].strip()
    surname = query_vars["surname"].strip()
    mail = query_vars["mail"].strip()
    street = query_vars["street"].strip()
    street_number = query_vars["street_number"].strip()
    additional_address = query_vars["additional_address"].strip()
    postal_code = query_vars["postal_code"].strip()
    country = query_vars["country"].strip()
    tel = query_vars["tel"].strip()

    if any(not var for var in (name, surname, mail, street, street_number, postal_code, country, tel)):
        rqw.send_error(HTTPStatus.BAD_REQUEST, None, "A parameter isn't valid")

        return None

    if not additional_address:
        additional_address = None

    return name, surname, mail, street, street_number, additional_address, postal_code, country, tel


# Creates a new user
def do_register(query_vars: dict[str, str], rqw: SimpleHTTPRequestHandler) -> Optional[str]:
    ru = read_user(query_vars, rqw)
    if ru is None:
        return None

    name, surname, mail, street, street_number, additional_address, postal_code, country, tel = ru

    with database.conn.cursor() as cursor:
        cursor.execute("INSERT INTO adresse VALUES (DEFAULT, %s, %s, %s, %s, %s) RETURNING id", (country, postal_code, street, street_number, additional_address))
        address_id = cursor.fetchone()[0]

        cursor.execute("INSERT INTO utilisateur VALUES (DEFAULT, %s, %s, %s, %s, %s) RETURNING id", (name, surname, mail, tel, address_id))
        user_id = cursor.fetchone()[0]

    database.conn.commit()

    rqw.send_response(HTTPStatus.SEE_OTHER)
    rqw.send_header("Set-Cookie", "userid=%d;" % user_id)
    rqw.send_header("Location", "/accueil.html")
    rqw.end_headers()

    return None


# Updates an existing user's data
def do_user_update(query_vars: dict[str, str], rqw: SimpleHTTPRequestHandler) -> Optional[str]:
    user_id = read_userid_cookie(rqw)
    ru = read_user(query_vars, rqw)

    if user_id is None or ru is None:
        return None

    name, surname, mail, street, street_number, additional_address, postal_code, country, tel = ru

    with database.conn.cursor() as cursor:
        cursor.execute("SELECT adresse FROM utilisateur WHERE utilisateur.id=%s", (user_id,))
        address_id = cursor.fetchone()[0]

        cursor.execute("UPDATE adresse SET rue = %s, numero = %s, complement = %s, code_postal = %s, pays = %s WHERE id=%s", (street, street_number, additional_address, postal_code, country, address_id))
        cursor.execute("UPDATE utilisateur SET nom = %s, prenom = %s, mail = %s, tel = %s WHERE id=%s", (name, surname, mail, tel, user_id))

    database.conn.commit()

    rqw.send_response(HTTPStatus.SEE_OTHER)
    rqw.send_header("Location", "/accueil.html")
    rqw.end_headers()

    return None
