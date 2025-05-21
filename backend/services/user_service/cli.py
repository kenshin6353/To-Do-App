# services/user_service/cli.py

import os
import json
import click
import getpass
import requests

# ─── Configuration ─────────────────────────────────────────────────────────────

# Base URL for your user-service API
API_BASE = os.getenv("USER_SERVICE_URL", "http://localhost:5001")

# Where to stash the JWT locally
TOKEN_PATH = "tmp/user_token.json"


def save_token(token: str):
    with open(TOKEN_PATH, "w") as f:
        f.write(token)


def load_token() -> str | None:
    if not os.path.exists(TOKEN_PATH):
        return None
    return open(TOKEN_PATH).read().strip()


def clear_token():
    try:
        os.remove(TOKEN_PATH)
    except FileNotFoundError:
        pass


def auth_header():
    token = load_token()
    if not token:
        click.echo("❌  You are not logged in. Run `login` first.", err=True)
        raise click.Abort()
    return {"Authorization": f"Bearer {token}"}


# ─── CLI Commands ──────────────────────────────────────────────────────────────

@click.group()
def cli():
    """To-Do User Service CLI"""
    pass

@cli.command()
def register():
    """Register a new user."""
    username = click.prompt("Username")
    email    = click.prompt("Email")
    password = getpass.getpass("Password: ")

    payload = {"username": username, "email": email, "password": password}
    r = requests.post(f"{API_BASE}/auth/register", json=payload)
    if r.status_code == 201:
        data = r.json()
        click.secho(f"✅  Registered {data['username']} (id={data['id']})", fg="green")
    else:
        msg = r.json().get("msg", r.text)
        click.secho(f"❌  {msg}", fg="red")

@cli.command()
def login():
    """Log in and save token locally."""
    username = click.prompt("Username")
    password = getpass.getpass("Password: ")

    r = requests.post(f"{API_BASE}/auth/login",
                      json={"username": username, "password": password})
    if r.status_code == 200:
        token = r.json()["access_token"]
        save_token(token)
        click.secho("🔐  Login successful, token saved.", fg="green")
    else:
        msg = r.json().get("msg", r.text)
        click.secho(f"❌  {msg}", fg="red")

@cli.command()
def logout():
    """Invalidate the current token."""
    headers = auth_header()
    r = requests.post(f"{API_BASE}/auth/logout", headers=headers)
    if r.status_code == 200:
        clear_token()
        click.secho("🔓  Logged out successfully.", fg="green")
    else:
        msg = r.json().get("msg", r.text)
        click.secho(f"❌  {msg}", fg="red")

@cli.command("profile")
def user_profile():
    """Fetch and display your user profile."""
    headers = auth_header()
    r = requests.get(f"{API_BASE}/users/me", headers=headers)
    if r.status_code == 200:
        data = r.json()
        click.secho("🧑  Your profile:", fg="cyan")
        for k in ("id", "username", "email", "created_at"):
            click.echo(f"  {k}: {data.get(k)}")
    else:
        msg = r.json().get("msg", r.text)
        click.secho(f"❌  {msg}", fg="red")


if __name__ == "__main__":
    cli()
