FROM python:3.9
RUN apt-get update && apt-get install -y lsb-release apt-transport-https python3-opencv default-jdk
RUN echo "deb https://notesalexp.org/tesseract-ocr-dev/$(lsb_release -cs)/ $(lsb_release -cs) main" \
| tee /etc/apt/sources.list.d/notesalexp.list > /dev/null
RUN apt-get update -oAcquire::AllowInsecureRepositories=true
RUN apt-get install -y --allow-unauthenticated notesalexp-keyring -oAcquire::AllowInsecureRepositories=true
RUN apt-get update
RUN apt-get install -y tesseract-ocr
ENV Tesseract_PATH=/usr/bin/tesseract
ENV ENVIRONMENT=staging
WORKDIR /underwriting-automation
ADD ./app ./app
ADD ./requirements.txt ./requirements.txt
ADD run_underwriting_automation.py ./run.py
ADD ./conf.py ./conf.py
ADD ./log.conf ./log.conf
RUN pip install --upgrade pip==20.2.4
RUN pip install -r requirements.txt
RUN pip install gunicorn
EXPOSE 80
CMD gunicorn -c conf.py app:app --log-config log.conf
#CMD python run.py
