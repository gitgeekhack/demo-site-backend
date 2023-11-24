FROM python:3.8-slim
WORKDIR /apa-industries
ADD . ./
RUN pip install --upgrade pip==20.2.4
RUN pip install -r requirements.txt
EXPOSE 80
CMD python run.py