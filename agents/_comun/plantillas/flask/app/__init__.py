# ===============================================
# <App> — Flask factory
# Author: Haz
# ===============================================
from flask import Flask, render_template


def create_app():
    app = Flask(__name__)
    app.config.from_prefixed_env()          # FLASK_SECRET_KEY y demás vienen del ambiente, nunca del código

    @app.after_request
    def security_headers(response):
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        response.headers["Referrer-Policy"] = "same-origin"
        return response

    @app.get("/")
    def home():
        return render_template("home.html")

    return app
