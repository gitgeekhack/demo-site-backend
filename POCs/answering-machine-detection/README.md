# Coregears Answering Machine Detection API

Python version 3.8.x is requried to run this API.

Please run the below listed steps to run this API,
1. Install the requirements.txt
`pip install -r requirements.txt`
2. The [conf.py](https://github.com/gitgeekhack/answering-machine-detection/blob/f19ca08db830c758402ed5eb18da389f5fa16bec/conf.py) contains the configaration for the Gunicorn. Edit the conf.py as per the available hardware resources.<br>
`bind = '0.0.0.0:8081'`<br>
The `bind` variable specifies the address along with the port number on which the application needs to be run.<br><br>
`workers = 16`<br>
The `workers` variable specifies the number of workers to spawn for the application. The ideal workers should be 2 x the available CPU. This can be fine tuned as per the requiremets and available resources.<br><br>
Here, 16 workers are specified which means 16 subprocesses are created for the application to manage and serve multiple requests.<br>
_Note: Higher number of workers will increase the memory consumption._<br><br>
`worker_connections = 1000` <br>
The `worker_connections` variable specifies the maximum number of connection a worker can have `1000` is a default value, it can be fine tuned as per the need and available resources.<br><br>
Here, The 1000 worker connections value specifies that a worker can have maximum of 1000 open connections at a time while serving the application.<br>
3. To run the application using the Gunicorn please execuet the following command from the application folder.<br>
`gunicorn -c conf.py app:app --log-file ./app/logs/ml_api.log`
