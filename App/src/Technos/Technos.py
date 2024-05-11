
"""
    @author: Greg 
    @code-reviewer: lnasri
"""

from datetime import datetime
import json
import time
from typing import List
from bs4 import BeautifulSoup
import pandas as pd
import requests

DB_ENGINES_URL = 'https://db-engines.com/en/ranking'
TIOBE_URL = 'https://www.tiobe.com/tiobe-index/'
GITHUB_SURVEY_URL = 'https://insights.stackoverflow.com/survey/2021#technology-most-popular-technologies'
OTHER_TECH = 'https://ecos-umons.github.io/catalogue-python/all'

# USER-AGENT - Maybe import it too
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)\
    AppleWebKit/537.36 (KHTML, like Gecko)\
        Chrome/116.0.0.0 Safari/537.36'

def other_tech():
    resp = requests.get(OTHER_TECH, headers={'User-Agent': USER_AGENT})
    # Manage requests issues
    if resp.status_code != 200:
        print(f"AN ERROR OCCURED: {resp.reason}")

    # Scraping
    html = BeautifulSoup(resp.text, 'html.parser')
    liste_other = []
    if html.find('article') is not None:
        # Extract Education and Experience informations
        text_edu_exp = html.find_all('h2')
        for i in text_edu_exp:
            liste_other.append(i.text)
    return liste_other

def get_db_engines_ranking() -> List[str]:
    """
    Get db engines ranking for database usage.
    Params
    ------
        `export`: str
            'csv' or 'json' to set the export type,
            the file will be saved in the data folder.
    Returns
    -------
        A list of strings of databases' names.
    """
    # Loading all tables from the page
    tables = pd.read_html(DB_ENGINES_URL)
    # Preprocessing
    ranking = (tables[3]
               .rename(columns={3: 'DataBase'})
               .loc[3:, 'DataBase']
               .str.replace(' Detailed vendor-provided information available', '')
               .reset_index(drop=True)
              )
    ranking_list = ranking.to_list()
    
    return ranking_list

def get_tiobe_top50() -> List[str]:
    """
    Get Tiobe's monthly ranking for programming languages.
    Params
    ------
        `export`: str
            'csv' or 'json' to set the export type,
            the file will be saved in the data folder.
    Returns
    -------
        A list of strings of languages' names.
    """
    # Scrape tables
    tiobe_tables = pd.read_html(TIOBE_URL)
    # Get top 20 then 21-50
    tiobe_top20 = (tiobe_tables[0]
               .rename(columns={'Programming Language.1': 'Language'})
               ['Language']
              )
    tiobe_21_50 = (tiobe_tables[1]
               .rename(columns={'Programming Language': 'Language'})
               ['Language']
              )
    # Merging and preprocessing for next text searches
    tiobe_top50 = (pd
                   .concat([tiobe_top20, tiobe_21_50])
                  )
    tiobe_top50_list = tiobe_top50.to_list()

    return tiobe_top50_list 

def get_github_frameworks():
    """
    Get names of web most popular frameworks from GitHub survey.
    Params
    ------
        `web`: bool (default: True)
            specify if you want web frameworks or not.
        `export`: bool (default: True)
            specifiy if a dump is required or not,
            it will be saved in the config_data folder.
    Returns
    -------
        A list of strings with the frameworks' names.
    """
    resp = requests.get(GITHUB_SURVEY_URL, headers={'User-Agent': USER_AGENT})
    # Manage requests issues
    if resp.status_code != 200:
        print(f"AN ERROR OCCURED: {resp.reason}")
        return []
        
    # Scraping
    html = BeautifulSoup(resp.text, 'html.parser')
    # fw_type = 'webframe' if web else 'misc-tech'
    liste = []
    
    fw_type = ['tools-tech', 'webframe' , 'misc-tech']
    for i in fw_type:
        # print(i)
        tags = (html
                .find('figure', {'id': f'most-popular-technologies-{i}'}) 
                .find('table', {'id': i})
                .find_all('td', {'class': 'label'}))
        # print('tags', tags)
        liste.append(tags)
    # print('liste', liste)
    liste1 = []
    for j in liste:
        [liste1.append(tag.text.strip()) for tag in j]
    print(liste1)

    # Split records containing '/'
    cleaned_fws = []
    
            
    return liste1


if __name__ == '__main__':
    all_techs = get_github_frameworks()
    ts = datetime.now().strftime("%Y-%m")
    path = '/home/lynda/Ln-project/App/data/Technos/pf' 
    
    json_path = f'{path}.json'
    
    with open(json_path, 'w', encoding='utf-8') as dump_file:
        # `ensure_ascii` to force display of non-ascii characters
        json.dump(all_techs, dump_file, indent=4, ensure_ascii=False)
        
        