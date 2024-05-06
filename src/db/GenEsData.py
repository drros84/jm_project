"""
    @author: lnasri
"""

from elasticsearch import Elasticsearch
import json
from pathlib import Path
import os
import spacy
import boto3
from dotenv import load_dotenv
import time

load_dotenv()
AWS_KEY_ID = os.getenv('AWS_KEY_ID')
AWS_SECRET = os.getenv('AWS_SECRET')

# Load spacy model for recognising skills
nlp = spacy.load("en_core_web_sm")
ruler = nlp.add_pipe("entity_ruler", before="ner")
ruler.from_disk("tech_lang_patterns.jsonl")


def check_index_exists(es, index_name):
    return es.indices.exists(index=index_name)


def main():
    # Elasticsearch Configuration
    es = Elasticsearch(hosts = "http://elasticsearch:9200")

    # Connect to S3
    s3 = boto3.client('s3',
                  aws_access_key_id = AWS_KEY_ID,
                  aws_secret_access_key = AWS_SECRET)

    # List elements in the all_jobs folder
    bucket_list = s3.list_objects(Bucket='jmproject', Prefix='all_jobs')
    
    # Get the key names for files in the all_jobs folder
    file_keys = [job['Key'] for job in bucket_list['Contents']]
    
    # Index name
    index_name = "adzuna_jobs"

    # Check if index exists
    if not check_index_exists(es, index_name):
        # Create index if it doesn't exist
        es.indices.create(index=index_name)

    # Browse the all_jobs file directory 
    for job_key in file_keys:

        # Read in the json file
        content_object = s3.get_object(Bucket = 'jmproject', Key = job_key)
        decoded_content = content_object['Body'].read().decode('utf-8')
        data = json.loads(decoded_content)
        
        for item in data:
            # Check if data already exists in Elasticsearch
            if es.exists(index=index_name, id=item['id']):
                # Print Id if data already exists
                print(f"Données existantes pour l'ID {item['id']}")
            else: 
                print(f"Nouvelles données pour l'ID {item['id']}")

                #Identify coding skills in the text
                job_desc = item['description']
                if isinstance(job_desc, list):
                    job_desc = ' '.join(job_desc)
                doc = nlp(job_desc)
                ents = [{'label': entity.label_, 'text': entity.text} for entity in doc.ents if entity.ent_id_ == 'SKILLS']
                item['skills'] = [ent['text'] for ent in ents]

                # title_stop_words = ['(it)', 'h/f', 'f/h', '(h/f)', '(f/h)']
                # clean_title = item['title'].lower().split(' ')
                # clean_title = [word for word in clean_title if word not in title_stop_words]
                # item['clean_title'] = ' '.join(clean_title).capitalize()

                # Store data in Elasticsearch
                es.index(index=index_name, id=item['id'], body=item)


if __name__ == '__main__':
    main()
    