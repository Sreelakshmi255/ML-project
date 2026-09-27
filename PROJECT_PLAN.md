# Prescription Medication Refill Price Predictor — Project Plan

## 1. Product Goal
Build a professional, responsive, multi-page healthcare analytics website that forecasts an expected out-of-pocket prescription refill cost using supervised regression. The backend is Python and serves the HTML pages directly; the frontend is strictly HTML, CSS and vanilla JavaScript.

## 2. Agent Ownership

### Frontend Agent — UI/UX only
Owns:
- HTML/Jinja template structure
- CSS design system and responsive layout
- Vanilla JavaScript interactions
- Forms, client-side validation, loading/error/empty states
- Navigation, accessibility and charts/visualizations
- Reusable visual components

Does not own:
- Database logic
- Authentication logic
- ML models
- Feature engineering
- Prediction/business rules
- Server configuration

### Backend Agent — backend logic only
Owns:
- Flask application and server-side rendering
- Authentication/session handling
- SQLite database and repositories
- Prediction APIs and ML pipeline
- Input validation and business rules
- History, analytics, admin services
- Dataset/model management
- Error handling, security and tests

Does not own:
- Visual design
- CSS/layout
- UX decisions
- Browser-only presentation behavior

## 3. Technology Constraints
- Python 3.10+
- Flask
- Jinja2
- SQLite
- SQLAlchemy
- scikit-learn
- pandas / numpy
- Werkzeug password hashing
- HTML5
- CSS3
- Vanilla JavaScript
- No React, Vue, Angular, Next.js, Tailwind, Bootstrap, Chart.js or other frontend framework/library.

## 4. Pages and navigation
Public:
- `/` Home
- `/about` About Project
- `/features` Features
- `/contact` Contact

Authentication:
- `/login`
- `/register`
- `/forgot-password`

Authenticated:
- `/dashboard`
- `/predict`
- `/results/<id>`
- `/history`
- `/comparison`
- `/trends`
- `/profile`
- `/logout`

Admin:
- `/admin/login`
- `/admin`
- `/admin/dataset`
- `/admin/model`

Every page is linked through the shared navigation and relevant call-to-action buttons.

## 5. Backend contract
HTML routes render Jinja templates. JSON endpoints:
- `GET /api/health`
- `GET /api/options`
- `POST /api/predict`
- `GET /api/history`
- `GET /api/insights`
- `GET /api/trends`
- `DELETE /api/history/<id>`
- `POST /api/contact`
- `POST /api/admin/dataset`
- `POST /api/admin/model/train`

Prediction input:
`drug_name`, `dosage_mg`, `brand_status`, `q1_price`, `q2_price`, `q3_price`, `q4_price`.

Prediction output:
predicted cost, indicative range, historical trend, model name and feature-based insight text.

## 6. ML plan
Feature engineering:
- TF-IDF drug-name text
- dosage strength
- generic/brand binary
- four quarterly prices
- historical mean
- recent price
- linear trend
- volatility

Models evaluated:
1. Linear Regression
2. Random Forest Regressor
3. Gradient Boosting Regressor

Metrics:
- MAE
- RMSE
- R²

The best model by validation RMSE is persisted to `models/best_model.joblib`.

## 7. Database
Tables:
- users
- predictions
- historical_prices
- contact_messages

The development database is SQLite. Passwords are hashed. Prediction records are associated with the signed-in user.

## 8. Security baseline
- Password hashing
- Session-based authentication
- Admin role checks
- Server-side validation
- Parameterized ORM/database access
- Maximum input lengths
- Secure upload extension allow-list
- Friendly error responses without stack traces

## 9. Definition of Done
- Multi-page site is functional and interconnected.
- Flask serves the HTML pages.
- Authentication works.
- Predictions work using the trained regression pipeline.
- Prediction history and trend analytics work.
- Admin model metrics are visible.
- Responsive desktop/tablet/mobile UI exists.
- No frontend framework is used.
- Project can run locally with `python app.py`.
