import os
import shutil
import sqlite3
from . import db_base


DB_FILENAME = "out.db"
FORCE = False


class DBSqlite(db_base.DB):
    sql_order = ""

    def __init__(self):
        super().__init__()
        self.db_filename_all = DB_FILENAME + ".all"
        self.db_filename = db_base.SAVE_DIR + "/" + DB_FILENAME

        self.conn_all = sqlite3.connect(self.db_filename_all)
        self.cur_all = self.conn_all.cursor()

        self.conn = sqlite3.connect(self.db_filename)
        self.cur = self.conn.cursor()

    @classmethod
    def setup(cls, filename_btc, filename_eth, ping_data):
        if FORCE:
            if os.path.exists(DB_FILENAME + ".all"):
                os.remove(DB_FILENAME + ".all")

        if os.path.exists(db_base.SAVE_DIR):
            shutil.rmtree(db_base.SAVE_DIR)

        # super().setup_btc(filename_btc, ping_data, force=FORCE)
        super().setup_eth(
            filename_eth,
            # "addr_csv/small.csv",
            # "addr_csv/out5.eth.csv",
            ping_data,
            force=FORCE,
        )

        print("\nSetup complete")


# https://yuyuublog.com/executemany/
# * local db server, not py lib
# * check size
# engine = create_engine("mysql://scott:tiger@localhost/foo")
