import re
import boto3
import os
import json
from langchain.llms.bedrock import Bedrock
from langchain.chains.question_answering import load_qa_chain

class BedrockDatesExtractor:
    def __init__(self):
        # Initialize the Textract client
        os.environ['AWS_PROFILE'] = "default"
        os.environ['AWS_DEFAULT_REGION'] = "us-east-1"
        self.bedrock = boto3.client('bedrock-runtime', region_name="us-east-1")
        self.modelId = 'cohere.command-text-v14'

        self.llm = Bedrock(
            model_id=self.modelId,
            model_kwargs={
                "max_tokens": 4000,
                "temperature": 0.75,
                "p": 0.01,
                "k": 0,
                "stop_sequences": ['}'],
                "return_likelihoods": "NONE",
            },
            client=self.bedrock,
        )

    def load_llm_model(self):
        modelId = "cohere.command-text-v14"

        llm = Bedrock(

            model_id=modelId,
            model_kwargs={
                "max_tokens": 4000,
                "temperature": 0.75,
                "p": 0.01,
                "k": 0,
                "stop_sequences": ['}'],
                "return_likelihoods": "NONE",
            },
            client=self.bedrock,
        )
        return llm

    def get_key(self, key):
        if "injury" in key.lower():
            result_key = "Injury Date"
        elif "admission" in key.lower():
            result_key = "Admission Date"
        elif "discharge" in key.lower():
            result_key = "Discharge Date"
        return result_key

    def generate_response(self, docs):
        query = """
                Your role is to extract important dates from a medical document, specifically focusing on the injury dates, admission dates, and discharge dates. This information is vital for medical records management and analysis. Your sole purpose is to provide the output in JSON format, without any additional text output.Don't refine anything, give an original answer.
                Provide the information in JSON format as follows: {"Injury date": ["dd/mm/yyyy", ...], "Admission date": ["dd/mm/yyyy", ...], "Discharge date": ["dd/mm/yyyy", ...]}. Strictly maintain the consistency in this format.
                Note: Don't include visit dates, encounter dates, date of birth, MRI scan dates, X-ray dates, checkup dates, admin date/time, follow-up dates and 'filed at' date.

                Instructions:
                1. 'Injury Date': Extract the date of the patient's injury from the given medical text. There can be multiple injury dates present in the text. If the injury date is not mentioned in the document, fill the field with "None." Provide the extracted date in JSON format with "injury date" as the key.
                2. 'Admission Date': Extract the date of the patient's admission from the given medical text. There can be multiple admission dates present in the text. Consider the date of the initial examination, initial visit, or the first time the patient was seen in as the admission date. The date with labels such as "Admit date" or "Admission date" should be considered as the admission date. If the admission date is not mentioned in the document, fill the field with "None." Provide the extracted date in JSON format with "admission date" as the key.
                3. 'Discharge Date': Extract the date of the patient's discharge from the given medical text. There can be multiple discharge dates present in the text. Consider the date of the last visit or the last time the patient was seen as the discharge date. The date with labels such as "Discharge date" or "Date of Discharge" should be considered as the discharge date. If the discharge date is not mentioned in the document, fill the field with "None." Provide the extracted date in JSON format with "discharge date" as the key.
                """
        chain_qa = load_qa_chain(self.llm, chain_type="refine")
        result = chain_qa.run(input_documents=docs, question=query)
        try:
            matches = self.extract_values_between_curly_braces(result)
            json_result = json.loads(matches[0])
            jr = {}
            for key, value in json_result.items():
                result_key = self.get_key(key)
                jr[result_key] = value if isinstance(value, list) else [value]
            return jr
        except Exception as e:
            return {}

    def data_formatter(self, json_data):
        raw_text = "".join(json_data.values())
        return raw_text

    def extract_values_between_curly_braces(self, text):
        pattern = r'\{.*?\}'
        matches = re.findall(pattern, text, re.DOTALL)
        return matches