import os
import re
import json
import boto3
import dateparser
from datetime import datetime, timedelta

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

    async def get_phi_dates(self, data):
        """ This method is to provide the PHI dates from the document """

        docs = await self.__data_formatter(data)

        vectorstore_faiss = FAISS.from_documents(
            documents=docs,
            embedding=self.bedrock_embeddings,
        )

        query = """
        Your role is to extract important dates from a medical document, specifically focusing on the injury dates, admission dates, and discharge dates. This information is vital for medical records management and analysis. Your sole purpose is to provide the output in JSON format, without any additional text output.Don't refine anything, give an original answer.
        Provide the information in JSON format as follows: {"Injury Date": ["dd/mm/yyyy", ...], "Admission Date": ["dd/mm/yyyy", ...], "Discharge Date": ["dd/mm/yyyy", ...]}. Strictly maintain the consistency in this format.
        Note: Don't include visit dates, encounter dates, date of birth, MRI scan dates, X-ray dates, checkup dates, admin date/time, follow-up dates and 'filed at' date. Avoid including times in the output.

        Here is the definition of valid Injury Date, Admission Date and Discharge Date:
        Injury Date: In the medical field context, the injury date refers to the specific date on which a patient sustained an injury or trauma. Accident date of patient is also considered as injury date. It is the date when the event leading to the patient's medical condition or injury occurred.
        Admission Date: The admission date, in the medical field context, refers to the date on which a patient is formally admitted to a healthcare facility, such as a hospital. It marks the beginning of the patient's stay for medical evaluation, treatment, or surgery.
        Discharge Date: The discharge date, in the medical field context, refers to the date when a patient is released or discharged from a healthcare facility after receiving medical care or treatment. It marks the end of the patient's stay in the facility.

        Instructions:
        1. 'Injury Date': Extract the date of the patient's injury from the given medical text. There can be multiple injury dates present in the text. If the injury date is not mentioned in the document, fill the field with "None." Provide the extracted date in JSON format with "injury date" as the key.
        2. 'Admission Date': Extract the date of the patient's admission from the given medical text. There can be multiple admission dates present in the text. Consider the date of the initial examination, initial visit, or the first time the patient was seen in as the admission date. The date with labels such as "Admit date" or "Admission date" should be considered as the admission date. If the admission date is not mentioned in the document, fill the field with "None." Provide the extracted date in JSON format with "admission date" as the key.
        3. 'Discharge Date': Extract the date of the patient's discharge from the given medical text. There can be multiple discharge dates present in the text. Consider the date of the last visit or the last time the patient was seen as the discharge date. The date with labels such as "Discharge date" or "Date of Discharge" should be considered as the discharge date. If the discharge date is not mentioned in the document, fill the field with "None." Provide the extracted date in JSON format with "discharge date" as the key.

        Note: Convert the final output to dd/mm/yyyy format
        """

        prompt_template = """
        Human: Use the following pieces of context to provide a concise answer to the question at the end. If you don't know the answer, don't try to make up an answer.
        <context>
        {context}
        </context>

        Question: {question}

        Assistant:"""

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

        query = """
        Your task is to identify the valid name and the date of birth of the patient from the user-provided text without including additional information, notes, and context. 

        Please follow the below guidelines:
        1) Consider Date of Birth, Birth Date, and DOB as date_of_birth.
        2) Do not consider age as value in date_of_birth.
        3) Consider Patient Name, only Patient, only Name and RE as patient_name.

        Please strictly only provide a JSON result containing the keys 'patient_name' and 'date_of_birth' containing a string as a value.
        """

        chain_qa = load_qa_chain(self.llm, chain_type="refine")
        result = chain_qa.run(input_documents=docs, question=query)
        response = await self.__convert_str_into_json(result)
        return response
