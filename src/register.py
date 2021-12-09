from http import HTTPStatus
from typing import Union


def do_register(query_vars: dict[str, str]) -> Union[str, tuple]:
    if not all(var in query_vars for var in ("name", "surname", "mail", "street", "street_number", "additional_address", "postal_code", "country", "tel")):
        return HTTPStatus.BAD_REQUEST, None, "The query string isn't valid"

    name = query_vars["name"]
    surname = query_vars["surname"]
    mail = query_vars["mail"]
    street = query_vars["street"]
    street_number = query_vars["street_number"]
    additional_address = query_vars["additional_address"]
    postal_code = query_vars["postal_code"]
    country = query_vars["country"]
    tel = query_vars["tel"]

    if any(not var.strip() for var in (name, surname, mail, street, street_number, additional_address, postal_code, country, tel)):
        return HTTPStatus.BAD_REQUEST, None, "A parameter isn't valid"

    return "OK"
