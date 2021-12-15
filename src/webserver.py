import logging
import urllib.parse
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, HTTPServer
from typing import Callable, Optional

import sys

import database
import item
import profile
import search
from add_item import do_add_item
from item import show_item
from login import do_login
from profile import show_profile, read_userid_cookie
from register import do_register, do_user_update
from search import do_search

# Webserver constants
PORT = 80
SERVER_ADDRESS = ("127.0.0.1", PORT)


# An object that supply the webpages requested by an browser
class WebpageSupplier(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.error_message_format = """\
<!DOCTYPE HTML>
<html lang="fr">
    <head>
        <title>Back Market &mdash; Erreur %(code)d</title>
    </head>
    <body style="margin: 1em;">
        <h2>Error %(code)d: %(message)s</h1>
        <p>%(explain)s.</p>
    </body>
</html>
"""

        super().__init__(*args, directory="website/", **kwargs)

    # Serve a GET request.
    def do_GET(self):
        # If the requested page is a dynamic one,
        # => generate it
        #
        # Else,
        # => serve the .html file on disk

        try:
            if self.path.startswith("/search.html"):
                self.do_dynamic("/search.html", do_search)

            elif self.path.startswith("/do_register.html"):
                self.do_dynamic("/do_register.html", do_register)

            elif self.path.startswith("/do_login.html"):
                self.do_dynamic("/do_login.html", do_login)

            elif self.path.startswith("/profile.html"):
                self.do_dynamic("/profile.html", show_profile)

            elif self.path.startswith("/do_update.html"):
                self.do_dynamic("/do_update.html", do_user_update)

            elif self.path.startswith("/do_add.html"):
                self.do_dynamic("/do_add.html", do_add_item)

            elif self.path.startswith("/item.html"):
                self.do_dynamic("/item.html", show_item)

            else:
                if self.path.startswith("/add_item.html"):
                    read_userid_cookie(self)  # force login

                super().do_GET()

        except (ConnectionAbortedError, ConnectionResetError):
            pass

        except:
            try:
                self.send_error(HTTPStatus.INTERNAL_SERVER_ERROR, None)
            except (ConnectionAbortedError, ConnectionResetError):
                pass

            logging.exception("webserver:do_dynamic")  # print strack trace
            database.conn.rollback()

        return

    def do_dynamic(self, path: str, f: Callable[[dict[str, str], SimpleHTTPRequestHandler], Optional[str]]):
        # query_string: all the characters after the `?` in an URL
        query_string = self.path[len(path) + len('?'):]

        if query_string:
            _qs_vars = urllib.parse.parse_qs(query_string, keep_blank_values=True, strict_parsing=True, errors='strict')
            qs_vars = dict()

            # `urllib.parse.parse_qs()` allows duplicated keys, we don't want this behavior
            for k, v in _qs_vars.items():
                l = len(v)

                if l == 0:
                    continue

                if l != 1:
                    self.send_error(HTTPStatus.BAD_REQUEST, None, "Duplicated paramter `{}`".format(k))
                    return

                qs_vars[k] = v[0]
        else:
            qs_vars = dict()

        # `f()` is the dynamic page handler
        result = f(qs_vars, self)
        if result is None:
            return  # `f()` return `None` if the event is already handled

        # `f()` return an `str` representing the HTML page to show
        content_bytes = result.encode()

        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", len(content_bytes))
        self.end_headers()

        self.wfile.write(content_bytes)

    def log_request(self, code='-', size='-'):
        pass  # don't spam me with success messages, aho! ૮₍ ˃ ⤙ ˂ ₎ა

    def log_message(self, format, *args):
        print("[src/webserver.py]: %s" % (format % args), file=sys.stderr)


# The webserver instance
inst: HTTPServer


def init():
    global inst

    inst = HTTPServer(SERVER_ADDRESS, WebpageSupplier)
    search.init()
    profile.init()
    item.init()
