# This is a template for a Python scraper on morph.io (https://morph.io)
# including some code snippets below that you should find helpful

import requests
from bs4 import BeautifulSoup
import pandas as pd
import sqlite3
import os
import fuzzymatcher

mainLink = 'https://www.ufc.com'

rankingsLink = mainLink + '/rankings'

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
    fightersLink = [mainLink + fighter.find('a', href=True)['href'] for fighter in fighters]
    fightersImg = []
    fightersNickName = []
    fightersRecord = []
    fightersWins = []
    fightersLoses = []
    fightersDraws = []
    for fighterpage in fightersLink:
        fighterData = requests.get(fighterpage)
        fighterSoup = BeautifulSoup(fighterData.text, 'html.parser')
        src = fighterSoup.find('div', {'class':'hero-profile__image-wrap'}).find('img')['src']
        nickName = fighterSoup.find('p', {'class':'hero-profile__nickname'})
        if nickName is None:
            nickName = 'N/A'
        else:
            nickName = nickName.text.strip()
        record = fighterSoup.find('p', {'class':'hero-profile__division-body'}).text.strip().split(' ')[0]
        fightersRecord.append(record)
        record = record.split('-')
        if len(record) == 3:
            wins = record[0]
            loss = record[1]
            draw = record[2]
        else:
            wins = record[0]
            loss = record[1]
            draw = '0'
            
        fightersImg.append(src)
        fightersNickName.append(nickName)
        fightersWins.append(wins)
        fightersLoses.append(loss)
        fightersDraws.append(draw)
        
    fighters = [fighter.text.strip() for fighter in fighters]
    print(fighters)
    print("==========\n")
    subDf['fighters'] = fighters
    subDf['nickName'] = fightersNickName
    subDf['record'] = fightersRecord
    subDf['wins'] = fightersWins
    subDf['losses'] = fightersLoses
    subDf['draws'] = fightersDraws
    subDf['weightclass'] = weightclass
    subDf['rank'] = [r for r in range(1, len(fighters)+1)]
    subDf['img'] = fightersImg
    subDf = subDf[['weightclass','rank', 'fighters','nickName','record','wins', 'losses', 'draws', 'img']]
    dfList.append(subDf)
    
    
finalDf = pd.concat(dfList)
finalDf = finalDf.reset_index().rename(columns={'index':'_id'})

conn = sqlite3.connect(':memory:')
cur = conn.cursor()
conn.enable_load_extension(True)

for (val,) in cur.execute('pragma compile_options'): 
    print (val)
    

# We're always asking for json because it's the easiest to deal with
morph_api_url = "https://api.morph.io/jasonchanhku/ufc_fighters_db/data.json"

# Keep this key secret using morph secret variables
morph_api_key = os.environ['MORPH_API_KEY']

r = requests.get(morph_api_url, params={
  'key': morph_api_key,
  'query': "select * from data"
})

j = r.json()
    
# fighters db dataset to me merged
fighters_db = pd.DataFrame.from_dict(j)

fighters_db.drop(['index'], axis=1, inplace=True)

fighters_db = fighters_db[['NAME','Age', 'Height', 'REACH', 'SLPM', 'SAPM', 'STRD', 'TD', 'TDA', 'TDD', 'SUBA']]

fighters_db.columns = [c.lower() for c in fighters_db.columns]

matched_df = fuzzymatcher.fuzzy_left_join(finalDf, fighters_db, left_on = "fighters", right_on = "name")

print(matched_df.head())

print(matched_df.isna().sum())

conn = sqlite3.connect('data.sqlite')
matched_df.to_sql('data', conn, if_exists='replace')
print('UFC Fighters Rankings successfully scraped and updated')
conn.close()