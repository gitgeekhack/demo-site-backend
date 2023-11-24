import aiohttp_jinja2
import json
import pandas as pd
from aiohttp import web
import re

from app.service.data_preparation import ETL
from app.service.make_request import fetch_data_from_url, fetch_data_using_thread_id
from app.service.ensemble_model import EnsembleModel
from app.service.overall_emotion import OverallEmotion
from app.constant import REMOVE_UNWANTED_SYMBOLS
from app import logger


class Index(web.View):  # class for Index route
    @aiohttp_jinja2.template("index.html")
    async def get(self):  # get method to load the index.html
        return {'response': ""}

    @aiohttp_jinja2.template("index.html")
    async def post(self):  # post method to gather form data and detect emotion
        fetched_data = await self.request.post()  # fetched data from the textarea
        cleaned_message = re.sub(REMOVE_UNWANTED_SYMBOLS, ' ', str(fetched_data['txt_area']))  # cleaning the message
        lst_message = [cleaned_message]  # preparing list of the cleaned message
        df = pd.DataFrame()
        df['message'] = lst_message  # storing fetched data into 'message' column
        model_obj = EnsembleModel()  # initialize object of EnsembleModel
        predicted_data, emotion_count = model_obj.ensemble_predicted_emotion(df)  # predict emotions on the messages
        context = {
            'message': predicted_data['message'].tolist(),
            'emotion': predicted_data['final_result'].tolist(),
        }
        return {'response': context}


class Dashboard(web.View):  # class for Dashboard route
    @aiohttp_jinja2.template("dashboard.html")
    async def get(self):  # get method for make requests and detect emotion
        fetched_data = fetch_data_from_url(self.request.match_info['time'])  # make request and fetched data from server
        logger.info(self.request.match_info['time'])
        json_data = json.loads(fetched_data)  # converting fetched_data into json format

        thread_ids = set()
        for item in json_data['hits']['hits']:  # iterate over the data list
            try:
                thread_ids.add(item['_source']['thread_id'])  # extract thread_id feature
            except KeyError:
                pass

        thread_ids = list(thread_ids)

        etl_obj = ETL()
        overall_emotion_obj = OverallEmotion()
        overall_emotion_list = []

        for i in range(len(thread_ids)):
            fetched_thread_data = fetch_data_using_thread_id(thread_ids[i])
            json_data = json.loads(fetched_thread_data)  # converting fetched_data into json format
            extracted_data = etl_obj.extract_data(json_data)  # extracted the json data
            transformed_data = etl_obj.transform_data(extracted_data)  # transformed the extracted data
            # prepare the adjacency pair of transformed data
            adjacency_pairs_data = overall_emotion_obj.prepare_adjacency_pair(transformed_data)
            if len(adjacency_pairs_data) > 1:
                model_obj = EnsembleModel()  # create model_obj
                predicted_data, emotion_count = model_obj.ensemble_predicted_emotion(adjacency_pairs_data)
                # predict overall emotions by performing the arithmetic average
                predicted_overall_emotion = overall_emotion_obj.perform_arithmetic_average(predicted_data, emotion_count)
                overall_emotion_list.append(predicted_overall_emotion)

        emotion_count_threads = {"Positive": overall_emotion_list.count('Positive'),
                                 "Negative": overall_emotion_list.count('Negative'),
                                 "Neutral": overall_emotion_list.count('Neutral')}
        context = {
            'thread_ids': thread_ids,
            'overall_emotion_list': overall_emotion_list,
            'emotion_count_threads': emotion_count_threads
        }
        return {'response': context}
