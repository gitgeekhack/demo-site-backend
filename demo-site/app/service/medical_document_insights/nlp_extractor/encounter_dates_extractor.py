import os
import re
import ast
import boto3
from langchain.chains import RetrievalQA
from langchain.docstore.document import Document
from langchain.embeddings import BedrockEmbeddings
from langchain.llms.bedrock import Bedrock
from langchain.prompts import PromptTemplate
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS


class BrEmbeddingsEncounterExtractor:
    def __init__(self):
        # Initialize the bedrock client
        os.environ['AWS_PROFILE'] = "default"
        os.environ['AWS_DEFAULT_REGION'] = "us-east-1"
        self.bedrock = boto3.client('bedrock-runtime', region_name="us-east-1")
        # Initialize the model Id
        self.modelIdLlm = 'anthropic.claude-v2:1'
        self.modelIdEmbeddings = 'amazon.titan-embed-text-v1'
        # Load the llm model
        self.llm = Bedrock(
            model_id=self.modelIdLlm,
            model_kwargs={
                "max_tokens_to_sample": 4000,
                "temperature": 0.00,
                "top_p": 1,
                "top_k": 0,
                "stop_sequences": [],
            },
            client=self.bedrock,
        )
        # Load the bedrock embeddings
        self.bedrock_embeddings = BedrockEmbeddings(model_id=self.modelIdEmbeddings, client=self.bedrock)

    def generate_response(self, data):
        docs = self.data_formatter(data)
        vectorstore_faiss = FAISS.from_documents(
            documents=docs,
            embedding=self.bedrock_embeddings,
        )
        query = """
        Above text is obtained from medical records. Based on the information provided, you are tasked with extracting the 'Encounter Date' and corresponding 'Event' from medical records.
        'Encounter Date' : In medical record, it is defined as the specific date when a patient had an interaction with a healthcare provider. This could be a visit to a clinic, a hospital admission, a telemedicine consultation, or any other form of medical service. 
        Ensure all the actual 'Encounter Date' are converted to 'dd/mm/yyyy' format. Ensure none of the 'Encounter Date' is left behind.
        'Event' : It is associated with the corresponding 'Encounter Date'. It is described as the summary of all activities that occurred on that particular 'Encounter Date'. 
        Ensure all 'Event' descriptions should include the key points, context, and any relevant supporting details. Also ensure all 'Event' descriptions are more detailed, thorough and comprehensive yet a concise summary in medium-sized paragraph. 
        You are required to present this output in a specific format using 'Tuple' and 'List'. 
        Strictly adhere to the format explained as below and strictly avoid giving output in any other format.
        'Tuple' : It is used to store multiple items - in this case, the 'Encounter Date' and 'Event'. It is created using parentheses and should be formatted as (Encounter Date, Event).
        'List' : It is used to store multiple items - in this case, the 'Tuple'. It is created using square brackets and should be formatted as [ (Encounter Date, Event) ].
        Additionally, arrange all tuples in the list in ascending or chronological order based on the 'Encounter Date'.
        Note: This extraction process is crucial for various aspects of healthcare, including patient care tracking, scheduling follow-up appointments, billing, and medical research. Your attention to detail and accuracy in this task is greatly appreciated.
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
        try:
            return self.post_processing(response)
        except:
            return {'response': f'Something went wrong\n{response}'}

    def data_formatter(self, json_data):
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
        # Create multiple documents
        docs = [Document(page_content=t) for t in texts]
        return docs

    def post_processing(self, response):
        # Use a regular expression to find the list in the string
        string_of_tuples = re.search(r'\[.*?\]', response, re.DOTALL).group()
        try:
            # Convert the string of tuples into a list of tuples
            list_of_tuples = ast.literal_eval(string_of_tuples.replace('“', '"').replace('”', '"'))
        except:
            # Use a regular expression to match the dates and events
            matches = re.findall(r'\(([^,]*), ([^\)]*)\)', string_of_tuples)
            # Convert the matches to a list of tuples
            list_of_tuples = [(date.strip(), event.strip()) for date, event in matches]

        # Convert the list of tuples to a dictionary
        output_json = {date: event for date, event in list_of_tuples}
        return output_json
