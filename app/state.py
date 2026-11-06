from typing import TypedDict


class AgentState(TypedDict):

    question: str
    schema: str

    sql_query: str

    validated: bool

    query_result: list

    error: str | None

    answer: str