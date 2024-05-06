"""
    @author: Greg 
    @code-reviewer: lnasri
"""

from datetime import datetime
import json
import time
from typing import List
from bs4 import BeautifulSoup
import boto3
import pandas as pd
import requests
import os
from dotenv import load_dotenv
from techno_fcts import get_db_engines_ranking, get_github_frameworks, get_tiobe_top50, other_tech

load_dotenv()
USER_AGENT = os.getenv('USER_AGENT')

# Get AWS credentials
AWS_KEY_ID = os.getenv('AWS_KEY_ID')
AWS_SECRET = os.getenv('AWS_SECRET')

DB_ENGINES_URL = 'https://db-engines.com/en/ranking'
TIOBE_URL = 'https://www.tiobe.com/tiobe-index/'
GITHUB_SURVEY_URL = 'https://insights.stackoverflow.com/survey/2021#technology-most-popular-technologies'
OTHER_TECH = 'https://ecos-umons.github.io/catalogue-python/all'

if __name__ == '__main__':
    all_techs = get_db_engines_ranking()+get_github_frameworks()+get_tiobe_top50()+other_tech()
    all_techs = list(set(all_techs))
    ts = datetime.now().strftime("%Y-%m")

        # Connect to S3
    s3 = boto3.client('s3',
                      aws_access_key_id = AWS_KEY_ID,
                      aws_secret_access_key = AWS_SECRET)
    
    all_techs_dump = json.dumps(all_techs, indent=4, ensure_ascii = False)

    s3.put_object(
        Bucket = 'jmproject', 
        Key = f"Technos/github_web_fws4_{ts}",
        Body = all_techs_dump)
