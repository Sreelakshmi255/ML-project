# Backend Agent — Prescription Medication Refill Price Predictor

Follow `PROJECT_PLAN.md`. This agent owns server-side logic only.

## Responsibilities
- Flask routing and server-side rendering
- Authentication and authorization
- SQLite/SQLAlchemy persistence
- ML model training/loading/inference
- Feature engineering
- API validation and error handling
- Dataset and model administration
- Analytics services

## Do not change
- Visual design
- CSS styling
- Page layout decisions
- Client-side UX
- Browser presentation code except the minimum API contract required for integration

## Integration contract
Frontend calls:
- `POST /api/predict`
- `GET /api/history`
- `GET /api/trends`
- `GET /api/insights`
- `DELETE /api/history/<id>`

All prediction values must be validated server-side.
