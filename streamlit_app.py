import requests
import streamlit as st
from app.config import get_database_url

FASTAPI_URL = "http://127.0.0.1:8000"


st.set_page_config(
    page_title="NLP to SQL Agent",
    page_icon="🧠",
    layout="wide"
)


st.title("🧠 NLP → SQL Agent")

st.caption(
    "Convert natural-language questions into executable SQL queries"
)


# --------------------------------------------------
# Sidebar
# --------------------------------------------------

with st.sidebar:

    st.header("Configuration")

    api_key = st.text_input(
        "Groq API Key",
        type="password",
        placeholder="Enter your Groq API key"
    )

    database_url = st.text_input(
        "Database URL",
        value=get_database_url()
    )


# --------------------------------------------------
# User question
# --------------------------------------------------

question = st.text_area(
    "Natural Language Query",

    placeholder=(
        "Example: Show the top 5 products by sales"
    ),

    height=120
)


# --------------------------------------------------
# Generate SQL
# --------------------------------------------------

if st.button(
    "Generate SQL",
    type="primary"
):

    if not question.strip():

        st.warning(
            "Please enter a natural-language query."
        )

        st.stop()


    if not api_key.strip():

        st.warning(
            "Please enter your API key."
        )

        st.stop()


    if not database_url.strip():

        st.warning(
            "Please enter a database URL."
        )

        st.stop()


    with st.spinner(
        "Generating SQL..."
    ):

        try:

            response = requests.post(

                f"{FASTAPI_URL}/generate-sql",

                json={
                    "question": question,
                    "database_url": database_url
                },

                headers={
                    "Authorization": f"Bearer {api_key}"
                },

                timeout=60
            )


            if response.status_code != 200:

                st.error(
                    response.json().get(
                        "detail",
                        "Failed to generate SQL"
                    )
                )

                st.stop()


            data = response.json()

            st.session_state["sql"] = data["sql"]
            st.session_state["sql_valid"] = data.get("valid", False)


        except requests.exceptions.ConnectionError:

            st.error(
                "Could not connect to FastAPI. "
                "Make sure the backend is running."
            )

        except Exception as e:

            st.error(
                f"Error: {e}"
            )


# --------------------------------------------------
# Display SQL
# --------------------------------------------------

if "sql" in st.session_state:

    st.subheader("Generated SQL")


    sql = st.session_state["sql"]


    st.code(
        sql,
        language="sql"
    )


    if st.session_state.get("sql_valid", False):
        st.success("SQL passed safety validation.")
    else:
        st.error("Generated SQL failed safety validation and cannot be executed.")


    # --------------------------------------------------
    # Execute
    # --------------------------------------------------

    if st.session_state.get("sql_valid", False) and st.button(
        "▶ Execute Query"
    ):

        with st.spinner(
            "Executing query..."
        ):

            try:

                response = requests.post(

                    f"{FASTAPI_URL}/execute-sql",

                    json={
                        "sql": sql,
                        "database_url": database_url
                    },

                    timeout=30
                )


                if response.status_code != 200:

                    st.error(
                        response.json().get(
                            "detail",
                            "Query execution failed"
                        )
                    )

                    st.stop()


                data = response.json()


                st.subheader(
                    "Query Results"
                )


                rows = data["rows"]


                if rows:

                    st.dataframe(
                        rows,
                        use_container_width=True
                    )

                else:

                    st.info(
                        "Query returned no results."
                    )


            except requests.exceptions.ConnectionError:

                st.error(
                    "Could not connect to FastAPI."
                )

            except Exception as e:

                st.error(
                    f"Error: {e}"
                )
