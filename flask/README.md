## Flask Service (Cloud Run)

Python 3.11 Flask app exposing endpoints to create and maintain Bluesky mirrors of Substack newsletters. Designed for Google Cloud Run. Uses Firebase/Firestore for persistence and Google Cloud Tasks for async jobs.

### Features

-   `POST /createNewsletter` — Streams progress while:
    -   Resolving Substack admin and publication details
    -   Creating a Bluesky account on your PDS
    -   Updating the profile
    -   Importing recent posts (as embedded link posts)
    -   Persisting newsletter metadata to Firestore
    -   Scheduling graph enrichment via Cloud Tasks
-   `POST /addNewsletterUserGraph` — Adds recommended newsletters and users + newsletter users into Firestore.
-   `POST /buildNewsletter` — Adds new posts since last build and updates last build details.
-   `POST /newsletterBuildCheck` — Scans Firestore for due newsletters and enqueues Cloud Tasks for `/buildNewsletter`.

### Requirements

-   Python 3.11+
-   Google Cloud project with Firestore and Cloud Tasks enabled (for production)
-   AT Protocol PDS endpoint and admin credentials

### Local setup

```bash
cd flask
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Make sure env variables are already set

# Run locally
python app.py  # listens on PORT (default 8080)
```

Note on private key formatting: keep literal `\n` within the environment value (the code replaces `\\n` with real newlines).

### Endpoints

All endpoints are defined in `app.py` and implemented in `endpoints/`.

-   `GET /` — health check
-   `POST /createNewsletter` — body: `{ "url": "https://<subdomain>.substack.com/" }`
    -   Streams JSON lines with `type` and optional payload
-   `POST /addNewsletterUserGraph` — body: `{ "subdomain": "<subdomain>", "publication_id": "<id>" }`
-   `POST /buildNewsletter` — body: `{ "lastBuildDate": "<ISO>Z", "noOfPosts": <int>, "postFrequency": <float>, "subdomain": "<subdomain>" }`
-   `POST /newsletterBuildCheck` — body: `{}` (no params)

### Running tests

Some tests require env vars (`ADMIN_PASS`, `USER_LOGIN_PASS`) and network access.

```bash
cd flask
source .venv/bin/activate
python run_tests.py
```

### Docker and Cloud Run

Dockerfile is provided. The image runs via Gunicorn.

Build locally (optional):

```bash
cd flask
docker build -t gcr.io/<gcp-project-id>/skystack-flask:latest .
```

Deploy to Cloud Run:

```bash
gcloud builds submit --tag gcr.io/<gcp-project-id>/skystack-flask:latest flask
gcloud run deploy skystack-flask \
  --image gcr.io/<gcp-project-id>/skystack-flask:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars ADMIN_PASS=<...>,USER_LOGIN_PASS=<...>,GOOGLE_CLOUD_PROJECT=<project>,CLOUD_TASKS_LOCATION=us-central1,CLOUD_TASKS_QUEUE=default \
  --set-env-vars FIREBASE_TYPE=service_account,FIREBASE_PROJECT_ID=<...>,FIREBASE_PRIVATE_KEY_ID=<...>,FIREBASE_PRIVATE_KEY=<...>,FIREBASE_CLIENT_EMAIL=<...>,FIREBASE_CLIENT_ID=<...>,FIREBASE_AUTH_URI=https://accounts.google.com/o/oauth2/auth,FIREBASE_TOKEN_URI=https://oauth2.googleapis.com/token,FIREBASE_AUTH_PROVIDER_X509_CERT_URL=https://www.googleapis.com/oauth2/v1/certs,FIREBASE_CLIENT_X509_CERT_URL=<...>,FIREBASE_UNIVERSE_DOMAIN=googleapis.com
```

After deployment, set:

```bash
gcloud run services describe skystack-flask --region us-central1 --format='value(status.url)'
```

Use that URL as `CLOUD_RUN_ENDPOINT` (and consider storing it also as a Secret/Config for the frontend if needed).

### Example cURL (streaming)

```bash
curl -N -X POST "$CLOUD_RUN_ENDPOINT/createNewsletter" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://hasir.substack.com/"}'
```

### Architecture notes

-   `utils/admin.py` and `utils/atproto_user.py` wrap PDS admin and user actions via `atproto` SDK.
-   `utils/newsletter.py` and `utils/user.py` fetch Substack data; `utils/utils.py` contains helpers for JSON, RSS, image normalization, and frequency calculations.
-   `utils/firebase.py` abstracts Firestore CRUD for newsletters and scheduling metadata.
-   `utils/create_cloud_task.py` creates HTTP Cloud Tasks against this service’s endpoints.
