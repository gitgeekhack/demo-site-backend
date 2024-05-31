import json
import pytest
from app.service.medical_document_insights.nlp_extractor import document_summarizer

pytest_plugins = ('pytest_asyncio',)


class TestDocumentSummarizer:
    @pytest.mark.asyncio
    async def test_is_summary_line_similar_with_valid_parameter(self):
        summary_extractor = document_summarizer.DocumentSummarizer()
        generated_summary_first_line = "Based on the provided medical report, here is a summary of the key information."
        result = await summary_extractor._DocumentSummarizer__is_summary_line_similar(generated_summary_first_line)
        assert result == True

    @pytest.mark.asyncio
    async def test_is_summary_line_with_invalid_parameter(self):
        summary_extractor = document_summarizer.DocumentSummarizer()
        generated_summary_first_line = "This is a completely different line."
        result = await summary_extractor._DocumentSummarizer__is_summary_line_similar(generated_summary_first_line)
        assert result == False

    @pytest.mark.asyncio
    async def test_get_stuff_calls_with_valid_parameter(self):
        summary_extractor = document_summarizer.DocumentSummarizer()
        docs = ["doc1"]
        chunk_length = [10000, 20000, 30000, 15000]
        result = await summary_extractor._DocumentSummarizer__get_stuff_calls(docs, chunk_length)
        expected = [["doc1"]]
        assert result == expected

    @pytest.mark.asyncio
    async def test_get_stuff_calls_with_invalid_parameter_1(self):
        summary_extractor = document_summarizer.DocumentSummarizer()
        docs = {"Hello"}
        chunk_length = [10000, 20000, 30000, 15000]
        try:
            await summary_extractor._DocumentSummarizer__get_stuff_calls(docs, chunk_length)
        except AssertionError as e:
            assert e

    @pytest.mark.asyncio
    async def test_get_stuff_calls_with_invalid_parameter_2(self):
        summary_extractor = document_summarizer.DocumentSummarizer()
        docs = ["doc1", "doc2"]
        chunk_length = [100000]
        try:
            await summary_extractor._DocumentSummarizer__get_stuff_calls(docs, chunk_length)
        except AssertionError as e:
            assert e

    @pytest.mark.asyncio
    async def test_get_stuff_calls_with_invalid_parameter_3(self):
        summary_extractor = document_summarizer.DocumentSummarizer()
        docs = []
        chunk_length = []
        result = await summary_extractor._DocumentSummarizer__get_stuff_calls(docs, chunk_length)
        expected = []
        assert result == expected

    @pytest.mark.asyncio
    async def test_post_processing_with_valid_parameter(self):
        summary_extractor = document_summarizer.DocumentSummarizer()
        input_summary = "This is the testing summary line."
        result = await summary_extractor._DocumentSummarizer__post_processing(input_summary)
        assert result is not None

    @pytest.mark.asyncio
    async def test_post_processing_with_invalid_parameter_1(self):
        summary_extractor = document_summarizer.DocumentSummarizer()
        input_summary = ["This is a example of summary line.", "This is a second example of summary line."]
        try:
            await summary_extractor._DocumentSummarizer__post_processing(input_summary)
        except AttributeError as e:
            assert e

    @pytest.mark.asyncio
    async def test_post_processing_with_invalid_parameter_2(self):
        summary_extractor = document_summarizer.DocumentSummarizer()
        input_summary = ""
        result = await summary_extractor._DocumentSummarizer__post_processing(input_summary)
        assert isinstance(result, str)

    @pytest.mark.asyncio
    async def test_get_summary_with_valid_parameter(self):
        summary_extractor = document_summarizer.DocumentSummarizer()
        json_file = 'data/json/04-26-17 Neurological Post Op Eval - Mobin_text.json'
        with open(json_file, 'r') as f:
            json_data = json.load(f)
        result = await summary_extractor.get_summary(json_data)
        assert result is not None

    @pytest.mark.asyncio
    async def test_get_summary_with_invalid_parameter(self):
        summary_extractor = document_summarizer.DocumentSummarizer()
        json_data = {}
        result = await summary_extractor.get_summary(json_data)
        assert result is not None
