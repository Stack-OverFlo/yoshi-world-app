FROM docker.io/library/python:3.14 as buildPython

WORKDIR /app

COPY app/server.py .

RUN useradd --create-home yoshi

EXPOSE 8080

USER yoshi

CMD ["python", "server.py"]
