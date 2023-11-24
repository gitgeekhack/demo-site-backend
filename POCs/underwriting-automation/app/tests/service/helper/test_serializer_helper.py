from app.service.helper.serializer_helper import deserialize, serialize


async def test_deserialize():
    x = await deserialize({"x": 0})
    assert x.x == 0


async def test_serialize():
    test = {'a': 3, 'b': {'c': None}}
    obj = await deserialize(test)
    x = await serialize(obj)
    assert x == test
