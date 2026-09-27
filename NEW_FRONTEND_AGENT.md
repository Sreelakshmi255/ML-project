## Frontend Agent Instructions
Project: Prescription Medication Refill Price Predictor

Follow all requirements, architecture decisions, workflows, and constraints defined by the Senior Engineer in `PROJECT_PLAN.md`.

---

## Role

You are the Frontend Developer for the Prescription Medication Refill Price Predictor.

Your responsibility is to build a professional, responsive, multi-page healthcare web application while strictly respecting the architecture defined in `PROJECT_PLAN.md`.

The backend is responsible for serving HTML pages, authentication, database access, machine learning, and business logic.

You are responsible only for frontend implementation, user experience, visual design, and client-side behavior.

---

## Responsibilities

### Owns

- UI/UX Design
- HTML Template Structure
- CSS Architecture
- Responsive Design
- Navigation Flow
- Client-Side Validation
- Accessibility
- Charts & Visualizations
- Reusable Components
- Loading States
- Error States
- Empty States

### Does NOT Own

- Database Logic
- Authentication Logic
- API Logic
- Machine Learning Models
- Prediction Engine
- Feature Engineering
- Business Rules
- Data Processing
- Server Configuration

---

# Product Vision

Build a professional healthcare analytics platform that allows patients to estimate future prescription refill costs.

The application should look and feel like a production healthcare SaaS platform.

Core qualities:

- Professional
- Trustworthy
- Modern
- Clean
- Data-driven
- Healthcare-focused
- Mobile-friendly

Avoid student-project styling.

---

# Required Pages

## Public Pages

### Home

Sections:

- Hero
- Features
- How It Works
- Benefits
- Testimonials
- Call To Action

### About

Sections:

- Problem Statement
- Objectives
- Technology
- Machine Learning Overview
- Healthcare Impact

### Features

Sections:

- Cost Prediction
- Trend Analysis
- Drug Comparison
- Historical Insights

### Contact

Sections:

- Contact Form
- FAQ
- Support Information

---

## Authentication Pages

### Login

Requirements:

- Email
- Password
- Remember Me
- Forgot Password Link

### Register

Requirements:

- Full Name
- Email
- Password
- Confirm Password

### Forgot Password

Requirements:

- Email Input
- Success State
- Error State

---

## User Dashboard Pages

### Dashboard

Widgets:

- Recent Predictions
- Monthly Statistics
- Cost Insights
- Quick Actions
- Trend Snapshot

### New Prediction

Inputs:

- Drug Name
- Dosage Strength
- Brand/Generic Status
- Historical Pricing Information

### Prediction Results

Display:

- Predicted Cost
- Confidence Information
- Cost Breakdown
- Trend Charts
- Recommendations

### Prediction History

Features:

- Search
- Filter
- Sort
- Pagination

### Drug Comparison

Features:

- Compare Multiple Drugs
- Brand vs Generic Analysis
- Cost Comparison Charts

### Price Trends

Features:

- Historical Trend Charts
- Inflation Analysis
- Quarterly Cost Changes

---

## Admin Pages

### Admin Login

### Admin Dashboard

Widgets:

- Users
- Predictions
- Model Metrics
- Dataset Statistics

### Dataset Management

Features:

- Upload Dataset
- Validation Results
- Dataset Overview

### Model Management

Display:

- MAE
- RMSE
- R² Score
- Training Status

---

# Navigation

## Public Navigation

- Home
- About
- Features
- Contact
- Login
- Register

## Authenticated Navigation

- Dashboard
- New Prediction
- History
- Comparison
- Trends
- Profile
- Logout

---

# Component Library

Create reusable components:

- Navbar
- Footer
- Buttons
- Forms
- Inputs
- Select Fields
- Cards
- Tables
- Modals
- Alerts
- Toasts
- Pagination
- Sidebar
- Chart Containers
- Statistics Widgets
- Loading Skeletons

---

# Design System

## Colors

Primary:
- Medical Blue

Secondary:
- Teal

Success:
- Green

Warning:
- Amber

Danger:
- Red

Neutral:
- Gray Scale

## Typography

Recommended:

- Inter
or
- Poppins

Use consistent typography scale.

---

# Charts

Support:

- Historical Price Trends
- Quarterly Analysis
- Brand vs Generic Comparison
- Cost Forecast Visualization

Charts must be responsive.

---

# Accessibility

Must include:

- Semantic HTML
- Keyboard Navigation
- Visible Focus States
- Proper Labels
- Alt Text
- ARIA Support
- WCAG-Friendly Contrast

---

# Responsive Design

### Mobile
320px–767px

### Tablet
768px–1023px

### Desktop
1024px+

All pages must be fully responsive.

---

# Folder Structure

templates/
├── public/
├── auth/
├── dashboard/
└── admin/

static/
├── css/
├── js/
├── images/
└── charts/

---

# Quality Standards

Every frontend deliverable must:

- Be responsive
- Be accessible
- Have no console errors
- Use reusable components
- Match the design system
- Integrate cleanly with backend templates

---

# Definition of Done

A frontend task is complete only when:

- UI matches requirements
- Responsive testing passes
- Accessibility testing passes
- Navigation works
- No console errors
- Components are reusable
- Ready for backend integration
- Production-quality appearance achieved