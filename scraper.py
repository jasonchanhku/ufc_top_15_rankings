# This is a template for a Python scraper on morph.io (https://morph.io)
# including some code snippets below that you should find helpful

import requests
from bs4 import BeautifulSoup
import pandas as pd
import sqlite3

rankingsLink = 'https://www.ufc.com/rankings'

data = requests.get(rankingsLink)
soup = BeautifulSoup(data.text, 'html.parser')


segments = soup.find_all('div', {'class': 'view-grouping-content'}, href=False)   

excludeList = ["Men's Pound-for-Pound Top Rank", "Women's Pound-for-Pound Top Rank", "Women's Featherweight"]
dfList = []
for segment in segments:
    weightclass = segment.find('div', {'class': 'info'}).find('h4').text.strip()
    if weightclass in excludeList:
        continue
    subDf = pd.DataFrame()
    print(f"{weightclass} Top 15")
    fighters = segment.find_all('div', {'class':'views-row'})
    fighters = [fighter.text.strip() for fighter in fighters]
    print(fighters)
    print("==========\n")
    subDf['fighters'] = fighters
    subDf['weightclass'] = weightclass
    subDf['rank'] = [r for r in range(1, len(fighters)+1)]
    subDf = subDf[['weightclass','rank', 'fighters']]
    dfList.append(subDf)
    
        

finalDf = pd.concat(dfList)

print(finalDf.head())

conn = sqlite3.connect('data.sqlite')
finalDf.to_sql('data', conn, if_exists='replace')
print('UFC Fighters Rankings successfully scraped and updated')
conn.close()