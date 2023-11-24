from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import numpy as np
import pandas as pd
import time
from app import logger
from transformers import pipeline
from app.constant import MODEL_PATH

vader_obj = SentimentIntensityAnalyzer()  # init vader object
roberta_model = pipeline('sentiment-analysis', model=MODEL_PATH)


class EnsembleModel:
    def __init__(self):
        self.data_frame = pd.DataFrame()

    def ensemble_predicted_emotion(self, dataframe):
        self.data_frame = dataframe
        x = time.time()

        # get "vader" library scores
        self.data_frame['vader_score'] = self.data_frame['message'].apply(lambda x: get_vader_scores(x))

        # get "roberta" results
        self.data_frame['roberta_results'] = roberta_model(self.data_frame['message'].tolist(), truncation=True)

        logger.info("Predicting time : {}".format(time.time() - x))

        # converting abbreviations like 'Positive', 'Negative'
        abbr = lambda x: "Positive" if x == "POS" else ("Negative" if x == "NEG" else "Neutral")

        # ensemble for getting better emotion with higher confidence
        self.data_frame['final_result'] = self.data_frame.apply(lambda x: abbr(x['vader_score']['label']) if x['vader_score']['score'] > x['roberta_results']['score'] else abbr(x['roberta_results']['label']), axis=1)

        # creating by default keys and initialize with 0
        emotion_count = dict.fromkeys(['Positive', 'Negative', 'Neutral'], 0)

        # converting final_result of emotion count into dictionary
        result_count = self.data_frame['final_result'].value_counts().to_dict()

        # filling emotion_count dictionary from the result_count dictionary
        for key in result_count.keys():
            emotion_count[key] = result_count[key]

        self.data_frame['sequence_number'] = np.arange(1, len(self.data_frame) + 1)
        return self.data_frame, emotion_count


# method that provides 'emotion' & 'confidence of vader library
def get_vader_scores(sentence):
    sentiment_dict = vader_obj.polarity_scores(sentence)

    if sentiment_dict['compound'] >= 0.05:
        confidence = sentiment_dict['pos']
        emotion_dict = {'label': "POS", 'score': confidence}
    elif sentiment_dict['compound'] <= -0.05:
        confidence = sentiment_dict['neg']
        emotion_dict = {'label': "NEG", 'score': confidence}
    else:
        confidence = sentiment_dict['neu']
        emotion_dict = {'label': "NEU", 'score': confidence}
    return emotion_dict
