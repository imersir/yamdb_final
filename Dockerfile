FROM python:3.8.5
WORKDIR /yamdb_final/
COPY . /yamdb_final
RUN pip install --upgrade pip && pip install -r requirements.txt