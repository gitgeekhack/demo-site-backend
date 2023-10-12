import json


class ObjectTemplate:
    def __init__(self, dictionary):
        self.__dict__.update(dictionary)


async def deserialize(dictionary):
    return json.loads(json.dumps(dictionary), object_hook=ObjectTemplate)


async def serialize(input_object):
    return json.loads(json.dumps(input_object, default=lambda x: x.__dict__))
