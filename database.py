import os

import mysql.connector

from dotenv import load_dotenv


# =========================================================
# LOAD ENVIRONMENT VARIABLES
# =========================================================

load_dotenv()


# =========================================================
# DATABASE CONNECTION
# =========================================================

def get_db_connection():

    connection = mysql.connector.connect(

        host=os.getenv(
            "DB_HOST",
            "localhost"
        ),

        user=os.getenv(
            "DB_USER",
            "root"
        ),

        password=os.getenv(
            "DB_PASSWORD",
            ""
        ),

        database=os.getenv(
            "DB_NAME",
            "skillbridge"
        ),

        port=int(
            os.getenv(
                "DB_PORT",
                "3306"
            )
        )

    )

    return connection