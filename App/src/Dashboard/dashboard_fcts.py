
from elasticsearch import Elasticsearch
import json

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