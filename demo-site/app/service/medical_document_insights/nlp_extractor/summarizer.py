import boto3
import os
from langchain.llms.bedrock import Bedrock
from langchain.embeddings import BedrockEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter


class SummarizerWrapper:
    def __init__(self):
        # Initialize the bedrock client
        os.environ['AWS_PROFILE'] = "default"
        os.environ['AWS_DEFAULT_REGION'] = "us-east-1"
        self.bedrock = boto3.client('bedrock-runtime', region_name="us-east-1")
        # Initialize the model Id
        self.modelId = 'anthropic.claude-v2'
        self.modelIdEmbeddings = 'amazon.titan-embed-text-v1'
        # Load the llm model
        self.llm = Bedrock(
            model_id=self.modelId,
            model_kwargs={
                "max_tokens_to_sample": 10000,
                "temperature": 0.5,
                "top_p": 0.9,
                "top_k": 250,
            },
            client=self.bedrock,
        )
        # Load the bedrock embeddings
        self.bedrock_embeddings = BedrockEmbeddings(model_id=self.modelIdEmbeddings, client=self.bedrock)

    def generate_summary(self, json_data):
        docs = self.data_formatter(json_data)
        vectorstore_faiss = FAISS.from_documents(
            documents=docs,
            embedding=self.bedrock_embeddings,
        )
        query = """Generate a detailed and accurate summary based on the user's input. Specifically, concentrate on identifying key medical diagnoses, outlining treatment plans, and highlighting pertinent aspects of the medical history. Strive for precision and conciseness to deliver a focused and insightful summary."""
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
        summary = self.pre_process_summary(response)
        final_summary = self.post_process_summary(summary)
        summary_dict = {
            "summary": final_summary
        }
        return summary_dict

    def data_formatter(self, json_data):
        raw_text = "".join(json_data.values())
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=10000, chunk_overlap=200
        )
        texts = text_splitter.split_text(raw_text)
        docs = [Document(page_content=t) for t in texts]
        return docs

    def pre_process_summary(self, summary):
        text = summary.replace('- ', '')
        return text

    def post_process_summary(self, summary):
        text = summary.strip()
        lines = text.split('\n')
        if lines[-1].__contains__('?'):
            lines = lines[:-1]
        modified_text = '\n'.join(lines)
        return modified_text
