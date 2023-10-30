FROM python:3.9
RUN apt-get update && apt-get install -y lsb-release apt-transport-https python3-opencv default-jdk
RUN echo "deb https://notesalexp.org/tesseract-ocr-dev/$(lsb_release -cs)/ $(lsb_release -cs) main" \
| tee /etc/apt/sources.list.d/notesalexp.list > /dev/null
RUN apt-get update -oAcquire::AllowInsecureRepositories=true
RUN apt-get install -y --allow-unauthenticated notesalexp-keyring -oAcquire::AllowInsecureRepositories=true
RUN apt-get update
RUN apt-get install -y tesseract-ocr
RUN apt-get install -y libzbar0
ENV Tesseract_PATH=/usr/bin/tesseract
WORKDIR /demo-site-backend
ADD ./app ./app
ADD ./requirements.txt ./requirements.txt
ADD run.py ./run.py
ADD ./conf.py ./conf.py
RUN pip install --upgrade pip==23.3
RUN pip install -r requirements.txt
RUN pip install gunicorn

EXPOSE 80
CMD gunicorn -c conf.py app:app
CMD python run.py