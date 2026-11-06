from sqlalchemy import create_engine, inspect, text


def get_schema(database_url: str):

    engine = create_engine(database_url)

    inspector = inspect(engine)

    schema = {}

    for table in inspector.get_table_names():

        columns = inspector.get_columns(table)

        schema[table] = [
            {
                "name": column["name"],
                "type": str(column["type"])
            }
            for column in columns
        ]

    return schema


def execute_query(database_url: str, sql: str):

    engine = create_engine(database_url)

    with engine.connect() as connection:

        result = connection.execute(text(sql))

        rows = result.fetchall()

        columns = result.keys()

        return [
            dict(zip(columns, row))
            for row in rows
        ]