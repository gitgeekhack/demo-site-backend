FROM python:3.9

WORKDIR /demo-site-backend

RUN apt-get update
RUN apt-get install tesseract-ocr python3-opencv libzbar0 -y

ADD ./app ./app
ADD ./requirements.txt ./requirements.txt
RUN pip install --upgrade pip==23.3
RUN pip install -r requirements.txt
RUN pip install gunicorn
ADD run.py ./run.py
ADD ./conf.py ./conf.py

EXPOSE 8001
CMD gunicorn -c conf.py app:app
#CMD python run.py