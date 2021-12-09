import os.path
from configparser import ConfigParser
from typing import Any

import psycopg2

# The database connection
conn: Any


def init():
    global conn

    # Allows other developers to have different settings in a .gitignored file.
    def load_config():
        configpath = "../config.ini"
        config = ConfigParser()

        if not os.path.exists(configpath):
            config['database'] = {
                'hostname': 'localhost',
                'port': '5432',
                'username': 'postgres',
                'password': '1234',
                'database': 'postgres'
            }

            with open(configpath, "w") as f:
                config.write(f)
        else:
            config.read(configpath)

        return config

    # Load config
    config = load_config()['database']

    # Database connection
    conn = psycopg2.connect(
        host=config['hostname'],
        port=config['port'],
        user=config['username'],
        password=config['password'],
        dbname=config['database']
    )
