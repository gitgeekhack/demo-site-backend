import boto3
import os
from langchain.llms.bedrock import Bedrock
from langchain.chains.summarize import load_summarize_chain


class LanguageModelWrapper:
    def __init__(self):
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

    def generate_summary(self, docs):
        chain = load_summarize_chain(self.llm, chain_type='refine')
        summary = chain.run(docs)

        summary_dict = {
            "summary": summary
        }
        return summary_dict