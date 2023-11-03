# Deployment Instruction

This file described the steps to deploy the application using docker.
## Install Docker

Install Docker Engine using the instruction provided by [Docker](https://docs.docker.com/engine/installation)

## Build Docker Image
Create a docker image using the following command.

```bash
docker build . -t underwriting-automation
```
## Create Docker Container
Create a docker container using the following command.

```bash
docker run -d --name underwriting_container -p 90:90 -v underwriting-automation-volume:/var/underwriting-automation/volume/ underwriting-automation
```
## Start & Stop Docker Container
Start and Stop the docker container using the following command.

```bash
docker start underwriting_container
```

```bash
docker stop underwriting_container
```
## Remove Container and Image
Remove the docker container and image using the following command.

```bash
docker rm -f underwriting_container
```

```bash
docker image rm -f underwriting-automation
```
## Connect to docker run time
Connect to the Docker runtime environment of a container using the following command.
```bash
docker exec -it underwriting_container /bin/bash
```
