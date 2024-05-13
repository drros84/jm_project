FROM python:3.12-slim
RUN apt-get update && apt-get install --assume-yes \
 cron \
 && rm -rf /var/lib/apt/lists/* 
 #Permet à Python d'afficher tout ce qui est imprimé dans l'application plutôt que de le mettre en mémoire tampon.
ENV PYTHONUNBUFFERED 1 
# RUN pip install elasticsearch requests python-dotenv pathlib
COPY /src/db/requirements.txt /app/App/src/db/requirements.txt
RUN pip install -r /app/App/src/db/requirements.txt

# RUN spacy download en_core_web_sm

#COPY /src/db/create_spacy_skills_model.py ./
#RUN python create_spacy_skills_model.py

COPY /src/db/crontab-ged /etc/cron.d/crontab-ged
RUN chmod 0644 /etc/cron.d/crontab-ged

RUN crontab /etc/cron.d/crontab-ged
RUN mkdir /var/log/logs
RUN touch /var/log/logs/cron.log

CMD /usr/sbin/cron start && tail -f /var/log/logs/cron.log