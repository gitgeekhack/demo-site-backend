import os
import re
import ast
import boto3
from app.constant import MedicalInsights

from langchain.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.llms.bedrock import Bedrock
from langchain.prompts import PromptTemplate
from langchain.docstore.document import Document
from langchain.embeddings import BedrockEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from app.constant import MedicalInsights
from app.service.medical_document_insights.nlp_extractor import bedrock_client


class EncountersExtractor:
    def __init__(self):
        os.environ['AWS_DEFAULT_REGION'] = MedicalInsights.AWS_DEFAULT_REGION
        self.bedrock_client = bedrock_client
        self.model_id_llm = 'anthropic.claude-v2:1'
        self.model_embeddings = 'amazon.titan-embed-text-v1'

        self.llm = Bedrock(
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
            chunk_length.append(self.llm.get_num_tokens(text))

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

        docs = await self.__data_formatter(data)

        vectorstore_faiss = FAISS.from_documents(
            documents=docs,
            embedding=self.bedrock_embeddings,
        )

        query = MedicalInsights.Prompts.ENCOUNTER_PROMPT
        prompt_template = MedicalInsights.Prompts.PROMPT_TEMPLATE

        prompt = PromptTemplate(
            template=prompt_template, input_variables=["context", "question"]
        )
        qa = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=vectorstore_faiss.as_retriever(
                search_type="similarity", search_kwargs={"k": 6}
            ),
            return_source_documents=True,
            chain_type_kwargs={"prompt": prompt}
        )

        answer = qa({"query": query})
        response = answer['result']

        return await self.__post_processing(response)
