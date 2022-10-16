# This is a template for a Python scraper on morph.io (https://morph.io)
# including some code snippets below that you should find helpful

import pandas as pd
import sqlite3


df = pd.DataFrame([['c', 3, 'cat'], ['d', 4, 'dog']],
                   columns=['letter', 'number', 'animal'])

conn = sqlite3.connect('data.sqlite')
df.to_sql('data', conn, if_exists='replace')