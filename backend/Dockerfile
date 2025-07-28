FROM python:3

ENV DD_SERVICE="notes-backend"
ENV DD_ENV="dev"
ENV DD_VERSION="0.1.0"
# references the postgres container
ENV DB_HOST="postgres-notes" 
ENV DB_PORT="5432"
ENV DB_NAME="notesdb"
ENV DB_USER="postgres"

LABEL com.datadoghq.tags.service="notes-backend"
LABEL com.datadoghq.tags.env="dev"
LABEL com.datadoghq.tags.version="0.1.0"

WORKDIR /home

COPY requirements.txt /home
COPY . /home

RUN pip install -r requirements.txt
# Run the application
CMD ["python", "app.py"] 
EXPOSE 5000