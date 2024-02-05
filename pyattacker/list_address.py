import glob
import pandas as pd


def concat_df(src_dirname, out_filename):
    with open(out_filename, "w") as f:
        f.write(",address\n")

    with open(out_filename, "a") as f:
        for file in glob.glob(src_dirname + "/*.csv"):
            df_tmp = pd.read_csv(file)
            ctx_csv = df_tmp.to_csv(index=False, header=False)
            f.write(ctx_csv)


concat_df(
    src_dirname="eth_addr_csv",
    out_filename="addr_list.eth.csv",
)
