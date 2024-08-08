import time

from app import logger
from app.constant import MedicalInsights
from app.service.medical_document_insights.nlp_extractor import bedrock_client
from fuzzywuzzy import fuzz
from langchain.chains.question_answering import load_qa_chain
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_aws import BedrockLLM


class DocumentSummarizer:
    def __init__(self):
        self.bedrock_client = bedrock_client
        self.model_id_llm = 'anthropic.claude-v2'

        self.anthropic_llm = BedrockLLM(
            model_id=self.model_id_llm,
            model_kwargs={
                "max_tokens_to_sample": 10000,
                "temperature": 0.5,
                "top_p": 0.9,
                "top_k": 250,
                "stop_sequences": [],
            },
            client=self.bedrock_client,
        )
        self.reference_summary_first_lines = MedicalInsights.LineRemove.SUMMARY_FIRST_LINE_REMOVE
        self.matching_threshold = 60

    async def __generate_summary(self, docs, query):
        qa = load_qa_chain(self.anthropic_llm, chain_type="stuff")
        chain_run = qa.invoke(input={'input_documents': docs, 'question': query})
        return chain_run['output_text']

    async def __data_formatter(self, json_data):
        """ This method is used to format the data and prepare chunks """

        raw_text = "".join(json_data.values())
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=200)
        texts = text_splitter.split_text(raw_text)

        chunk_length = []
        for text in texts:
            chunk_length.append(self.anthropic_llm.get_num_tokens(text))
        docs = [Document(page_content=t) for t in texts]
        return docs, chunk_length

    async def __is_summary_line_similar(self, generated_summary_first_line):
        for reference_line in self.reference_summary_first_lines:
            if fuzz.token_sort_ratio(reference_line, generated_summary_first_line) > self.matching_threshold:
                return True
        return False

    async def __get_stuff_calls(self, docs, chunk_length):
        stuff_calls = []
        current_chunk = []
        total_length = 0
        lengths = []

        for doc, length in zip(docs, chunk_length):
            if total_length + length >= 92000:
                lengths.append(total_length)

                stuff_calls.append(current_chunk)
                current_chunk = []
                total_length = 0
            current_chunk.append(doc)
            total_length += length

        if current_chunk:
            lengths.append(total_length)
            stuff_calls.append(current_chunk)

        return stuff_calls

    async def __post_processing(self, summary):
        """ This method is used to post-process the summary generated by LLM"""

        text = summary.replace('- ', '')
        text = text.strip()
        lines = text.split('\n')
        if await self.__is_summary_line_similar(lines[0]):
            lines = lines[1:]

        if lines[-1].__contains__('?'):
            lines = lines[:-1]

        modified_text = '\n'.join(lines)
        return modified_text.strip()

    async def get_summary(self, json_data):
        """ This method is used to get the summary of document """

        raw_text = "".join(json_data.values()).strip()
        if not raw_text:
            return {"summary": MedicalInsights.TemplateResponse.SUMMARY_RESPONSE}

        chunk_prepare_start_time = time.time()
        docs, chunk_length = await self.__data_formatter(json_data)

        logger.info(f'[Summary] Chunk Preparation Time: {time.time() - chunk_prepare_start_time}')

        stuff_calls = await self.__get_stuff_calls(docs, chunk_length)

        query = MedicalInsights.Prompts.SUMMARY_PROMPT
        concatenate_query = MedicalInsights.Prompts.CONCATENATE_SUMMARY

        summary_start_time = time.time()

        if len(stuff_calls) <= 1:
            if stuff_calls:
                docs = stuff_calls[0]
                summary = await self.__generate_summary(docs, query)
                logger.info(
                    f'[Summary][{self.model_id_llm}] LLM execution time: {time.time() - summary_start_time}')
        else:
            response_summary = [await self.__generate_summary(docs, query) for docs in stuff_calls]
            final_response_summary = [Document(page_content=response) for response in response_summary]
            summary = await self.__generate_summary(final_response_summary, concatenate_query)

            logger.info(f'[Summary][{self.model_id_llm}] LLM execution time: {time.time() - summary_start_time}')

        final_summary = await self.__post_processing(summary)

        return {"summary": final_summary}
