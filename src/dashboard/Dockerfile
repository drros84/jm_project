FROM python:3.9.19-bookworm
#FROM jupyter/datascience-notebook

USER root

EXPOSE 9000

RUN apt-get update 

COPY requirements.txt ./
COPY dashboard.py ./
COPY dashboard_fcts.py ./
COPY 2018095159_strategie-de-recherche-d-emploi.png ./

RUN pip install --no-cache-dir -r requirements.txt



