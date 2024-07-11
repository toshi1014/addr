import glob
import os
import sqlite3
from . import db_base


# SRC_FILENAME = "addr_csv/small.csv"
SRC_FILENAME = "addr_csv/addr_list.eth.csv"

DB_FILENAME_ALL = "out"
DB_FILENAME = "out"
FORCE_ALL = False
TBL_LAST_DIGITS = 4


def remove_if_exits(filepath):
    if os.path.exists(filepath):
        os.remove(filepath)


class DBSqlite(db_base.DB):
    sql_order = ""

    db_filename_all = db_base.SAVE_DIR + "/" + DB_FILENAME_ALL + ".all.db"
    db_filename = f"{db_base.SAVE_DIR}/{DB_FILENAME}" + "{suffix}.db"

    def __init__(self):
        super().__init__(TBL_LAST_DIGITS)

        self.conn_all = sqlite3.connect(self.db_filename_all)
        self.cur_all = self.conn_all.cursor()

        self.conn = sqlite3.connect(
            self.db_filename.format(suffix=TBL_LAST_DIGITS)
        )
        self.cur = self.conn.cursor()

        optimizes = [
            "PRAGMA journal_mode = OFF;",
            "PRAGMA synchronous = OFF;",
            "PRAGMA temp_store = MEMORY;",
            "PRAGMA cache_size = -64000;",
            "PRAGMA mmap_size = 268435456;",
            "PRAGMA optimize;",
        ]
        for opt in optimizes:
            self.conn.execute(opt)

    def setup(self, filename_btc, filename_eth, ping_data):
        if FORCE_ALL:
            remove_if_exits(self.db_filename_all)

        for filepath in glob.glob(self.db_filename.format(suffix="?")):
            remove_if_exits(filepath)

        # super().setup_btc(filename_btc, ping_data, force=FORCE)
        super().setup_eth(
            SRC_FILENAME,
            ping_data,
            force_all=FORCE_ALL,
        )

        print("\nSetup complete")


# https://yuyuublog.com/executemany/
# * local db server, not py lib
# * check size
# engine = create_engine("mysql://scott:tiger@localhost/foo")
