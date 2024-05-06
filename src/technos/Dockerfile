FROM python:3.9.19-bookworm

COPY requirements.txt ./
COPY techno_fcts.py ./
COPY Technos.py ./

RUN pip install --no-cache-dir -r requirements.txt

# RUN python Technos.py