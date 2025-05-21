# services/task_service/cli.py

import os
import json
import click
import requests
from datetime import datetime

# by default, talk to localhost:5002
API_BASE   = os.getenv("TASK_SERVICE_URL", "http://localhost:5002")
TOKEN_PATH = "tmp/user_token.json"

def load_token():
    if not os.path.exists(TOKEN_PATH):
        return None
    return open(TOKEN_PATH).read().strip()

def auth_header():
    token = load_token()
    if not token:
        click.secho("❌ You must log in (via user CLI) first.", fg="red", err=True)
        raise click.Abort()
    return {"Authorization": f"Bearer {token}"}

@click.group()
def cli():
    """Task Service CLI"""
    pass

@cli.command("create")
@click.option("--title", prompt=True)
@click.option("--description", default="", prompt=False)
@click.option("--due", prompt="Due (YYYY-MM-DDTHH:MM:SS)")
def create(title, description, due):
    """Create a new task."""
    # validate due
    try:
        datetime.fromisoformat(due)
    except ValueError:
        click.secho("❌ Invalid due format. Use YYYY-MM-DDTHH:MM:SS", fg="red")
        return

    payload = {"title": title, "description": description, "due_date": due}
    r = requests.post(f"{API_BASE}/tasks",
                      json=payload,
                      headers=auth_header())
    if r.status_code == 201:
        t = r.json()
        click.secho(f"✅ Created task #{t['id']} – {t['title']}", fg="green")
    else:
        click.secho(f"❌ {r.json().get('msg', r.text)}", fg="red")

@cli.command("list")
def list_tasks():
    """List your tasks."""
    r = requests.get(f"{API_BASE}/tasks", headers=auth_header())
    if r.status_code == 200:
        tasks = r.json()
        for t in tasks:
            flag = "✓" if t["completed"] else " "
            click.echo(f"[{flag}] {t['id']}: {t['title']} (due {t['due_date']})")
    else:
        click.secho(f"❌ {r.json().get('msg', r.text)}", fg="red")

@cli.command("get")
@click.argument("task_id", type=int)
def get_one(task_id):
    """Get a single task by ID."""
    r = requests.get(f"{API_BASE}/tasks/{task_id}", headers=auth_header())
    if r.status_code == 200:
        click.echo(json.dumps(r.json(), indent=2))
    else:
        click.secho(f"❌ {r.json().get('msg', r.text)}", fg="red")

@cli.command("update")
@click.argument("task_id", type=int)
@click.option("--title",        default=None)
@click.option("--description",  default=None)
@click.option("--due",          default=None,
              help="YYYY-MM-DDTHH:MM:SS")
@click.option("--completed/--not-completed", default=None)
def update(task_id, title, description, due, completed):
    """Update fields on a task."""
    payload = {}
    if title is not None:       payload["title"] = title
    if description is not None: payload["description"] = description
    if due is not None:          payload["due_date"] = due
    if completed is not None:    payload["completed"] = completed

    if not payload:
        click.secho("❌ Nothing to update", fg="red")
        return

    r = requests.put(f"{API_BASE}/tasks/{task_id}",
                     json=payload,
                     headers=auth_header())
    if r.status_code == 200:
        click.secho("✅ Updated:", fg="green")
        click.echo(json.dumps(r.json(), indent=2))
    else:
        click.secho(f"❌ {r.json().get('msg', r.text)}", fg="red")

@cli.command("delete")
@click.argument("task_id", type=int)
def delete(task_id):
    """Delete a task."""
    r = requests.delete(f"{API_BASE}/tasks/{task_id}",
                        headers=auth_header())
    if r.status_code == 200:
        click.secho(f"✅ Task {task_id} deleted", fg="green")
    else:
        click.secho(f"❌ {r.json().get('msg', r.text)}", fg="red")

if __name__ == "__main__":
    cli()
