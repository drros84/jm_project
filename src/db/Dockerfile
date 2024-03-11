FROM jupyter/datascience-notebook

USER root

RUN apt-get update && apt-get -y install cron

COPY requirements.txt ./
COPY GenEsData.py ./
COPY cron_file ./

RUN pip install --no-cache-dir -r requirements.txt

RUN chmod 0644 cron_file

RUN crontab cron_file

CMD cron 