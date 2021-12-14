from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler
from typing import Optional

import urllib.parse
import database


# Login attempt with a specified email
def do_login(query_vars: dict[str, str], rqw: SimpleHTTPRequestHandler) -> Optional[str]:
    if 'mail' not in query_vars:
        rqw.send_error(HTTPStatus.BAD_REQUEST, None, "The query string isn't valid")

        return None

    mail = query_vars['mail'].strip()

    if 'redirect' in query_vars:
        redirect = urllib.parse.unquote(query_vars['redirect'].strip(), errors='strict')
    else:
        redirect = None

    if redirect is None or not redirect or redirect[0] != '/':
        redirect = "/accueil.html"

    with database.conn.cursor() as cursor:
        cursor.execute("SELECT id FROM utilisateur WHERE mail = LOWER(%s)", (mail,))
        rs = cursor.fetchone()

        if rs is None:
            rqw.send_error(HTTPStatus.UNAUTHORIZED, None, "No account is associated with this email")

            return None

        user_id = rs[0]

    # Set authentification cookie, then redirect to main page
    rqw.send_response(HTTPStatus.SEE_OTHER)
    rqw.send_header("Set-Cookie", "userid=%d;" % user_id)
    rqw.send_header("Location", redirect)
    rqw.end_headers()

    return None
