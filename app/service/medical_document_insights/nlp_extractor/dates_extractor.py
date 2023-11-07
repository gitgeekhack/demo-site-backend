import re
import boto3
import os
import json
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.llms.bedrock import Bedrock
from langchain.chains.question_answering import load_qa_chain
from langchain.docstore.document import Document

class BedrockDatesExtractor:
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
                "stop_sequences": ['}'],
                "return_likelihoods": "NONE",
            },
            client=self.bedrock,
        )
        return llm


    def generate_response(self, raw_text, llm):
        # Instantiate the LLM model
        llm = llm
        # Split text
        text_splitter = RecursiveCharacterTextSplitter(
         chunk_size=10000, chunk_overlap=200
        )
        texts = text_splitter.split_text(raw_text)
        # Create multiple documents
        docs = [Document(page_content=t) for t in texts]
        query = '''In this task, your role is to extract crucial dates from a medical document, specifically focusing on the injury date, admission date, and discharge date. This information is vital for medical records management and analysis. Your sole purpose is to provide the output in JSON format, donot provide any other output other than the JSON output.
                'injury date' : Extract the date of the patient's injury from the given medical text. Provide the date in a consistent format. If the injury date is not mentioned in the document, fill the field with "None". Provide the extracted date in JSON format with "injury date" as the key
                'admission date' : Extract the date of the patient's admission from the given medical text. Provide the date in a consistent format. If the admission date is not mentioned in the document, fill the field with "None". Provide the extracted date in JSON format with "admission date" as the key.
                'discharge date' : Extract the date of the patient's discharge from the given medical text. Provide the date in a consistent format. If the discharge date is not mentioned in the document, fill the field with "None". Provide the extracted date in JSON format with "discharge date" as the key.
                '''
        chain_qa = load_qa_chain(llm, chain_type="refine")
        temp = chain_qa.run(input_documents=docs, question=query)
        return temp
    def data_formatter(self, json_data):
        raw_text = "".join(json_data.values())
        return raw_text

    def extract_values_between_curly_braces(self, text):
        pattern = r'\{.*?\}'
        matches = re.findall(pattern, text, re.DOTALL)
        return matches


if __name__ == "__main__":
    json_data = {
    "Page 1": "Los Robles Hospital and Medical Center 215 West Janss Road, Thousand Oaks, California 91360 (805) 497-2727 N O STATE R PAT-IBNT ADIMISSI o R ECORD ACCOUNT#: G00219014660 ADM DATE: :02/23/16 UNIT RCRD #:G000306466 ARRIVAL:AMB ROOM/BED: 3140-A ADM TIME:0228 MARKET URN: G245754 CONF: VIP:N PT. TYPE:DIS IN ADMIT PRI/SRC:TR / PR LOCATION (S) G. 3MED FC:07 PACTIENT I N RFO R M A T I O. N NAME: CARTER, DANIEL B OTHER NAME: UNK,UN STREET: 6039 DOVETAIL DRIVE DOB: 10/18/1991 SS#: XXX-XX-7777 STREET: AGE: 24 RACE: WHITE/CAUC C/S/ZP: AGOURA HILLS, 91301 SEX: M MAR STATUS: S PHONE#: (818)597-0622 CNTY/RES: LA REL: CATHOLIC LANG: ENGLISH S S PERSON TO NOTTEY CARTER, ANNE CARTER, WILLIAM 6039 DOVETAIL DRIVE 6039 DOVETAIL DRIVE AGOURA HILLS, CA 91301 AGOURA HILLS,CA 91301 (818) 421-7383 RELTN: MOTHER (818)421-7399 RELTN: FATHER WORK PH: WORK PH: PAATEANT G-USARAENO R ARTISAN CUSTOM REMODEL CARTER, DANIEL B 6039 DOVETAIL DRIVE 6039 DOVETAIL DRIVE AGOURA, CA 91301 AGOURA HILLS, CA 91301 (818) 597-0622 OCC: STAFF (818)597-0622 RELTN: SELF GUO A RANTO OCCURRENCE CODES CONDITION CODES ARTISAN CUSTOM REMODEL 01 02/23/16 6039 DOVETAIL DRIVE AGOURA, CA 91301 (818)597-0622 IN-SG.RANCE TFOPRSMAN PRIMARY: BSHMO - 34509 SECONDARY: AUTX035 - 22835 TERTIARY: BLUE SHIELD HMO AXMINSTER AUTO INSURANCE PENDING PO BOX 272540 CHICO, CA 95927-2540 CA 99999 POLICY #:XEH903241712 POLICY #:777777777 POLICY #: COVERAGE : AXMINSTER COVERAGE #: COVERAGE #: INS PHONE #: (800)541-6652 INS PHONE #: (999)999-9999 INS PHONE #: GRP #:W0051411 GRP#: GRP#: AUTH #:PENDING/I AUTH #: AUTH #: AUTH DT: 02/23 VER DT: 02/23 AUTH DT: VER DT: AUTH DT: VER DT: SUB: CARTER, ANNE M SUB: CARTER DANIEL B SUB: RELAT: SA DOB: 10/18/1991 RELAT: SA DOB: 10/18/1991 RELAT: DOB: ADM: SUPBR Supple, Brian J MD PCP: NO PCP NO PRIMARY OR FAMILY PHYSICIAN HCS 1064 (805) 499-7971 HCS:7943 ATT: SUPBR Supple,Brian J MD REF:.SELF SELF REFERRED HCS :1064 (805) 499-7971 HCS: 9715 ER: ROBJOR Roberts, Jordan DO, 7098 REASON FOR VISIT/CHIEF COMPL:CODE GREEN TR2 MVA AMS FRONTAL SKULL FX PRINCIPAL DIAGNOSIS: FOR MR USE ONLY Assembly PRINCIPAL OPERATION/PROCEDURE: Analysis Coding CONSULTATIONS: Printed Final Check COMMENTS: NOTES ADVANCE DIRECTIVE:N PRT BY:R.HIM.) RLM ON:04/07/16 1830 DISCH DATE: 04/07/16 TIME: 1500 DISPO: PAT Patient:CARTER, DANIEL B MRN:G000306466 Encounter:G00219014660 Page 1 of 1 LOS ROBLES HOSPITAL AND MEDICAL CENTER [5890040-01] 2427 "
}
    extractor = BedrockDatesExtractor()
    raw_text = extractor.data_formatter(json_data)
    result = extractor.generate_response(raw_text, extractor.loaded_llm)
    try:
        json_result = json.loads(result)
        print(json_result)
    except Exception as e:
        matches = extractor.extract_values_between_curly_braces(result)
        json_result = json.loads(matches[0])
        print(json_result)

