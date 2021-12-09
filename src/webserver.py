import logging
import urllib.parse
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, HTTPServer
from typing import Callable

import sys

import search
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
        <title>Error response</title>
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
            else:
                super().do_GET()

        except:
            self.send_error(HTTPStatus.INTERNAL_SERVER_ERROR, None)
            logging.exception("webserver:do_dynamic")

        return

    def do_dynamic(self, path: str, f: Callable[[dict[str, list[str]]], str]):
        query_string = self.path[len(path) + len('?'):]

        if query_string:
            qs_vars = urllib.parse.parse_qs(query_string, keep_blank_values=True, strict_parsing=True, errors='strict')
        else:
            qs_vars = dict()
        
        content_bytes = f(qs_vars).encode()

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
