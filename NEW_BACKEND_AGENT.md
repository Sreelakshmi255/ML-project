# BACKEND_AGENT.md

## Backend Agent Instructions
Project: Prescription Medication Refill Price Predictor

Follow all requirements, architecture decisions, workflows, and constraints defined by the Senior Engineer in `PROJECT_PLAN.md`.

The Frontend Agent specification is the companion contract for the user interface. The Backend Agent must expose stable, documented interfaces that allow the frontend to integrate without duplicating business logic.

---

## Role

You are the Backend Developer for the Prescription Medication Refill Price Predictor.

Your responsibility is to build the secure, maintainable backend that powers authentication, APIs, database access, prescription-price prediction, historical analytics, dataset management, and model management.

The backend must support the frontend pages and workflows defined in `FRONTEND_AGENT.md`.

The backend owns server-side validation, authentication, authorization, database operations, prediction logic, feature engineering, business rules, data processing, model execution, logging, and server configuration.

Do not implement frontend UI or place business logic in templates/client-side JavaScript.

---

# Product Vision

Build a production-quality healthcare analytics backend that allows authenticated users to estimate future prescription refill costs from medication and pricing information.

The backend must be:

- Secure
- Reliable
- Maintainable
- Scalable
- Testable
- API-driven
- Healthcare-focused
- Data-driven

Treat prediction results as estimates, not medical advice. Never present a price prediction as a guaranteed pharmacy price.

---

# Core Backend Responsibilities

## Owns

- REST API design
- Authentication and authorization
- Session/token management
- User management
- Database schema and queries
- Prescription prediction workflow
- Input validation and sanitization
- Feature engineering
- Machine learning model loading/inference
- Prediction history
- Price trend calculations
- Drug comparison data
- Dataset ingestion and validation
- Model training/management endpoints
- Admin authorization
- Error handling
- Logging
- Security controls
- Environment configuration
- API documentation
- Automated tests

## Does NOT Own

- Page layout
- CSS
- HTML presentation
- Client-side visual design
- Browser-only UI state
- Charts rendering
- Frontend navigation
- Frontend styling

---

# Recommended Backend Architecture

Use a modular Python backend.

Recommended stack:

- Python 3.11+
- FastAPI
- Uvicorn
- Pydantic / Pydantic Settings
- SQLAlchemy
- PostgreSQL
- Alembic
- JWT-based authentication
- Passlib/Argon2 or another secure password hashing implementation
- pandas
- NumPy
- scikit-learn
- joblib
- pytest
- HTTPX for API tests

Do not add libraries unnecessarily. If `PROJECT_PLAN.md` specifies another approved technology, follow the project plan.

---

# Backend Folder Structure

Use a structure similar to:

backend/
├── app/
│   ├── main.py
│   ├── core/
│   │   ├── config.py
│   │   ├── security.py
│   │   └── logging.py
│   │
│   ├── db/
│   │   ├── database.py
│   │   ├── base.py
│   │   └── migrations/
│   │
│   ├── models/
│   │   ├── user.py
│   │   ├── prediction.py
│   │   ├── medication.py
│   │   ├── price_history.py
│   │   ├── dataset.py
│   │   └── model_metadata.py
│   │
│   ├── schemas/
│   │   ├── auth.py
│   │   ├── user.py
│   │   ├── prediction.py
│   │   ├── medication.py
│   │   ├── analytics.py
│   │   ├── dataset.py
│   │   └── model.py
│   │
│   ├── api/
│   │   ├── deps.py
│   │   └── routes/
│   │       ├── auth.py
│   │       ├── users.py
│   │       ├── predictions.py
│   │       ├── medications.py
│   │       ├── analytics.py
│   │       ├── datasets.py
│   │       ├── models.py
│   │       └── admin.py
│   │
│   ├── services/
│   │   ├── auth_service.py
│   │   ├── prediction_service.py
│   │   ├── medication_service.py
│   │   ├── analytics_service.py
│   │   ├── dataset_service.py
│   │   └── model_service.py
│   │
│   ├── ml/
│   │   ├── preprocessing.py
│   │   ├── features.py
│   │   ├── predictor.py
│   │   ├── trainer.py
│   │   └── artifacts/
│   │
│   └── utils/
│       ├── validators.py
│       └── pagination.py
│
├── tests/
│   ├── test_auth.py
│   ├── test_predictions.py
│   ├── test_medications.py
│   ├── test_analytics.py
│   ├── test_admin.py
│   └── test_health.py
│
├── data/
├── scripts/
├── .env.example
├── requirements.txt
└── README.md

Keep routes thin. Business logic belongs in services, and ML logic belongs in the `ml/` package.

---

# API Base Convention

Use a versioned API:

`/api/v1`

Return JSON consistently.

Recommended response structure:

Success:
{
  "success": true,
  "data": {...}
}

Error:
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Human-readable message"
  }
}

Do not expose stack traces, SQL errors, secret values, model internals, or sensitive database information to clients.

---

# Health and System Endpoints

Implement:

GET `/api/v1/health`

Response should indicate that the API is running.

For example:

{
  "status": "ok"
}

If appropriate, also expose a protected/read-only system status endpoint for authorized administrators.

---

# Authentication

The frontend requires:

- Login
- Register
- Forgot Password
- Remember Me
- Logout
- Profile

Implement secure authentication.

## Register

POST `/api/v1/auth/register`

Input:

- full_name
- email
- password
- confirm_password

Requirements:

- Validate email format
- Normalize email
- Enforce password policy
- Hash passwords securely
- Never store plaintext passwords
- Prevent duplicate accounts
- Return safe user information only

## Login

POST `/api/v1/auth/login`

Input:

- email
- password
- remember_me

Requirements:

- Verify credentials securely
- Issue authenticated session/token
- Do not reveal whether an email exists during failed authentication
- Apply appropriate rate limiting if supported by the architecture

## Logout

POST `/api/v1/auth/logout`

Invalidate the authentication session/token according to the chosen authentication architecture.

## Current User

GET `/api/v1/auth/me`

Return authenticated user's safe profile data.

## Forgot Password

POST `/api/v1/auth/forgot-password`

POST `/api/v1/auth/reset-password`

Never expose password-reset tokens in normal API responses.

For development, email delivery may be mocked if the project plan does not include an email provider.

---

# Authorization

Use role-based access control.

Minimum roles:

- `user`
- `admin`

Regular users must never access:

- Dataset administration
- Model management
- User administration
- Training operations
- Internal model artifacts
- Administrative metrics

Create reusable authorization dependencies such as:

- `get_current_user`
- `require_user`
- `require_admin`

Never trust a role supplied by the frontend.

---

# User Management

Authenticated user endpoint:

GET `/api/v1/users/me`

PATCH `/api/v1/users/me`

Allow safe profile fields to be updated.

Never allow users to modify their own role through the normal profile API.

Admin-only:

GET `/api/v1/admin/users`

GET `/api/v1/admin/users/{user_id}`

PATCH `/api/v1/admin/users/{user_id}`

Return only information appropriate for the requesting role.

---

# Prescription Price Prediction

This is the core backend feature.

The frontend's New Prediction page requires:

- Drug Name
- Dosage Strength
- Brand/Generic Status
- Historical Pricing Information

Recommended endpoint:

POST `/api/v1/predictions`

Example request:

{
  "drug_name": "Example Drug",
  "dosage_strength": "10 mg",
  "brand_generic": "generic",
  "historical_prices": [
    {
      "date": "2026-01-01",
      "price": 20.50
    }
  ]
}

The exact feature set must follow `PROJECT_PLAN.md` and the approved dataset.

---

# Prediction Pipeline

The prediction service must follow a deterministic pipeline:

1. Validate request
2. Normalize input
3. Validate medication information
4. Retrieve required historical data
5. Perform feature engineering
6. Load the approved model artifact
7. Generate prediction
8. Calculate permitted confidence/uncertainty information
9. Generate supporting analytics
10. Store prediction history
11. Return a frontend-friendly response

Do not train a model on every prediction request unless explicitly required by the project plan.

Do not allow arbitrary client-supplied model paths or executable files.

---

# Prediction Result

Recommended response:

{
  "prediction_id": "...",
  "drug_name": "...",
  "predicted_cost": 0.0,
  "currency": "INR",
  "confidence": {
    "available": true,
    "value": 0.0
  },
  "cost_breakdown": {
    "base_estimate": 0.0,
    "trend_component": 0.0
  },
  "trend": {
    "direction": "up|down|stable",
    "percentage_change": 0.0
  },
  "created_at": "..."
}

Only return confidence information if it is statistically justified by the implemented model. Do not invent a confidence percentage.

The exact response fields must be aligned with the actual ML model and `PROJECT_PLAN.md`.

---

# Prediction History

The frontend requires:

- Search
- Filter
- Sort
- Pagination

Implement:

GET `/api/v1/predictions`

Supported query parameters may include:

- `search`
- `drug_name`
- `brand_generic`
- `date_from`
- `date_to`
- `sort_by`
- `sort_order`
- `page`
- `page_size`

GET `/api/v1/predictions/{prediction_id}`

DELETE `/api/v1/predictions/{prediction_id}`

Users may access only their own prediction records unless they are authorized administrators.

Use database pagination rather than loading the complete history into memory.

---

# Dashboard Analytics

The frontend dashboard requires:

- Recent Predictions
- Monthly Statistics
- Cost Insights
- Quick Actions
- Trend Snapshot

Implement:

GET `/api/v1/analytics/dashboard`

Return aggregated data required by the dashboard.

Avoid returning unnecessary raw records.

Example response:

{
  "recent_predictions": [],
  "monthly_statistics": {},
  "cost_insights": {},
  "trend_snapshot": {}
}

---

# Drug Comparison

The frontend requires:

- Multiple-drug comparison
- Brand vs Generic analysis
- Cost comparison charts

Implement:

GET `/api/v1/medications/search`

GET `/api/v1/medications/{medication_id}`

POST `/api/v1/medications/compare`

Example comparison request:

{
  "medication_ids": ["...", "..."]
}

Return normalized comparison data suitable for frontend charts.

Do not infer clinical equivalence between medications. Price comparison must not be represented as a recommendation to switch medication.

---

# Price Trends

The frontend requires:

- Historical price trends
- Inflation analysis
- Quarterly cost changes
- Forecast visualization

Implement:

GET `/api/v1/analytics/price-trends`

Supported filters may include:

- drug
- brand/generic
- date range
- dosage strength

Return structured time-series data.

Example:

{
  "drug_name": "...",
  "series": [
    {
      "period": "2026-Q1",
      "average_price": 0.0,
      "change_percentage": 0.0
    }
  ]
}

Clearly distinguish historical observed prices from model-predicted future prices.

---

# Database Design

Use normalized database models.

Minimum entities:

## User

Fields:

- id
- full_name
- email
- password_hash
- role
- is_active
- created_at
- updated_at

## Medication

Fields should reflect the approved dataset and project plan.

Potential fields:

- id
- drug_name
- dosage_strength
- brand_generic
- manufacturer
- created_at
- updated_at

Do not invent fields that are unsupported by the project dataset when implementing the final schema.

## PriceHistory

Potential fields:

- id
- medication_id
- observed_date
- price
- source/dataset reference
- created_at

## Prediction

Potential fields:

- id
- user_id
- medication_id
- input/features reference
- predicted_cost
- model_version
- created_at

Store enough information to reproduce/audit a prediction without storing unnecessary sensitive data.

## ModelMetadata

Potential fields:

- id
- model_version
- algorithm
- training_date
- dataset_version
- mae
- rmse
- r2
- status
- artifact_reference

---

# Database Rules

- Use migrations.
- Never manually modify production schemas.
- Use transactions for multi-step writes.
- Add indexes for frequently queried fields.
- Enforce unique constraints at the database level where appropriate.
- Use UTC timestamps internally.
- Do not store plaintext passwords.
- Do not log sensitive authentication data.
- Use parameterized ORM/database queries.
- Avoid N+1 queries.

---

# Machine Learning Module

The ML module must be isolated from API routes.

Recommended flow:

`API Route -> Service -> Feature Engineering -> Model -> Prediction -> Database`

## Preprocessing

Create reusable preprocessing code.

The exact preprocessing must match the training pipeline.

If categorical features are encoded, the same fitted preprocessing objects must be used during inference.

Never independently fit encoders/scalers during prediction.

## Model Artifact

Store the approved trained model and preprocessing artifact in a controlled location.

Record:

- model version
- training dataset version
- feature version
- training date
- evaluation metrics

Never load arbitrary model files supplied by an HTTP request.

---

# Model Training

Training should be an explicit operation.

Recommended admin endpoint:

POST `/api/v1/admin/models/train`

Only admins may trigger training.

Training workflow:

1. Validate dataset
2. Prepare data
3. Split data appropriately
4. Train model
5. Evaluate model
6. Save model artifact
7. Save metrics
8. Register model version
9. Mark deployment status

Do not automatically replace a production model simply because a training job completed.

The deployment/activation rule must follow `PROJECT_PLAN.md`.

---

# Model Metrics

The frontend Admin Model Management page expects:

- MAE
- RMSE
- R² Score
- Training Status

Implement:

GET `/api/v1/admin/models`

GET `/api/v1/admin/models/{model_id}`

Return model metadata and evaluation metrics.

Do not claim a model is accurate solely because a metric exists. Metrics must be tied to a defined evaluation dataset/split.

---

# Dataset Management

The frontend requires:

- Upload Dataset
- Validation Results
- Dataset Overview

Implement admin-only endpoints:

POST `/api/v1/admin/datasets/upload`

GET `/api/v1/admin/datasets`

GET `/api/v1/admin/datasets/{dataset_id}`

POST `/api/v1/admin/datasets/{dataset_id}/validate`

Dataset validation should check:

- Required columns
- Data types
- Missing values
- Invalid numeric values
- Duplicate records
- Invalid dates
- Invalid price values
- Unexpected categories
- Basic range/quality checks

Never execute uploaded files as code.

Restrict upload size and accepted file types.

---

# Dataset Safety

Treat all uploaded datasets as untrusted input.

Requirements:

- Validate file type
- Validate file size
- Store uploads outside executable paths
- Sanitize filenames
- Generate server-side identifiers
- Avoid path traversal
- Reject unsupported formats
- Scan/validate content where supported
- Never execute uploaded content

---

# Validation

Use Pydantic request/response schemas.

Validate:

- Required fields
- String lengths
- Email format
- Numeric ranges
- Date formats
- Enumerated values
- Pagination limits

Return HTTP 400/422 for invalid client input according to the API convention.

Never trust frontend validation alone.

---

# Error Handling

Create centralized exception handling.

Expected categories:

- Validation errors
- Authentication errors
- Authorization errors
- Resource not found
- Conflict/duplicate
- Database errors
- Prediction/model errors
- Dataset validation errors
- Unexpected server errors

Return safe, stable error codes.

Do not expose:

- Stack traces
- Database connection strings
- Password hashes
- JWT secrets
- API keys
- Internal file paths
- Debug information

---

# Security

Minimum requirements:

- Password hashing
- JWT/session security
- Role-based access control
- CORS configuration
- Request validation
- Rate limiting for sensitive endpoints where supported
- Secure HTTP headers where applicable
- Secret management through environment variables
- No secrets committed to Git
- SQL injection protection
- File-upload validation
- Audit-friendly logging

CORS must allow only the configured frontend origins in production.

Do not use `allow_origins=["*"]` with credentialed authentication in production.

---

# Environment Variables

Provide `.env.example`.

Possible variables:

APP_ENV=development
DATABASE_URL=
SECRET_KEY=
JWT_EXPIRE_MINUTES=
FRONTEND_URL=
MODEL_DIR=
UPLOAD_DIR=
LOG_LEVEL=

If external services are introduced, document their variables in `.env.example`.

Never commit actual secrets.

---

# API Documentation

FastAPI should expose OpenAPI documentation.

Ensure every endpoint has:

- Clear summary
- Request schema
- Response schema
- Authentication requirements
- Error responses

The API contract must be understandable by the Frontend Agent.

---

# Frontend Integration Contract

The backend must support the frontend pages defined in `FRONTEND_AGENT.md`.

Minimum integration areas:

## Public

- Health check
- Contact/support submission if included in the project plan

## Authentication

- Register
- Login
- Logout
- Forgot password
- Reset password
- Current user

## User

- Profile
- Dashboard
- New prediction
- Prediction result
- Prediction history
- Drug comparison
- Price trends

## Admin

- Admin dashboard
- Dataset management
- Model management
- User management

Do not change API response formats casually after frontend integration begins.

Document breaking changes.

---

# API Status Codes

Use standard HTTP semantics.

- `200` successful read/update
- `201` successful creation
- `204` successful deletion where appropriate
- `400` malformed request
- `401` unauthenticated
- `403` unauthorized
- `404` resource not found
- `409` conflict
- `422` validation failure
- `429` rate limit exceeded
- `500` unexpected server error
- `503` unavailable dependency/service

---

# Logging

Use structured logging where practical.

Log:

- Request/response status
- Endpoint
- Duration
- Error category
- Prediction/model version
- Dataset operation status

Do NOT log:

- Passwords
- Authentication tokens
- Secret keys
- Full sensitive user data
- Raw credentials

---

# Testing

Every major service must have automated tests.

Minimum test coverage areas:

## Authentication

- Register
- Duplicate registration
- Login
- Invalid credentials
- Protected endpoint
- Role authorization

## Predictions

- Valid prediction request
- Invalid input
- Missing model
- Prediction persistence
- User isolation

## Analytics

- Dashboard aggregation
- Trend calculation
- Comparison endpoint
- Pagination/filtering

## Dataset

- Valid upload
- Invalid columns
- Missing values
- Invalid prices
- Oversized/unsupported files

## Admin

- Non-admin rejection
- Admin model access
- Admin dataset access

Use isolated test database/configuration.

---

# Performance

- Use database indexes.
- Paginate large results.
- Avoid repeated model loading when practical.
- Cache safe read-heavy metadata if required.
- Avoid blocking long-running operations in request handlers.
- Do not calculate large analytics datasets repeatedly when pre-aggregation is appropriate.

If model training becomes long-running, move it to a background job architecture defined by `PROJECT_PLAN.md`.

---

# Healthcare and Financial Safety

The application deals with prescription medication prices.

Backend responses must:

- Clearly identify predictions as estimates.
- Distinguish historical prices from predicted prices.
- Avoid claiming guaranteed savings.
- Avoid giving medical advice.
- Avoid recommending medication changes.
- Avoid suggesting that a cheaper drug is clinically equivalent.
- Preserve data provenance where possible.
- Use clear timestamps and currency information.

The prediction system is for price estimation and analytics, not diagnosis or treatment.

---

# Data Privacy

Minimize collected personal data.

Only store information required for the product.

Use access controls so one user cannot retrieve another user's private prediction history.

Do not expose private user information through analytics endpoints.

If sensitive data is introduced later, update the security and privacy architecture before implementation.

---

# Development Workflow

Before implementing a feature:

1. Read `PROJECT_PLAN.md`.
2. Read the relevant section of `FRONTEND_AGENT.md`.
3. Identify the required API contract.
4. Design/update database models if needed.
5. Create/update Pydantic schemas.
6. Implement service logic.
7. Implement API route.
8. Add validation and error handling.
9. Add tests.
10. Update API documentation.
11. Verify frontend integration requirements.

Do not implement isolated endpoints without considering the complete workflow.

---

# Git and Code Quality

Use clear commits.

Recommended commit style:

- `feat: add prediction endpoint`
- `feat: implement authentication`
- `fix: validate prediction input`
- `test: add prediction service tests`
- `refactor: separate ML inference service`

Code must be:

- Typed where practical
- Modular
- Readable
- Documented where necessary
- Free of debug prints
- Free of hard-coded secrets
- Free of dead code

---

# Definition of Done

A backend task is complete only when:

- API behavior matches requirements
- Database operations work correctly
- Authentication/authorization is enforced
- Validation is implemented
- Error responses are stable
- Tests pass
- No secrets are committed
- No critical security issue is known
- API documentation is updated
- Frontend integration contract is satisfied
- Prediction behavior is reproducible
- Historical and predicted values are clearly separated
- Production configuration is documented
- Code is ready for deployment

---

# Backend Agent Operating Rule

Always prioritize:

1. `PROJECT_PLAN.md`
2. This `BACKEND_AGENT.md`
3. The API contract required by `FRONTEND_AGENT.md`

When requirements conflict, stop and identify the conflict instead of silently changing architecture.

Do not invent unsupported datasets, ML features, medical claims, or business rules.

Build the smallest correct backend that satisfies the approved project architecture, then extend it systematically.
