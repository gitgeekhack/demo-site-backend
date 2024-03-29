import os
import time

from langchain.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.llms.bedrock import Bedrock
from langchain.prompts import PromptTemplate
from langchain.embeddings import BedrockEmbeddings

from app import logger
from app.constant import BotoClient
from app.service.medical_document_insights.nlp_extractor import bedrock_client, get_llm_input_tokens


class DocumentQnA:
    def __init__(self):
        os.environ['AWS_DEFAULT_REGION'] = BotoClient.AWS_DEFAULT_REGION
        self.bedrock_client = bedrock_client
        self.model_id_llm = 'anthropic.claude-instant-v1'
        self.model_embeddings = 'amazon.titan-embed-text-v1'

        self.anthropic_llm = Bedrock(
            model_id=self.model_id_llm,
            model_kwargs={
                "max_tokens_to_sample": 4000,
                "temperature": 0.75,
                "top_p": 0.01,
                "top_k": 0,
                "stop_sequences": [],
            },
            client=self.bedrock_client,
        )

        self.titan_llm = Bedrock(model_id=self.model_embeddings, client=self.bedrock_client)
        self.bedrock_embeddings = BedrockEmbeddings(model_id=self.model_embeddings, client=self.bedrock_client)
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

        self.prompt_template_tokens = self.anthropic_llm.get_num_tokens(prompt_template)

        prompt = PromptTemplate(
            input_variables=["context", "question"], template=prompt_template
        )

        return prompt

    async def __prepare_data(self, project_response_path):
        vectored_data = FAISS.load_local(project_response_path, self.bedrock_embeddings, index_name='embeddings')
        return vectored_data

    async def __create_conversation_chain(self, vectored_data, prompt_template):

        qa = RetrievalQA.from_chain_type(
            llm=self.anthropic_llm,
            chain_type="stuff",
            retriever=vectored_data.as_retriever(
                search_type="similarity", search_kwargs={"k": 6}
            ),
            return_source_documents=True,
            chain_type_kwargs={"prompt": prompt_template},
        )

        return qa

    async def get_query_response(self, query, project_response_path):

        x = time.time()
        vectored_data = await self.__prepare_data(project_response_path)
        logger.info(f"[Medical-Insights-QnA] Input data preparation for LLM is completed in {time.time() - x} seconds.")

        x = time.time()
        conversation_chain = await self.__create_conversation_chain(vectored_data, self.prompt)
        answer = conversation_chain({'query': query})

        input_tokens = get_llm_input_tokens(self.anthropic_llm, answer) + self.prompt_template_tokens
        output_tokens = self.anthropic_llm.get_num_tokens(answer['result'])

        logger.info(f'[Medical-Insights-QnA][{self.model_embeddings}] Embedding tokens for LLM call: '
                    f'{self.titan_llm.get_num_tokens(query) + self.prompt_template_tokens}')

        logger.info(f'[Medical-Insights-QnA][{self.model_id_llm}] Input tokens: {input_tokens} '
                    f'Output tokens: {output_tokens} LLM execution time: {time.time() - x}')

        logger.info(f"[Medical-Insights-QnA] LLM generated response for input query in {time.time() - x} seconds.")

        return answer
