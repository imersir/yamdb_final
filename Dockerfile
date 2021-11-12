FROM python:3.8.5
COPY ./ /yamdb_final
WORKDIR /yamdb_final/
RUN pip install --upgrade pip && pip install -r requirements.txt