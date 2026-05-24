# Project Name: Finance Tracker MVP

## 🎯 1. Vision & Features
**Brief description of the MVP:** 
The Finance Tracker is a secure and intuitive application designed to help individuals track their personal finances, manage new payments, and monitor pending transactions effectively.

**Core Features:**
- **User Authentication:** Secure login and registration system.
- **Payment Management:** Create new payment entries and manage transaction states (e.g., Pending).
- **Dashboard & Visualization:** View upcoming/pending payments and overall financial status.

## 🏗 2. Architecture (C4 Model)
**Level 1: System Context**
- **Users:** Individuals tracking their personal finances.
- **System:** The Finance Tracker system that securely processes and stores the user's financial entries.

**Level 2: Container Diagram**
- **Web-App:** Python/Flask application that serves the frontend, processes payment logic, and handles RESTful API requests.
- **Database:** PostgreSQL container that persistently stores user data, payment records, and transaction histories. The web app communicates with the database via SQLAlchemy/psycopg2.

## 💻 3. Tech Stack & Setup
- **Backend:** Python / Flask
- **Database:** PostgreSQL (with offline SQLite fallback)
- **Infrastructure:** Docker & Docker-Compose

**Quick Start (The "30-Second Rule")**
To start the application locally, run the following command in the root directory:
```bash
docker-compose up --build
```
The app will be available at: http://localhost:5000

## 🧪 4. Quality & Testing
**Run Tests:**
```bash
# Run the test suite and output coverage metrics locally
.\.venv\Scripts\python -m pytest --cov=app tests/
```

**Test Coverage:**
- **Current Coverage:** > 75%
- **Tested Core Logic:** Payment creation validation, transaction status transitions (Pending), and database model integrity.

## 🛡 5. Security & Clean Code
- **Prepared Statements:** All database queries use parameter binding (via ORM) to prevent SQL injection.
- **Secrets:** No passwords or API keys are stored in the repository (environment variables managed via `.env`).
- **Clean Code:** Adherence to SOLID principles, specifically employing the Single Responsibility Principle by separating routing controllers from core payment logic.

## 📉 6. Agile Reflection (Self-Assessment)
- **Major Technical Debt:** Adopted simple synchronous processing for immediate payment updates in the "Pending" section instead of asynchronous event-driven queues, to speed up MVP delivery.
- **Key Learning:** Orchestrating a multi-container environment (Flask + PostgreSQL) with Docker Compose, especially handling database health checks and connection readiness before the web service starts.
- **Future Iteration:** In the next iteration/Sprint 4, we plan to implement data visualization charts for monthly expenses and support for scheduled/recurring payments.
