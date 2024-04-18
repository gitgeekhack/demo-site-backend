import os
import re
import ast
import time

import dateparser
from datetime import datetime

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


class MedicalChronologyExtractor:
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

    async def __find_page_range(self, page_indexes_dict, chunk_indexes, search_start_page):
        start_index, end_index = chunk_indexes
        search_index = end_index - 200
        start_page, end_page = None, None
        for page, indexes in list(page_indexes_dict.items())[search_start_page - 1:]:
            if indexes[0] <= start_index <= indexes[1]:
                start_page = int(page.split('_')[1])
            if indexes[0] <= end_index <= indexes[1]:
                end_page = int(page.split('_')[1])
            if indexes[0] <= search_index <= indexes[1]:
                search_start_page = int(page.split('_')[1])
            if start_page and end_page and search_start_page:
                break
        return start_page, end_page, search_start_page

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
        search_start_page = 1
        overlap = 0
        max_overlap = 200
        previous_text = ''
        for text in texts:
            current_text = text
            if len(previous_text) != 0:
                overlap_threshold = min(len(previous_text), len(current_text))
                possible_overlap = min(max_overlap, overlap_threshold)
                for i in range(1, possible_overlap + 1):
                    if previous_text[-i:] == current_text[:i]:
                        overlap = i
            chunk_start_index = chunk_start_index + len(previous_text) - overlap
            chunk_indexes = [int(chunk_start_index), int(chunk_start_index) + len(current_text) - 1]
            previous_text = current_text

            chunk_length.append(self.anthropic_llm.get_num_tokens(text))
            start_page, end_page, search_start_page = await self.__find_page_range(page_indexes_dict, chunk_indexes, search_start_page)
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

    async def __get_page_number(self, date_doctor_event, list_of_page_contents, relevant_chunks):
        if len(relevant_chunks) == 1:
            most_similar_chunk_index = 0
        else:
            cosine_similarities = []
            all_text = []
            for chunk in relevant_chunks:
                all_text.append(chunk.page_content)
                all_text.append(date_doctor_event)

                vectorizer = CountVectorizer()
                vectorized_text = vectorizer.fit_transform(all_text)

                cosine_similarities.append(cosine_similarity(vectorized_text[-1], vectorized_text[:-1]).flatten())
                all_text = []

            most_similar_chunk_index = cosine_similarities.index(max(cosine_similarities))

        most_similar_chunk = relevant_chunks[most_similar_chunk_index]
        filename = most_similar_chunk.metadata['source']
        start_page = most_similar_chunk.metadata['start_page']
        end_page = most_similar_chunk.metadata['end_page']
        relevant_pages = list_of_page_contents[start_page - 1: end_page]

        if len(relevant_pages) == 1:
            most_similar_page_index = 0
        else:
            cosine_similarities = []
            all_text = []
            for page in relevant_pages:
                all_text.append(page.page_content)
                all_text.append(date_doctor_event)

                vectorizer = CountVectorizer()
                vectorized_text = vectorizer.fit_transform(all_text)

                cosine_similarities.append(cosine_similarity(vectorized_text[-1], vectorized_text[:-1]).flatten())
                all_text = []

            most_similar_page_index = cosine_similarities.index(max(cosine_similarities))

        most_similar_page = [page.metadata['page'] for page in relevant_pages][most_similar_page_index]

        return most_similar_page, filename

    def __format_date(self, is_alpha, input_date):
        """ This method is used to parse the date into MM-DD-YYYY format """

        output_date = dateparser.parse(input_date, settings={'RELATIVE_BASE': datetime(2000, 1, 1)})
        if output_date:
            output_date = output_date.strftime("%m-%d-%Y")
            if is_alpha:
                return output_date
            if len(input_date.split('/')) == 2:
                parts = [int(part) for part in output_date.split('-')]
                if 1 in parts:
                    return output_date
                else:
                    return input_date.replace('/', '-')

            if len(input_date.split('/')) == 1:
                parts = [int(part) for part in output_date.split('-')]
                if parts[0] == 1 and parts[1] == 1:
                    return output_date
                else:
                    return input_date.replace('/', '-')
            return output_date
        return input_date.replace('/', '-')

    async def __post_processing(self, list_of_page_contents, response, relevant_chunks):
        """ This method is used to post-process the LLM response """

        try:
            # Use a regular expression to find the list in the string
            string_of_tuples = re.search(r'\[.*?\]', response, re.DOTALL).group()

            try:
                # Convert the string of tuples into a list of tuples
                list_of_tuples = ast.literal_eval(string_of_tuples.replace('“', '"').replace('”', '"'))

            except Exception:
                # Use a regular expression to match the dates, events and doctor
                matches = re.findall(r'\((\"[\d\/]+\")\s*,\s*\"([^\"]+)\"\s*,\s*\"([^\"]+)\"', string_of_tuples)

                # Convert the matches to a list of tuples
                list_of_tuples = [(date.strip(), event.strip(), doctor.strip()) for date, event, doctor in matches]

            medical_chronology = []
            for date, event, doctor in list_of_tuples:
                ## Post-processing for date

                # Validation of date by checking alphabet is present or not
                alpha_pattern = r'[a-zA-Z]'
                is_alpha = True if re.search(alpha_pattern, date) else False

                # Formatting of date
                formatted_date = self.__format_date(is_alpha, date)
                date_parts = formatted_date.split('-')
                if len(date_parts) == 3 and int(date_parts[0]) > 12:
                    date_parts[0], date_parts[1] = date_parts[1], date_parts[0]
                year = date_parts[-1]
                if len(year) < 4:
                    year = str(2000 + int(year))
                    date_parts[-1] = year
                date = '-'.join(date_parts)
                date = re.findall(r'(?:\d{1,2}-\d{1,2}-\d{1,4})|(?:\d{1,2}-\d{1,4})|(?:\d{1,4})', date)[0]
                input_date_parts = date.split('-')
                if len(input_date_parts[0]) == 1:
                    input_date_parts[0] = '0' + input_date_parts[0]
                if len(input_date_parts[1]) == 1:
                    input_date_parts[1] = '0' + input_date_parts[1]

                # Post-processing for doctor name
                doctor_json = doctor
                doctor_name = doctor_json['Doctor']
                doctor_role = doctor_json['Role']
                doctor_inst = doctor_json['Institution']
                if doctor_name == 'None':
                    if doctor_role == 'None':
                        if doctor_inst == 'None':
                            doctor = 'Medical Professional'
                        else:
                            doctor = 'Medical Professional at ' + doctor_inst
                    else:
                        if doctor_inst == 'None':
                            doctor = doctor_role
                        else:
                            doctor = doctor_role + ' at ' + doctor_inst
                else:
                    if doctor_role == 'None':
                        if doctor_inst == 'None':
                            doctor = doctor_name
                        else:
                            doctor = doctor_name + ' from ' + doctor_inst
                    else:
                        if doctor_inst == 'None':
                            doctor = doctor_name + '; ' + doctor_role
                        else:
                            doctor = doctor_name + '; ' + doctor_role + ' at ' + doctor_inst

                if doctor == 'Medical Professional':
                    date_doctor_event = date + " " + event
                else:
                    date_doctor_event = date + " " + doctor + " " + event

                page, filename = await self.__get_page_number(date_doctor_event, list_of_page_contents, relevant_chunks)
                medical_chronology.append({'date': date, 'event': event, 'doctor_name': doctor, 'page_no': page})

            return medical_chronology

        except Exception:
            return []

    def parse_date(self, date_str):
        parts = date_str.split('-')
        if len(parts) == 3:
            month, day, year = map(int, parts)
            return year, month, day
        elif len(parts) == 2:
            month, year = map(int, parts)
            day = 1
            return year, month, day
        elif len(parts) == 1:
            year = int(parts[0])
            month = 1
            day = 1
            return year, month, day
        else:
            raise ValueError("Invalid date format: {}".format(date_str))

    async def get_medical_chronology(self, document):
        """ This method is used to generate the medical chronology """
        filename = os.path.basename(document['name'])
        data = document['page_wise_text']
        x = time.time()
        docs, chunk_length, list_of_page_contents = await self.__data_formatter(filename, data)
        stuff_calls = await self.__get_stuff_calls(docs, chunk_length)
        emb_tokens = 0
        for i in docs:
            emb_tokens += self.titan_llm.get_num_tokens(i.page_content)

        z = time.time()
        logger.info(f'[Medical-Insights][Medical Chronology] Chunk Preparation Time: {z - x}')

        query = MedicalInsights.Prompts.MEDICAL_CHRONOLOGY_PROMPT
        prompt_template = MedicalInsights.Prompts.PROMPT_TEMPLATE
        prompt = PromptTemplate(
            template=prompt_template, input_variables=["context", "question"]
        )

        medical_chronology = []
        for docs in stuff_calls:
            vectorstore_faiss = FAISS.from_documents(
                documents=docs,
                embedding=self.bedrock_embeddings,
            )
            y = time.time()
            logger.info(f'[Medical-Insights][Medical Chronology][{self.model_embeddings}] Input Embedding tokens: {emb_tokens} '
                        f'and Generation time: {y - z}')

            logger.info(f'[Medical-Insights][Medical Chronology][{self.model_embeddings}] Embedding tokens for LLM call: '
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

            logger.info(f'[Medical-Insights][Medical Chronology][{self.model_id_llm}] Input tokens: {input_tokens} '
                        f'Output tokens: {output_tokens} LLM execution time: {time.time() - y}')

            medical_chronology_list = await self.__post_processing(list_of_page_contents, response, relevant_chunks)
            medical_chronology.extend(medical_chronology_list)

        medical_chronology = sorted(medical_chronology, key=lambda e: self.parse_date(e['date']))
        return {'medical_chronology': medical_chronology, 'document_name': document['name']}
