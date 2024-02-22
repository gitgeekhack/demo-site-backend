import os
import json
import time

from app import logger
from app.common.utils import update_file_path, vector_data_path

from langchain.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.llms.bedrock import Bedrock
from langchain.prompts import PromptTemplate
from langchain.docstore.document import Document
from langchain.embeddings import BedrockEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from app.constant import BotoClient
from app.service.medical_document_insights.nlp_extractor import bedrock_client

class DocumentQnA:
    def __init__(self):
        os.environ['AWS_DEFAULT_REGION'] = BotoClient.AWS_DEFAULT_REGION
        self.bedrock_client = bedrock_client

        self.llm = Bedrock(
            model_id="anthropic.claude-instant-v1",
            model_kwargs={
                "max_tokens_to_sample": 4000,
                "temperature": 0.75,
                "top_p": 0.01,
                "top_k": 0,
                "stop_sequences": [],
            },
            client=self.bedrock_client,
        )

        self.bedrock_embeddings = BedrockEmbeddings(model_id="amazon.titan-embed-text-v1", client=self.bedrock_client)
        self.prompt = self.__create_prompt_template()

    def __create_prompt_template(self):

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

    async def __prepare_data(self, document_name):

        doc_basename = os.path.basename(document_name).split(".")[0]
        vector_file = os.path.join(vector_data_path, f'{doc_basename}.pkl')

        if os.path.exists(vector_file):
            vectored_data = FAISS.load_local(vector_data_path, self.bedrock_embeddings, index_name=doc_basename)
        else:
            pdf_name, output_dir = await update_file_path(document_name)
            dir_name = os.path.join(output_dir, 'textract_response')
            with open(f'{dir_name}/{pdf_name}_text.json', 'r') as file:
                json_data = json.loads(file.read())

            raw_text = "".join(json_data.values())
            texts = RecursiveCharacterTextSplitter(chunk_size=15000, chunk_overlap=200).split_text(raw_text)
            docs = [Document(page_content=t) for t in texts]
            vectored_data = FAISS.from_documents(
                documents=docs,
                embedding=self.bedrock_embeddings,
            )
            vectored_data.save_local(vector_data_path, index_name=doc_basename)

        return vectored_data

    async def __create_conversation_chain(self, vectored_data, prompt_template):

        qa = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=vectored_data.as_retriever(
                search_type="similarity", search_kwargs={"k": 6}
            ),
            chain_type_kwargs={"prompt": prompt_template},
        )

        return qa

    async def get_query_response(self, query, document):

        x = time.time()
        vectored_data = await self.__prepare_data(document)
        logger.info(f"[Medical-Insights-QnA] Input data preparation for LLM is completed in {time.time() - x} seconds.")

        x = time.time()
        conversation_chain = await self.__create_conversation_chain(vectored_data, self.prompt)
        answer = conversation_chain({'query': query})
        logger.info(f"[Medical-Insights-QnA] LLM generated response for input query in {time.time() - x} seconds.")

        return answer
