# This is a template for a Python scraper on morph.io (https://morph.io)
# including some code snippets below that you should find helpful

import pandas as pd
import sqlite3


# Read sqlite query results into a pandas DataFrame
conn = sqlite3.connect('data.sqlite')
df = pd.read_sql_query("SELECT * from data", conn)

# Verify that result of SQL query is stored in the dataframe
print(df.head())


df = pd.DataFrame([['c', 3, 'cat'], ['d', 4, 'dog']],
                   columns=['letter', 'number', 'animal'])

#conn = sqlite3.connect('data.sqlite')
df.to_sql('data', conn, if_exists='append')