import os
import sqlite3
from . import db_base


DB_FILENAME_ALL = "out"
DB_FILENAME = "out_three"
FORCE = False


class DBSqlite(db_base.DB):
    sql_order = ""

    db_filename_all = db_base.SAVE_DIR + "/" + DB_FILENAME_ALL + ".all.db"
    db_filename = db_base.SAVE_DIR + "/" + DB_FILENAME + ".db"

    def __init__(self):
        super().__init__()

        self.conn_all = sqlite3.connect(self.db_filename_all)
        self.cur_all = self.conn_all.cursor()

        self.conn = sqlite3.connect(self.db_filename)
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

    @classmethod
    def setup(cls, filename_btc, filename_eth, ping_data):
        if FORCE:
            if os.path.exists(cls.db_filename_all):
                os.remove(cls.db_filename_all)

        if os.path.exists(cls.db_filename):
            os.remove(cls.db_filename)

        # super().setup_btc(filename_btc, ping_data, force=FORCE)
        super().setup_eth(
            filename_eth,
            # "addr_csv/small.csv",
            ping_data,
            force=FORCE,
        )

        print("\nSetup complete")


# https://yuyuublog.com/executemany/
# * local db server, not py lib
# * check size
# engine = create_engine("mysql://scott:tiger@localhost/foo")
