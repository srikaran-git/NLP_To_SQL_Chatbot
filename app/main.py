from fastapi import FastAPI, HTTPException, Header

from app.config import get_database_url
from app.services.agent import generate_sql
from app.services.sql_validator import validate_sql
from app.services.sql_executor import execute_sql

from pydantic import BaseModel

def require_configured_database(database_url: str) -> None:
    if database_url.strip() != get_database_url():
        raise HTTPException(status_code=400, detail="Requested database is not configured on the server")


app = FastAPI(
    title="NLP to SQL Agent API",
    description="Natural Language to SQL Agent",
    version="1.0.0"
)


class SQLRequest(BaseModel):
    question: str
    database_url: str


class ExecuteRequest(BaseModel):
    sql: str
    database_url: str


@app.get("/health")
def health_check():

    return {
        "status": "healthy"
    }


@app.post("/generate-sql")
def generate_sql_endpoint(
    request: SQLRequest,
    authorization: str | None = Header(default=None)
):
    require_configured_database(request.database_url)

    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="API key is required"
        )

    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Invalid authorization format"
        )

    api_key = authorization.replace(
        "Bearer ",
        "",
        1
    ).strip()

    if not api_key:
        raise HTTPException(
            status_code=401,
            detail="Invalid API key"
        )

    try:

        sql = generate_sql(
            question=request.question,
            api_key=api_key,
            database_url=request.database_url
        )

        valid = validate_sql(sql)

        return {
            "question": request.question,
            "sql": sql,
            "valid": valid
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@app.post("/execute-sql")
def execute_sql_endpoint(
    request: ExecuteRequest
):
    require_configured_database(request.database_url)

    if not validate_sql(request.sql):

        raise HTTPException(
            status_code=400,
            detail="Unsafe SQL query"
        )

    try:

        results = execute_sql(
            request.sql,
            request.database_url
        )

        return {
            "success": True,
            "rows": results
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
