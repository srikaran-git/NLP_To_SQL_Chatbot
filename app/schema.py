from pydantic import BaseModel, Field


class SQLRequest(BaseModel):
    question: str = Field(..., min_length=1)
    database_url: str


class SQLResponse(BaseModel):
    question: str
    sql: str
    valid: bool


class ExecuteRequest(BaseModel):
    sql: str
    database_url: str