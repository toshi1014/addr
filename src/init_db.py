import pyattacker


config = pyattacker.utils.read_config()


def init_db():
    if config["DB_TYPE"] == "sqlite":
        cls_db = pyattacker.db_handlers.DBSqlite
    elif config["DB_TYPE"] == "postgres":
        cls_db = pyattacker.db_handlers.DBPostgres
    else:
        raise ValueError(config["DB_TYPE"])

    cls_db.setup(config["SRC_FILENAME"], config["PING_DATA"])


if __name__ == "__main__":
    init_db()
