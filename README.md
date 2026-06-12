<div align="center">

# 🧪 ChemViz — Chemical Equipment Parameter Visualizer

### A hybrid web and desktop application for uploading, analyzing, and visualizing chemical equipment data.

[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-REST-092E20?style=for-the-badge&logo=django&logoColor=white)](https://www.djangoproject.com/)
[![React](https://img.shields.io/badge/React-18-61DAFB?style=for-the-badge&logo=react&logoColor=white)](https://react.dev/)
[![PyQt5](https://img.shields.io/badge/PyQt5-Desktop-41CD52?style=for-the-badge&logo=qt&logoColor=white)](https://riverbankcomputing.com/software/pyqt/)
[![SQLite](https://img.shields.io/badge/SQLite-Database-003B57?style=for-the-badge&logo=sqlite&logoColor=white)](https://www.sqlite.org/)

[🌐 Web App](#) · [🖥️ Desktop App](#) · [🔌 Backend API](#)

</div>

---

## 📌 About

**ChemViz** is an advanced data visualization and analysis tool built for chemical engineering parameters. It offers a seamless experience across both a browser-based web application and a native desktop interface. Both clients connect to a centralized Django REST backend that handles secure authentication, robust CSV data processing using Pandas, and automated PDF report generation.

---

## ✨ Features

### 📊 Data Processing & Analytics
- **CSV Uploads** — Easily upload equipment parameter datasets for immediate parsing.
- **Statistical Summaries** — Automatic calculations and aggregations powered by Pandas.
- **Historical Tracking** — Securely store and retrieve the last 5 uploaded datasets per user.
- **PDF Report Generation** — Export comprehensive analysis reports via ReportLab.

### 🌐 Web Dashboard (React)
- Browser-based interactive dashboards.
- Dynamic charts and visualizations built with **Chart.js**.
- Fully responsive design for accessible analytics.

### 🖥️ Native Desktop Interface (PyQt5)
- High-performance native desktop application.
- Granular table views and powerful plotting via **Matplotlib**.
- Shared authentication state with the web ecosystem.

### 🔐 Security & Backend
- **Token-based Authentication** ensuring secure API access.
- Centralized SQLite database for streamlined local deployments.

---

## 🏗️ System Architecture

```mermaid
graph TB
    subgraph Clients["💻 Client Applications"]
        WEB["🌐 Web Frontend<br/><i>React + Chart.js</i>"]
        DESK["🖥️ Desktop Frontend<br/><i>PyQt5 + Matplotlib</i>"]
    end

    subgraph Server["⚙️ Server Layer"]
        API["🔌 Django REST Backend<br/><i>Authentication & API</i>"]
        PD["📊 Pandas Engine<br/><i>Data Parsing</i>"]
        RL["📄 ReportLab<br/><i>PDF Generation</i>"]
    end

    subgraph Database["🗄️ Storage Layer"]
        DB[("SQLite Database<br/><i>User & Dataset Info</i>")]
    end

    WEB -->|"REST API (JSON)"| API
    DESK -->|"REST API (JSON)"| API
    API -->|"Data Processing"| PD
    API -->|"Generate Reports"| RL
    API -->|"CRUD Operations"| DB
```

---

## 🔄 Request Flow

```mermaid
sequenceDiagram
    participant U as 👤 User
    participant C as 💻 Client (Web/Desktop)
    participant API as ⚙️ Django API
    participant P as 📊 Pandas
    participant DB as 🗄️ SQLite

    Note over U,DB: Data Upload & Analysis
    U->>C: Upload equipment CSV file
    C->>API: POST /api/upload/ (Token Auth)
    API->>P: Parse CSV & calculate statistics
    P-->>API: Analytics results
    API->>DB: Store dataset metadata
    DB-->>API: Confirmation
    API-->>C: JSON Response (Stats & Data)
    C-->>U: Render Charts & Data Tables

    Note over U,DB: Report Generation
    U->>C: Request PDF Report
    C->>API: GET /api/dataset/<id>/report/
    API->>DB: Fetch dataset details
    API->>API: Generate PDF (ReportLab)
    API-->>C: Downloadable PDF File
    C-->>U: Display/Save PDF
```

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|:---:|:---|:---|
| **Backend** | Django, Django REST Framework | API, authentication, business logic |
| **Data Processing** | Pandas | CSV parsing and analytics |
| **Database** | SQLite | Dataset storage |
| **Reports** | ReportLab | PDF report generation |
| **Web Frontend** | React, Chart.js | Interactive browser dashboards |
| **Desktop Frontend**| PyQt5, Matplotlib | Native desktop visualization |
| **Authentication** | Token-based Auth | Secure API access |

---

## 📂 Project Structure

```text
ChemViz/
├── backend/                   # Django REST API
│   ├── chemical_project/      # Main Django project config
│   ├── equipment_api/         # API app for endpoints
│   ├── manage.py              # Django entrypoint
│   └── requirements.txt       # Python dependencies
├── frontend_web/              # React Web Application
│   ├── public/
│   ├── src/
│   └── package.json           # Node dependencies
├── frontend_desktop/          # PyQt5 Desktop Application
│   ├── app.py                 # Desktop app entrypoint
│   └── requirements.txt       # Python dependencies
├── sample_equipment_data.csv  # Sample dataset for testing
└── README.md
```

---

## 🔌 API Reference

### Authentication Endpoints

| Method | Endpoint | Description |
|:---:|:---|:---|
| `POST` | `/api/auth/register/` | Register a new user |
| `POST` | `/api/auth/login/` | Login and receive auth token |

### Equipment Data Endpoints (Requires Token)

| Method | Endpoint | Description |
|:---:|:---|:---|
| `POST` | `/api/upload/` | Upload CSV dataset |
| `GET` | `/api/history/` | List last 5 uploaded datasets |
| `GET` | `/api/dataset/<id>/` | Retrieve dataset details and stats |
| `DELETE`| `/api/dataset/<id>/delete/` | Delete dataset |
| `GET` | `/api/dataset/<id>/report/` | Download PDF report |

---

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- Node.js 18+ and npm

### 1. Backend Setup (Django)

```bash
cd backend
python -m venv venv
# Windows: venv\Scripts\activate
source venv/bin/activate
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```
> Backend runs at: `http://localhost:8000`

### 2. Web Frontend Setup (React)

```bash
cd frontend_web
npm install
npm start
```
> Web app runs at: `http://localhost:3000`

### 3. Desktop Frontend Setup (PyQt5)

```bash
cd frontend_desktop
python -m venv venv
# Windows: venv\Scripts\activate
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

---

## 🤝 Contributing

Contributions are welcome!

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

<div align="center">

**Built with ❤️ by [Ziaur Rahman](https://github.com/iZiaur)**

⭐ Star this repo if you found it helpful!

</div>
