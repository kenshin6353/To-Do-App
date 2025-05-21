from flask import Flask, jsonify
from utils.db import engine, Base
import services.notification_service.models  # register table

from .worker import due_soon_notify, overdue_notify

app = Flask(__name__)

# ensure our table exists
Base.metadata.create_all(bind=engine)

@app.route("/health")
def health():
    return jsonify({"status": "ok"}), 200

@app.route("/notify/due-soon", methods=["POST"])
def trigger_due_soon():
    due_soon_notify.delay()
    return jsonify({"msg": "due-soon job queued"}), 202

@app.route("/notify/overdue", methods=["POST"])
def trigger_overdue():
    overdue_notify.delay()
    return jsonify({"msg": "overdue job queued"}), 202

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5003, debug=True)
