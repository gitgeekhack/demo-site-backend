from datetime import datetime
import boto3
import os
import re
import json
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.llms.bedrock import Bedrock
from langchain.chains.question_answering import load_qa_chain
from langchain.docstore.document import Document


class BedrockEncounterDatesExtractor:
    def __init__(self):
        # Initialize the Textract client
        os.environ['AWS_PROFILE'] = "default"
        os.environ['AWS_DEFAULT_REGION'] = "us-east-1"
        self.bedrock = boto3.client('bedrock-runtime', region_name="us-east-1")
        self.loaded_llm = self.load_llm_model()

    def load_llm_model(self):
        modelId = "cohere.command-text-v14"
        llm = Bedrock(
            model_id=modelId,
            model_kwargs={
                "max_tokens": 4000,
                "temperature": 0.75,
                "p": 0.01,
                "k": 0,
                "stop_sequences": [],
                "return_likelihoods": "NONE",
            },
            client=self.bedrock,
        )
        return llm

    def generate_response(self, json_data, llm):
        # Data Formatter
        raw_text = self.data_formatter(json_data)
        # Instantiate the LLM model
        llm = llm
        # Split text
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=10000, chunk_overlap=200
        )
        texts = text_splitter.split_text(raw_text)
        # Create multiple documents
        docs = [Document(page_content=t) for t in texts]

        query = """
        'Encounter Date' in medical records refers to the specific day when a patient had an interaction with a healthcare provider. This could be a visit to a clinic, a hospital admission, a telemedicine consultation, or any other form of medical service. The encounter date is important for tracking patient care, scheduling follow-up appointments, billing, and medical research.
        'Event' which is associated with the corresponding 'Encounter Date' is described as all the activities which are happened on that particular 'Encounter Date'.
        Above text is obtained from the medical record. Give all the actual 'Encounter Date' and corresponding 'Event' in the following JSON format { Encounter Date : Event }. Strictly maintain the given format of JSON.
        Note: Convert all the 'Encounter Date' in 'dd/mm/yyyy' format. Describe events in more detailed manner.
        """
        chain_qa = load_qa_chain(llm, chain_type="refine")
        response = chain_qa.run(input_documents=docs, question=query)
        return self.post_processing(response)

    def data_formatter(self, json_data):
        raw_text = "".join(json_data.values())
        return raw_text

    def post_processing(self, response):
        # Use a regular expression to find the dictionary in the string
        dict_string = re.search(r'\{.*?\}', response, re.DOTALL).group()
        # Use the json.loads function to convert the string into a dictionary
        result_json = json.loads(dict_string)
        # Convert the keys to datetime objects and store in a new dictionary
        result_with_datetime_keys = {datetime.strptime(date, '%m/%d/%Y'): event for date, event in result_json.items()}
        # Sort the dictionary by keys (i.e., dates) in ascending order
        sorted_result = dict(sorted(result_with_datetime_keys.items()))
        # Convert the datetime objects back to strings
        sorted_result_with_string_keys = {date.strftime('%m/%d/%Y'): event for date, event in sorted_result.items()}

        output_json = sorted_result_with_string_keys
        return output_json