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
        Above text is obtained from medical records. Based on the information provided, you are tasked with extracting the 'Encounter Date' and corresponding 'Event' from medical records.
        'Encounter Date' : In medical record, it is defined as the specific date when a patient had an interaction with a healthcare provider. This could be a visit to a clinic, a hospital admission, a telemedicine consultation, or any other form of medical service. 
        Ensure all the actual 'Encounter Date' are converted to 'dd/mm/yyyy' format. Ensure none of the 'Encounter Date' is left behind.
        'Event' : It is associated with the corresponding 'Encounter Date'. It is described as all the activities that occurred on that particular 'Encounter Date'. 
        Ensure all 'Event' descriptions are more detailed, thorough and comprehensive in very long paragraph.
        You are required to present this output in a specific format using 'Tuple' and 'List'. 
        Strictly adhere to the format explained as below and strictly avoid giving output in any other format.
        'Tuple' : It is used to store multiple items - in this case, the 'Encounter Date' and 'Event'. It is created using parentheses and should be formatted as (Encounter Date, Event).
        'List' : It is used to store multiple items - in this case, the 'Tuple'. It is created using square brackets and should be formatted as [ (Encounter Date, Event) ].
        Additionally, arrange all tuples in the list in ascending or chronological order based on the 'Encounter Date'.
        Note: This extraction process is crucial for various aspects of healthcare, including patient care tracking, scheduling follow-up appointments, billing, and medical research. Your attention to detail and accuracy in this task is greatly appreciated.
        """
        chain_qa = load_qa_chain(llm, chain_type="refine")
        response = chain_qa.run(input_documents=docs, question=query)
        return self.post_processing(response)

    def data_formatter(self, json_data):
        raw_text = "".join(json_data.values())
        return raw_text

    def post_processing(self, response):
        # Use a regular expression to find the list in the string
        string_of_tuples = re.search(r'\[.*?\]', response, re.DOTALL).group()
        # Convert the string of tuples into a list of tuples
        list_of_tuples = eval(string_of_tuples)
        # Convert the list of tuples to a dictionary
        output_json = {date: event for date, event in list_of_tuples}
        return output_json