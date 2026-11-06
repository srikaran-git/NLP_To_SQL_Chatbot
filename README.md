# NLP to SQL Assistant

A small full-stack application that turns a natural-language question into a SQL `SELECT` query and displays the results. The project uses a Streamlit interface, a FastAPI backend, LangChain with Groq, SQLAlchemy, and a local SQLite sample database.

## Features

- Reads database table and column metadata and includes it in the prompt sent to the language model.
- Generates SQL from a user's question and applies a basic read-only SQL validation step.
- Executes supported queries through SQLAlchemy using a read-only database transaction or connection setting.
- Displays query results in a Streamlit table.
- Builds a sample commerce database from hardcoded product examples and `shopping_products_dataset.csv`.

## Tech stack

- Python 3.11+
- FastAPI and Uvicorn
- Streamlit
- LangChain and `langchain-groq`
- SQLAlchemy
- SQLite and pandas

## Project structure

```text
app/
  config.py                 # Project configuration and database URL
  main.py                   # FastAPI endpoints
  services/
    agent.py                # Schema-aware SQL generation
    database.py             # Schema introspection
    sql_executor.py         # Read-only SQL execution
    sql_validator.py        # SELECT query validation
setup_db.py                 # Creates and seeds the sample database
streamlit_app.py            # Streamlit user interface
shopping_products_dataset.csv
```

## Database schema

`setup_db.py` creates these related tables:

- `products`: merged hardcoded and CSV product catalog
- `customers`: sample customer contact and location details
- `sales`: sample customer purchases, quantities, prices, and payment methods
- `suppliers`: supplier contact information
- `product_suppliers`: supplier-to-product links and supplier pricing
- `inventory_movements`: sample stock receipts and sales movements
- `reviews`: sample product reviews
- `orders`: simple product order records

## Run locally

Open a terminal in the project directory and create a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Create a local environment file and add your Groq API key:

```powershell
Copy-Item .env.example .env
```

Edit `.env` if needed to configure `DATABASE_URL`, which must be the same for the UI and API. By default, the app uses the `store.db` file in the project directory. Enter your Groq API key in the Streamlit password field when you run the app; the current UI does not load `GROQ_API_KEY` from `.env`.

Build or rebuild the sample database:

```powershell
python setup_db.py
```

> **Warning:** Running `setup_db.py` recreates the sample data, replacing rows in the product, review, order, customer, sales, supplier, and inventory tables.

Start the backend in one terminal:

```powershell
uvicorn app.main:app --reload
```

Start the UI in another terminal:

```powershell
streamlit run streamlit_app.py
```

The Streamlit interface will be available at `http://localhost:8501`. FastAPI's interactive API documentation is at `http://127.0.0.1:8000/docs`.

## Example questions

- Which five products have the highest prices?
- What are the total sales by customer?
- Which products have the most inventory movements?
- Show the average review rating by product.

## API overview

- `GET /health` — backend health check
- `POST /generate-sql` — generates a query; expects a bearer token containing the Groq API key and a `question` plus configured `database_url`
- `POST /execute-sql` — validates and executes a query against the configured database

Use the Streamlit interface for the normal workflow. This is a learning/demo project, not a production database gateway: SQL validation is a conservative lexical check, and the execute endpoint does not implement application-level user authentication. Keep the backend private and use a database account with read-only permissions.

## Resume description

**NLP to SQL Assistant** | Python, FastAPI, Streamlit, LangChain, Groq, SQLAlchemy, SQLite

- Built a full-stack application that converts natural-language questions into SQL queries using schema metadata and a Groq-hosted language model.
- Developed FastAPI endpoints for SQL generation and execution, with SQL validation and database-level read-only query settings.
- Created a relational sample commerce database with products, customers, sales, suppliers, inventory movements, orders, and reviews, populated from CSV and seed data.
- Built a Streamlit interface for entering questions, reviewing generated SQL, and viewing query results.

Add a GitHub repository link to the project title when you publish the repository. Keep the bullets aligned with what you can explain in an interview.
