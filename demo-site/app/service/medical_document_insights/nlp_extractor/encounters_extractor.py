import os
import re
import ast
import time

from langchain.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.llms.bedrock import Bedrock
from langchain.prompts import PromptTemplate
from langchain.docstore.document import Document
from langchain.embeddings import BedrockEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter

from app import logger
from app.constant import BotoClient
from app.constant import MedicalInsights
from app.service.medical_document_insights.nlp_extractor import bedrock_client, get_llm_input_tokens


class EncountersExtractor:
    def __init__(self):
        os.environ['AWS_DEFAULT_REGION'] = BotoClient.AWS_DEFAULT_REGION
        self.bedrock_client = bedrock_client
        self.model_id_llm = 'anthropic.claude-v2:1'
        self.model_embeddings = 'amazon.titan-embed-text-v1'

        self.anthropic_llm = Bedrock(
            model_id=self.model_id_llm,
            model_kwargs={
                "max_tokens_to_sample": 4000,
                "temperature": 0.00,
                "top_p": 1,
                "top_k": 0,
                "stop_sequences": [],
            },
            client=self.bedrock_client,
        )

        self.titan_llm = Bedrock(model_id=self.model_embeddings, client=self.bedrock_client)
        self.bedrock_embeddings = BedrockEmbeddings(model_id=self.model_embeddings, client=self.bedrock_client)

    async def __data_formatter(self, json_data):
        """ This method is used to format the data and prepare chunks """

        raw_text = "".join(json_data.values())

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=20000, chunk_overlap=200
        )

        texts = text_splitter.split_text(raw_text)

        chunk_length = []
        for text in texts:
            chunk_length.append(self.anthropic_llm.get_num_tokens(text))

        threshold = max(chunk_length)
        if threshold > 7000:
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=10000, chunk_overlap=200
            )
            texts = text_splitter.split_text(raw_text)

        docs = [Document(page_content=t) for t in texts]
        return docs

    async def __post_processing(self, response):
        """ This method is used to post-process the LLM response """

        try:
            # Use a regular expression to find the list in the string
            string_of_tuples = re.search(r'\[.*?\]', response, re.DOTALL).group()

            try:
                # Convert the string of tuples into a list of tuples
                list_of_tuples = ast.literal_eval(string_of_tuples.replace('“', '"').replace('”', '"'))

            except Exception:
                # Use a regular expression to match the dates and events
                matches = re.findall(r'\(([^,]*), ([^\)]*)\)', string_of_tuples)

                # Convert the matches to a list of tuples
                list_of_tuples = [(date.strip(), event.strip()) for date, event in matches]

            encounters = []
            for date, event in list_of_tuples:
                encounters.append({'date': date, 'event': event})

            # Convert the list of tuples to a dictionary
            return {'encounters': encounters}

        except Exception:
            return {'encounters': []}

    async def get_encounters(self, data):
        """ This method is used to generate the encounters """

        x = time.time()
        docs = await self.__data_formatter(data)

        emb_tokens = 0
        for i in docs:
            emb_tokens += self.titan_llm.get_num_tokens(i.page_content)

        z = time.time()
        logger.info(f'[Medical-Insights][Encounter] Chunk Preparation Time: {z - x}')

        vectorstore_faiss = FAISS.from_documents(
            documents=docs,
            embedding=self.bedrock_embeddings,
        )
        y = time.time()
        logger.info(f'[Medical-Insights][Encounter][{self.model_embeddings}] Input Embedding tokens: {emb_tokens} '
                    f'and Generation time: {y - z}')

        query = MedicalInsights.Prompts.ENCOUNTER_PROMPT
        prompt_template = MedicalInsights.Prompts.PROMPT_TEMPLATE

        logger.info(f'[Medical-Insights][Encounter][{self.model_embeddings}] Embedding tokens for LLM call: '
                    f'{self.titan_llm.get_num_tokens(query) + self.titan_llm.get_num_tokens(prompt_template)}')

        prompt = PromptTemplate(
            template=prompt_template, input_variables=["context", "question"]
        )
        qa = RetrievalQA.from_chain_type(
            llm=self.anthropic_llm,
            chain_type="stuff",
            retriever=vectorstore_faiss.as_retriever(
                search_type="similarity", search_kwargs={"k": 6}
            ),
            return_source_documents=True,
            chain_type_kwargs={"prompt": prompt}
        )

        answer = qa({"query": query})
        response = answer['result']

        input_tokens = get_llm_input_tokens(self.anthropic_llm, answer) + self.anthropic_llm.get_num_tokens(prompt_template)
        output_tokens = self.anthropic_llm.get_num_tokens(response)

        logger.info(f'[Medical-Insights][Encounter][{self.model_id_llm}] Input tokens: {input_tokens} '
                    f'Output tokens: {output_tokens} LLM execution time: {time.time() - y}')

        return await self.__post_processing(response)
