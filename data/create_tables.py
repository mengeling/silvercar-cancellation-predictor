import os
import pandas as pd
from sqlalchemy import create_engine


def write_to_sql(f):
    df = pd.read_csv(f, encoding="ISO-8859-1")
    table_name = f.split(".")[0]
    df.to_sql(table_name, engine)


if __name__ == '__main__':
    engine = create_engine('postgresql://mengeling:mengeling@localhost:5432/silvercar')
    for f in os.listdir('.'):
        if (f.endswith(".csv")) & (f != "CCI.csv"):
            write_to_sql(f)
