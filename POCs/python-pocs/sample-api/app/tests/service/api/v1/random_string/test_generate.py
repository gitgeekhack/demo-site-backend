from app.service.api.v1.random_string.generate_v1 import RandomStringGeneratorV1


async def test_random_string_generator_v1_valid1():
    generator = RandomStringGeneratorV1()
    s1 = await generator.generate()
    assert s1


async def test_random_string_generator_v1_valid2():
    generator = RandomStringGeneratorV1()
    s1 = await generator.generate()
    s2 = await generator.generate()
    assert s1 != s2
