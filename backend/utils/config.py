# backend/common/config.py
from datetime import timedelta
import os
from dotenv import load_dotenv

load_dotenv()  # reads .env in project root

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./db.sqlite3")
JWT_SECRET   = os.getenv("JWT_SECRET",   "super-secret")
SMTP_URL     = os.getenv("SMTP_URL",     "")
JWT_SECRET_KEY     = os.getenv("JWT_SECRET_KEY")
JWT_ACCESS_EXPIRES = timedelta(hours=1)

# Turn on blacklisting
JWT_BLACKLIST_ENABLED        = True
JWT_BLACKLIST_TOKEN_CHECKS   = ["access"]

BROKER_URL      = os.getenv("BROKER_URL", "redis://localhost:6379/0")
SMTP_SERVER   = os.getenv("SMTP_SERVER")
SMTP_PORT     = int(os.getenv("SMTP_PORT", 587))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
EMAIL_FROM    = os.getenv("EMAIL_FROM", "no-reply@example.com")