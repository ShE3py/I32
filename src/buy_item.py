from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler
from typing import Optional

import database
from profile import read_userid_cookie


def do_buy_item(query_vars: dict[str, str], rqw: SimpleHTTPRequestHandler) -> Optional[str]:
    user_id = read_userid_cookie(rqw)
    if user_id is None:
        return None

    if "ref" not in query_vars:
        rqw.send_error(HTTPStatus.BAD_REQUEST, None, "The query string isn't valid")

        return None

    ref = query_vars["ref"].strip()
    if not ref:
        rqw.send_error(HTTPStatus.BAD_REQUEST, None, "A parameter isn't valid")

        return None

    with database.conn.cursor() as cursor:
        cursor.execute("SELECT EXISTS(SELECT * FROM article_en_vente WHERE article=%s)", (ref,))
        rs = cursor.fetchone()

        if rs is None or rs[0] is False:
            rqw.send_error(HTTPStatus.BAD_REQUEST, None, "There are no buyable items referenced by `%s`" % ref)

            return None

        cursor.execute("DELETE FROM article_en_vente WHERE article=%s", (ref,))
        cursor.execute("INSERT INTO achat VALUES (%s, %s)", (user_id, ref))

    database.conn.commit()

    rqw.send_response(HTTPStatus.SEE_OTHER)
    rqw.send_header("Set-Cookie", "userid=%d;" % user_id)
    rqw.send_header("Location", "/accueil.html")
    rqw.end_headers()

    return None
