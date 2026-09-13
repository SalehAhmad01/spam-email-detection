# Deployment Guide for Render 🚀

This document details step-by-step instructions for deploying **SMS & Email Guard** to [Render](https://render.com/).

---

## ⚡ Option A: Quick Deployment with SQLite Database (Simplest)

If you don't want to create a PostgreSQL server, you can deploy using **SQLite** directly!

### Step 1: Create a Web Service on Render

1. Log into your **Render Dashboard**.
2. Click **New +** ➔ **Web Service**.
3. Connect your **GitHub / GitLab** repository.
4. Configure Web Service options:
   - **Name**: `sms-email-guard`
   - **Environment**: `Python 3`
   - **Branch**: `main`
   - **Build Command**:
     ```bash
     pip install -r requirements.txt && python manage.py collectstatic --noinput
     ```
   - **Start Command**:
     ```bash
     python manage.py migrate --noinput && gunicorn config.wsgi:application
     ```

### Step 2: Set Environment Variables

Under your Web Service's **Environment** tab, set:

| Key | Value |
|---|---|
| `DJANGO_SETTINGS_MODULE` | `config.settings.prod` |
| `SECRET_KEY` | *Generates a random key* |
| `DEBUG` | `False` |
| `ALLOWED_HOSTS` | `.onrender.com, localhost` |
| `CSRF_TRUSTED_ORIGINS` | `https://*.onrender.com` |
| `SECURE_SSL_REDIRECT` | `False` |

---

### 💾 Step 3 (Optional): Add Render Persistent Disk (For Permanent SQLite Storage)

To prevent SQLite data from resetting when Render restarts:

1. In Render Dashboard ➔ Go to your Web Service ➔ Click **Disks** tab (left sidebar).
2. Click **Add Disk**:
   - **Name**: `sqlite-data`
   - **Mount Path**: `/var/data`
   - **Size**: `1 GB` (or desired size)
3. Click **Save Changes**.
4. Go to **Environment** tab ➔ Add a new variable:
   - **Key**: `SQLITE_DB_PATH`
   - **Value**: `/var/data/db.sqlite3`
5. Click **Save Changes**. Render will automatically redeploy and save your SQLite database safely on the persistent disk!

---

## 🐘 Option B: Production Deployment with PostgreSQL Database

1. Click **New +** ➔ **PostgreSQL**.
2. Name it `sms-email-guard-db` and copy the **Internal Database URL**.
3. In your Web Service Environment settings, add:
   - `DATABASE_URL` = *Paste copied PostgreSQL URL*

---

## 🔑 Administrative User Creation

After your app deploys on Render:
1. Go to your Web Service dashboard ➔ Click **Shell**.
2. Run:
   ```bash
   python manage.py createsuperuser
   ```
3. Follow prompts to set admin credentials.
