import os
import pandas as pd
import sqlalchemy
import sqlite3
from tqdm import tqdm


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

    #  tbl size   itr/sec
    #  5000 000   600
    # 10000 000   420
    # 16000 000   400
    # 80000 000   100

    def __init__(self, tbl_last_digits):
        self.conn = None
        self.cur = None
        self.col_addr = DB.col_addr

        self.tbl_last_digits = tbl_last_digits

        if not os.path.exists(SAVE_DIR):
            os.makedirs(SAVE_DIR)

    @classmethod
    def get_params_to_sql(cls, engine):
        return {
            "con": engine,
            "if_exists": "append",
            "index": False,
            "method": "multi",
            "chunksize": 10*4,
        }

    @classmethod
    def init_engine(cls, db_filename, tbl_names, index):
        print(f"Init {db_filename}...")

        engine = sqlalchemy.create_engine(f"sqlite:///{db_filename}")
        metadata = sqlalchemy.MetaData()
        for tbl_name in tbl_names:
            table = sqlalchemy.Table(
                tbl_name,
                metadata,
                sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
                sqlalchemy.Column("address", sqlalchemy.BLOB, index=index),
            )
        metadata.create_all(engine)
        return engine, metadata

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

    def setup_eth(self, src_filename, ping_data, force_all=True):
        with open(src_filename, mode="r", encoding="utf-8") as f:
            lines = sum(1 for _ in f if _.strip() != "")
        lines -= 1  # remove header

        if force_all:
            engine_all, metadata = self.init_engine(
                db_filename=self.db_filename_all,
                tbl_names=[self.tbl_eth],
                index=False,
            )

            self.insert(
                engine=engine_all,
                df=pd.DataFrame({"address": ping_data["addr_eth"]}).copy(),
                tbl_name=self.tbl_eth,
            )

            reader = pd.read_csv(
                src_filename,
                iterator=True,
                chunksize=CHUNKSIZE,
            )
            for df in tqdm(reader, total=lines // CHUNKSIZE):
                df = df.dropna().rename(columns={1: "address"})[["address"]]
                self.insert(
                    engine=engine_all,
                    df=df.map(lambda x: x.lower()).copy(),        # lower
                    tbl_name=self.tbl_eth,
                )

            print("indexing...")
            tbl_eth = metadata.tables[self.tbl_eth]
            index = sqlalchemy.Index("idx_address", tbl_eth.c.address)
            index.create(engine_all)

        print(
            "\nStats\n"
            f"  size:\t{lines}\n"
            f"  hit:\t{lines/(2**128)}\n"
        )

        self.divide_tbl(lines + len(ping_data["addr_eth"]))

        print("ETH setup complete")

    @classmethod
    def insert(cls, engine, df, tbl_name, compress=False):
        params_to_sql = cls.get_params_to_sql(engine)

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
            f" (= {str(sum_size_legacy/sum_records)[:5]}:{str(sum_size_segwit/sum_records)[:5]})\n"  # noqa
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
            engine=None,
            df=df_legacy.copy(),
            tbl_name=cls.tbl_legacy,
        )
        cls.insert(
            engine=None,
            df=df_segwit.copy(),
            tbl_name=cls.tbl_segwit,
        )
        return len(df_legacy), len(df_segwit)

    @ classmethod
    def format_tbl_name(cls, base, idx):
        return f"{base}{str(idx)}"

    def divide_tbl(self, size):
        for digits in range(1, self.tbl_last_digits + 1):
            dividend_length = 16**digits
            if digits == 1:
                db_read = self.db_filename_all
                cur_read = self.conn_all.cursor()
            else:
                db_read = self.db_filename.format(suffix=digits-1)
                cur_read = sqlite3.connect(db_read).cursor()

            engine, _ = self.init_engine(
                db_filename=self.db_filename.format(suffix=digits),
                tbl_names=[
                    self.format_tbl_name(self.tbl_eth, i)
                    for i in range(dividend_length)
                ],
                index=True,
            )

            print(f"Dividing {db_read} into {16**digits}...")

            sum_record = 0
            for i in tqdm(range(dividend_length)):
                tbl_read_suf = "" if digits == 1 else i % (
                    16 ** (digits - 1))
                cmd = f"""
                    SELECT * FROM {self.format_tbl_name(self.tbl_eth, tbl_read_suf)}
                    WHERE substr(address, -{digits}) = '{hex(i)[2:].zfill(digits)}'
                    ORDER BY {self.col_addr}{self.sql_order};
                    """

                cur_read.execute(cmd)
                rows = cur_read.fetchall()
                df = pd.DataFrame({"address": [row[1] for row in rows]})

                is_valid = df.address.apply(
                    lambda addr: (int(addr, 16) % dividend_length) == i
                )
                assert is_valid.all(), "dividing_tbl err"

                sum_record += len(df)

                self.insert(
                    engine=engine,
                    df=df.copy(),
                    tbl_name=self.format_tbl_name(self.tbl_eth, i),
                    compress=digits == self.tbl_last_digits,
                )

            assert size == sum_record, f"size error\t{size} != {sum_record}"

    def get_tbl_name(self, addr):
        if addr[:2] == "0x":
            tbl_name = DB.tbl_eth
        elif addr[0] == "1":
            tbl_name = DB.tbl_legacy
        else:
            tbl_name = DB.tbl_segwit

        address_int = int(addr[(-self.tbl_last_digits):], 16)
        i = address_int % (16**self.tbl_last_digits)
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
