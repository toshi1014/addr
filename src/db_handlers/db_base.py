import pandas as pd
from tqdm import tqdm


class DB:
    tbl_name = "addresses"
    col_addr = "address"

    def __init__(self):
        self.conn = None
        self.cur = None
        self.col_addr = DB.col_addr

    @classmethod
    def setup(cls, src_filename, ping_data, engine=None):
        db = cls()
        CHUNKSIZE = 10**5
        con_tmp = engine if engine else db.conn

        reader = pd.read_csv(
            src_filename,
            sep="\t",
            iterator=True,
            chunksize=CHUNKSIZE,
        )

        with open(src_filename, mode="r", encoding="utf-8") as f:
            lines = sum(1 for _ in f)

        for df in tqdm(reader, total=lines // CHUNKSIZE):
            df = cls.filter_addr(df)[cls.col_addr]
            df.to_sql(
                name=cls.tbl_name,
                con=con_tmp,
                if_exists="append",
                method="multi",
                chunksize=10*4,
            )

        # add address for ping
        ser = pd.Series(
            [ping_data["addr"]],
            name=cls.col_addr,
        )
        print("to_sql")
        ser.to_sql(
            name=cls.tbl_name,
            con=con_tmp,
            if_exists="append",
        )

        print("setup complete")

    @classmethod
    def filter_addr(cls, df):
        df_legacy = df.query(f"{cls.col_addr}.str.startswith('1')")
        df_segwit = df.query(f"{cls.col_addr}.str.startswith('bc1q')")
        return pd.concat([df_legacy, df_segwit])

    def insert(self, addr):
        self.cur.execute(
            f"""
            INSERT INTO {DB.tbl_name} ({self.col_addr}) values ('{addr}');
            """
        )
        self.conn.commit()

    def search(self, addr):
        self.cur.execute(
            f"""
            SELECT * FROM {DB.tbl_name} where {self.col_addr} = '{addr}';
            """
        )
        row = self.cur.fetchone()
        return row

    def find(self, addr):
        print("searching...")
        rtn = bool(self.search(addr))
        print("done")
        return rtn

    def __del__(self):
        self.conn.close()


# https://yuyuublog.com/executemany/
# * local db server, not py lib
# * check size
# engine = create_engine("mysql://scott:tiger@localhost/foo")
