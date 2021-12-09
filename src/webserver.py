import urllib.parse
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, HTTPServer

import database

# Webserver constants
PORT = 80
SERVER_ADDRESS = ("127.0.0.1", PORT)


# An object that supply the webpages requested by an browser
class WebpageSupplier(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory="website/", **kwargs)

    # Serve a GET request.
    def do_GET(self):
        # If the requested page is a dynamic one,
        # => generate it
        #
        # Else,
        # => serve the .html file on disk

        if self.path.startswith("/search.html"):
            self.do_search()
        else:
            super().do_GET()

    def do_search(self):
        search_input = urllib.parse.unquote(self.path[len("/search.html?s="):].replace('+', ' '))

        text = ""
        with database.conn.cursor() as cursor:
            cursor.execute("SELECT * FROM recherche(%s)", ('%' + search_input + '%',))

            for record in cursor:
                text += "Modèle: {}<br />" \
                        "Catégorie: {}<br />" \
                        "Vendeur: {} {}<br />" \
                        "Prix: {}€<br />" \
                    .format(record[0], record[1], record[3], record[4], record[2])

        text_bytes = text.encode()

        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(text_bytes)))
        self.end_headers()

        self.wfile.write(text_bytes)


# The webserver instance
inst: HTTPServer


def init():
    global inst

    inst = HTTPServer(SERVER_ADDRESS, WebpageSupplier)
