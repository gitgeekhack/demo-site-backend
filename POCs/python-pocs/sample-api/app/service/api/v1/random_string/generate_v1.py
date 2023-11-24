import uuid


class RandomStringGeneratorV1():

    async def generate(self):
        random_string = uuid.uuid4()
        random_string = random_string.hex
        return random_string
