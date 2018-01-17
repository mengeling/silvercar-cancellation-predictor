import os
import sys
import pandas as pd
from sqlalchemy import create_engine


sys.path.append('../model')
import constants as C


def write_zips_to_sql():
    df = pd.read_table('zip_codes.txt', sep="\t", header=None)
    df.rename(columns={1: "zip", 9: "latitude", 10: "longitude"}, inplace=True)
    df[["zip", "latitude", "longitude"]].to_sql("zip_codes", engine, if_exists="replace")


def write_csvs_to_sql(f):
    df = pd.read_csv(f, encoding="ISO-8859-1")
    table_name = f.split(".")[0]
    df.to_sql(table_name, engine, if_exists="replace")


if __name__ == '__main__':
    engine = create_engine(C.ENGINE)
    for f in os.listdir('.'):
        if f.endswith(".csv"):
            write_csvs_to_sql(f)
    write_zips_to_sql()
