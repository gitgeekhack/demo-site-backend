import os
import json
import boto3

from langchain.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.llms.bedrock import Bedrock
from langchain.prompts import PromptTemplate
from langchain.docstore.document import Document
from langchain.embeddings import BedrockEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter


class DocumentQnA:
    def __init__(self):
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

        self.embeddings = BedrockEmbeddings(model_id="amazon.titan-embed-text-v1", client=self.boto3_bedrock)
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

        dir_name = document_name.replace(".pdf", "")
        pdf_name = os.path.basename(dir_name)
        dir_name = os.path.join(dir_name, 'textract_response')

        with open(f'{dir_name}/{pdf_name}_text.json', 'r') as file:
            json_data = json.loads(file.read())

        raw_text = "".join(json_data.values())

        texts = RecursiveCharacterTextSplitter(chunk_size=20000, chunk_overlap=200).split_text(raw_text)

        threshold = self.cohere_llm.get_num_tokens(texts[0])

        if threshold >= 3650:
            texts = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=200).split_text(raw_text)

        docs = [Document(page_content=t) for t in texts]

        vectored_data = FAISS.from_documents(
            documents=docs,
            embedding=self.embeddings,
        )

        return vectored_data

    async def __create_conversation_chain(self, vectored_data, prompt_template):

        qa = RetrievalQA.from_chain_type(
            llm=self.cohere_llm,
            chain_type="stuff",
            retriever=vectored_data.as_retriever(
                search_type="similarity", search_kwargs={"k": 6}
            ),
            chain_type_kwargs={"prompt": prompt_template},
        )

        return qa

    async def __remove_question(self, output):

        text = output["result"].strip()
        lines = text.split('\n')

        if lines[-1].__contains__('?'):
            lines = lines[:-1]

        modified_text = '\n'.join(lines)
        output["result"] = modified_text

        return output

    async def get_query_response(self, query, document):

        try:
            vectored_data = await self.__prepare_data(document)
            conversation_chain = await self.__create_conversation_chain(vectored_data, self.prompt)
            answer = conversation_chain({'query': query})
            processed_answer = await self.__remove_question(answer)

            return processed_answer

        except Exception as e:
            return {'response': f'Exception: {e}\n{query}'}
