# demo-site-backend

The Marut OCR repository contains proof-of-concepts for the Machine Learning Project. Projects like object detection, OCR (Optical Character Recognition), data annotation, and extraction from PDF documents.

### List of POCs currently presented in Demo Site

---
1. Driving Licence OCR
2. Certificate Of Title OCR
3. Vehicle Damage Part Detection
4. PDF Data Annotation & Extraction

### Prerequisite 

---
- `python == 3.9.x` (Any Patch version would work)
- `tesseract == 5.1.0`
- `CVAT == 2.1.0` (In Order to run **PDF Annotation & Extraction** POC, CVAT should be installed in development machine. To install and configure CVAT please refer following [link](https://openvinotoolkit.github.io/cvat/docs/administration/basics/installation/))
  - Once CVAT installed successfully in your development machine, please follow this steps.

### Getting Started 

---
```commandline
git clone https://github.com/gitgeekhack/demo-site-backend.git
```
```commandline
cd demo-site-backend && pip install -r requirements.txt
```
```commandline
python run.py
```

### Configure CVAT

---
- Grab your local IP address of development machine using terminal (Ubuntu) or CMD (Windows)
  - #### Ubuntu
    ```commandline
    ifconfig
    ```
  - #### Windows
    ```commandline 
    ipconfig
    ```
- Once IP address got, set the environment variable accordingly.
  - #### Ubuntu
    ```commandline
    export CVAT_IP="http://<YOUR_IP_ADDRESS>:8081"
    ```
  - #### Windows
    > To set environment variable in Windows machine please refer this [link](https://docs.oracle.com/en/database/oracle/machine-learning/oml4r/1.5.1/oread/creating-and-modifying-environment-variables-on-windows.html)
