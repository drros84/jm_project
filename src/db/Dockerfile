FROM python:3.9.19-bookworm

USER root

RUN apt-get update 

COPY requirements.txt ./
COPY create_spacy_skills_model.py ./
COPY GenEsData.py ./

RUN pip install --no-cache-dir -r requirements.txt

RUN spacy download en

# RUN python create_spacy_skills_model.py
# RUN python GenEsData.py
