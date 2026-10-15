# MAKITEST Deployment Guide: Google Cloud Run

This guide provides step-by-step instructions for deploying **MAKITEST** (Django ASGI + Channels + Daphne + OpenCV / MediaPipe) to **Google Cloud Run**.

Google Cloud Run is an ideal hosting platform for MAKITEST because it supports Docker containers, persistent WebSocket connections (required for real-time video streaming/proctoring), and provides a generous free tier.

---

## Prerequisites

1. A **Google Cloud Platform (GCP)** account ([Sign up for free](https://cloud.google.com/)).
2. [Google Cloud CLI (`gcloud`)](https://cloud.google.com/sdk/docs/install) installed on your machine (or use **Google Cloud Shell** directly in your browser).
3. Your forked GitHub repository (`New-MAKITEST-Web-App-Analytics-test`).

---

## Deployment Option A: Quick CLI Deployment (Recommended)

You can build and deploy the application directly from your terminal or Google Cloud Shell with a single command.

### Step 1: Login to Google Cloud and Select Project

Open your terminal or Cloud Shell and run:

```bash
gcloud auth login
gcloud config set project YOUR_GCP_PROJECT_ID
```

*(Replace `YOUR_GCP_PROJECT_ID` with your Google Cloud Project ID).*

### Step 2: Deploy to Cloud Run

From the root directory of this repository, run the following command:

```bash
gcloud run deploy makitest \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --timeout 3600 \
  --max-instances 1 \
  --session-affinity \
  --set-env-vars "DEBUG=False,SECRET_KEY=generate-a-secure-secret-key-here,ALLOWED_HOSTS=*"
```

**Key Configuration Parameters:**
- `--source .`: Automatically builds the `Dockerfile` in the root folder using Google Cloud Build.
- `--allow-unauthenticated`: Makes the web app publicly accessible.
- `--memory 2Gi` & `--cpu 2`: Recommended resources for handling MediaPipe and OpenCV image processing in Python without OOM errors.
- `--timeout 3600`: Increases request timeout to 1 hour (essential for uninterrupted exam proctoring over WebSockets).
- `--max-instances 1`: Ensures single-instance execution to maintain in-memory WebSocket tracking state consistently.
- `--session-affinity`: Routes continuous WebSocket and HTTP connections from the same user to the same container instance.

### Step 3: Set CSRF Trusted Origins and Database URL

Once deployment completes, Google Cloud Run will display your live app URL (e.g., `https://makitest-xyz123-uc.a.run.app`).

Update `CSRF_TRUSTED_ORIGINS` to allow Django form submissions and WebSockets from your Cloud Run domain:

```bash
gcloud run services update makitest \
  --set-env-vars "DEBUG=False,SECRET_KEY=your-secure-key,ALLOWED_HOSTS=*,CSRF_TRUSTED_ORIGINS=https://makitest-xyz123-uc.a.run.app"
```

> **Important (Data Persistence)**:
> By default, the app uses an ephemeral SQLite database inside the container. Whenever Cloud Run scales down to 0, data (users and exams) resets.
> For persistent storage across container restarts, provision a free PostgreSQL database (e.g., via Supabase or Neon) and pass `DATABASE_URL`:
> ```bash
> gcloud run services update makitest \
>   --update-env-vars "DATABASE_URL=postgres://user:password@ep-host.region.aws.neon.tech/neondb?sslmode=require"
> ```

---

## Deployment Option B: Automatic Continuous Deployment via Google Cloud Console

If you want Google Cloud Run to automatically redeploy every time you push changes to your GitHub main branch:

1. Open the [Google Cloud Run Console](https://console.cloud.google.com/run).
2. Click **Create Service**.
3. Select **Continuously deploy new revisions from a source repository**.
4. Click **Set up Cloud Build** and authorize your GitHub account.
5. Select your repository (`New-MAKITEST-Web-App-Analytics-test`) and `main` branch.
6. Under Build Configuration, select **Dockerfile** (location: `/Dockerfile`).
7. Set Service Name: `makitest`.
8. Under **Capacity**: Set Memory to `2 GiB` and CPU to `2`.
9. Under **Variables & Secrets**, add:
   - `DEBUG`: `False`
   - `SECRET_KEY`: `<your-random-secret-key>`
   - `ALLOWED_HOSTS`: `*`
   - `CSRF_TRUSTED_ORIGINS`: `https://<your-service-url>.run.app`
10. Click **Create**. Google Cloud will build and host your web application automatically!

---

## Environment Variables Reference

| Variable Name | Description | Default / Example |
|---|---|---|
| `DEBUG` | Enables or disables Django debug mode | `False` (in production) |
| `SECRET_KEY` | Django secret key | A long, random string |
| `ALLOWED_HOSTS` | Comma-separated allowed hostnames | `*` or `makitest.run.app` |
| `CSRF_TRUSTED_ORIGINS` | Comma-separated trusted origins for CSRF/WebSockets | `https://makitest.run.app` |
| `DATABASE_URL` | Database connection URL | Defaults to local SQLite if omitted |

---

## Verifying Deployment

1. Visit your Cloud Run URL (`https://makitest-xyz123-uc.a.run.app`).
2. Register/Login as a Teacher or Student.
3. Access the camera / live exam proctoring page and allow webcam access.
4. Verify that WebSockets connect properly and live video/gaze tracking processes smoothly.
