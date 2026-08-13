import os
from flask import Flask, jsonify, request, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

# --- Database config ---
# Pulls connection info from environment variables so the same image works
# locally (docker-compose) and later in AWS (RDS) without code changes.
DB_USER = os.environ.get("DB_USER", "postgres")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "postgres")
DB_HOST = os.environ.get("DB_HOST", "db")
DB_PORT = os.environ.get("DB_PORT", "5432")
DB_NAME = os.environ.get("DB_NAME", "appdb")

app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# --- Model ---
class Item(db.Model):
    __tablename__ = "items"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


# --- Frontend page ---
@app.route("/")
def index():
    return render_template("index.html")


# --- Health check (used later by the ALB target group) ---
@app.route("/health")
def health():
    return jsonify({"status": "ok"}), 200


# --- CRUD routes ---
@app.route("/items", methods=["GET"])
def get_items():
    items = Item.query.order_by(Item.id).all()
    return jsonify([item.to_dict() for item in items]), 200


@app.route("/items/<int:item_id>", methods=["GET"])
def get_item(item_id):
    item = Item.query.get_or_404(item_id)
    return jsonify(item.to_dict()), 200


@app.route("/items", methods=["POST"])
def create_item():
    data = request.get_json(force=True)
    if not data or "name" not in data:
        return jsonify({"error": "'name' is required"}), 400

    item = Item(name=data["name"], description=data.get("description", ""))
    db.session.add(item)
    db.session.commit()
    return jsonify(item.to_dict()), 201


@app.route("/items/<int:item_id>", methods=["PUT"])
def update_item(item_id):
    item = Item.query.get_or_404(item_id)
    data = request.get_json(force=True)

    item.name = data.get("name", item.name)
    item.description = data.get("description", item.description)
    db.session.commit()
    return jsonify(item.to_dict()), 200


@app.route("/items/<int:item_id>", methods=["DELETE"])
def delete_item(item_id):
    item = Item.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    return jsonify({"message": f"Item {item_id} deleted"}), 200


# --- Create tables on startup (fine for this project; a real prod app would use migrations) ---
with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
