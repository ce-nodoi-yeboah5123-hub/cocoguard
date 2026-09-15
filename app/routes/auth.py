from flask import Blueprint, jsonify, request
from sqlalchemy import text
from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from app import db


auth_bp = Blueprint(
    "auth",
    __name__
)


@auth_bp.route("/")
def home():

    return jsonify({
        "app": "CocoaGuard",
        "status": "running"
    })


@auth_bp.route("/test-db")
def test_db():

    try:

        result = db.session.execute(
            text(
                "SELECT DB_NAME() AS database_name"
            )
        ).fetchone()

        return jsonify({
            "success": True,
            "database": result.database_name
        })

    except Exception as e:

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@auth_bp.route(
    "/api/register",
    methods=["POST"]
)
def register():

    try:

        data = request.get_json()

        if not data:

            return jsonify({
                "success": False,
                "message": "No data provided"
            }), 400

        full_name = data.get("full_name")
        email = data.get("email")
        phone = data.get("phone")
        password = data.get("password")
        role = data.get(
            "role",
            "Farmer"
        )

        if not full_name or not password:

            return jsonify({
                "success": False,
                "message":
                    "Full name and password are required"
            }), 400

        if role not in [
            "Farmer",
            "Officer",
            "Admin"
        ]:

            return jsonify({
                "success": False,
                "message": "Invalid role"
            }), 400

        if email:

            existing = db.session.execute(
                text("""
                    SELECT UserID
                    FROM dbo.Users
                    WHERE Email = :email
                """),
                {
                    "email": email
                }
            ).fetchone()

            if existing:

                return jsonify({
                    "success": False,
                    "message":
                        "Email already registered"
                }), 409

        password_hash = generate_password_hash(
            password
        )

        db.session.execute(
            text("""
                INSERT INTO dbo.Users
                (
                    FullName,
                    Email,
                    PhoneNumber,
                    PasswordHash,
                    Role
                )
                VALUES
                (
                    :full_name,
                    :email,
                    :phone,
                    :password_hash,
                    :role
                )
            """),
            {
                "full_name": full_name,
                "email": email,
                "phone": phone,
                "password_hash": password_hash,
                "role": role
            }
        )

        db.session.commit()

        return jsonify({
            "success": True,
            "message":
                "User registered successfully"
        }), 201

    except Exception as e:

        db.session.rollback()

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@auth_bp.route(
    "/api/login",
    methods=["POST"]
)
def login():

    try:

        data = request.get_json()

        if not data:

            return jsonify({
                "success": False,
                "message": "No data provided"
            }), 400

        email = data.get("email")
        password = data.get("password")

        if not email or not password:

            return jsonify({
                "success": False,
                "message":
                    "Email and password are required"
            }), 400

        user = db.session.execute(
            text("""
                SELECT
                    UserID,
                    FullName,
                    Email,
                    PasswordHash,
                    Role,
                    IsActive
                FROM dbo.Users
                WHERE Email = :email
            """),
            {
                "email": email
            }
        ).fetchone()

        if not user:

            return jsonify({
                "success": False,
                "message":
                    "Invalid email or password"
            }), 401

        if not user.IsActive:

            return jsonify({
                "success": False,
                "message":
                    "Account is inactive"
            }), 403

        if not check_password_hash(
            user.PasswordHash,
            password
        ):

            return jsonify({
                "success": False,
                "message":
                    "Invalid email or password"
            }), 401

        return jsonify({
            "success": True,
            "message": "Login successful",
            "user": {
                "user_id": user.UserID,
                "full_name": user.FullName,
                "email": user.Email,
                "role": user.Role
            }
        }), 200

    except Exception as e:

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500