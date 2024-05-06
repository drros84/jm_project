FROM python:3.9.19-bookworm

COPY requirements.txt ./
COPY GenAdzunaJobs.py ./
COPY data_models.py ./
COPY utils.py ./
COPY GenHWJobs.py ./
COPY GenAllJobs.py ./

RUN pip install --no-cache-dir -r requirements.txt

