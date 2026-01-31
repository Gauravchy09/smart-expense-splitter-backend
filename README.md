# 💰 Smart Expense Splitter - Backend

A high-performance, asynchronous REST API built with **FastAPI** for managing group expenses, optimizing settlements, and scanning receipts using **OCR**.

## 🚀 Features

-   **⚡ High Performance**: Built on [FastAPI](https://fastapi.tiangolo.com/), one of the fastest Python frameworks.
-   **🐘 PostgreSQL + AsyncPG**: Fully asynchronous database operations for maximum concurrency.
-   **🧾 OCR Receipt Scanning**: Integrated **Tesseract OCR** to automatically extract expense details from images.
-   **💱 Multi-Currency Support**: Real-time currency conversion and normalization to a group's base currency.
-   **🔄 Smart Settlements**: Algorithm to simplify debts and minimize the number of transactions needed to settle up.
-   **🐳 Dockerized**: Production-ready `Dockerfile` optimized for Render/Cloud deployment.
-   **🔒 Secure**: JWT Authentication and Robust CORS configuration.

## 🛠️ Tech Stack

-   **Framework**: FastAPI
-   **Database**: PostgreSQL
-   **ORM**: SQLAlchemy (Async)
-   **OCR Engine**: Tesseract
-   **Authentication**: JWT (OAuth2)
-   **Containerization**: Docker

## ⚙️ Installation & Setup

### Prerequisites
-   Python 3.10+
-   PostgreSQL
-   Tesseract OCR installed on system (`sudo apt install tesseract-ocr` or Windows installer)

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/smart-expense-splitter-backend.git
cd smart-expense-splitter-backend
```

### 2. Create Virtual Environment
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment
Create a `.env` file in the root directory:
```env
# Database
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/smart_split_db

# Security
SECRET_KEY=your_super_secret_key_here
ACCESS_TOKEN_EXPIRE_MINUTES=10080

# CORS (Frontend URL)
BACKEND_CORS_ORIGINS=["http://localhost:5173","https://your-frontend.vercel.app"]
```

### 5. Run the Server
```bash
uvicorn app.main:app --reload
```
The API will be available at `http://localhost:8000`.
Interactive docs: `http://localhost:8000/docs`.

## 🐳 Docker Deployment
The application is containerized and ready for Render/Railway/Fly.io.

```bash
docker build -t smart-split-backend .
docker run -p 8000:8000 --env-file .env smart-split-backend
```

## 🧪 Key Endpoints

-   `POST /api/v1/auth/login` - Authenticate user
-   `POST /api/v1/expenses/ocr` - Upload receipt image for scanning
-   `GET /api/v1/groups/{id}/balances` - Get optimized settlement plan
-   `POST /api/v1/expenses/` - Create a new expense (supports split shares)

## 🤝 Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.
