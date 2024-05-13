FROM python:3.12-slim
RUN apt-get update && apt-get install --assume-yes \
 cron \
 && rm -rf /var/lib/apt/lists/* 
 #Permet à Python d'afficher tout ce qui est imprimé dans l'application plutôt que de le mettre en mémoire tampon.
ENV PYTHONUNBUFFERED 1 
# RUN pip install elasticsearch requests python-dotenv pathlib \
#   dash pillow pandas numpy folium gunicorn dash-bootstrap-components
COPY /src/Dashboard/requirements.txt /app/App/src/Dashboard/requirements.txt
RUN pip install -r /app/App/src/Dashboard/requirements.txt

COPY /src/Dashboard/crontab-dash /etc/cron.d/crontab-dash
RUN chmod 0644 /etc/cron.d/crontab-dash

RUN crontab /etc/cron.d/crontab-dash
RUN mkdir /var/log/logs
RUN touch /var/log/logs/cron.log

EXPOSE 8050
# CMD ["gunicorn", "-b", "0.0.0.0:8050", "--reload", ":server"]
#  CMD ["python", "/app/App/src/Dashboard/app.py"]

CMD /usr/sbin/cron start && tail -f /var/log/logs/cron.log
