# Dwellora

Dwellora is a Django REST backend with a React/Vite management frontend.

## Backend: local setup

Run these commands from the `dwellora/` directory (the directory containing `manage.py`):

```bash
python3.13 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
cp .env.example .env
python manage.py check
```

On Windows PowerShell, activate the environment with:

```powershell
.venv\Scripts\Activate.ps1
```

Then run:

```bash
python manage.py runserver
```

The default local database is SQLite. **Do not run migrations yet.** The custom user model and several application models need to be reconciled, and initial migrations must be generated only after that review.

## Frontend: local setup

Run from `dwellora/frontend/`:

```bash
npm install
npm run build
npm run dev
```

Set `VITE_API_BASE_URL` in the frontend environment to the API origin including the `/api/` prefix when the application API routes are restored.

## Current stabilization status

The repository is being stabilized in small, verifiable steps. The Django project configuration and process health endpoint are restored first. Application API routes are intentionally not mounted yet because several existing app modules have unresolved model/import inconsistencies. They will be re-enabled after those modules are repaired and tested.

Never commit `.env`, database files, virtual environments, or generated build output.
