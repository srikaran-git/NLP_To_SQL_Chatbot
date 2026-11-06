import json

from langchain_groq import ChatGroq

from app.services.database import get_schema


def generate_sql(
    question: str,
    api_key: str,
    database_url: str
):

    schema = get_schema(database_url)

    llm = ChatGroq(
        api_key=api_key,
        model="openai/gpt-oss-120b",
        temperature=0
    )

    prompt = f"""
You are an expert SQL developer.

Database schema:

{json.dumps(schema, indent=2)}

User question:

{question}

Rules:

- Generate only SELECT queries.
- Use only tables and columns from the schema.
- Never modify database data.
- Never use INSERT.
- Never use UPDATE.
- Never use DELETE.
- Never use DROP.
- Never use ALTER.
- Never use CREATE.
- Return only executable SQL.
- For normal row-level queries, use LIMIT 100.

Return only SQL.
"""

    response = llm.invoke(prompt)

    sql = response.content.strip()

    sql = sql.replace("```sql", "")
    sql = sql.replace("```", "")

    return sql.strip()