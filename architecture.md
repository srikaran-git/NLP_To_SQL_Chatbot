
### Agent Architecture

START
   │
   ▼
Understand Question
   │
   ▼
Retrieve Relevant Schema
   │
   ▼
Generate SQL
   │
   ▼
Validate SQL
   │
   ├── invalid ──────┐
   │                 │
   │                 ▼
   │            Fix SQL
   │                 │
   └─────────────────┘
   │
   ▼
Execute Query
   │
   ├── SQL Error ────┐
   │                 │
   │                 ▼
   │            Analyze Error
   │                 │
   └─────────────────┘
   │
   ▼
Explain Results
   │
   ▼
END


## App Architecture

                    ┌─────────────────┐
                    │   Streamlit UI  │
                    └────────┬────────┘
                             │
                         HTTP/REST
                             │
                             ▼
                    ┌─────────────────┐
                    │    FastAPI      │
                    │     Backend     │
                    └────────┬────────┘
                             │
                ┌────────────┼────────────┐
                ▼            ▼            ▼
          Schema Tool    SQL Agent    Validator
                │            │            │
                └────────────┼────────────┘
                             ▼
                       SQL Execution
                             │
                             ▼
                         SQLite DB
                             │
                             ▼
                         Results
                             │
                             ▼
                    ┌─────────────────┐
                    │   Streamlit UI  │
                    └─────────────────┘