import glob
import os


def concat_df(src_dirname, out_filename):
    if os.path.exists(out_filename):
        os.remove(out_filename)

    with open(out_filename, "a") as f:
        f.write(",address\n")

        for file in glob.glob(src_dirname + "/out?.eth.csv"):
            print(file)
            with open(file, "r") as f2:
                f.write(f2.read())


concat_df(
    src_dirname="addr_csv",
    out_filename="addr_csv/addr_list.eth.csv",
)
