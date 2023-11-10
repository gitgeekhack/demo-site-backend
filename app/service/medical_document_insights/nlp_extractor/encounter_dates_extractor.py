import json

import boto3
import os
import re
from langchain.llms.bedrock import Bedrock
from langchain.chains.question_answering import load_qa_chain


class BedrockEncounterDatesExtractor:
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
                "stop_sequences": [],
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
                "stop_sequences": [],
                "return_likelihoods": "NONE",
            },
            client=self.bedrock,
        )
        return llm

    def generate_response(self, docs):

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
        chain_qa = load_qa_chain(self.llm, chain_type="refine")
        response = chain_qa.run(input_documents=docs, question=query)
        try:
            return self.post_processing(response)
        except:
            return {'document_origanizer'
                    : "Something went wrong\n The refined answer is as follows:\n\nThe 'Encounter Date' and 'Event' from "
                      "the medical records provided are as follows:\n1. (12/12/2015, Patient visit to clinic for medical "
                      "examination)\n2. (15/06/2023, Results of medical examination and diagnostic tests)\n3. (30/11/2018, "
                      "Medical history report)\n\nThe 'Event' descriptions are detailed below:\n1. On 12/12/2015, "
                      "the patient visited the clinic for a medical examination. A comparison was not made as no previous "
                      "examination report was provided. The examination focused on the patient's cardiovascular system and "
                      "identified several notable findings. \n2. The results of the medical examination and diagnostic "
                      "tests ordered on 15/06/2023 are as follows: The patient's heart was found to be in normal condition, "
                      "with no signs of pericardial effusion or thickening. However, the patient was diagnosed with mild "
                      "stenosis in the left anterior descending artery (LAD). A calcium score of 48 indicated mild to "
                      "moderate coronary artery narrowing. The patient was advised to continue taking prescribed "
                      "medications and to schedule a follow-up appointment for further evaluation.\n3. The medical history "
                      "report, generated on 30/11/2018, detailed the patient's medical conditions and health concerns. It "
                      "mentioned the patient's history of cardiovascular disease and the ongoing treatment plan, "
                      "including medications and lifestyle modifications. It also documented the patient's family history "
                      "of heart disease and the recent medical examination results. \n\nPlease note that the provided "
                      "information is extracted from the given medical records. If further information is required, "
                      "additional context will be provided.\n\nIs there anything else I can help you with regarding medical "
                      "records extraction or formatting?"
                    }

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
