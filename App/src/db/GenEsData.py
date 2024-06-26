"""

   @author: lnasri

"""




from elasticsearch import Elasticsearch

import json

from pathlib import Path

import os






def check_index_exists(es, index_name):

   return es.indices.exists(index=index_name)






def main():

   # Elasticsearch Configuration

   es = Elasticsearch("http://es-container:9200")

   # all_jobs file directory 

   all_jobs_path = [jobs_path for jobs_path in Path("/app/App/data/all_jobs").iterdir()]

   # Index name

   index_name = "adzuna_jobs"




   # Check if index exists

   if not check_index_exists(es, index_name):

       # Create index if it doesn't exist

       es.indices.create(index=index_name)




   # Browse the all_jobs file directory 

   for json_file in all_jobs_path:

       if os.path.exists(json_file):

           

           with open(json_file, encoding='utf-8') as file:

               data = json.load(file)

               for item in data:

                   # Check if data already exists in Elasticsearch

                   if es.exists(index=index_name, id=item['id']):

                       # Print Id if data already exists

                       print(json_file)

                       print(f"Données existantes pour l'ID {item['id']}")

                   else: 

                       try:

                           print(json_file)

                           print(f"Nouvelles données pour l'ID {item['id']}")

                           # Store data in Elasticsearch

                           es.index(index=index_name, id=item['id'], body=item)

                       except Exception as inst:

                           pass






if __name__ == '__main__':

   main()