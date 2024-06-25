import json
import os
import pandas as pd
from tqdm import tqdm
import sqlalchemy


# FIXME: param
CHUNKSIZE = 10**5
SAVE_DIR = "db"


def fnv1a_hash(data):
    FNV_prime = 0x100000001b3
    FNV_offset_basis = 0xcbf29ce484222325
    hash_value = FNV_offset_basis
    for byte in data:
        hash_value ^= byte
        hash_value *= FNV_prime
        hash_value &= 0xffffffffffffffff  # 64-bit hash
    return hash_value


def fn_compress(x):
    val = fnv1a_hash(
        bytes.fromhex(x[2:])
    )
    return val.to_bytes(8, "big")


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
    def get_params_to_sql(cls, db_filename, tbl_name):
        def init_engine(db_filename, tbl_name):
            engine = sqlalchemy.create_engine(f"sqlite:///{db_filename}")
            metadata = sqlalchemy.MetaData()
            table = sqlalchemy.Table(
                tbl_name,
                metadata,
                sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
                sqlalchemy.Column("address", sqlalchemy.BLOB,
                                  #   index=True
                                  ),
            )
            metadata.create_all(engine)
            return engine

        return {
            "con": init_engine(db_filename, tbl_name),
            "if_exists": "append",
            "index": False,
            "method": "multi",
            "chunksize": 10*4,
        }

    @classmethod
    def setup_btc(cls, src_filename, ping_data, force=True):
        db = cls()
        if force:
            size_legacy, size_segwit = cls.insert_all(
                db, src_filename, ping_data)
        else:
            size_legacy, size_segwit = 22961294, 16410460

        cls.divide_tbl(db, cls.tbl_legacy, size_legacy)
        cls.divide_tbl(db, cls.tbl_segwit, size_segwit)

        print("\nBTC setup complete")

    @classmethod
    def setup_eth(cls, src_filename, ping_data, force=True):
        db = cls()
        with open(src_filename, mode="r", encoding="utf-8") as f:
            lines = sum(1 for _ in f)

        if force:
            cls.insert(
                df=pd.DataFrame({"address": ping_data["addr_eth"]}).copy(),
                db_filename=db.db_filename_all,
                tbl_name=cls.tbl_eth,
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
                    df=df.map(lambda x: x.lower()).copy(),        # lower
                    db_filename=db.db_filename_all,
                    tbl_name=cls.tbl_eth,
                )

        print(
            "\nStats\n"
            f"  size:\t{lines}\n"
            f"  hit:\t{lines/(2**128)}\n"
        )

        cls.divide_tbl(db, cls.tbl_eth, lines)

        print("ETH setup complete")

    @classmethod
    def insert(cls, df, db_filename, tbl_name, compress=False):
        params_to_sql = cls.get_params_to_sql(db_filename, tbl_name)

        if compress:
            df[cls.col_addr] = df[cls.col_addr].apply(lambda x: fn_compress(x))

        df[cls.col_addr].to_sql(name=tbl_name, **params_to_sql)

    @classmethod
    def insert_all(cls, db, src_filename, ping_data):
        # insert address for ping
        cls.insert_with_filter(
            df=pd.DataFrame({
                "address": ping_data["addr_btc"]
            }),
            db_filename=db.db_filename_all,
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
                df, db.db_filename_all)
            sum_size_legacy += size_legacy
            sum_size_segwit += size_segwit

        sum_records = sum_size_legacy + sum_size_segwit
        print(
            "\nStats\n"
            f"  size:\t{sum_records}/{lines} (= {sum_records/lines})\n"
            f"  hit:\t{sum_records/(2**128)}\n"
            f"  legacy:segwit = {sum_size_legacy}:{sum_size_segwit}"
            f" (= {str(sum_size_legacy/sum_records)
                   [:5]}:{str(sum_size_segwit/sum_records)[:5]})\n"
        )

        return sum_size_legacy, sum_size_segwit

    @ classmethod
    def filter_addr(cls, df):
        df_legacy = df.query(f"{cls.col_addr}.str.startswith('1')")
        df_segwit = df.query(f"{cls.col_addr}.str.startswith('bc1q')")
        return df_legacy, df_segwit

    @ classmethod
    def insert_with_filter(cls, df, db_filename):
        df_legacy, df_segwit = cls.filter_addr(df)

        cls.insert(
            df=df_legacy.copy(),
            db_filename=db_filename,
            tbl_name=cls.tbl_legacy,
        )
        cls.insert(
            df=df_segwit.copy(),
            db_filename=db_filename,
            tbl_name=cls.tbl_segwit,
        )
        return len(df_legacy), len(df_segwit)

    @ classmethod
    def format_tbl_name(cls, base, idx):
        return f"{base}{str(idx)}"

    @ classmethod
    def divide_tbl(cls, db, tbl_name_all, size):
        size_per_tbl = size // cls.dividend_length
        assert size_per_tbl > cls.dividend_length, "too much table"

        cur_all = db.conn_all.cursor()
        print(f"Dividing {tbl_name_all}...")
        cur_all.execute(
            f"SELECT * FROM {tbl_name_all} ORDER BY {cls.col_addr}{cls.sql_order};")

        tbl_index = []
        for i in tqdm(range(cls.dividend_length + 1)):
            rows = cur_all.fetchmany(size_per_tbl)
            df = pd.DataFrame({"address": [row[1] for row in rows]})
            cls.insert(
                df=df.copy(),
                db_filename=db.db_filename,
                tbl_name=cls.format_tbl_name(tbl_name_all, i),
                compress=True,
            )

            # memo the end as index
            tbl_index.append(df.iloc[len(df)-1]["address"])

        assert len(cur_all.fetchall()) == 0

        # save indices
        with open(f"{SAVE_DIR}/{tbl_name_all}.json", "w", encoding="utf-8") as f:
            f.write(json.dumps(tbl_index))

    @ classmethod
    def divide_tbl1(cls, db, tbl_name_all, size):
        size_per_tbl = size // cls.dividend_length
        assert size_per_tbl > cls.dividend_length, "too much table"

        cur_all = db.conn_all.cursor()
        print(f"Dividing {tbl_name_all}...")

        for i in tqdm(range(cls.dividend_length)):
            print(i)
            cur_all.execute(
                f"""
                SELECT * FROM {tbl_name_all}
                WHERE {cls.col_addr} % {cls.dividend_length} == {i}
                ORDER BY {cls.col_addr}{cls.sql_order};
            """)

            rows = cur_all.fetchall()
            df = pd.DataFrame({"address": [row[0] for row in rows]})
            cls.insert(
                df=df.copy(),
                db_filename=db.db_filename,
                tbl_name=cls.format_tbl_name(tbl_name_all, i),
            )

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
        # i = addr % self.dividend_length

        return DB.format_tbl_name(tbl_name, i)

    def search(self, addr):
        self.cur.execute(
            f"""
            SELECT * FROM {self.get_tbl_name(addr)} where {self.col_addr} = ?;
            """,
            (fn_compress(addr),),
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
