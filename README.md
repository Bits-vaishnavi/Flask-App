# ACEest Fitness & Gym API

This repository contains a Flask-based REST API for managing clients, programs, workouts, progress, and metrics for a gym/coaching service.

---

## ✅ What’s Included

- **Flask API** with endpoints for: health check, programs, clients, progress, workouts, and metrics
- **SQLite** persistence (`aceest_fitness.db`)
- **Swagger UI** via Flasgger (`/apidocs/`)
- **Unit tests** with `pytest` (`test_app.py`)
- **Docker support** with `Dockerfile` + `docker-compose.yml`
- **CI workflow** via GitHub Actions (build/test/docker)
- **Jenkins pipeline** example (`Jenkinsfile`)

---

## 🚀 Running Locally (Python)

```bash
python -m venv .venv
source .venv/Scripts/activate    # Windows
# or: source .venv/bin/activate  # macOS/Linux

pip install -r requirements.txt
python app.py
```

Then open:
- `http://127.0.0.1:5000/` (health)
- `http://127.0.0.1:5000/apidocs/` (Swagger UI)

---

## 🧪 Running Tests

```bash
pytest -v
```

---

## 🐳 Running in Docker

### Build & run

```bash
docker build -t aceest-fitness-api .
docker run --rm -p 5000:5000 aceest-fitness-api
```

### With docker-compose (recommended)

```bash
docker compose up --build
```

This mounts the project into the container and persists the SQLite DB.

---

## ✅ CI/CD Overview

### GitHub Actions
The workflow at `.github/workflows/ci.yml` runs on pushes and pull requests to `main` and executes:

1. Install dependencies
2. Lint & syntax check (`py_compile`, `ruff`)
3. Run unit tests (`pytest`)
4. Build Docker image

### Jenkins (Optional)
This repo includes a `Jenkinsfile` that can be used by a Jenkins pipeline job. It performs the same steps as the GitHub Actions workflow:

- Checkout code
- Install deps
- Lint + unit tests
- Build Docker image + simple container sanity check

---

## 📌 Notes
- The SQLite database is stored in `aceest_fitness.db`.
- If you want to reset data, delete `aceest_fitness.db` and restart.

---

## ✨ Tips
- Use `Postman` or `curl` to hit endpoints.
- Add Swagger docstrings to any new endpoints to keep `/apidocs/` updated.
