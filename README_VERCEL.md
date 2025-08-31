This project contains a Flask app inside the `src/` folder.

Minimal steps to deploy to Vercel:

1. Sign in to Vercel and create a new project from this repository.
2. Ensure the project root contains `vercel.json` and `requirements.txt` (done).
3. Set environment variables in the Vercel project settings (database URL, FLASK_CONFIG, secret keys).
   - Example: DATABASE_URL, SECRET_KEY
4. Deploy. Vercel will build using the Python runtime and route requests to `api/index.py`.

Notes and caveats:
- This project uses a relational DB (psycopg2). You must provide an external Postgres URL via an env var (e.g., DATABASE_URL) — Vercel doesn't provide managed Postgres.
- The app creates DB tables on startup; initial migrations are not included.
- Large native dependencies (psycopg2) may increase build time. Consider using `psycopg2-binary` if build fails.
