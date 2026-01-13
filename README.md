# Simple RDBMS - Contact Manager
A custom-built relational database management system (RDBMS) with a Flask backend and React frontend for managing contacts

##  Project Overview
This project implements a fully functional RDBMS from scratch, including:

* **Custom Database Engine**: Core database with storage, indexing, and SQL-like query parsing
* **Flask REST API**: Backend server with complete CRUD operations
* **React Frontend**: Modern web interface for contact management
* **SQL Parser**: Custom SQL query parser supporting CREATE, SELECT, INSERT, UPDATE, DELETE

## Project Structure

```markdown
simple-rdbms/
├── core/                     # Custom RDBMS Engine
│   ├── __init__.py
│   ├── database.py           # Database class – main engine
│   ├── storage.py            # File-based storage engine
│   ├── index.py              # Index management
│   └── types.py              # Data type definitions
├── parser/                   # SQL Parser
│   ├── __init__.py
│   └── sql_parser.py         # SQL query parser
├── web_app/                  # Web Application
│   ├── backend/              # Flask API
│   │   ├── app.py            # Main Flask application
│   │   └── __init__.py
│   └── frontend/             # React application
│       ├── src/
│       │   ├── components/   # React components
│       │   ├── services/     # API services
│       │   ├── types.ts      # TypeScript types
│       │   └── App.tsx       # Main React app
│       ├── package.json
│       └── vite.config.ts
├── repl.py                   # Database REPL interface
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```


## Prerequisites
* Python 3.8+
* Node.js 18+
* npm or yarn

## Installation
1. **Clone and setup Python environment:**
```markdown
cd simple-rdbms
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

````
2. **Setup frontend:**
```markdown
cd web_app/frontend
npm install
```
## Running the Application

**Terminal 1 - Backend API:**
```markdown
cd simple-rdbms/web_app/backend
source ../../venv/bin/activate
python app.py
```
**Terminal 2 - Frontend:**
```markdown
cd simple-rdbms/web_app/frontend
npm run dev
```
**Option 2: Database REPL Only**
```markdown
cd simple-rdbms
source venv/bin/activate
python repl.py
```

## Core RDBMS Features
```markdown
-- Table Operations
CREATE TABLE contacts (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT UNIQUE,
    phone TEXT,
    address TEXT,
    company TEXT,
    created_at DATE
)

DROP TABLE contacts

-- Data Operations
INSERT INTO contacts (name, email, phone) 
VALUES ('John Doe', 'john@example.com', '123-456-7890')

SELECT * FROM contacts
SELECT * FROM contacts WHERE id = 1
SELECT * FROM contacts ORDER BY name
SELECT * FROM contacts WHERE name LIKE '%John%'

UPDATE contacts SET phone = '987-654-3210' WHERE id = 1

DELETE FROM contacts WHERE id = 1
```
## Database Architecture
1. **Storage Engine**
* File-based JSON storage
* Automatic table persistence
* Metadata management

2. **Index Manager**
* Simple hash-based indexing
* Support for unique constraints
* Automatic index updates

3.**Data Types**
* INTEGER, TEXT, DATE, BOOLEAN, FLOAT
* Type validation and conversion
* NULL support with constraints

4. **Table Operations**
* CREATE, DROP tables
* INSERT, SELECT, UPDATE, DELETE rows
* WHERE clause filtering
* ORDER BY sorting
* JOIN operations (basic)

## Web Application Features
## Backend API Endpoints

| Method | Endpoint                          | Description          |
|--------|-----------------------------------|----------------------|
| GET    | `/api/contacts`                   | Get all contacts     |
| GET    | `/api/contacts/:id`               | Get single contact   |
| GET    | `/api/contacts/search?q=:query`   | Search contacts      |
| POST   | `/api/contacts`                   | Create new contact   |
| PUT    | `/api/contacts/:id`               | Update contact       |
| DELETE | `/api/contacts/:id`               | Delete contact       |
| GET    | `/api/health`                     | Health check         |

## Frontend Components
1.**ContactList**: Displays all contacts in a table format
2.**ContactForm**: Modal form for creating/editing contacts
3.**SearchBar**: Real-time contact search
4.**App**: Main application layout and state management

## Development Workflow
1.Fork the repository
2.Create a feature branch
3.Make your changes
4.Add tests
5.Submit pull request

## Acknowledgments
* Inspired by SQLite and minimal database implementations
* Built for educational purposes to understand RDBMS internals
* Thanks to the open source community for tools and libraries








