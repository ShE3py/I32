import urllib.parse
from http import HTTPStatus
from http.server import HTTPServer, SimpleHTTPRequestHandler

import psycopg2 as sql

# Database authentication constants
HOSTNAME = 'localhost'
USERNAME = 'postgres'
PASSWORD = '1234'
DATABASE = 'postgres'

# Webserver constants
PORT = 80
SERVER_ADDRESS = ("127.0.0.1", PORT)

# Global mutable variables
KEEP_RUNNING = True

# Database connection
sqlConnection = sql.connect(host=HOSTNAME, user=USERNAME, password=PASSWORD, dbname=DATABASE)


# Webserver creation
class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory="website/", **kwargs)

    def do_GET(self):
        if self.path.startswith("/search.html"):
            self.do_search()
        else:
            super().do_GET()

    def do_search(self):
        search_input = urllib.parse.unquote(self.path[len("/search.html?s="):].replace('+', ' '))

        text = ""
        with sqlConnection.cursor() as cursor:
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


handler = Handler
webServer = HTTPServer(SERVER_ADDRESS, handler)

print("Webserver started on port", PORT)

while KEEP_RUNNING:
    webServer.handle_request()

webServer.server_close()
sqlConnection.close()
