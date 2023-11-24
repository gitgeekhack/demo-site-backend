from app.service.helper.authentication import BearerToken


async def test_bearer_token_valid():
    assert BearerToken().validate('hXCQjAvi5ScCZk3cjBEEak5lLc038Hkb')


async def test_bearer_token_invalid():
    assert not BearerToken().validate('hXCQjABEEak5lLc038vi5ScCZk3cjHkb')
