from sqlalchemy import create_engine, text


def execute_sql(
    sql: str,
    database_url: str
):

    engine = create_engine(database_url)

    with engine.connect() as connection:
        # Enforce read-only behavior in the database itself. SQL text filters
        # alone are not a security boundary (for example, SELECT INTO).
        dialect = connection.dialect.name
        if dialect == "sqlite":
            connection.exec_driver_sql("PRAGMA query_only = ON")
        elif dialect == "postgresql":
            connection.exec_driver_sql("SET TRANSACTION READ ONLY")
        elif dialect in {"mysql", "mariadb"}:
            connection.exec_driver_sql("SET TRANSACTION READ ONLY")
        else:
            raise ValueError(f"Read-only execution is not configured for {dialect}")

        result = connection.execute(
            text(sql)
        )

        rows = result.fetchall()

        columns = result.keys()

        return [
            dict(zip(columns, row))
            for row in rows
        ]
