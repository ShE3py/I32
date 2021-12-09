import database
import webserver as websrv

# Global mutable variables
KEEP_RUNNING = True

database.init()
websrv.init()

print("Webserver started on port", websrv.PORT)

while KEEP_RUNNING:
    websrv.inst.handle_request()

websrv.inst.server_close()
database.conn.close()
