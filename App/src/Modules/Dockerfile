FROM python:3.12-slim
RUN apt-get update && apt-get install --assume-yes \
 cron \
 && rm -rf /var/lib/apt/lists/* 
#Permet à Python d'afficher tout ce qui est imprimé dans l'application plutôt que de le mettre en mémoire tampon.
ENV PYTHONUNBUFFERED 1 

# RUN pip install elasticsearch requests python-dotenv pathlib bs4 rich httpx  pydantic typing numpy
COPY /src/Modules/requirements.txt /app/App/src/Modules/requirements.txt
RUN pip install -r /app/App/src/Modules/requirements.txt
COPY /src/Modules/crontab-jobs /etc/cron.d/crontab-jobs
RUN chmod 0644 /etc/cron.d/crontab-jobs

RUN crontab /etc/cron.d/crontab-jobs

RUN mkdir /var/log/logs
RUN touch /var/log/logs/cron.log

CMD /usr/sbin/cron start && tail -f /var/log/logs/cron.log