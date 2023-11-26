import src


# SRC_FILENAME = "addr_list.short.tsv"
SRC_FILENAME = "addr_list.tsv"

PING_DATA = {
    "entropy":  "b0e8160f51929bf718a3f28ddc15cf27",
    "addr": "15VLC7awxvzWR44vX5ruDGGUuNfzosJBct",
}


def init_db():
    cls_db = src.db_handlers.DBSqlite
    # cls_db = src.db_handlers.DBPostgres

    cls_db.setup(SRC_FILENAME, PING_DATA)


if __name__ == "__main__":
    init_db()
