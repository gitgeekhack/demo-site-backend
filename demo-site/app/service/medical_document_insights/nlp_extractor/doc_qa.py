import json
import os
import boto3
from langchain.embeddings import BedrockEmbeddings
from langchain.vectorstores import FAISS
from langchain.prompts import PromptTemplate
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.llms.bedrock import Bedrock
from langchain.docstore.document import Document
from langchain.chains import RetrievalQA


class MedicalAssistant:
    def __init__(self):
        os.environ['AWS_PROFILE'] = "default"
        os.environ['AWS_DEFAULT_REGION'] = "us-east-1"
        self.boto3_bedrock = boto3.client('bedrock-runtime', region_name="us-east-1")
        self.cohere_llm = Bedrock(
            model_id="cohere.command-text-v14",
            model_kwargs={
                "max_tokens": 4000,
                "temperature": 0.75,
                "p": 0.01,
                "k": 0,
                "stop_sequences": [],
                "return_likelihoods": "NONE",
            },
            client=self.boto3_bedrock,
        )
        self.br_embeddings = BedrockEmbeddings(model_id="amazon.titan-embed-text-v1", client=self.boto3_bedrock)
        self.prompt = self.create_prompt_template()

    def prepare_data(self, document_name):
        user_dir = os.path.join(USER_DATA_PATH, 'medical_insights_poc')
        pdf_files_directory = os.path.join(user_dir, 'pdf_files')
        input_dir = os.path.join(pdf_files_directory, document_name)
        pdf_name = input_dir.split("/")[-1].split(".")[0]

        json_dir = "medical_insights_poc/json_save"
        with open(f'{json_dir}/{pdf_name}_text.json', 'r') as file:
            json_data = json.loads(file.read())

        raw_text = "".join(json_data.values())
        texts = RecursiveCharacterTextSplitter(chunk_size=20000, chunk_overlap=200).split_text(raw_text)
        threshold = self.cohere_llm.get_num_tokens(texts[0])
        if threshold >= 3650:
            texts = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=200).split_text(raw_text)
        docs = [Document(page_content=t) for t in texts]
        vector_store = FAISS.from_documents(
            documents=docs,
            embedding=self.br_embeddings,
        )
        return vector_store

    def create_prompt_template(self):
        prompt_template = """
        Human: You are a Medical Assistant that provides concise answers to the questions related to the medical text context given to you. Strictly answer the questions related to the following information 
        <context>
        {context}
        </context>
        to answer in a helpful manner. If you don't know the answer, just say that you don't know, don't try to make up an answer.

        Question: {question}

        Medical Assistant:"""
        prompt = PromptTemplate(
            input_variables=["context", "question"], template=prompt_template
        )
        return prompt

    def create_conversation_chain(self, vector_store, prompt_template):
        qa = RetrievalQA.from_chain_type(
            llm=self.cohere_llm,
            chain_type="stuff",
            retriever=vector_store.as_retriever(
                search_type="similarity", search_kwargs={"k": 6}
            ),
            return_source_documents=True,
            chain_type_kwargs={"prompt": prompt_template},
            # verbose = True
        )

        return qa

    def remove_question(self, output):
        text = output['result'].strip()
        lines = text.split('\n')
        if lines[-1].__contains__('?'):
            lines = lines[:-1]
        modified_text = '\n'.join(lines)
        output['result'] = modified_text
        return output

    def run_medical_assistant(self, query, vector_store):
        conversation_chain = assistant.create_conversation_chain(vector_store, self.prompt)
        answer = conversation_chain({'query': query})
        print(answer)
        processed_answer = assistant.remove_question(answer)
        return processed_answer