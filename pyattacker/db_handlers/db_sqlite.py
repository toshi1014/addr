import os
import sqlite3
from . import db_base


DB_FILENAME = "out.db"
FORCE = False


class DBSqlite(db_base.DB):
    sql_order = ""

    def __init__(self):
        super().__init__()
        self.conn_all = sqlite3.connect(DB_FILENAME + ".all")
        self.cur_all = self.conn_all.cursor()

        self.conn = sqlite3.connect(DB_FILENAME)
        self.cur = self.conn.cursor()

    @classmethod
    def setup(cls, filename_btc, filename_eth, ping_data):
        if FORCE:
            if os.path.exists(DB_FILENAME + ".all"):
                os.remove(DB_FILENAME + ".all")

        if os.path.exists(DB_FILENAME):
            os.remove(DB_FILENAME)

        super().setup_btc(filename_btc, ping_data, force=FORCE)
        super().setup_eth(filename_eth, ping_data, force=FORCE)

        print("\nSetup complete")


# https://yuyuublog.com/executemany/
# * local db server, not py lib
# * check size
# engine = create_engine("mysql://scott:tiger@localhost/foo")
