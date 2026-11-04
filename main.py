from flask import Flask, redirect, url_for
from src.routes import bp

app = Flask(__name__)
app.config["SECRET_KEY"] = "your-secret-key-change-in-production"
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

app.register_blueprint(bp)


@app.route("/")
def index():
    return redirect(url_for('api.index'))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
