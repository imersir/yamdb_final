FROM python:3.8
COPY ./ /yamdb_final
WORKDIR /yamdb_final/
RUN pip install --upgrade pip && pip install -r requirements.txt
