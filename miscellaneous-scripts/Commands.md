  ### SQS queues in DEV

* [pareit-dev-nlp-api-tasks-queue](https://sqs.us-east-2.amazonaws.com/580568194365/pareit-dev-nlp-api-tasks-queue)
* [pareit-dev-nlp-api-textclassifier-queue](https://sqs.us-east-2.amazonaws.com/580568194365/pareit-dev-nlp-api-textclassifier-queue)
* [pareit-dev-nlp-api-ocr-queue](https://sqs.us-east-2.amazonaws.com/580568194365/pareit-dev-nlp-api-ocr-queue)
* [pareit-dev-nlp-api-entityfinder-queue](https://sqs.us-east-2.amazonaws.com/580568194365/pareit-dev-nlp-api-entityfinder-queue)
* [pareit-dev-nlp-api-entitylinker-queue](https://sqs.us-east-2.amazonaws.com/580568194365/pareit-dev-nlp-api-entitylinker-queue)

### S3 bucket in DEV

```
* pareit-dev-nlp-api-flow-storage
```

### AWS-cli profiles

```
* pareit-download (access to model bucket)
* pareit-dev  (access to s3, sqs, textract, comprehend)
* pareit-root (root user)
```

### Aws Assume Role (12hrs) (pareit-dev)

###### NOTE: Configure region us-east-1

```bash
aws sts assume-role --role-arn arn:aws:iam::580568194365:role/developers-access \
                    --role-session-name developers-account --serial-number (add your iam user) \
                    --profile=pareit-root --token-code (add mfa token) \
                    --duration-seconds 43200
```

### Copying S3 model in local file machine (pareit-download)

###### NOTE: Configure region us-east-2

```bash
aws sts get-session-token --serial-number (add your iam user)  --profile=pareit-root --token-code (add mfa token)
```

___

# Prebuild Copy Model files from S3

### documentsplitter

##### s3 documentsplitter/bigfiles.yml

```bash
aws s3 cp "s3://pareit-nlp-services/documentsplitter/document_splitter/pretrained_transformers/Bio_ClinicalBERT/pytorch_model.bin"\
          "documentsplitter/document_splitter/pretrained_transformers/Bio_ClinicalBERT/pytorch_model.bin"\
          --profile=pareit-download

aws s3 cp "s3://pareit-nlp-services/documentsplitter/document_splitter/detectron2/model_final_trimmed.pth"\
          "documentsplitter/document_splitter/detectron2/model_final_trimmed.pth"\
          --profile=pareit-download
```

### textclassifier

##### s3 textclassifier/bigfiles.yml

```bash
aws s3 cp "s3://pareit-nlp-services/textclassifier/cataloger_ml/pretrained_transformers/Bio_ClinicalBERT/pytorch_model.bin"\
          "textclassifier/cataloger_ml/pretrained_transformers/Bio_ClinicalBERT/pytorch_model.bin"\
          --profile=pareit-download
```

### ocr

##### s3 ocr/bigfiles.yml

```bash
aws s3 cp "s3://pareit-nlp-services/ocr/smartsearch/layout_model/model_final.pth"\
          "ocr/smartsearch/layout_model/model_final.pth"\
          --profile=pareit-download

aws s3 cp "s3://pareit-nlp-services/ocr/smartsearch/sc_model/optimizer.pt"\
          "ocr/smartsearch/sc_model/optimizer.pt"\
          --profile=pareit-download

aws s3 cp "s3://pareit-nlp-services/ocr/smartsearch/sc_model/pytorch_model.bin"\
          "ocr/smartsearch/sc_model/pytorch_model.bin"\
          --profile=pareit-download

aws s3 cp "s3://pareit-nlp-services/ocr/entity_extraction/bert_model/optimizer.pt"\
          "ocr/entity_extraction/bert_model/optimizer.pt"\
          --profile=pareit-download

aws s3 cp "s3://pareit-nlp-services/ocr/entity_extraction/bert_model/pytorch_model.bin"\
          "ocr/entity_extraction/bert_model/pytorch_model.bin"\
          --profile=pareit-download

aws s3 cp "s3://pareit-nlp-services/ocr/entity_extraction/embed_model/wiki_unigrams.bin"\
          "ocr/entity_extraction/embed_model/wiki_unigrams.bin"\
          --profile=pareit-download

aws s3 cp "s3://pareit-nlp-services/ocr/entity_extraction/un-ner.model/pytorch_model.bin"\
          "ocr/entity_extraction/un-ner.model/pytorch_model.bin"\
          --profile=pareit-download
```

### entityfinder

##### s3 entityfinder/bigfiles.yml

```bash
aws s3 cp "s3://pareit-nlp-services/entityfinder/handwritten/model_hw/model_final.pth"\
          "entityfinder/handwritten/model_hw/model_final.pth"\
          --profile=pareit-download
```

___

# Create Docker Containers for modules (Run)

### Document Splitter

```bash
docker run -v $HOME/.aws:/root/.aws/:ro --env PYTHONUNBUFFERED=1 \
    --env INPUT_SQS=pareit-dev-nlp-api-tasks-queue \
    --env OUTPUT_SQS=pareit-dev-nlp-api-textclassifier-queue \
    --env AWS_PROFILE=pareit-dev \
    --env AWS_REGION=us-east-2 \
    --env AWS_BUCKET=pareit-dev-nlp-api-flow-storage \
    --env SERVICE=documentsplitter \
    documentsplitter
```

### Text Classifier

```bash
docker run -v $HOME/.aws:/root/.aws/:ro --env PYTHONUNBUFFERED=1 \
    --env INPUT_SQS=pareit-dev-nlp-api-textclassifier-queue \
    --env OUTPUT_SQS=pareit-dev-nlp-api-ocr-queue \
    --env AWS_PROFILE=pareit-dev \
    --env AWS_REGION=us-east-2 \
    --env AWS_BUCKET=pareit-dev-nlp-api-flow-storage \
    --env SERVICE=textclassifier \
    textclassifier
```

### OCR

```bash
docker run -v $HOME/.aws:/root/.aws/:ro --env PYTHONUNBUFFERED=1 \
    --env INPUT_SQS=pareit-dev-nlp-api-ocr-queue \
    --env OUTPUT_SQS=pareit-dev-nlp-api-entityfinder-queue \
    --env AWS_PROFILE=pareit-dev \
    --env AWS_REGION=us-east-2 \
    --env AWS_BUCKET=pareit-dev-nlp-api-flow-storage \
    --env SERVICE=ocr \
    ocr
```

### Entity Finder

```bash
docker run -v $HOME/.aws:/root/.aws/:ro --env PYTHONUNBUFFERED=1 \
    --env INPUT_SQS=pareit-dev-nlp-api-entityfinder-queue \
    --env OUTPUT_SQS=pareit-dev-nlp-api-entitylinker-queue \
    --env AWS_PROFILE=pareit-dev \
    --env AWS_REGION=us-east-2 \
    --env AWS_BUCKET=pareit-dev-nlp-api-flow-storage \
    --env SERVICE=entityfinder \
    entityfinder
```

### Entity Linker

```bash
docker run -v $HOME/.aws:/root/.aws/:ro --env PYTHONUNBUFFERED=1 \
    --env INPUT_SQS=pareit-dev-nlp-api-entitylinker-queue \
    --env AWS_PROFILE=pareit-dev \
    --env AWS_REGION=us-east-2 \
    --env AWS_BUCKET=pareit-dev-nlp-api-flow-storage \
    --env SERVICE=entitylinker \
    entitylinker
```

___

# Docker Build

### Document Splitter

```bash
docker build -t documentsplitter -f documentsplitter/Dockerfile .
```

### Text Classifier

```bash
docker build -t textclassifier -f textclassifier/Dockerfile .
```

### OCR

```bash
docker build -t ocr -f ocr/Dockerfile .
```

### Entity Finder

```bash
docker build -t entityfinder -f entityfinder/Dockerfile .
```

### Entity Linker

```bash
docker build -t entitylinker -f entitylinker/Dockerfile .
```

___

# Download Annotated Data from S3

#### First step: Assume pareit-dev role

#### Second step: Execute below command

```bash
aws s3 cp "s3://pareit-dev-datalabeling-anno/" dataset/ --recursive --profile pareit-dev --sse-c-key fileb://s3_sse_key.bin --sse-c AES256
```

___

# Test

Sample request in sqs:

```bash
aws sqs send-message --queue-url https://sqs.us-east-2.amazonaws.com/580568194365/pareit-dev-nlp-api-tasks-queue --message-body "{\"payload\": [\"s3://pareit-dev-nlp-api-flow-storage/pdfs/2018.09.20 Dilanchian - Report.pdf\"], \"requestId\": \"20220711test\", \"postbackUrl\": \"https://eobcudpdzzgbx6k.m.pipedream.net\", \"userId\": \"1\"}" --delay-seconds 2 --profile=pareit-dev
```

Direct run without queue:

```bash
docker run -v $HOME/.aws:/root/.aws/:ro --env PYTHONUNBUFFERED=1 \
    --env INPUT_MESSAGE="{\"payload\": [\"s3://pareit-dev-nlp-api-flow-storage/pdfs/[MD] FISHMAN -- B+R Dr. Mobin Updated all B+R.pdf\"], \"requestId\": \"20220711test\", \"postbackUrl\": \"https://eobcudpdzzgbx6k.m.pipedream.net\", \"userId\": \"1\"}"\
    --env AWS_PROFILE=pareit-dev \
    --env AWS_REGION=us-east-2 \
    --env AWS_BUCKET=pareit-dev-nlp-api-flow-storage \
    --env SERVICE=documentsplitter \
    documentsplitter
```
