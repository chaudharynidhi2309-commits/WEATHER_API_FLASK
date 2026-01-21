# 🌦️ Weather API - Flask & PostgreSQL with Connection Pooling

A robust RESTful API built with Flask that integrates with the OpenWeatherMap API to fetch live weather data. This project demonstrates clean code principles, database connection pooling for high performance, and automated API documentation.

## 🚀 Key Features
- **Live Data Fetching:** Real-time integration with OpenWeatherMap.
- **Connection Pooling:** Uses `psycopg2.pool.SimpleConnectionPool` for efficient database resource management.
- **Modular Design:** Clear separation between API routes (`app.py`) and database logic (`db_config.py`).
- **Interactive Documentation:** Fully documented using Swagger UI (Flasgger).
- **CRUD Operations:** Supports saving live data and retrieving historical logs.

---

## 🛠️ Tech Stack
- **Backend:** Python, Flask
- **Database:** PostgreSQL
- **Documentation:** Swagger / Flasgger
- **Libraries:** `requests`, `psycopg2-binary`, `flask`

---

## 📂 Project Structure
```text
/weather_api_project
├── app.py             # API Endpoints and logic
├── db_config.py       # DB Connection pooling and query helpers
├── README.md          # Documentation
└── requirements.txt   # Dependencies
