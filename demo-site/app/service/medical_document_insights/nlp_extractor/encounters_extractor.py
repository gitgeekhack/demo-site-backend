import os
import re
import ast
import time

from langchain.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.llms.bedrock import Bedrock
from langchain.prompts import PromptTemplate
from langchain.docstore.document import Document
from langchain.embeddings import BedrockEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app import logger
from app.constant import BotoClient
from app.constant import MedicalInsights
from app.service.medical_document_insights.nlp_extractor import bedrock_client, get_llm_input_tokens


class EncountersExtractor:
    def __init__(self):
        os.environ['AWS_DEFAULT_REGION'] = BotoClient.AWS_DEFAULT_REGION
        self.bedrock_client = bedrock_client
        self.model_id_llm = 'anthropic.claude-v2:1'
        self.model_embeddings = 'amazon.titan-embed-text-v1'

        self.anthropic_llm = Bedrock(
            model_id=self.model_id_llm,
            model_kwargs={
                "max_tokens_to_sample": 4000,
                "temperature": 0.00,
                "top_p": 1,
                "top_k": 0,
                "stop_sequences": [],
            },
            client=self.bedrock_client,
        )

        self.titan_llm = Bedrock(model_id=self.model_embeddings, client=self.bedrock_client)
        self.bedrock_embeddings = BedrockEmbeddings(model_id=self.model_embeddings, client=self.bedrock_client)

    async def __find_page_range(self, page_indexes_dict, chunk_indexes):
        start_index, end_index = chunk_indexes
        page_numbers = []
        for page, indexes in page_indexes_dict.items():
            if indexes[0] <= start_index <= indexes[1] or indexes[0] <= end_index <= indexes[1]:
                page_numbers.append(int(page.split('_')[1]))
        start_page = page_numbers[0]
        end_page = page_numbers[-1]
        return [start_page, end_page]

    async def __data_formatter(self, filename, json_data):
        """ This method is used to format the data and prepare chunks """
        raw_text = ""
        list_of_page_contents = []
        page_indexes_dict = {}
        page_start_index = 0
        for page, content in json_data.items():
            raw_text += content
            list_of_page_contents.append(Document(page_content=content, metadata={'page': int(page.split('_')[1])}))
            page_indexes_dict[page] = [int(page_start_index), int(page_start_index) + len(content) - 1]
            page_start_index += len(content)


        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=20000, chunk_overlap=200
        )

        texts = text_splitter.split_text(raw_text)

        for text in texts:
            threshold = self.anthropic_llm.get_num_tokens(text)
            if threshold > 6000:
                text_splitter = RecursiveCharacterTextSplitter(
                    chunk_size=10000, chunk_overlap=200
                )
                texts = text_splitter.split_text(raw_text)
                break

        chunk_length = []
        docs = []
        chunk_start_index = 0
        for text in texts:
            chunk_indexes = [int(chunk_start_index), int(chunk_start_index) + len(text) - 1]
            chunk_start_index += len(text)

            chunk_length.append(self.anthropic_llm.get_num_tokens(text))
            start_page, end_page = await self.__find_page_range(page_indexes_dict, chunk_indexes)
            # Create multiple documents
            docs.append(Document(page_content=text, metadata={'source': filename, 'start_page': start_page, 'end_page': end_page}))
        return docs, chunk_length, list_of_page_contents

    async def __get_stuff_calls(self, docs, chunk_length):
        stuff_calls = []
        current_chunk = []
        total_length = 0
        lengths = []

        for doc, length in zip(docs, chunk_length):
            if total_length + length >= 100000:
                lengths.append(total_length)

                stuff_calls.append(current_chunk)
                current_chunk = []
                total_length = 0
            current_chunk.append(doc)
            total_length += length

        # Add any remaining documents to the last chunk
        if current_chunk:
            lengths.append(total_length)

            stuff_calls.append(current_chunk)

        return stuff_calls

    async def __get_page_number(self, date_with_event, list_of_page_contents, relevant_chunks):
        cosine_similarities = []
        for chunk in relevant_chunks:
            all_text = [chunk.page_content]
            all_text.append(date_with_event)

            vectorizer = CountVectorizer()
            vectorized_text = vectorizer.fit_transform(all_text)

            cosine_similarities.append(cosine_similarity(vectorized_text[-1], vectorized_text[:-1]).flatten())
            all_text = []

        # Find the index of the page with the highest cosine similarity
        most_similar_chunk_index = cosine_similarities.index(max(cosine_similarities))

        most_similar_chunk = relevant_chunks[most_similar_chunk_index]
        filename = most_similar_chunk.metadata['source']
        start_page = most_similar_chunk.metadata['start_page']
        end_page = most_similar_chunk.metadata['end_page']
        relevant_pages = list_of_page_contents[start_page - 1: end_page]

        cosine_similarities = []
        for page in relevant_pages:
            all_text = [page.page_content]
            all_text.append(date_with_event)

            vectorizer = CountVectorizer()
            vectorized_text = vectorizer.fit_transform(all_text)

            cosine_similarities.append(cosine_similarity(vectorized_text[-1], vectorized_text[:-1]).flatten())
            all_text = []

        # Find the index of the page with the highest cosine similarity
        most_similar_page_index = cosine_similarities.index(max(cosine_similarities))

        most_similar_page = [page.metadata['page'] for page in relevant_pages][most_similar_page_index]

        return most_similar_page, filename

    async def __post_processing(self, list_of_page_contents, response, relevant_chunks):
        """ This method is used to post-process the LLM response """

        try:
            # Use a regular expression to find the list in the string
            string_of_tuples = re.search(r'\[.*?\]', response, re.DOTALL).group()

            try:
                # Convert the string of tuples into a list of tuples
                list_of_tuples = ast.literal_eval(string_of_tuples.replace('“', '"').replace('”', '"'))

            except Exception:
                # Use a regular expression to match the dates and events
                matches = re.findall(r'\(([^,]*), ([^\)]*)\)', string_of_tuples)

                # Convert the matches to a list of tuples
                list_of_tuples = [(date.strip(), event.strip()) for date, event in matches]

            encounters = []
            for date, event in list_of_tuples:
                date_with_event = date+" "+event
                page, filename = await self.__get_page_number(date_with_event, list_of_page_contents, relevant_chunks)
                encounters.append({'date': date.replace('/', '-'), 'event': event, 'document_name': filename, 'page_no': page})

            return encounters

        except Exception:
            return []

    async def get_encounters(self, document):
        """ This method is used to generate the encounters """
        filename = os.path.basename(document['name'])
        data = document['page_wise_text']
        x = time.time()
        docs, chunk_length, list_of_page_contents = await self.__data_formatter(filename, data)
        stuff_calls = await self.__get_stuff_calls(docs, chunk_length)
        emb_tokens = 0
        for i in docs:
            emb_tokens += self.titan_llm.get_num_tokens(i.page_content)

        z = time.time()
        logger.info(f'[Medical-Insights][Encounter] Chunk Preparation Time: {z - x}')

        query = MedicalInsights.Prompts.ENCOUNTER_PROMPT
        prompt_template = MedicalInsights.Prompts.PROMPT_TEMPLATE
        prompt = PromptTemplate(
            template=prompt_template, input_variables=["context", "question"]
        )

        encounters = []
        for docs in stuff_calls:
            vectorstore_faiss = FAISS.from_documents(
                documents=docs,
                embedding=self.bedrock_embeddings,
            )
            y = time.time()
            logger.info(f'[Medical-Insights][Encounter][{self.model_embeddings}] Input Embedding tokens: {emb_tokens} '
                        f'and Generation time: {y - z}')

            logger.info(f'[Medical-Insights][Encounter][{self.model_embeddings}] Embedding tokens for LLM call: '
                        f'{self.titan_llm.get_num_tokens(query) + self.titan_llm.get_num_tokens(prompt_template)}')

            qa = RetrievalQA.from_chain_type(
                llm=self.anthropic_llm,
                chain_type="stuff",
                retriever=vectorstore_faiss.as_retriever(
                    search_type="similarity", search_kwargs={"k": len(docs)}
                ),
                return_source_documents=True,
                chain_type_kwargs={"prompt": prompt}
            )

            answer = qa({"query": query})
            response = answer['result']
            relevant_chunks = answer['source_documents']
            input_tokens = get_llm_input_tokens(self.anthropic_llm, answer) + self.anthropic_llm.get_num_tokens(prompt_template)
            output_tokens = self.anthropic_llm.get_num_tokens(response)

            logger.info(f'[Medical-Insights][Encounter][{self.model_id_llm}] Input tokens: {input_tokens} '
                        f'Output tokens: {output_tokens} LLM execution time: {time.time() - y}')

            encounters_list = await self.__post_processing(list_of_page_contents, response, relevant_chunks)
            encounters.extend(encounters_list)

        return {'encounters': encounters}
