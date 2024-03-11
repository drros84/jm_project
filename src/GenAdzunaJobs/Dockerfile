FROM jupyter/datascience-notebook

COPY requirements.txt ./
COPY GenAdzunaJobs.py ./
COPY data_models.py ./
COPY utils.py ./

RUN pip install --no-cache-dir -r requirements.txt

