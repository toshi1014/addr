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
    def __init__(self):
        super().__init__()
        self.conn = psycopg2.connect(**POSTGRES_CONFIG)
        self.cur = self.conn.cursor()

    def clean_table(self):
        self.drop_table(db_base.DB.tbl_legacy)
        self.drop_table(db_base.DB.tbl_segwit)

        for i in range(db_base.DB.dividend_lengh + 1):
            self.drop_table(db_base.DB.tbl_legacy + str(i))
            self.drop_table(db_base.DB.tbl_segwit + str(i))

    @classmethod
    def setup(cls, src_filename, ping_data):
        engine = create_engine(
            "postgresql://{user}:{password}@{host}:{port}/{database}".format(
                **POSTGRES_CONFIG)
        )

        cls().clean_table()
        super().setup(src_filename, ping_data, engine)


"""
init postgres

sudo -u postgres psql
ALTER ROLE postgres WITH password "password";
CREATE DATABASE mydb;
"""
