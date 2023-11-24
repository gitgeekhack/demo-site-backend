import numpy as np
import pandas as pd
import re
from fast_ml.model_development import train_valid_test_split
from sklearn.metrics import accuracy_score
from transformers import DistilBertTokenizer, TFDistilBertModel
from tensorflow import keras
import tensorflow as tf


def read_split_csv():
    tweets = pd.read_csv('../data/Twitter_20220331/Twitter_Data.csv')
    tweets.dropna(inplace=True)
    tweets['clean_text'] = tweets['clean_text'].apply(lambda x: re.sub('[^a-zA-Z0-9(+*) \n\.]', ' ', str(x)))
    tweets['clean_text'] = tweets['clean_text'].apply(lambda x: re.sub("\s+", " ", str(x)))

    tweets['category'] = tweets['category'].replace([1, -1, 0], [0, 1, 2])
    X_train, y_train, X_valid, y_valid, X_test, y_test = train_valid_test_split(tweets, target='category',
                                                                                train_size=0.7, valid_size=0.2,
                                                                                test_size=0.1)

    test_messages = X_test['clean_text'].tolist()
    test_labels = y_test.tolist()
    return test_messages, test_labels


# define tokenize function that tokenize sentences and converting them into tensors
def tokenize(sentences, tokenizer):
    input_ids, input_masks = [], []
    for sentence in sentences:
        inputs = tokenizer.encode_plus(sentence, add_special_tokens=True, max_length=128, truncation=True,
                                       pad_to_max_length=True, return_attention_mask=True, return_token_type_ids=True)
        input_ids.append(inputs['input_ids'])
        input_masks.append(inputs['attention_mask'])

    return np.asarray(input_ids, dtype='int32'), np.asarray(input_masks, dtype='int32')


# load sentiment analysis model
def load_model():
    # init distilbert model
    distilbert = TFDistilBertModel.from_pretrained('distilbert-base-uncased')

    # load model with distilbert custom object
    loaded_model = keras.models.load_model('model/sentiment-analysis.h5',
                                           custom_objects={'TFDistilBertModel': distilbert})
    return loaded_model


def predict_sentiment(test):
    # define distilbert tokenizer
    tokenizer = DistilBertTokenizer.from_pretrained('distilbert-base-uncased')
    length = len(test)
    # call load_model for prediction
    model = load_model()

    # tokenize the data
    test = tokenize(test, tokenizer)
    test_input_ids = test[0]
    test_attention_mask = test[1]

    predicted_value = model.predict([test_input_ids, test_attention_mask])

    # predict in whole dataset
    predicted_values = []
    for i in range(0, length):
        predicted_values.append(tf.argmax(predicted_value[i].reshape(1, -1), axis=1).numpy()[0])

    return predicted_values


# Driver code

# read the csv file and split the test dataset
X_test, y_test = read_split_csv()

# predict on test dataset
predicted_list = predict_sentiment(X_test)

# checking the accuracy of the model on the first seen data
print("Accuracy : {}".format(accuracy_score(predicted_list, y_test)))
