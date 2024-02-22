import os
import re
import json
import boto3
import dateparser
from datetime import datetime, timedelta
from app.constant import MedicalInsights

from langchain.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.llms.bedrock import Bedrock
from langchain.prompts import PromptTemplate
from langchain.docstore.document import Document
from langchain.embeddings import BedrockEmbeddings
from langchain.chains.question_answering import load_qa_chain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from app.constant import MedicalInsights
from app.service.medical_document_insights.nlp_extractor import bedrock_client


class PHIDatesExtractor:
    def __init__(self):
        os.environ['AWS_DEFAULT_REGION'] = MedicalInsights.AWS_DEFAULT_REGION
        self.bedrock_client = bedrock_client
        self.model_id_llm = 'anthropic.claude-instant-v1'
        self.model_embeddings = 'amazon.titan-embed-text-v1'

        self.llm = Bedrock(
            model_id=self.model_id_llm,
            model_kwargs={
                "max_tokens_to_sample": 4000,
                "temperature": 0.75,
                "top_p": 0.01,
                "top_k": 0,
                "stop_sequences": [],
            },
            client=self.bedrock_client,
        )

        self.bedrock_embeddings = BedrockEmbeddings(model_id=self.model_embeddings, client=self.bedrock_client)

    async def __get_key(self, key):
        """ This method is used to provide the JSON key """

        if "injury" in key.lower():
            result_key = "injury_dates"
        elif "admission" in key.lower():
            result_key = "admission_dates"
        elif "discharge" in key.lower():
            result_key = "discharge_dates"

        return result_key

    async def __data_formatter(self, json_data):
        """ This method is used to format the data and prepare chunks """

        raw_text = "".join(json_data.values())

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=15000, chunk_overlap=200
        )

        texts = text_splitter.split_text(raw_text)

        docs = [Document(page_content=t) for t in texts]
        return docs

    async def __extract_values_between_curly_braces(self, text):

        pattern = r'\{.*?\}'
        matches = re.findall(pattern, text, re.DOTALL)
        return matches

    async def __get_document_type(self, vector_st):
        doc_type_query = MedicalInsights.Prompts.DOC_TYPE_PROMPT
        prompt_template = MedicalInsights.Prompts.PROMPT_TEMPLATE

        prompt = PromptTemplate(
            template=prompt_template, input_variables=["context", "question"]
        )

        qa = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=vector_st.as_retriever(
                search_type="similarity", search_kwargs={"k": 6}
            ),
            return_source_documents=True,
            chain_type_kwargs={"prompt": prompt}
        )

        answer = qa({"query": doc_type_query})
        response = json.loads(answer['result'])
        doc_type_value = response['document_type']
        return doc_type_value

    async def get_phi_dates(self, data):
        """ This method is to provide the PHI dates from the document """

        docs = await self.__data_formatter(data)

        vectorstore_faiss = FAISS.from_documents(
            documents=docs,
            embedding=self.bedrock_embeddings,
        )

        doc_type = await self.__get_document_type(vectorstore_faiss)
        query = MedicalInsights.Prompts.PHI_PROMPT
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

        matches = await self.__extract_values_between_curly_braces(response)
        json_result = json.loads(matches[0])
        dates = {}

        for key, value in json_result.items():
            result_key = await self.__get_key(key)
            dates[result_key] = value if isinstance(value, list) else [value]

        if doc_type == "Ambulance" or doc_type == "Emergency":
            dates["injury_dates"] = dates["admission_dates"]
        return {'patient_information': dates}

class PatientInfoExtractor:
    def __init__(self):

        os.environ['AWS_DEFAULT_REGION'] = "us-east-1"
        self.bedrock_client = boto3.client('bedrock-runtime', region_name="us-east-1")
        self.model_id_llm = 'anthropic.claude-instant-v1'

        self.llm = Bedrock(
            model_id=self.model_id_llm,
            model_kwargs={
                "max_tokens_to_sample": 10000,
                "temperature": 0.0,
                "top_p": 1,
                "top_k": 250,
                "stop_sequences": [],
            },
            client=self.bedrock_client,
        )

    async def __data_formatter(self, json_data):
        """ This method is used to format the data and prepare chunks """

        raw_text = "".join(json_data.values())
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=10000, chunk_overlap=200
        )

        texts = text_splitter.split_text(raw_text)

        # Create multiple documents
        docs = [Document(page_content=t) for t in texts]
        return docs

    async def __parse_date(self, date):
        """ This method is used to parse the date into MM-DD-YYYY format """

        date = dateparser.parse(date, settings={'RELATIVE_BASE': datetime(1800, 1, 1)})
        if date and date.year != 1800:
            if date.year > datetime.now().year:
                date = date - timedelta(days=36525)
            date = date.strftime("%d/%m/%Y")
            return date
        return ""

    async def __convert_str_into_json(self, text):
        """ This method is used to convert the string response of LLM into the JSON """

        start_index = text.find('{')
        end_index = text.rfind('}') + 1
        json_str = text[start_index:end_index]

        if len(json_str) == 0:
            final_data = {'patient_name': '', 'date_of_birth': ''}
            return final_data

        data = json.loads(json_str)
        data_keys = ['patient_name', 'date_of_birth']

        final_data = dict(zip(data_keys, list(data.values())))

        if final_data['date_of_birth'] and isinstance(final_data['date_of_birth'], str):
            x = await self.__parse_date(final_data['date_of_birth'])
            final_data['date_of_birth'] = x

        return final_data

    async def get_patient_info(self, data):
        """ This method is to provide the Patient Name and DOB from the document """

        docs = await self.__data_formatter(data)

        query = MedicalInsights.Prompts.PATIENT_INFO_PROMPT

        chain_qa = load_qa_chain(self.llm, chain_type="refine")
        result = chain_qa.run(input_documents=docs, question=query)
        response = await self.__convert_str_into_json(result)
        return response
