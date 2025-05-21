# api.py
from flask import Flask, request, jsonify
from flask_jwt_extended import (
    JWTManager, create_access_token,
    jwt_required, get_jwt, get_jwt_identity
)
from sqlalchemy.exc import IntegrityError
from utils.config import JWT_SECRET, JWT_ACCESS_EXPIRES
from utils.db import SessionLocal, engine, Base
from .models import User
from services.task_service.models import Task
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS

BLACKLIST = set()

# create tables if they don’t exist
Base.metadata.create_all(bind=engine)

app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = JWT_SECRET
app.config["JWT_ACCESS_TOKEN_EXPIRES"]  = JWT_ACCESS_EXPIRES
app.config["JWT_BLACKLIST_ENABLED"]     = True
app.config["JWT_BLACKLIST_TOKEN_CHECKS"] = ["access"]
jwt = JWTManager(app)
CORS(app, origins=["http://localhost:5173"], supports_credentials=True)

@app.route("/auth/register", methods=["POST"])
def register():
    data = request.get_json() or {}
    for f in ("username","email","password"):
        if f not in data:
            return jsonify({"msg": f"'{f}' is required"}), 400

    db = SessionLocal()
    try:
        hashed = generate_password_hash(data["password"])
        user = User(
          username=data["username"],
          email=data["email"],
          password_hash=hashed
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return jsonify({"id":user.id,"username":user.username}), 201

    except IntegrityError:
        db.rollback()
        return jsonify({"msg":"Username or email already exists"}), 409

    finally:
        db.close()

@app.route("/auth/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    for f in ("username","password"):
        if f not in data:
            return jsonify({"msg": f"'{f}' is required"}), 400

    db = SessionLocal()
    user = db.query(User).filter_by(username=data["username"]).first()
    db.close()
    if not user or not check_password_hash(user.password_hash, data["password"]):
        return jsonify({"msg":"Bad credentials"}), 401

    token = create_access_token(identity=str(user.id))
    return jsonify({"access_token": token}), 200

@app.route("/users/me", methods=["GET"])
@jwt_required()
def user_profile():
    """
    Returns the current user’s profile.
    Protected: must send Authorization: Bearer <token>
    """
    # 1) get the user id out of the JWT
    user_id = get_jwt_identity()

    # 2) load the user from the database
    db = SessionLocal()
    user = db.query(User).get(user_id)
    db.close()

    if not user:
        return jsonify({"msg": "User not found"}), 404

    # 3) return whatever fields you want exposed
    return jsonify({
        "id":         user.id,
        "username":   user.username,
        "email":      user.email,
        "created_at": user.created_at.isoformat()
    }), 200

@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload) -> bool:
    """
    This function is called on every protected request.
    Return True if the token’s jti is in our blacklist.
    """
    return jwt_payload["jti"] in BLACKLIST

@app.route("/auth/logout", methods=["POST"])
@jwt_required()
def logout():
    jti = get_jwt()["jti"]            # grab the unique token identifier
    BLACKLIST.add(jti)                # revoke it
    return jsonify({"msg": "Successfully logged out"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
