import nltk
# Uncomment to download "stopwords"
# nltk.download("stopwords")
import torch
from nltk.corpus import stopwords
import re
import os
import pathlib
import cv2
from itertools import islice
from itertools import groupby
import numpy as np
from sklearn import preprocessing
from transformers import DistilBertTokenizer
from transformers import AutoModelForSequenceClassification
from transformers import Trainer
from transformers import TrainingArguments
from sklearn.metrics import precision_recall_fscore_support, accuracy_score
import pandas as pd

MODEL_PATH = '/home/heli/Documents/git/PareIT/ds-nlp-services/ocr/smartsearch/sc_model'  # model file path
TRAIN_DATASET_PATH = './DATASET/train.csv'  # path to train dataset csv
UNSEEN_TEST_DATASET_PATH = './DATASET/test.csv'  # path to test dataset csv
OUTPUT_DIR = './RESULTS/'  # path to output dataset csv to save results
NUMBER_OF_LABELS = 9
TOKENIZER_PATH = os.path.join(MODEL_PATH, "tokenizer/")

model = AutoModelForSequenceClassification.from_pretrained("emilyalsentzer/Bio_ClinicalBERT",
                                                           num_labels=NUMBER_OF_LABELS)
tokenizer = DistilBertTokenizer.from_pretrained(TOKENIZER_PATH)


class DatasetCreate(torch.utils.data.Dataset):
    def __init__(self, encodings, labels):
        self.encodings = encodings
        self.labels = labels

    def __getitem__(self, idx):
        item = {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}
        item['labels'] = torch.tensor(self.labels[idx])
        return item

    def __len__(self):
        return len(self.labels)


def compute_metrics(pred):
    labels = pred.label_ids
    preds = pred.predictions.argmax(-1)
    precision, recall, f1, _ = precision_recall_fscore_support(labels, preds, average='weighted', warn_for=tuple())
    acc = accuracy_score(labels, preds)
    return {'accuracy': acc, 'f1': f1, 'precision': precision, 'recall': recall}


async def label_encode(train, test):
    le = preprocessing.LabelEncoder()
    train_category = train['label']
    test_category = test['label']
    train['label'] = le.fit_transform(train_category)
    test['label'] = le.transform(test_category)
    return (train, test), le, test_category


async def tokenize_n_load_dataset(test):
    global tokenizer
    tokenized_test = tokenizer(test['text'].tolist(), padding=True, truncation=True, max_length=200)
    label_test = test.label.tolist()
    test_dataset = DatasetCreate(tokenized_test, label_test)
    return test_dataset


async def main():
    test = pd.read_csv(UNSEEN_TEST_DATASET_PATH, index_col=False).dropna()
    train = pd.read_csv(TRAIN_DATASET_PATH, index_col=False).dropna()
    (train, test), le, test_category = await label_encode(train, test)
    test_dataset = await tokenize_n_load_dataset(test)
    sc_model = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH)
    training_args = TrainingArguments(do_train=False, do_eval=True, output_dir=OUTPUT_DIR)
    trainer = Trainer(model=sc_model, args=training_args, eval_dataset=test_dataset, compute_metrics=compute_metrics)
    results = trainer.evaluate()
    print(results)


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
