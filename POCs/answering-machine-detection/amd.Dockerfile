FROM python:3.8

WORKDIR /answering-machine-detection

RUN apt-get update

ENV ENVIRONMENT=staging
ADD ./app ./app
ADD ./requirements.txt ./requirements.txt
RUN pip install --upgrade pip==23.3
RUN pip install -r requirements.txt
RUN pip install gunicorn
ADD ./run_dev_server.py ./run.py
ADD ./conf.py ./conf.py

EXPOSE 8082
CMD gunicorn -c conf.py app:app
#CMD python run.py
