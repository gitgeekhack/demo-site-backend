# demo-site-backend

The Marut OCR repository contains proof-of-concepts for the Machine Learning Project. Projects like object detection, OCR (Optical Character Recognition), data annotation, and extraction from PDF documents.

### List of POCs currently presented in Demo Site

1. Driving Licence OCR
2. Certificate Of Title OCR
3. Vehicle Damage Part Detection
4. PDF Data Annotation & Extraction

### Prerequisite
- `python >= 3.9.x`
- `tesseract == 5.1.0-72-gb8b6`
- `CVAT` (In Order to run **PDF Annotation & Extraction** POC, CVAT should be installed in development machine. To install and configure CVAT please refer following [link](https://openvinotoolkit.github.io/cvat/docs/administration/basics/installation/))

### Getting Started
* `git clone https://github.com/gitgeekhack/demo-site-backend.git`
* `cd demo-site-backend && pip install -r requirements.txt`
* `python run.py`
