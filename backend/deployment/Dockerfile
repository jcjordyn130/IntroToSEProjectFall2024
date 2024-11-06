FROM python:3.13-alpine
LABEL maintainer="onlinecloud1@gmail.com"
COPY IntroToSEProjectFall2024/backend /app
WORKDIR /app
RUN pip install -r requirements.txt
WORKDIR /
RUN python3 app/gendummydb.py
EXPOSE 5000
ENTRYPOINT ["python"]
CMD ["-m", "app.api.api"]
