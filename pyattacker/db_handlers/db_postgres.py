import psycopg2
from sqlalchemy import create_engine
from . import db_base


POSTGRES_CONFIG = {
    "host": "localhost",
    "user": "postgres",
    "password": "password",
    "database": "mydb",
    "port": 5432,
}


class DBPostgres(db_base.DB):
    sql_order = "::bytea"

    def __init__(self):
        super().__init__()
        self.conn = psycopg2.connect(**POSTGRES_CONFIG)
        self.cur = self.conn.cursor()

    def clean_table(self):
        self.drop_table(db_base.DB.tbl_legacy)
        self.drop_table(db_base.DB.tbl_segwit)

        for i in range(db_base.DB.dividend_length + 1):
            self.drop_table(
                db_base.DB.format_tbl_name(db_base.DB.tbl_legacy, i)
            )
            self.drop_table(
                db_base.DB.format_tbl_name(db_base.DB.tbl_segwit, i)
            )

    @classmethod
    def setup(cls, filename_btc, filename_eth, ping_data):
        engine = create_engine(
            "postgresql://{user}:{password}@{host}:{port}/{database}".format(
                **POSTGRES_CONFIG)
        )

        cls().clean_table()
        super().setup_btc(filename_btc, ping_data, engine)
        super().setup_eth(filename_eth, ping_data, engine)


"""
init postgres

sudo -u postgres psql
ALTER ROLE postgres WITH password "password";
CREATE DATABASE mydb;

\c mydb
\dt
"""
