# SMS & Email Guard 🛡️

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.0%2B-092E20.svg)](https://www.djangoproject.com/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-3.4-38B2AC.svg)](https://tailwindcss.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An anti-fraud & phishing threat intelligence web platform built with Django and Tailwind CSS. Designed specifically for inspecting communication channels (SMS, Email, Instant Messaging), identifying BVN/NIN scams, and flagging fraudulent messages targeting users across Nigerian financial networks.

---

## ✨ Key Features

- **🛡️ Real-Time Threat Detection**: Classifies message inputs into `Legitimate`, `Spam`, or `Fraud / Phishing` with confidence scoring.
- **🇳🇬 Regional Fraud Vectors**: Tailored to detect banking impersonation, BVN audit scams, lottery spam, and eNaira phishing patterns.
- **⚙️ Modular Settings Architecture**: Settings cleanly split into `base.py`, `dev.py`, and `prod.py` under `config/settings/`.
- **🔒 Environment Secrets**: Complete separation of secrets using `python-decouple` (`.env` file configuration).
- **🗄️ Dual Database Strategy**: Native PostgreSQL support via `dj-database-url` with seamless SQLite (`db.sqlite3`) fallback for local development.
- **🎨 Trustworthy Dark Slate UI**: Responsive layout built with a calm slate & blue palette (`#0f172a`, `#1e293b`, `#2563eb`), reserving red/amber accents strictly for threat alerts.
- **🔑 Full Authentication System**: User registration, sign-in, logout, user profile dashboard, and `@login_required` route security.
- **🔁 Active Learning Feedback Loop**: Analysts can flag misclassifications, polish corrections in Django Admin, and export merged datasets for model retraining.

---

## 🛠️ Technology Stack

| Layer | Technology |
|---|---|
| **Backend Framework** | Django 5.0+ (Python 3.10+) |
| **Database** | PostgreSQL (Production) / SQLite (Local Dev Fallback) |
| **Configuration** | `python-decouple`, `dj-database-url` |
| **Frontend & Styling** | Django Templates, Tailwind CSS |
| **Visualization** | Chart.js (CDN) |
| **Image Processing** | Pillow 10.2+ |

---

## 📂 Repository Structure

```
spam email detection/
├── manage.py                   # Django management script
├── requirements.txt             # Project dependencies
├── .env.example                 # Environment variables template
├── .gitignore                  # Git ignore rules
│
├── config/                      # Core configuration package
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base.py             # Shared settings & app registrations
│   │   ├── dev.py              # Local development overrides
│   │   └── prod.py             # Production security settings
│   ├── urls.py                 # Main URL routing
│   ├── wsgi.py                 # WSGI entry point
│   └── asgi.py                 # ASGI entry point
│
├── apps/                        # Modular Django applications
│   ├── accounts/               # User authentication & profile management
│   ├── detector/               # Threat detection models, rule engine & feedback
│   │   ├── management/commands/
│   │   │   ├── load_starter_data.py    # Command to seed starter dataset
│   │   │   └── export_training_data.py # Command to export retraining CSV
│   │   └── data/               # Starter CSV training datasets
│   ├── inbox/                  # Message logs, submission form & history
│   └── dashboard/              # Analytics & Chart.js reports
│
├── static/                      # Static assets (CSS, JS, Images)
│   ├── css/
│   │   ├── input.css           # Tailwind source directives
│   │   └── dist/styles.css     # Compiled stylesheet
│   └── js/
│       └── main.js
│
└── templates/                   # Global HTML templates
    ├── base.html               # Main base layout with navbar & sidebar
    ├── components/             # Reusable UI components (navbar, sidebar, footer)
    ├── accounts/               # Auth templates (login, register, profile)
    ├── dashboard/              # Analytics grid template with Chart.js
    ├── detector/               # Threat inspector screen
    ├── inbox/                  # Submit form, result detail & submission history
    └── pages/                  # Overview dashboard
```

---

## 🚀 Quick Start Guide

### Prerequisites

- **Python 3.10+** installed on your system.
- **Git** for version control.

---

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/sms-email-guard.git
cd sms-email-guard
```

---

### 2. Create and Activate a Virtual Environment

**Windows (PowerShell)**:
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**Linux / macOS**:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 4. Configure Environment Variables

Create your `.env` file from the provided template:

**Windows (PowerShell)**:
```powershell
Copy-Item .env.example .env
```

**Linux / macOS**:
```bash
cp .env.example .env
```

---

### 5. Run Database Migrations & Seed Starter Data

Apply the database migrations and populate the local database with 86 Nigerian training records:

```bash
python manage.py migrate
python manage.py load_starter_data
```

---

### 6. Create an Administrative Superuser

```bash
python manage.py createsuperuser
```

---

### 7. Run Automated Tests

Verify that all models, threat engines, views, and authentication protections function cleanly:

```bash
python manage.py test
```

> Output: `Ran 9 tests ... OK`

---

### 8. Start the Development Server

```bash
python manage.py runserver
```

Open your browser and navigate to **`http://127.0.0.1:8000/`**.

---

## 🔁 Active-Learning Retraining Loop

SMS & Email Guard incorporates a continuous human-in-the-loop retraining pipeline to update threat classification rules and ML models over time:

```
[1. User Inspection / CSV Upload] ➔ [2. Rule Engine / ML Prediction]
                                            │
                                            ▼
                               [3. "This was Misclassified"]
                                            │
                                            ▼
                               [4. FeedbackCorrection Saved]
                                            │
                                            ▼
                               [5. Admin Review & Polish]
                                            │
                                            ▼
                               [6. export_training_data]
                                            │
                                            ▼
                             [7. Updated Retraining CSV Feed]
```

### Steps in the Retraining Loop:

1. **Submit Corrections**: On any inspection detail page (`/inbox/result/<pk>/`), users or analysts click **"This was misclassified"** to submit a `FeedbackCorrection` (correct label + reasoning note).
2. **Review in Django Admin**: Administrative superusers inspect correction entries at `/admin/detector/feedbackcorrection/` with color-coded label badges and raw message snippets.
3. **Export Retraining Dataset**: Run the management command to merge original dataset records with human corrections:
   ```bash
   python manage.py export_training_data
   ```
   *By default, this writes an updated CSV to `apps/detector/data/retraining_dataset.csv` ready to feed into ML training scripts (`train_model.py`).*

---

## 🔑 Application Endpoints

| URL Path | Access | Description |
|---|---|---|
| `/` | Logged In | Main Anti-Fraud Overview Dashboard |
| `/dashboard/analytics/` | Logged In | Interactive Chart.js Threat Analytics |
| `/inbox/submit/` | Logged In | Message Threat Inspector & Bulk CSV Upload |
| `/inbox/history/` | Logged In | User Submission History with Filters & Pagination |
| `/inbox/result/<pk>/` | Logged In | Inspection Result Details & Feedback Correction Form |
| `/accounts/login/` | Public | Standalone User Sign-In Page |
| `/accounts/register/` | Public | Standalone User Registration Page |
| `/accounts/profile/` | Logged In | Account Security & Profile Dashboard |
| `/admin/` | Admin Only | Django Administration Portal |

---

## 🗄️ Database Models Summary

- **`Message` (`apps.inbox`)**: Stores raw message bodies, channels (`sms`, `email`, `whatsapp`), sender details, submission timestamp, and user relation.
- **`DetectionResult` (`apps.detector`)**: Linked 1:1 with `Message`. Stores threat classification label (`legit`, `spam`, `fraud`), confidence score, extracted keywords, language mix (`english`, `pidgin`, `mixed`), and model version.
- **`FeedbackCorrection` (`apps.detector`)**: Stores human analyst corrections (`corrected_label`, `note`, `corrected_by`) for model retraining.

---

## 📄 License

Distributed under the **MIT License**. See `LICENSE` for more information.
