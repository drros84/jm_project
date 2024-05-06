
from elasticsearch import Elasticsearch
import boto3
import json
from datetime import datetime
import os
from dotenv import load_dotenv
import pandas as pd

load_dotenv()
AWS_KEY_ID = os.getenv('AWS_KEY_ID')
AWS_SECRET = os.getenv('AWS_SECRET')

def get_latest_technos():

    """
    Read in the file with the latest list of technologies from an S3 bucket.
    """

    # Connect to S3
    s3 = boto3.client('s3',
                  aws_access_key_id = AWS_KEY_ID,
                  aws_secret_access_key = AWS_SECRET)

    # List elements in the Technos folder
    bucket_list = s3.list_objects(Bucket='jmproject', Prefix='Technos')

    # Get the key names for files in the all_jobs folder
    file_keys = [job['Key'] for job in bucket_list['Contents']]

    # Get the dates (year-month) for each techno file
    file_dates = [datetime.strptime(file[-7:], '%Y-%m') for file in file_keys]

    # Select the file with the latest date
    latest_file = file_keys[file_dates == max(file_dates)]

    # Read in and parse the file with the latest technologies
    s3_object = s3.get_object(Bucket = 'jmproject', Key = latest_file)
    decoded_content = s3_object['Body'].read().decode('utf-8')
    
    return json.loads(decoded_content)

def get_tech_stats(elasticsearch_connexion: Elasticsearch,
                   tech: str):

    """
    Get frequency of technologies within job vacancy descriptions
    """

    query_str = {
        "query": {
            "match": {
                "description": tech
                }
            },
        "size": 0,
        "aggs": {
            "avg_min_wage": {
                "avg": {
                    "field": "salary_min"
                    }
                },
            "avg_max_wage": {
                "avg": {
                    "field": "salary_max"
                    }
                }
            }
        }

    resp = elasticsearch_connexion.search(index = 'adzuna_jobs', body = query_str)

    tech_frequency = resp['hits']['total']['value']
    avg_min_wage = resp['aggregations']['avg_min_wage']['value']
    avg_max_wage = resp['aggregations']['avg_max_wage']['value']

    return {'tech': tech, 'frequency': tech_frequency, 'avg_min_wage': avg_min_wage, 'avg_max_wage': avg_max_wage}


def query_index(elasticsearch_connexion: Elasticsearch,
                query_term: str,
                field_name: str,
                index_name: str = 'adzuna_jobs'):
    """
    A function to count the number of documents in a given elasticsearch index that contains a specific string
    """
    my_query = {
        "match": {
            field_name: {
                "query": query_term
                }
        }
    }

    resp = elasticsearch_connexion.search(index = index_name, query = my_query)

    documents = []
    for hit in resp['hits']['hits']:
        documents.append(hit['_source'])


    # dataframe
    df = pd.DataFrame(documents)

    return df