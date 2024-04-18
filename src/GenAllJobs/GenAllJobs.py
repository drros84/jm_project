"""
@author: Greg 
@code-reviewer: lnasri

This module is created to obtain the URL of the
Hellowork page based on the Adzuna API response. 
If a Hellowork URL is available, a dumps is created 
containing all the Hellowork page information. 
Otherwise, dumps are generated from the Adzuna API data.

"""

import time
from GenAdzunaJobs import *
from GenHWJobs import * 
from data_models import *
from bs4 import BeautifulSoup
import numpy as np
from rich import print
from utils import *
from pathlib import Path
import boto3
import os
from dotenv import load_dotenv


def gen_jobs(adzuna_jobs_list, all_jobs_list):
    """In this function, we scan the azuna_jobs file directory, 
       then process a single file of 50 dumps.
       This process checks the existence of the hellowork url.

    Args:
        adzuna_jobs_list (list[str]): a list of file names in adzuna_jobs
        all_jobs_list (list[str]): a list of file names in all_jobs
                               

    Returns:
        tuple: liste of adzuna dumps, file name processed
    """
    

    # List of dictionaries, containing all adzuna api informations + 
    # Hellowork url + the name of the file to be processed
    adzuna_url_jobs = []

    # contains a single name from the azuna api json file
    adzuna_jobs_fname = []

    no_prefix_all_jobs = [job.removeprefix('all_jobs/') for job in all_jobs_list]
   
    #print(all_jobs_list)
    for i in adzuna_jobs_list:
        
        #if len(adzuna_jobs_fname) >= 1:
        #    break

        if i.removeprefix('adzuna_jobs/') not in no_prefix_all_jobs:
            adzuna_jobs_fname.append(i)
            
            # Read in the json file
            content_object = s3.get_object(Bucket = 'jmproject', Key = i)
            decoded_content = content_object['Body'].read().decode('utf-8')
            json_data_adzuna = json.loads(decoded_content)
            
            for data in json_data_adzuna:
                Id =  data['id']
                red_url = data["redirect_url"] 
                adzuna_url, is_redirected = forge_adzuna_url(red_url)
                print(is_redirected)
        
                if is_redirected == True:
                    # Requesting red_url to get the Job Board's page,
                    # Which is named hellowork_url as this is often the case.
                    cli = create_client()
                    resp = cli.get(red_url)
                    html = BeautifulSoup(resp.text, 'html.parser')
                    try:
                        ugly_url = (html
                                    .find_all('meta')
                                    [-1]
                                    .attrs['content']
                                    .split('https')
                                    [-1]
                                    )
                        hellowork_url = forge_hellowork_url(ugly_url)
                        print(hellowork_url)
                        print(f'[green]Step : Redirection - Both urls successfully generated[/green]')
                        # Temporizing before next request
                        pause = 3 + 4 * np.random.rand()
                        print(f'\t[yellow]Gonna wait for {pause:.1f} seconds...')
                        time.sleep(pause)
                    except BaseException as e:
                        print(f'[red]Step : Exception {type(e)} for url {red_url}[/red]')
                        hellowork_url = None
                else:
                    print(f'[#F3B664]Step : No redirection - Only adzuna_url generated[/#F3B664]')
                    hellowork_url = None
                
                adzuna_url_jobs.append({
                'id': Id,
                'hellowork_url': hellowork_url,
                'file_name' : i,
                'title': data["title"] ,
                'redirect_url': data["redirect_url"] ,
                'company': data["company"] ,
                'created': data["created"] ,
                'area': data["area"] ,
                'latitude': data["latitude"] ,
                'longitude': data["longitude"] ,
                'location': data["location"] ,
                'contract': data["contract"] ,
                'education': None,
                'duration' :None,
                'remote' : None,
                'experience': None,
                'salary_min': data["salary_min"] ,
                'salary_max': data["salary_max"] ,
                'salary' :None,
                'salary_min_e' : None,
                'salary_med_e' :None,
                'salary_max_e' :None,
                'description': data["description"] 
                })
                
                     
    return adzuna_url_jobs, adzuna_jobs_fname
       
        
if __name__ == "__main__":

    # Get AWS credentials
    load_dotenv()
    AWS_KEY_ID = os.getenv('AWS_KEY_ID')
    AWS_SECRET = os.getenv('AWS_SECRET')
    
    # Connect to S3
    s3 = boto3.client('s3',
                      aws_access_key_id = AWS_KEY_ID,
                      aws_secret_access_key = AWS_SECRET)
    
    # List elements in the adzuna_jobs s3 folder
    adzuna_jobs_find = s3.list_objects(Bucket = 'jmproject', Prefix = 'adzuna_jobs')
    adzuna_jobs_list = [job['Key'] for job in adzuna_jobs_find['Contents']] 
    
    # List elements in the adzuna_jobs s3 folder
    all_jobs_find = s3.list_objects(Bucket = 'jmproject', Prefix = 'all_jobs')
    all_jobs_list = [job['Key'] for job in all_jobs_find['Contents']]

    jobs, file_name = gen_jobs(adzuna_jobs_list, all_jobs_list)
    #
    liste_all_data = []
    
    for data in jobs:
        Id =  data['id']
        hellowork_url = data["hellowork_url"]  
        if IsValidHwUrl(hellowork_url).eq_netloc():
            model = scrape_hw_page(Id, hellowork_url, data)
            # print(model)
            if model is not None:
                liste_all_data.append(model.model_dump())
                time.sleep(2)
        else:
            liste_all_data.append(data)

    for name in file_name:
        temp_data = [data for data in liste_all_data if data['file_name'] == name]
        temp_data_dump = json.dumps(temp_data, indent=4, ensure_ascii = False)
        no_prefix_name = name.removeprefix('adzuna_jobs/')
        s3.put_object(
            Bucket = 'jmproject', 
            Key = f"all_jobs/{no_prefix_name}",
            Body = temp_data_dump)
    

             















