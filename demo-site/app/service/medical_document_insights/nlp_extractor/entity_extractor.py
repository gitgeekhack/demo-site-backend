import os
import json
import boto3

from langchain.chains import RetrievalQA
from langchain.vectorstores import FAISS
from langchain.llms.bedrock import Bedrock
from langchain.prompts import PromptTemplate
from langchain.docstore.document import Document
from langchain.embeddings import BedrockEmbeddings


class EntityExtraction:
    def __init__(self):
        # Initialize the bedrock client
        os.environ['AWS_PROFILE'] = "default"
        os.environ['AWS_DEFAULT_REGION'] = "us-east-1"
        self.bedrock = boto3.client('bedrock-runtime', region_name="us-east-1")
        # Initialize the model Id
        self.modelIdLlm = 'anthropic.claude-instant-v1'
        self.modelIdEmbeddings = 'amazon.titan-embed-text-v1'
        # Load the llm model
        self.llm = Bedrock(
            model_id=self.modelIdLlm,
            model_kwargs={
                "max_tokens_to_sample": 10000,
                "temperature": 0.0,
                "top_p": 1,
                "top_k": 250
            },
            client=self.bedrock,
        )
        # Load the bedrock embeddings
        self.bedrock_embeddings = BedrockEmbeddings(model_id=self.modelIdEmbeddings, client=self.bedrock)

    def detect_entities(self, data):
        docs = [Document(page_content=data)]
        vectorstore_faiss = FAISS.from_documents(
            documents=docs,
            embedding=self.bedrock_embeddings,
        )
        query = """
            Your task is to identify valid diagnoses, valid treatments and valid medications from the user-provided text without including additional information, notes, and context. 

            The definition of a valid diagnosis, valid treatment and valid medications is given below:
            Diagnosis: It is a process of identifying a patient's medical condition based on the evaluation of symptoms, history, and clinical evidence.
            Treatment: It is a proven, safe, and effective therapeutic intervention aligned with medical standards, to manage or cure a diagnosed health condition.
            Medication: It refers to drugs or substances used to treat, prevent, or diagnose diseases, relieve symptoms, or improve health.

            Please follow the below guidelines:
            1. Do not consider any diagnosis, treatment or medication information with negation.
            2. Do not misinterpret the symptoms as diagnoses or treatments.
            3. Associate the system organs and direction of organs with the medical entities.
            4. Ensure a clear distinction between diagnosis, treatment and medications entities, avoiding overlap.
            5. Consider Signs and Medical Conditions as a diagnosis. 
            6. Consider Surgery, Psychotherapy, Immunotherapy, Imaging tests, and procedures as a treatment. 
            7. Do not consider any diagnosis or treatment with hypothetical or conditional statements.
            8. Do not consider the specialty of the doctor or practitioner as a medical entity.
            9. Avoid repeating diagnoses and treatments when different terms refer to the same medical condition or treatment.

            Please strictly only provide a JSON result containing the keys 'diagnosis', 'treatments' and 'medications' containing a list of valid entities.
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
        entities = self.convert_str_into_json(response)
        return entities

    def convert_str_into_json(self, text):
        start_index = text.find('{')
        end_index = text.rfind('}') + 1
        json_str = text[start_index:end_index]
        if len(json_str) == 0:
            final_data = {'diagnosis': [], 'treatments': [], 'medications': []}
            return final_data
        data = json.loads(json_str)
        data_keys = ['diagnosis', 'treatments', 'medications']
        final_data = dict(zip(data_keys, list(data.values())))
        return final_data

    def pagewise_entity_extractor(self, json_data):
        pagewise_entities = dict()
        for key, value in json_data.items():
            entities = self.detect_entities(value)
            pagewise_entities[key] = entities
        return pagewise_entities