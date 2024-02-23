FROM python:3.9

WORKDIR /underwriting-automation

RUN apt-get update
RUN apt-get install tesseract-ocr python3-opencv libzbar0 -y

ENV ENVIRONMENT=development
ADD ./app ./app
ADD ./requirements.txt ./requirements.txt
RUN pip install --upgrade pip==23.3
RUN pip install -r requirements.txt
RUN pip install gunicorn
ADD ./run_underwriting_automation.py ./run.py
ADD ./conf.py ./conf.py
ADD ./log.conf ./log.conf

EXPOSE 8000
CMD gunicorn -c conf.py app:app
#CMD python run.py
