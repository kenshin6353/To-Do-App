# services/task_service/api.py

from datetime import datetime
from flask import Flask, request, jsonify
from flask_jwt_extended import (
    JWTManager, jwt_required, get_jwt_identity
)
from sqlalchemy.exc import IntegrityError
from utils.config import JWT_SECRET      # from utils/config.py
from utils.db     import SessionLocal, engine, Base
from .models      import Task
from services.user_service.models import User
from flask_cors import CORS

# ensure tables exist
Base.metadata.create_all(bind=engine)

app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = JWT_SECRET
jwt = JWTManager(app)
CORS(app, origins=["http://localhost:5173"], supports_credentials=True)


@app.route("/tasks", methods=["POST"])
@jwt_required()
def create_task():
    data = request.get_json() or {}
    for f in ("title", "due_date"):
        if f not in data:
            return jsonify({"msg": f"'{f}' is required"}), 400

    try:
        due = datetime.fromisoformat(data["due_date"])
    except ValueError:
        return jsonify({"msg": "Invalid due_date. Use ISO format"}), 400

    user_id = get_jwt_identity()
    db = SessionLocal()
    task = Task(
        user_id=user_id,
        title=data["title"],
        description=data.get("description", ""),
        due_date=due
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    db.close()

    return (
        jsonify({
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "due_date": task.due_date.isoformat(),
            "completed": task.completed
        }),
        201
    )


@app.route("/tasks", methods=["GET"])
@jwt_required()
def list_tasks():
    user_id = get_jwt_identity()
    db = SessionLocal()
    tasks = db.query(Task).filter_by(user_id=user_id).all()
    db.close()
    return jsonify([
        {
            "id": t.id,
            "title": t.title,
            "description": t.description,
            "due_date": t.due_date.isoformat(),
            "completed": t.completed
        }
        for t in tasks
    ]), 200


@app.route("/tasks/<int:task_id>", methods=["GET"])
@jwt_required()
def get_task(task_id):
    user_id = get_jwt_identity()
    db = SessionLocal()
    task = db.query(Task).filter_by(id=task_id, user_id=user_id).first()
    db.close()
    if not task:
        return jsonify({"msg": "Not found"}), 404
    return jsonify({
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "due_date": task.due_date.isoformat(),
        "completed": task.completed
    }), 200


@app.route("/tasks/<int:task_id>", methods=["PUT", "PATCH"])
@jwt_required()
def update_task(task_id):
    data = request.get_json() or {}
    user_id = get_jwt_identity()
    db = SessionLocal()
    task = db.query(Task).filter_by(id=task_id, user_id=user_id).first()
    if not task:
        db.close()
        return jsonify({"msg": "Not found"}), 404

    # apply updates if present
    if "title" in data:
        task.title = data["title"]
    if "description" in data:
        task.description = data["description"]
    if "due_date" in data:
        try:
            task.due_date = datetime.fromisoformat(data["due_date"])
        except ValueError:
            db.close()
            return jsonify({"msg": "Invalid due_date"}), 400
    if "completed" in data:
        task.completed = bool(data["completed"])

    db.commit()
    db.refresh(task)
    db.close()
    return jsonify({
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "due_date": task.due_date.isoformat(),
        "completed": task.completed
    }), 200


@app.route("/tasks/<int:task_id>", methods=["DELETE"])
@jwt_required()
def delete_task(task_id):
    user_id = get_jwt_identity()
    db = SessionLocal()
    task = db.query(Task).filter_by(id=task_id, user_id=user_id).first()
    if not task:
        db.close()
        return jsonify({"msg": "Not found"}), 404

    db.delete(task)
    db.commit()
    db.close()
    return jsonify({"msg": "Deleted"}), 200


if __name__ == "__main__":
    # pick a port that doesn’t collide with user-service
    app.run(host="0.0.0.0", port=5002, debug=True)
