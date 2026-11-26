# Dwellora

Dwellora is a Ghana-focused property platform with a Django REST API and a React/Vite account workspace. The current branch is deliberately being stabilised before database migrations and public marketplace features are enabled.

## Backend setup

Run from the `dwellora/` directory (the directory containing `manage.py`).

### Linux / macOS / GitHub Codespaces

```bash
python3.13 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
cp .env.example .env
python manage.py check
python manage.py runserver
```

### Windows PowerShell

```powershell
py -3.13 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
Copy-Item .env.example .env
python manage.py check
python manage.py runserver
```

The default local database is SQLite. Set the database and allowed-host environment variables in `.env` when using another environment.

## Frontend setup

Run from `dwellora/frontend/`:

```bash
npm install
cp .env.example .env
npm run build
npm run dev
```

Set `VITE_API_BASE_URL` to the Django API origin including the `/api/` prefix. The default is `http://127.0.0.1:8000/api/`.

## Current active API surface

- `/health/` — process health.
- `/api/auth/token/` and `/api/auth/token/refresh/` — JWT sign-in and refresh.
- `/api/accounts/profile/` — account registration.
- `/api/accounts/profile/view_details/` — authenticated user's own profile.
- `/api/accounts/profile/update/` and `/api/accounts/profile/delete/` — authenticated user's own profile.
- `/api/property/property/list/` and `/api/property/property/<id>/detail/` — public property discovery.
- Property create/update/delete — staff-only until a safe owner/lister relationship is implemented.
- `/api/services/` — public provider directory; provider profile creation is authenticated and updates/deletion are owner-scoped.
- Booking management — staff-only until customer ownership is represented.

The React application currently supports account creation, sign-in, refresh-token handling, sign-out and access to the enabled workspace resources.

## Feedback and review work

The branch contains tested models and views for viewing/tenancy interactions, verified-experience reviews, property questions/comments, staff moderation and content reports. Their URL definitions are kept separately in `property/feedback_urls.py` and are not mounted in the active API URLConf yet.

**Do not expose these endpoints or run migrations against production until the deployed database has been inspected, backed up and a data-preserving migration plan approved.** The existing custom user model and application model history require review before the initial migration set is created.

## Tests

Run the CI test modules from `dwellora/`:

```bash
python manage.py test accounts.tests property.tests booking.tests services.tests property.feedback_tests property.interaction_tests property.report_tests --verbosity 2
```

CI also runs `python manage.py check`, Python compilation and the React/TypeScript production build.

## Safety notes

- Never commit `.env`, database files, virtual environments, or generated build output.
- Do not treat a profile identity check, REAC licence lookup, property visit or user review as proof of property title or structural safety.
- Do not create migrations against a live database before inspection and backup.

## Ownership and listing architecture (implemented, gated)

The stabilization branch now separates physical Property records from ownership claims, authorised listers and marketplace offers. The listing workflow includes staff verification/moderation, owner-scoped draft operations, listing freshness confirmations, availability pause and cost estimate fields.

Routes are defined in `property/listing_urls.py` but are not mounted in the active URLConf until the deployed database has been inspected and a data-preserving migration plan is reviewed. Read `docs/OWNERSHIP_AND_LISTING_ARCHITECTURE.md` for the full model and rollout plan.

Run the focused architecture tests with:

```bash
python manage.py test property.listing_tests --verbosity 2
```

### Structured listing cost entries

Draft listing charges are represented by ListingCharge records. They carry a category, nullable amount, currency, payer, frequency, mandatory/unknown state, description and source note. A cost with unknown payer/amount/mandatory status is not silently treated as zero in the upfront estimate. Charge management endpoints are part of the gated listing route definitions and are not live until migration review.
