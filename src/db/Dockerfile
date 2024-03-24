FROM jupyter/datascience-notebook

USER root

RUN apt-get update && apt-get -y install cron

COPY requirements.txt ./
COPY create_spacy_skills_model.py ./
COPY GenEsData.py ./
COPY crontab ./

RUN pip install --no-cache-dir -r requirements.txt

RUN spacy download en

RUN python create_spacy_skills_model.py

RUN sudo service cron status
RUN sudo service cron start
RUN crontab -l