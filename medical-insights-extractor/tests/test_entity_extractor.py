import json
import pytest
from app.service.medical_document_insights.nlp_extractor import entity_extractor

pytest_plugins = ('pytest_asyncio',)


class TestEntityExtractor:
    @pytest.mark.asyncio
    async def test_is_alpha_valid_parameter(self):
        entity = "Hello"
        assert await entity_extractor.is_alpha(entity)

    @pytest.mark.asyncio
    async def test_is_alpha_invalid_parameter_1(self):
        entity = "123"
        try:
            await entity_extractor.is_alpha(entity)
        except TypeError as e:
            assert e

    @pytest.mark.asyncio
    async def test_is_alpha_invalid_parameter_2(self):
        entity = ""
        try:
            await entity_extractor.is_alpha(entity)
        except TypeError as e:
            assert e

    @pytest.mark.asyncio
    async def test_is_alpha_invalid_parameter_3(self):
        entity = None
        try:
            await entity_extractor.is_alpha(entity)
        except TypeError as e:
            assert e

    @pytest.mark.asyncio
    async def test_is_alpha_invalid_parameter_4(self):
        entity = "!@#$%"
        try:
            await entity_extractor.is_alpha(entity)
        except TypeError as e:
            assert e

    @pytest.mark.asyncio
    async def test_get_valid_entity_with_valid_parameter(self):
        entities = {
            "keys1": ["hello", "world"],
            "keys2": ["python", "pytest"]
        }
        expected_output = {
            "keys1": ["Hello", "World"],
            "keys2": ["Python", "Pytest"]
        }
        assert await entity_extractor.get_valid_entity(entities) == expected_output

    @pytest.mark.asyncio
    async def test_get_valid_entity_with_invalid_parameter_1(self):
        entities = {
            "keys1": ["123", "456"],
            "keys2": ["!@#", "$%^"]
        }
        expected_output = {
            "keys1": [],
            "keys2": []
        }
        assert await entity_extractor.get_valid_entity(entities) == expected_output

    @pytest.mark.asyncio
    async def test_get_valid_entity_with_invalid_parameter_2(self):
        entities = {
            "keys1": ["", "world"],
            "keys2": ["python", ""]
        }
        expected_output = {
            "keys1": ["World"],
            "keys2": ["Python"]
        }
        assert await entity_extractor.get_valid_entity(entities) == expected_output

    @pytest.mark.asyncio
    async def test_get_valid_entity_with_invalid_parameter_3(self):
        entities = {
            "keys1": [None, "world"],
            "keys2": ["python", None]
        }
        try:
            await entity_extractor.get_valid_entity(entities)
        except TypeError as e:
            assert e

    @pytest.mark.asyncio
    async def test_convert_str_into_json_with_valid_parameter(self):
        text = '{"diagnosis": ["flu", "cold"], "treatments": ["rest", "fluids"], "medications": ["ibuprofen", "acetaminophen"]}'
        expected_output = {
            "diagnosis": ["Flu", "Cold"],
            "treatments": ["Rest", "Fluids"],
            "medications": ["Ibuprofen", "Acetaminophen"]
        }
        assert await entity_extractor.convert_str_into_json(text) == expected_output

    @pytest.mark.asyncio
    async def test_convert_str_into_json_with_invalid_parameter_1(self):
        text = '{"diagnosis": ["flu", "cold"], "treatments": ["rest", "fluids",], "medications": ["ibuprofen", "acetaminophen"]}'
        assert await entity_extractor.convert_str_into_json(text) == {'diagnosis': [], 'treatments': [],
                                                                      'medications': []}

    @pytest.mark.asyncio
    async def test_convert_str_into_json_with_invalid_parameter_2(self):
        text = ''
        assert await entity_extractor.convert_str_into_json(text) == {'diagnosis': [], 'treatments': [],
                                                                      'medications': []}

    @pytest.mark.asyncio
    async def test_convert_str_into_json_with_invalid_parameter_3(self):
        text = None
        try:
            await entity_extractor.convert_str_into_json(text)
        except AttributeError as e:
            assert e

    @pytest.mark.asyncio
    async def test_convert_str_into_json_with_invalid_parameter_4(self):
        text = '{"diagnosis": ["flu", "cold"]}'
        expected_output = {
            "diagnosis": ["Flu", "Cold"],
            "treatments": [],
            "medications": []
        }
        assert await entity_extractor.convert_str_into_json(text) == expected_output

    @pytest.mark.asyncio
    async def test_get_extracted_entities_with_valid_parameter(self):
        json_file = 'data/json/04-26-17 Neurological Post Op Eval - Mobin_text.json'

        with open(json_file, 'r') as f:
            json_data = json.load(f)

        result = await entity_extractor.get_extracted_entities(json_data)
        assert result is not None

    @pytest.mark.asyncio
    async def test_get_extracted_entities_with_invalid_parameter(self):
        json_data = "My name is Kashyap and I've fever since 4 days and doctor suggested me to take medicine of Dolo365."
        try:
            await entity_extractor.get_extracted_entities(json_data)
        except AttributeError as e:
            assert e
