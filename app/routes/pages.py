from flask import Blueprint, render_template

pages_bp = Blueprint(
    "pages",
    __name__
)


@pages_bp.route("/login")
def login_page():
    return render_template("login.html")


@pages_bp.route("/register")
def register_page():
    return render_template("register.html")


@pages_bp.route("/dashboard")
def dashboard_page():
    return render_template("dashboard.html")


@pages_bp.route("/diagnose")
def diagnose_page():
    return render_template("diagnose.html")