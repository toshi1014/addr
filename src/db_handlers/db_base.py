import json
import pandas as pd
from tqdm import tqdm


CHUNKSIZE = 10**5


class DB:
    tbl_legacy = "tbl_legacy"
    tbl_segwit = "tbl_segwit"
    col_addr = "address"
    dividend_lengh = 100

    def __init__(self):
        self.conn = None
        self.cur = None
        self.col_addr = DB.col_addr

    @classmethod
    def setup(cls, src_filename, ping_data, engine=None):
        db = cls()
        params_to_sql = {
            "con": engine if engine else db.conn,
            "if_exists": "append",
            "index": False,
            "method": "multi",
            "chunksize": 10*4,
        }
        cls.insert_all(src_filename, ping_data, params_to_sql)
        cls.divide_tbl(db, cls.tbl_legacy, params_to_sql)
        cls.divide_tbl(db, cls.tbl_segwit, params_to_sql)
        print("\nSetup complete")

    @classmethod
    def insert_all(cls, src_filename, ping_data, params_to_sql):
        # insert address for ping
        cls.insert_with_filter(
            df=pd.DataFrame({
                "address": [ping_data["addr_legacy"], ping_data["addr_segwit"]]
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

        sum_records = 0
        for df in tqdm(reader, total=lines // CHUNKSIZE):
            size = cls.insert_with_filter(df, params_to_sql)
            sum_records += size

        print("\nStats")
        print(f"  size:\t{sum_records}/{lines} (= {sum_records/lines})")
        print(f"  hit:\t{sum_records/(2**128)}\n")

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
        return len(df_legacy) + len(df_segwit)

    @classmethod
    def divide_tbl(cls, db, tbl_name_all, params_to_sql):
        cur = db.conn.cursor()
        print(f"Dividing {tbl_name_all}...")
        cur.execute(f"SELECT * FROM {tbl_name_all} ORDER BY {cls.col_addr};")
        row_all = cur.fetchall()
        size_per_tbl = len(row_all) // cls.dividend_lengh

        tbl_index = []
        for i in tqdm(range(cls.dividend_lengh)):
            rows = row_all[i*size_per_tbl:(i+1)*size_per_tbl]
            df = pd.DataFrame({"address": [row[0] for row in rows]})
            cls.insert(
                df=df,
                tbl_name=tbl_name_all + str(i),
                params_to_sql=params_to_sql,

            )

            # memo the end as index
            tbl_index.append(df.iloc[len(df)-1]["address"])

        last_rows = row_all[(i+1)*size_per_tbl:]
        df = pd.DataFrame({"address": [row[0] for row in last_rows]})
        cls.insert(
            df=df,
            tbl_name=tbl_name_all + str(i),
            params_to_sql=params_to_sql,

        )

        # save indices
        with open(f"{tbl_name_all}.json.tmp", "w", encoding="utf-8") as f:
            f.write(json.dumps(tbl_index))

    def prepare_index(self):
        with open(f"tbl_legacy.json.tmp", "r", encoding="utf-8") as f:
            self.idx_tbl_legacy = json.loads(f.read())
        with open(f"tbl_segwit.json.tmp", "r", encoding="utf-8") as f:
            self.idx_tbl_segwit = json.loads(f.read())

    def get_tbl_name(self, addr):
        idx_tbl_xxx, tbl_name = (self.idx_tbl_legacy, DB.tbl_legacy) \
            if addr[0] == "1" else (self.idx_tbl_segwit, DB.tbl_segwit)

        for i, idx in enumerate(idx_tbl_xxx):
            if idx > addr:
                return tbl_name + str(i)

        return tbl_name + str(i+1)

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
