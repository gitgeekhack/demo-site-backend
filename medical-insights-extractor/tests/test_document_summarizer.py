import json
import pytest
from langchain.docstore.document import Document
from app.service.medical_document_insights.nlp_extractor import document_summarizer

pytest_plugins = ('pytest_asyncio',)


class TestDocumentSummarizer:
    @pytest.mark.asyncio
    async def test_is_summary_line_similar_with_valid_first_line(self):
        summary_extractor = document_summarizer.DocumentSummarizer()
        generated_summary_first_line = "Based on the provided medical report, here is a summary of the key information."
        assert await summary_extractor._DocumentSummarizer__is_summary_line_similar(generated_summary_first_line)

    @pytest.mark.asyncio
    async def test_is_summary_line_with_invalid_first_line(self):
        summary_extractor = document_summarizer.DocumentSummarizer()
        generated_summary_first_line = "This is a completely different line."
        assert not await summary_extractor._DocumentSummarizer__is_summary_line_similar(generated_summary_first_line)

    @pytest.mark.asyncio
    async def test_get_stuff_calls_with_valid_parameter(self):
        summary_extractor = document_summarizer.DocumentSummarizer()
        docs = [Document(page_content="This is a first line"),
                Document(page_content="This is a second line"),
                Document(page_content="This is a third line"),
                Document(page_content="This is a fourth line")]
        chunk_length = [20000, 20000, 30000, 25000]
        result = await summary_extractor._DocumentSummarizer__get_stuff_calls(docs, chunk_length)
        assert result == [
            [docs[0], docs[1], docs[2]],
            [docs[3]]
        ]

    @pytest.mark.asyncio
    async def test_get_stuff_calls_with_string_input(self):
        summary_extractor = document_summarizer.DocumentSummarizer()
        docs = "This is invalid parameter of string"
        chunk_length = [10000, 20000, 30000, 15000]
        try:
            await summary_extractor._DocumentSummarizer__get_stuff_calls(docs, chunk_length)
        except AssertionError:
            assert True

    @pytest.mark.asyncio
    async def test_get_stuff_calls_with_invalid_size_of_chunk_length(self):
        summary_extractor = document_summarizer.DocumentSummarizer()
        docs = [Document(page_content="This is a first line"),
                Document(page_content="This is a second line")]
        chunk_length = [100000]
        try:
            await summary_extractor._DocumentSummarizer__get_stuff_calls(docs, chunk_length)
        except AssertionError:
            assert True

    @pytest.mark.asyncio
    async def test_get_stuff_calls_with_invalid_parameter_of_empty_list(self):
        summary_extractor = document_summarizer.DocumentSummarizer()
        docs = []
        chunk_length = []
        result = await summary_extractor._DocumentSummarizer__get_stuff_calls(docs, chunk_length)
        assert result == []

    @pytest.mark.asyncio
    async def test_post_processing_with_valid_parameter(self):
        summary_extractor = document_summarizer.DocumentSummarizer()
        input_summary = "This is the testing summary line."
        result = await summary_extractor._DocumentSummarizer__post_processing(input_summary)
        assert result is not None

    @pytest.mark.asyncio
    async def test_post_processing_with_list_input(self):
        summary_extractor = document_summarizer.DocumentSummarizer()
        input_summary = ["This is a example of summary line.", "This is a second example of summary line."]
        try:
            await summary_extractor._DocumentSummarizer__post_processing(input_summary)
        except AttributeError:
            assert True

    @pytest.mark.asyncio
    async def test_post_processing_with_empty_string(self):
        summary_extractor = document_summarizer.DocumentSummarizer()
        input_summary = ""
        result = await summary_extractor._DocumentSummarizer__post_processing(input_summary)
        assert len(result) == 0

    @pytest.mark.asyncio
    async def test_get_summary_with_valid_parameter(self):
        summary_extractor = document_summarizer.DocumentSummarizer()
        json_file = 'data/json/04-26-17 Neurological Post Op Eval - Mobin_text.json'

        with open(json_file, 'r') as f:
            json_data = json.load(f)

        result = await summary_extractor.get_summary(json_data)
        assert result is not None

    @pytest.mark.asyncio
    async def test_get_summary_with_empty_json(self):
        summary_extractor = document_summarizer.DocumentSummarizer()
        json_data = {}
        result = await summary_extractor.get_summary(json_data)
        assert result is not None
