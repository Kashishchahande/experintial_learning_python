# Digital Notice Board System

A Python and Streamlit web application for managing college notices.

## Features
- Administrator login
- Add, edit and delete notices
- Search notices by title and description
- Filter by category
- Sort by publication date
- Optional expiry dates
- SQLite database

## Requirements
- Python 3.10 or later
- pip

## Run on Windows

Open PowerShell in this folder and run:

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m streamlit run app.py
```

Open the local URL shown in the terminal.

## Demo administrator account

- Username: `admin`
- Password: `admin123`

This default account is for local testing only. Change credentials before deployment.

You can set environment variables in PowerShell before launching the app:

```powershell
$env:ADMIN_USERNAME = "your-admin"
$env:ADMIN_PASSWORD = "your-strong-password"
```

## Database

SQLite creates `notices.db` automatically when the app starts. Back up this file to preserve notices.

For cloud deployment, use secure credentials and a persistent managed database.

## Project structure

- `app.py` — main Streamlit application
- `requirements.txt` — Python dependencies
- `README.md` — documentation
- `.gitignore` — excluded files

## Author

Add your name here.
