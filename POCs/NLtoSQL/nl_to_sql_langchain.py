import time
import boto3
from sqlalchemy import create_engine, text

from langchain_aws import ChatBedrock
from langchain.sql_database import SQLDatabase
from langchain.chains import create_sql_query_chain


def get_llm():
    bedrock_client = boto3.client(service_name='bedrock-runtime', region_name='us-east-1')

    # model_id_llm = 'anthropic.claude-3-haiku-20240307-v1:0'

    model_id_llm = 'anthropic.claude-3-sonnet-20240229-v1:0'

    llm = ChatBedrock(
        model_id=model_id_llm,
        model_kwargs={
            "max_tokens": 4096,
            "temperature": 0.0,
            "top_p": 0.9,
            "top_k": 500,
            "stop_sequences": [],
        },
        client=bedrock_client,
    )

    return llm


def connect_database(username, password, host, database_name):
    """Connect to the database and return a SQLDatabase object."""

    database_url = f"postgresql://{username}:{password}@{host}/{database_name}"
    database_engine = create_engine(database_url)
    db = SQLDatabase(database_engine)
    return db, database_engine


def extract_sql_query(response):
    """Extract the SQL query from the LLM response."""

    if "SQLQuery:" in response:
        return response.split("SQLQuery:")[-1].strip()
    return response.strip()


def execute_query(db, query):
    """Execute the SQL query and return all results."""

    with db.engine.connect() as connection:
        result = connection.execute(text(query))
        columns = result.keys()
        rows = result.fetchall()
        return [dict(zip(columns, row)) for row in rows]


def get_response(db, database_engine, llm, nl_query):
    """Generate a response from the natural language query."""

    try:
        # enhanced_query = f"""
        #  Task: {nl_query}
        #
        #  Important PostgreSQL syntax guidelines:
        #  1. For calculating duration between dates:
        #     - Convert interval to days using: EXTRACT(EPOCH FROM (end_date - start_date))/86400.0
        #     - Cast dates to TIMESTAMP when doing arithmetic: CAST(date_column AS TIMESTAMP)
        #     - Use ::numeric when rounding results
        #
        #  2. When calculating averages with dates:
        #     - First calculate the duration in days
        #     - Then use AVG() on the numeric result
        #     - Finally use ROUND() on the average
        #
        #  Generate a PostgreSQL query following these guidelines.
        #  """

        chain = create_sql_query_chain(llm=llm, db=db)

        table_info = db.get_table_info()

        response = chain.invoke({
            "question": nl_query,
            "table_info": table_info,
            "top_k": 10
        })

        sql_query = extract_sql_query(response)

        results = execute_query(database_engine, sql_query)

        return f"""Generated SQL Query: {sql_query} Results: {format_results(results)}"""

    except Exception as e:
        return f"An error occurred: {str(e)}\nFull error: {type(e).__name__}"


def format_results(results):
    """Format the results in a readable way."""

    if not results:
        return "No results found"

    columns = results[0].keys()

    widths = {col: max(len(str(row[col])) for row in results + [{col: col}]) for col in columns}

    header = " | ".join(f"{col:<{widths[col]}}" for col in columns)
    separator = "-" * len(header)

    rows = [
        " | ".join(f"{str(row[col]):<{widths[col]}}" for col in columns)
        for row in results
    ]

    return f"\n{header}\n{separator}\n" + "\n".join(rows)


if __name__ == "__main__":
    start_time = time.time()
    db, database_engine = connect_database('postgres', 'postgres', 'localhost', 'EmployeeData')
    llm = get_llm()

    # nl_query = "Calculate the completion ratio of employees who completed the course / employees pursuing the course month over month for CCP Course. Present this data in percentage format, and ensure that the month column includes the word month for all rows."
    nl_query = "List the names of employees who completed the SAA course with its duration of completion"
    # nl_query = "List the total number of certificate with its name"
    response = get_response(db, database_engine, llm, nl_query)
    print(response)
    print(f"Time taken to generate output: {time.time() - start_time}")
