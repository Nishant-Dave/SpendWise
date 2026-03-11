# SpendWise 💸

SpendWise is a production-ready, full-stack personal finance application built with Django. It provides a clean, responsive interface for users to track their daily transactions, categorize expenses with visual identifiers, and analyze their spending habits through dynamic charts.

Designed with modern deployment in mind, this project utilizes a serverless architecture on Vercel backed by a cloud-native PostgreSQL database.

## ✨ Key Features

* **Interactive Analytics:** A dynamic, Chart.js-powered dashboard featuring custom time-range filtering (1-month, 3-month, and 6-month trends).
* **Smart Categorization:** Users can create custom categories assigned with specific emojis for quick visual identification across the app.
* **Frictionless UX:** Auto-generation of default categories for new users via Django Signals, and Post/Redirect/Get (PRG) patterns for seamless data entry.
* **Data Portability:** Built-in CSV export engine allowing users to download their complete transaction history.
* **Secure Authentication:** Full user lifecycle management, including secure, password-verified account deletion.

## 🛠️ Tech Stack & Architecture

* **Backend:** Python 3, Django
* **Database:** PostgreSQL (Hosted on Neon.tech), managed via `dj-database-url`
* **Frontend:** HTML5, Tailwind CSS (via CDN), Chart.js
* **Environment Management:** `python-decouple`
* **Deployment:** Vercel (Serverless WSGI)
* **Static Asset Management:** WhiteNoise

## 🚀 Deployment Strategy (Vercel + Neon)

This application is configured for a serverless environment. 
* **Routing:** The `vercel.json` file explicitly maps all incoming traffic to the Django `wsgi.py` application.
* **Static Files:** Django's `collectstatic` is intercepted and served efficiently via WhiteNoise middleware, bypassing Vercel's standard static file limitations.
* **Directory Structure:** The project is configured to run from a `backend` root directory, cleanly separating the Python environment from root-level repository files.

## 💻 Local Setup & Installation

To run SpendWise locally, ensure you have Python installed and follow these steps:

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/yourusername/spendwise.git](https://github.com/yourusername/spendwise.git)
   cd spendwise
