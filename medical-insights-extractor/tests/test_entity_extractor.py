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
    async def test_is_alpha_with_integer_input(self):
        entity = "123"
        try:
            await entity_extractor.is_alpha(entity)
        except TypeError:
            assert True

    @pytest.mark.asyncio
    async def test_is_alpha_with_empty_string(self):
        entity = ""
        try:
            await entity_extractor.is_alpha(entity)
        except TypeError:
            assert True

    @pytest.mark.asyncio
    async def test_is_alpha_with_none_input(self):
        entity = None
        try:
            await entity_extractor.is_alpha(entity)
        except TypeError:
            assert True

    @pytest.mark.asyncio
    async def test_is_alpha_with_special_characters(self):
        entity = "!@#$%"
        try:
            await entity_extractor.is_alpha(entity)
        except TypeError:
            assert True

    @pytest.mark.asyncio
    async def test_get_valid_entity_with_valid_parameter(self):
        entities = {
            "keys1": ["hello", "world"],
            "keys2": ["python", "pytest"]
        }
        assert await entity_extractor.get_valid_entity(entities) == {
            "keys1": ["Hello", "World"],
            "keys2": ["Python", "Pytest"]
        }

    @pytest.mark.asyncio
    async def test_get_valid_entity_with_special_characters(self):
        entities = {
            "keys1": ["123", "456"],
            "keys2": ["!@#", "$%^"]
        }
        assert await entity_extractor.get_valid_entity(entities) == {
            "keys1": [],
            "keys2": []
        }

    @pytest.mark.asyncio
    async def test_get_valid_entity_with_empty_string(self):
        entities = {
            "keys1": ["", "world"],
            "keys2": ["python", ""]
        }
        assert await entity_extractor.get_valid_entity(entities) == {
            "keys1": ["World"],
            "keys2": ["Python"]
        }

    @pytest.mark.asyncio
    async def test_get_valid_entity_with_none_input(self):
        entities = {
            "keys1": [None, "world"],
            "keys2": ["python", None]
        }
        try:
            await entity_extractor.get_valid_entity(entities)
        except TypeError:
            assert True

    @pytest.mark.asyncio
    async def test_convert_str_into_json_with_valid_parameter(self):
        text = '{"diagnosis": ["flu", "cold"], "treatments": ["rest", "fluids"], "medications": ["ibuprofen", "acetaminophen"]}'
        assert await entity_extractor.convert_str_into_json(text) == {
            "diagnosis": ["Flu", "Cold"],
            "treatments": ["Rest", "Fluids"],
            "medications": ["Ibuprofen", "Acetaminophen"]
        }

    @pytest.mark.asyncio
    async def test_convert_str_into_json_with_invalid_comma_input(self):
        text = '{"diagnosis": ["flu", "cold"], "treatments": ["rest", "fluids",], "medications": ["ibuprofen", "acetaminophen"]}'
        assert await entity_extractor.convert_str_into_json(text) == {'diagnosis': [], 'treatments': [],
                                                                      'medications': []}

    @pytest.mark.asyncio
    async def test_convert_str_into_json_with_empty_string(self):
        text = ''
        assert await entity_extractor.convert_str_into_json(text) == {'diagnosis': [], 'treatments': [],
                                                                      'medications': []}

    @pytest.mark.asyncio
    async def test_convert_str_into_json_with_none_input(self):
        text = None
        try:
            await entity_extractor.convert_str_into_json(text)
        except AttributeError:
            assert True

    @pytest.mark.asyncio
    async def test_convert_str_into_json_with_only_diagnosis(self):
        text = '{"diagnosis": ["flu", "cold"]}'
        assert await entity_extractor.convert_str_into_json(text) == {
            "diagnosis": ["Flu", "Cold"],
            "treatments": [],
            "medications": []
        }

    @pytest.mark.asyncio
    async def test_get_extracted_entities_with_valid_parameter(self):
        json_file = 'data/json/04-26-17 Neurological Post Op Eval - Mobin_text.json'

        with open(json_file, 'r') as f:
            json_data = json.load(f)

        result = await entity_extractor.get_extracted_entities(json_data)
        assert result is not None

    @pytest.mark.asyncio
    async def test_get_extracted_entities_with_invalid_string_parameter(self):
        json_data = "My name is Umaima and I've fever since 4 days and doctor suggested me to take medicine of Dolo365."
        try:
            await entity_extractor.get_extracted_entities(json_data)
        except AttributeError:
            assert True
