import db_handlers
import utils


config = utils.read_config()


def init_db():
    if config["DB_TYPE"] == "sqlite":
        cls_db = db_handlers.DBSqlite
    elif config["DB_TYPE"] == "postgres":
        cls_db = db_handlers.DBPostgres
    else:
        raise ValueError(config["DB_TYPE"])

    cls_db.setup(
        filename_btc=config["SRC_FILENAME_BTC"],
        filename_eth=config["SRC_FILENAME_ETH"],
        ping_data=config["PING_DATA"],
    )


if __name__ == "__main__":
    init_db()
