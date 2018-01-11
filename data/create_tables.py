import os
import pandas as pd
from sqlalchemy import create_engine


def write_zips_to_sql():
    df = pd.read_table('zip_codes.txt', sep="\t", header=None)
    df.rename(columns={1: "zip", 9: "latitude", 10: "longitude"}, inplace=True)
    df[["zip", "latitude", "longitude"]].to_sql("zip_codes", engine)


def write_csvs_to_sql(f):
    df = pd.read_csv(f, encoding="ISO-8859-1")
    table_name = f.split(".")[0]
    df.to_sql(table_name, engine)


if __name__ == '__main__':
    engine = create_engine('postgresql://mengeling:mengeling@localhost:5432/silvercar')
    for f in os.listdir('.'):
        if (f.endswith(".csv")) & (f != "CCI.csv"):
            write_csvs_to_sql(f)
    write_zips_to_sql()
