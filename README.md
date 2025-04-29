# README.md
# Selenium E2E Automation Framework

## 🚀 Overview
An end-to-end automation framework covering UI, API, and DB validations for domains like Healthcare, Banking, and E-Commerce.

## 📦 Features
- UI Testing (Selenium + Pytest)
- API Testing
- DB Validations
- Allure Reporting
- Cross-browser Support
- Smart Logging

# Selenium E2E Framework (Manual + AI Execution)

## Overview
- Full Selenium E2E automation framework.
- Supports both traditional (manual) and AI-assisted execution.
- Automatic fallback: if manual fails, AI retries execution.
- Environment-controlled execution mode (`.env` file).

## Project Structure
- `manual_execution/` → Manual page objects and tests.
- `ai_execution/` → AI-powered page objects and tests.
- `common/` → Shared utilities, drivers, configs.
- `main.py` → Single test runner.

## Execution Modes
Set inside `.env` file:
```bash
EXECUTION_MODE=manual
# or
EXECUTION_MODE=ai



## 🛠 Prerequisites
- Python 3.8+
- Google Chrome / Firefox
- pip, virtualenv

## ⚙️ Setup

```bash
git clone https://github.com/sqamentor/selenium_e2e.git
cd selenium_e2e
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
