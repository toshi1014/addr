import json
import os
import pandas as pd
from tqdm import tqdm


# FIXME: param
CHUNKSIZE = 10**5
SAVE_DIR = "db"


class DB:
    tbl_legacy = "tbl_legacy"
    tbl_segwit = "tbl_segwit"
    tbl_eth = "tbl_eth"
    col_addr = "address"

    dividend_length = 8000
    #  tbl size   itr/sec
    #  5000 000   600
    # 10000 000   420
    # 16000 000   400
    # 80000 000   100

    def __init__(self):
        self.conn = None
        self.cur = None
        self.col_addr = DB.col_addr

        if not os.path.exists(SAVE_DIR):
            os.makedirs(SAVE_DIR)

    @classmethod
    def get_params_to_sql(cls, conn, engine):
        return {
            "con": engine if engine else conn,
            "if_exists": "append",
            "index": False,
            "method": "multi",
            "chunksize": 10*4,
        }

    @classmethod
    def setup_btc(cls, src_filename, ping_data, engine=None, force=True):
        db = cls()
        if force:
            params_to_sql = cls.get_params_to_sql(db.conn_all, engine)

            size_legacy, size_segwit = cls.insert_all(
                src_filename, ping_data, params_to_sql
            )
        else:
            size_legacy, size_segwit = 22961294, 16410460

        params_to_sql = cls.get_params_to_sql(db.conn, engine)
        cls.divide_tbl(db, cls.tbl_legacy, size_legacy, params_to_sql)
        cls.divide_tbl(db, cls.tbl_segwit, size_segwit, params_to_sql)

        print("\nBTC setup complete")

    @classmethod
    def setup_eth(cls, src_filename, ping_data, engine=None, force=True):
        db = cls()
        with open(src_filename, mode="r", encoding="utf-8") as f:
            lines = sum(1 for _ in f)

        if force:
            params_to_sql = cls.get_params_to_sql(db.conn_all, engine)
            cls.insert(
                df=pd.DataFrame({"address": ping_data["addr_eth"]}),
                tbl_name=cls.tbl_eth,
                params_to_sql=params_to_sql,
            )

            reader = pd.read_csv(
                src_filename,
                iterator=True,
                chunksize=CHUNKSIZE,
                header=None,
            )
            for df in tqdm(reader, total=lines // CHUNKSIZE):
                df = df.dropna().rename(columns={1: "address"})[["address"]]
                cls.insert(
                    df=df.map(lambda x: x.lower()),        # lower
                    tbl_name=cls.tbl_eth,
                    params_to_sql=params_to_sql,
                )

        print(
            "\nStats\n"
            f"  size:\t{lines}\n"
            f"  hit:\t{lines/(2**128)}\n"
        )

        params_to_sql = cls.get_params_to_sql(db.conn, engine)
        cls.divide_tbl(db, cls.tbl_eth, lines, params_to_sql)

        print("ETH setup complete")

    @classmethod
    def insert_all(cls, src_filename, ping_data, params_to_sql):
        # insert address for ping
        cls.insert_with_filter(
            df=pd.DataFrame({
                "address": ping_data["addr_btc"]
            }),
            params_to_sql=params_to_sql,
        )

        # insert file data
        with open(src_filename, mode="r", encoding="utf-8") as f:
            lines = sum(1 for _ in f)

        reader = pd.read_csv(
            src_filename,
            sep="\t",
            iterator=True,
            chunksize=CHUNKSIZE,
        )

        sum_size_legacy = 0
        sum_size_segwit = 0
        for df in tqdm(reader, total=lines // CHUNKSIZE):
            size_legacy, size_segwit = cls.insert_with_filter(
                df, params_to_sql)
            sum_size_legacy += size_legacy
            sum_size_segwit += size_segwit

        sum_records = sum_size_legacy + sum_size_segwit
        print(
            "\nStats\n"
            f"  size:\t{sum_records}/{lines} (= {sum_records/lines})\n"
            f"  hit:\t{sum_records/(2**128)}\n"
            f"  legacy:segwit = {sum_size_legacy}:{sum_size_segwit}"
            f" (= {str(sum_size_legacy/sum_records)[:5]}:{str(sum_size_segwit/sum_records)[:5]})\n"
        )

        return sum_size_legacy, sum_size_segwit

    @classmethod
    def insert(cls, df, tbl_name, params_to_sql):
        df[cls.col_addr].to_sql(name=tbl_name, **params_to_sql)

    @classmethod
    def filter_addr(cls, df):
        df_legacy = df.query(f"{cls.col_addr}.str.startswith('1')")
        df_segwit = df.query(f"{cls.col_addr}.str.startswith('bc1q')")
        return df_legacy, df_segwit

    @classmethod
    def insert_with_filter(cls, df, params_to_sql):
        df_legacy, df_segwit = cls.filter_addr(df)
        cls.insert(
            df=df_legacy,
            tbl_name=cls.tbl_legacy,
            params_to_sql=params_to_sql,
        )
        cls.insert(
            df=df_segwit,
            tbl_name=cls.tbl_segwit,
            params_to_sql=params_to_sql,
        )
        return len(df_legacy), len(df_segwit)

    @classmethod
    def format_tbl_name(cls, base, idx):
        return f"{base}{str(idx)}"

    @classmethod
    def divide_tbl(cls, db, tbl_name_all, size, params_to_sql):
        size_per_tbl = size // cls.dividend_length
        assert size_per_tbl > cls.dividend_length, "too much table"

        cur_all = db.conn_all.cursor()
        print(f"Dividing {tbl_name_all}...")
        cur_all.execute(
            f"SELECT * FROM {tbl_name_all} ORDER BY {cls.col_addr}{cls.sql_order};")

        tbl_index = []
        for i in tqdm(range(cls.dividend_length + 1)):
            rows = cur_all.fetchmany(size_per_tbl)
            df = pd.DataFrame({"address": [row[0] for row in rows]})
            cls.insert(
                df=df,
                tbl_name=cls.format_tbl_name(tbl_name_all, i),
                params_to_sql=params_to_sql,
            )

            # memo the end as index
            tbl_index.append(df.iloc[len(df)-1]["address"])

        assert len(cur_all.fetchall()) == 0

        # save indices
        with open(f"{SAVE_DIR}/{tbl_name_all}.json", "w", encoding="utf-8") as f:
            f.write(json.dumps(tbl_index))

    def prepare_index(self):
        # with open(f"{SAVE_DIR}/tbl_legacy.json", "r", encoding="utf-8") as f:
        #     self.idx_tbl_legacy = json.loads(f.read())
        # with open(f"{SAVE_DIR}/tbl_segwit.json", "r", encoding="utf-8") as f:
        #     self.idx_tbl_segwit = json.loads(f.read())
        with open(f"{SAVE_DIR}/tbl_eth.json", "r", encoding="utf-8") as f:
            self.idx_tbl_eth = json.loads(f.read())

    def get_tbl_name(self, addr):
        if addr[:2] == "0x":
            idx_tbl_xxx, tbl_name = self.idx_tbl_eth, DB.tbl_eth
        elif addr[0] == "1":
            idx_tbl_xxx, tbl_name = self.idx_tbl_legacy, DB.tbl_legacy
        else:
            idx_tbl_xxx, tbl_name = self.idx_tbl_segwit, DB.tbl_segwit

        for i, idx in enumerate(idx_tbl_xxx):
            if idx > addr:
                return DB.format_tbl_name(tbl_name, i)

        return DB.format_tbl_name(tbl_name, i)

    def search(self, addr):
        self.cur.execute(
            f"""
            SELECT * FROM {self.get_tbl_name(addr)} where {self.col_addr} = '{addr}';
            """
        )
        row = self.cur.fetchone()
        return row

    def find(self, addr):
        return bool(self.search(addr))

    def drop_table(self, tbl_name):
        sql = f"DROP TABLE IF EXISTS {tbl_name};"
        self.cur.execute(sql)
        self.conn.commit()

    def __del__(self):
        self.conn.close()


# https://yuyuublog.com/executemany/
# * local db server, not py lib
# * check size
# engine = create_engine("mysql://scott:tiger@localhost/foo")
