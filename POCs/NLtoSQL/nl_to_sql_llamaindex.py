import time
import boto3
from sqlalchemy import create_engine

from llama_index.core import SQLDatabase
from llama_index.llms.bedrock import Bedrock
from llama_index.embeddings.bedrock import BedrockEmbedding
from llama_index.core.query_engine import NLSQLTableQueryEngine


def get_llm():
    """Initialize and return the Bedrock LLM client."""

    bedrock_client = boto3.client(service_name='bedrock-runtime', region_name='us-east-1')
    model_id_llm = 'anthropic.claude-3-sonnet-20240229-v1:0'

    llm = Bedrock(
        model=model_id_llm,
        max_tokens=4096,
        temperature=0.0,
        client=bedrock_client
    )
    return llm


def get_embedding_llm():
    """Initialize and return the Bedrock embedding client."""

    bedrock_client = boto3.client(service_name='bedrock-runtime', region_name='us-east-1')
    model_id_llm = 'amazon.titan-embed-text-v2:0'

    embedding_llm = BedrockEmbedding(
        model=model_id_llm,
        client=bedrock_client
    )
    return embedding_llm


def connect_database(username, password, host, database_name):
    """Connect to the database and return SQLDatabase object."""

    database_url = f"postgresql://{username}:{password}@{host}/{database_name}"
    database_engine = create_engine(database_url)
    db = SQLDatabase(database_engine)
    return db, database_engine


def get_query_engine(db, database_engine, llm, embedding_llm):
    """ This method creates an query engine object using llama-index """

    tables = list(db._all_tables)

    custom_data = custom_schema_data(db, tables)

    sql_database = SQLDatabase(database_engine, include_tables=tables, custom_table_info=custom_data)

    context_data = (
        f"Using PostgreSQL database with tables: {', '.join(tables)}. "
        'All identifiers must be enclosed in double quotes (e.g., "TableName"."ColumnName").'
    )

    query_engine = NLSQLTableQueryEngine(sql_database=sql_database, embed_model=embedding_llm, llm=llm,
                                         sql_only=False, context_str_prefix=context_data)

    return query_engine


def custom_schema_data(db, tables):
    """Generate custom schema information."""

    schema_data = {}
    for table in tables:
        columns = db.get_table_columns(table)
        schema_data[table] = columns

    return schema_data


def format_results(data_dict):
    """ Format the results in a readable way using column keys as headers. """

    if not data_dict or 'result' not in data_dict or 'col_keys' not in data_dict:
        return "No results found or invalid data structure"

    headers = data_dict['col_keys']
    results = data_dict['result']

    if not results:
        return "No results found"

    formatted_rows = []
    for row in results:
        formatted_rows.append([str(item) for item in row])

    widths = []
    for col_idx in range(len(headers)):
        header_width = len(headers[col_idx])
        data_width = max(len(row[col_idx]) for row in formatted_rows)
        widths.append(max(header_width, data_width))

    header_row = " | ".join(f"{header:<{width}}" for header, width in zip(headers, widths))

    separator = "-" * (sum(widths) + (len(widths) - 1) * 3)

    data_rows = []
    for row in formatted_rows:
        formatted_row = " | ".join(f"{str(val):<{width}}" for val, width in zip(row, widths))
        data_rows.append(formatted_row)

    return f"\n{header_row}\n{separator}\n" + "\n".join(data_rows)


def get_response(query_engine, nl_query):
    """Generate a response from the natural language query using NLSQLRetriever."""

    try:
        response = query_engine.query(nl_query)
        sql_query = response.metadata['sql_query']
        return f"""Generated SQL Query: {sql_query} Results: {format_results(response.metadata)}"""

    except Exception as e:
        error_msg = f"Error processing query: {str(e)}\nFull error: {type(e).__name__}"
        print(error_msg)
        return error_msg


def main():
    """Main function to run the query process."""

    try:
        start_time = time.time()
        db, database_engine = connect_database('postgres', 'postgres',
                                               'localhost', 'EmployeeData')

        llm = get_llm()
        embedding_llm = get_embedding_llm()
        query_engine = get_query_engine(db, database_engine, llm, embedding_llm)

        nl_query = "List the names of employees who completed the SAA course with its duration of completion"
        response = get_response(query_engine, nl_query)
        print(response)
        print(f"Time taken to generate output: {time.time() - start_time}")

    except Exception as e:
        print(f"Application error: {str(e)}")


if __name__ == "__main__":
    main()
