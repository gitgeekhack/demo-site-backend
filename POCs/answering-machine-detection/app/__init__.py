import os
import logging

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'

import warnings
warnings.filterwarnings("ignore")

import uuid
import json
import traceback
from aiohttp import web

import tensorflow as tf

tf.executing_eagerly()
from tensorflow.python.keras.models import load_model

from app.constant import headers, S3
from app.services.helper.authentication import BearerToken
from app.services.helper.pre_processing_helper import PreProcessingPipeLine
from app.business_rule_exception import InvalidFile, FileLimitExceeded, FilePathNull, MultipleFileUploaded, \
    MissingRequestBody, MissingRequiredParameter, ShortAudioLengthException

MODEL_PATH = "./app/model/2s_model.h5"

pipe_line = PreProcessingPipeLine()

MODEL = load_model(MODEL_PATH)

from app.services.amd import BinaryPredictor
binary_predictor = BinaryPredictor()
logger = logging.getLogger('AMD')


async def options_request(request):
    return web.json_response(headers=headers, status=200)


async def amd(request):
    x_uuid = uuid.uuid1()
    try:
        token = request.headers.get('Authorization')
        token = token.split(' ')[-1]

        if BearerToken.validate(token):

            data_bytes = await request.content.read()
            if not data_bytes:
                raise MissingRequestBody

            data = json.loads(data_bytes)

            if 'file_path' not in data.keys():
                raise MissingRequiredParameter(message='Missing required parameter file_path')

            file_path = data['file_path']

            if file_path == '':
                raise FilePathNull()

            if isinstance(file_path, str):
                if file_path.startswith(S3.PREFIX):
                    s3_key = file_path.replace(S3.PREFIX, '')
                else:
                    raise MissingRequestBody

                filename = os.path.basename(s3_key)

                if not filename.lower().endswith('.ulaw'):
                    raise InvalidFile(filename)

                file_size = os.path.getsize(file_path) / 1024 ** 2
                if file_size > 25:
                    raise FileLimitExceeded(file_path)
            else:
                raise MultipleFileUploaded()

            audio_file = open(file_path, 'rb')
            result, audio_length = await binary_predictor.predict(audio_file.read())
            if result == 0:
                is_human_answer = True
            else:
                is_human_answer = False
            res = {"is_human_answer": is_human_answer, 'input_audio_length': f'{audio_length} seconds'}
            logger.info(f'[{filename}] => is_human_answer: {is_human_answer}]')
            return web.json_response(res, headers=headers, status=200)
        else:
            return web.json_response({"message": 'Unauthorized'}, headers=headers, status=401)

    except FilePathNull as e:
        response = {"message": f"{e}"}
        return web.json_response(response, headers=headers, status=400)

    except MultipleFileUploaded as e:
        response = {"message": f"{e}"}
        return web.json_response(response, headers=headers, status=400)

    except FileNotFoundError:
        response = {"message": "File Not Found"}
        return web.json_response(response, headers=headers, status=404)

    except FileLimitExceeded as e:
        response = {"message": f"{e}"}
        return web.json_response(response, headers=headers, status=400)

    except InvalidFile:
        response = {"message": "Unsupported Media Type, Only 'ulaw' format is Supported!"}
        return web.json_response(response, headers=headers, status=415)

    except MissingRequestBody as e:
        response = {"message": f"{e}"}
        return web.json_response(response, headers=headers, status=400)

    except MissingRequiredParameter as e:
        response = {"message": f"{e}"}
        return web.json_response(response, headers=headers, status=400)

    except ShortAudioLengthException as e:
        response = {"message": f"{e}"}
        return web.json_response(response, headers=headers, status=400)

    except Exception as e:
        logger.error(f'Request ID: [{x_uuid}] %s -> %s', e, traceback.format_exc())
        response = {"message": "Internal Server Error"}
        logger.info(f'Request ID: [{x_uuid}] Response: {response}')
        return web.json_response(response, headers=headers, status=500)


logging.basicConfig(level=logging.INFO, format='[Time: %(asctime)s] - '
                                               'Level: %(levelname)s - '
                                               'Module: %(module)s - '
                                               'Function: %(funcName)s - '
                                               '%(message)s')
app = web.Application(client_max_size=1024 * 1024 * 25)
app.add_routes([web.options('/api/v1/amd', options_request), web.post('/api/v1/amd', amd)])
