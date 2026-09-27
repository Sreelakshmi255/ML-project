# Prescription Medication Refill Price Predictor

A professional multi-page Flask application for demonstrating prescription refill cost forecasting.

## Run locally

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
python app.py
```

Open `http://127.0.0.1:5000`.

### Demo accounts
- User: `demo@example.com` / `Demo@12345`
- Admin: `admin@example.com` / `Admin@12345`

The application creates its SQLite database and trains a deterministic demonstration model on first start.

## Architecture
Flask serves Jinja HTML pages and JSON endpoints. The frontend is only HTML, CSS and vanilla JavaScript. No frontend framework or chart library is used.

## Important
This is a software/ML demonstration. Predictions are estimates, not guaranteed pharmacy prices or medical advice.

## Refill planning features
- Medicine search provides generic/brand record counts, latest quarterly prices, and available historical entries.
- Pharmacy comparison derives illustrative estimates from the latest sample price. Pharmacy names, availability, and prices are not live data or quotes.
- Prediction results include a model-derived range and an indicative confidence score. The score is a heuristic, not a calibrated probability.
- Trend views summarize the latest one, two, or four available quarterly observations (3 months, 6 months, or 1 year) and overlay the user's latest matching prediction when present.
- Price alerts are stored per user and checked against the latest historical sample price when the dashboard loads. They appear in the dashboard but do not send email, SMS, or push notifications.

The existing sample dataset and interface use USD. Live pharmacy feeds, INR conversion, and external notification delivery are not configured.
