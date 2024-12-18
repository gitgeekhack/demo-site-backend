import pytest
import os
import tensorflow as tf
os.chdir("../")

from app.services.helper.pre_processing_helper import PreProcessingPipeLine
from app.business_rule_exception import ShortAudioLengthException

pytest_plugins = ('pytest_asyncio',)

class TestPreProcessingHelper:
    @pytest.mark.asyncio
    async def test_pre_processing_helper_with_valid_audio(self):
        pipe = PreProcessingPipeLine()
        with open("tests/static_data/answering_machine.ulaw", "rb") as audio_file:
            file_content = audio_file.read()
        response, length = await pipe.pre_process(file_content)
        assert isinstance(response, tf.Tensor)
        assert length == 38.32

    @pytest.mark.asyncio
    async def test_pre_processing_helper_with_invalid_audio(self):
        pipe = PreProcessingPipeLine()
        file_content = b"invalid-content-bytes"
        try:
            await pipe.pre_process(file_content)
        except ShortAudioLengthException:
            assert True


