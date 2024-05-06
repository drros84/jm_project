
import json
import spacy
import boto3
import json
from datetime import datetime
import os
from dotenv import load_dotenv

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

# tech_list = ['C++', 'C', 'Javascript', 'Java', 'SQL', 'R', 'Python']
latest_technos = get_latest_technos()

patterns = []
for x in latest_technos:
    patterns.append({"label": "PROG_LANG", "pattern": x, "id": "SKILLS"})

nlp = spacy.load("en_core_web_sm")
ruler = nlp.add_pipe("entity_ruler", before="ner")
ruler.add_patterns(patterns)
ruler.to_disk("tech_lang_patterns.jsonl")