# Fit Fusion

Fit Fusion is a full-stack fitness tracking app: a **Flask REST API** backend and a **React (Vite) SPA** frontend, styled with Tailwind CSS and charted with Recharts.

## Features

- **Auth** — register/login with JWT, on-site "forgot password" reset (no email required), profile management, data export as JSON.
- **Dashboard** — BMI, TDEE-based calorie plans, and an interactive weight/BMI trend chart.
- **Workout Tracking** — log sets/reps/weight, exercise autocomplete from the library, paginated history with inline edit/delete.
- **Goals** — set weight, strength, workout-count, or custom goals with progress bars; auto-marks complete when the target is hit.
- **Exercise Library** — searchable/filterable catalog (category, muscle group, equipment, difficulty, instructions).
- **Nutrition Logging** — log meals/macros per day, tracked against your TDEE target with a daily progress bar.
- **Fit Bot** — AI chat widget for quick fitness/nutrition advice (falls back to a canned tip if no OpenAI key is configured).

## Project Structure

```
backend/    Flask REST API (SQLAlchemy models, JWT auth, blueprints per feature)
frontend/   React + Vite SPA (Tailwind CSS, React Router, Recharts, Axios)
```

## Running locally

### Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # set SECRET_KEY / JWT_SECRET_KEY / OPENAI_API_KEY
python run.py                   # runs on http://127.0.0.1:5000
```

The API auto-creates its SQLite database and seeds the exercise library on first run.

### Frontend

```bash
cd frontend
npm install
npm run dev                     # runs on http://localhost:5173, proxies /api to the backend
```

Open `http://localhost:5173` in your browser. Register an account to get started.

## API Overview

All endpoints are under `/api` and (aside from `/api/auth/*`) require a `Authorization: Bearer <token>` header.

| Area | Endpoints |
|------|-----------|
| Auth | `POST /auth/register`, `POST /auth/login`, `GET /auth/me`, `POST /auth/forgot-password`, `POST /auth/reset-password` |
| Profile | `GET/PUT /profile`, `GET /profile/download` |
| Workouts | `GET/POST /workouts`, `PUT/DELETE /workouts/<id>`, `GET /workouts/dashboard` |
| Goals | `GET/POST /goals`, `PUT/DELETE /goals/<id>` |
| Exercises | `GET /exercises?search=&category=&muscle_group=` |
| Nutrition | `GET/POST /nutrition`, `DELETE /nutrition/<id>` |
| Fit Bot | `POST /chatbot` |

## Environment Variables (`backend/.env`)

| Variable | Purpose |
|----------|---------|
| `SECRET_KEY` | Flask session secret |
| `JWT_SECRET_KEY` | JWT signing secret |
| `OPENAI_API_KEY` | Enables live Fit Bot responses (optional) |
| `DATABASE_URL` | SQLAlchemy database URI (defaults to local SQLite) |
