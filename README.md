# ChemViz — Chemical Equipment Parameter Visualizer

ChemViz is a hybrid **web and desktop application** for uploading, analyzing, and visualizing chemical equipment data. Both frontends connect to a shared Django REST backend for authentication, data processing, and reporting.

---

## System Architecture

**Backend (Django + REST API)**
- User authentication (register/login)
- CSV upload and parsing
- Data analysis with Pandas
- PDF report generation
- SQLite database (stores the last 5 datasets per user)

**Clients**
- **Web App (React + Chart.js)** — Browser-based dashboards and charts  
- **Desktop App (PyQt5 + Matplotlib)** — Native desktop interface with tables and visualizations

All components communicate through a token-secured JSON REST API.

---

## Technology Stack

| Layer | Technology | Purpose |
|------|------------|---------|
| Backend | Django + Django REST Framework | API, authentication, business logic |
| Data Processing | Pandas | CSV parsing and analytics |
| Database | SQLite | Dataset storage |
| Reports | ReportLab | PDF report generation |
| Web Frontend | React + Chart.js | Interactive browser dashboards |
| Desktop Frontend | PyQt5 + Matplotlib | Native desktop visualization |
| Authentication | Token-based | Secure API access |

---

## Project Structure

```
project/
│
├── backend/
│   ├── chemical_project/
│   ├── equipment_api/
│   ├── manage.py
│   └── requirements.txt
│
├── frontend_web/
│   ├── public/
│   ├── src/
│   └── package.json
│
├── frontend_desktop/
│   ├── app.py
│   └── requirements.txt
│
├── sample_equipment_data.csv
└── README.md
```

---

## Setup Instructions

### Prerequisites

- Python 3.9 or higher  
- Node.js 18+ and npm  
- Terminal or command prompt  

---

### Backend (Django)

```
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser   # optional
python manage.py runserver
```

Backend runs at: **http://localhost:8000**

---

### Web Frontend (React)

```
cd frontend_web
npm install
npm start
```

Web app runs at: **http://localhost:3000**

If the backend URL changes, set the environment variable:

```
REACT_APP_API_URL=http://your-backend-url
```

---

### Desktop Frontend (PyQt5)

```
cd frontend_desktop
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

To change the backend URL:

```
CHEMVIZ_API_URL=http://your-backend-url
```

---

## API Overview

All endpoints require token authentication unless noted otherwise.

### Authentication

| Method | Endpoint | Description |
|-------|----------|-------------|
| POST | /api/auth/register/ | Register a new user |
| POST | /api/auth/login/ | Login and receive auth token |

**Request Body**
```
{
  "username": "alice",
  "email": "alice@example.com",
  "password": "secure123"
}
```

**Response**
```
{
  "token": "abc123...",
  "username": "alice",
  "email": "alice@example.com"
}
```

---

### Equipment Data

| Method | Endpoint | Description |
|-------|----------|-------------|
| POST | /api/upload/ | Upload CSV dataset |
| GET | /api/history/ | List last 5 datasets |
| GET | /api/dataset/<id>/ | Retrieve dataset details |
| DELETE | /api/dataset/<id>/delete/ | Delete dataset |
| GET | /api/dataset/<id>/report/ | Download PDF report |

**Upload Example**

```
curl -X POST http://localhost:8000/api/upload/   -H "Authorization: Token YOUR_TOKEN"   -F "file=@sample_equipment_data.csv"
```

---

## Core Features

- Upload equipment data via CSV  
- Automatic statistical summaries  
- Interactive charts and tables  
- Dataset history (last 5 per user)  
- Downloadable PDF reports  
- Shared login between web and desktop apps  

---

## Sample Dataset

The file **sample_equipment_data.csv** includes 30 equipment items across multiple equipment types. Use it to test uploads and visualizations in both applications.

---

## Typical Workflow

1. Start the Django backend  
2. Launch the web or desktop app  
3. Register or log in  
4. Upload a CSV dataset  
5. View summaries, charts, and tables  
6. Access previous uploads in History  
7. Download a generated PDF report  

---

## License

MIT License. Intended for educational and evaluation purposes.
