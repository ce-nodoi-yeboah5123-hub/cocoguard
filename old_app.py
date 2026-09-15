from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

from config import Config
from detector import detect_cocoa_disease
from risk_engine import calculate_risk

import os
import uuid


# =========================================================
# FLASK APP
# =========================================================

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)


# =========================================================
# UPLOAD CONFIGURATION
# =========================================================

UPLOAD_FOLDER = os.path.join(
    os.path.dirname(__file__),
    "uploads"
)

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Maximum uploaded image size: 10 MB
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024

ALLOWED_EXTENSIONS = {
    "jpg",
    "jpeg",
    "png"
}


def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in ALLOWED_EXTENSIONS
    )


# =========================================================
# HOME
# =========================================================

@app.route("/")
def home():
    return jsonify({
        "app": "CocoaGuard",
        "status": "running"
    })


# =========================================================
# DATABASE TEST
# =========================================================

@app.route("/test-db")
def test_db():
    try:

        result = db.session.execute(
            text("SELECT DB_NAME() AS database_name")
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


# =========================================================
# USER REGISTRATION
# =========================================================

@app.route("/api/register", methods=["POST"])
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
        role = data.get("role", "Farmer")

        if not full_name or not password:
            return jsonify({
                "success": False,
                "message": "Full name and password are required"
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

        # -------------------------------------------------
        # Check duplicate email
        # -------------------------------------------------

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
                    "message": "Email already registered"
                }), 409

        # -------------------------------------------------
        # Hash password
        # -------------------------------------------------

        password_hash = generate_password_hash(
            password
        )

        # -------------------------------------------------
        # Insert user
        # -------------------------------------------------

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
            "message": "User registered successfully"
        }), 201

    except Exception as e:

        db.session.rollback()

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# =========================================================
# LOGIN
# =========================================================

@app.route("/api/login", methods=["POST"])
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
                "message": "Email and password are required"
            }), 400

        # -------------------------------------------------
        # Find user
        # -------------------------------------------------

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
                "message": "Invalid email or password"
            }), 401

        # -------------------------------------------------
        # Account status
        # -------------------------------------------------

        if not user.IsActive:

            return jsonify({
                "success": False,
                "message": "Account is inactive"
            }), 403

        # -------------------------------------------------
        # Verify password
        # -------------------------------------------------

        if not check_password_hash(
            user.PasswordHash,
            password
        ):

            return jsonify({
                "success": False,
                "message": "Invalid email or password"
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


# =========================================================
# FARM REGISTRATION
# =========================================================

@app.route("/api/farms", methods=["POST"])
def register_farm():

    try:

        data = request.get_json()

        if not data:

            return jsonify({
                "success": False,
                "message": "No data provided"
            }), 400

        farmer_id = data.get("farmer_id")
        farm_name = data.get("farm_name")
        region = data.get("region")
        district = data.get("district")
        community = data.get("community")
        latitude = data.get("latitude")
        longitude = data.get("longitude")
        farm_size = data.get("farm_size_hectares")

        if not farmer_id or not farm_name:

            return jsonify({
                "success": False,
                "message":
                    "Farmer ID and farm name are required"
            }), 400

        # -------------------------------------------------
        # Check farmer
        # -------------------------------------------------

        farmer = db.session.execute(
            text("""
                SELECT
                    UserID,
                    Role
                FROM dbo.Users
                WHERE UserID = :farmer_id
            """),
            {
                "farmer_id": farmer_id
            }
        ).fetchone()

        if not farmer:

            return jsonify({
                "success": False,
                "message": "Farmer not found"
            }), 404

        if farmer.Role != "Farmer":

            return jsonify({
                "success": False,
                "message":
                    "The selected user is not a farmer"
            }), 400

        # -------------------------------------------------
        # Insert farm
        # -------------------------------------------------

        result = db.session.execute(
            text("""
                INSERT INTO dbo.Farms
                (
                    FarmerID,
                    FarmName,
                    Region,
                    District,
                    Community,
                    Latitude,
                    Longitude,
                    FarmSizeHectares
                )

                OUTPUT INSERTED.FarmID

                VALUES
                (
                    :farmer_id,
                    :farm_name,
                    :region,
                    :district,
                    :community,
                    :latitude,
                    :longitude,
                    :farm_size
                )
            """),
            {
                "farmer_id": farmer_id,
                "farm_name": farm_name,
                "region": region,
                "district": district,
                "community": community,
                "latitude": latitude,
                "longitude": longitude,
                "farm_size": farm_size
            }
        )

        farm_id = result.scalar()

        db.session.commit()

        return jsonify({
            "success": True,
            "message":
                "Farm registered successfully",
            "farm": {
                "farm_id": farm_id,
                "farmer_id": farmer_id,
                "farm_name": farm_name,
                "region": region,
                "district": district,
                "community": community
            }
        }), 201

    except Exception as e:

        db.session.rollback()

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# =========================================================
# COCOA DIAGNOSIS
# =========================================================

@app.route("/api/diagnose", methods=["POST"])
def diagnose():

    image_path = None

    try:

        # -------------------------------------------------
        # Form data
        # -------------------------------------------------

        farmer_id = request.form.get(
            "farmer_id"
        )

        farm_id = request.form.get(
            "farm_id"
        )

        symptoms = request.form.get(
            "symptoms"
        )

        latitude = request.form.get(
            "latitude"
        )

        longitude = request.form.get(
            "longitude"
        )

        # -------------------------------------------------
        # Validate farmer ID
        # -------------------------------------------------

        if not farmer_id:

            return jsonify({
                "success": False,
                "message": "Farmer ID is required"
            }), 400

        # -------------------------------------------------
        # Validate image
        # -------------------------------------------------

        if "image" not in request.files:

            return jsonify({
                "success": False,
                "message": "Cocoa image is required"
            }), 400

        image = request.files["image"]

        if image.filename == "":

            return jsonify({
                "success": False,
                "message": "No image selected"
            }), 400

        if not allowed_file(
            image.filename
        ):

            return jsonify({
                "success": False,
                "message":
                    "Only JPG, JPEG and PNG images are allowed"
            }), 400

        # -------------------------------------------------
        # Verify farmer
        # -------------------------------------------------

        farmer = db.session.execute(
            text("""
                SELECT UserID
                FROM dbo.Users
                WHERE UserID = :farmer_id
                  AND Role = 'Farmer'
                  AND IsActive = 1
            """),
            {
                "farmer_id": farmer_id
            }
        ).fetchone()

        if not farmer:

            return jsonify({
                "success": False,
                "message": "Farmer not found"
            }), 404

        # -------------------------------------------------
        # Verify farm
        # -------------------------------------------------

        if farm_id:

            farm = db.session.execute(
                text("""
                    SELECT FarmID
                    FROM dbo.Farms
                    WHERE FarmID = :farm_id
                      AND FarmerID = :farmer_id
                """),
                {
                    "farm_id": farm_id,
                    "farmer_id": farmer_id
                }
            ).fetchone()

            if not farm:

                return jsonify({
                    "success": False,
                    "message":
                        "Farm does not belong to this farmer"
                }), 400

        # -------------------------------------------------
        # Save uploaded image
        # -------------------------------------------------

        original_name = secure_filename(
            image.filename
        )

        extension = original_name.rsplit(
            ".",
            1
        )[1].lower()

        unique_filename = (
            f"{uuid.uuid4().hex}.{extension}"
        )

        image_path = os.path.join(
            app.config["UPLOAD_FOLDER"],
            unique_filename
        )

        image.save(
            image_path
        )

        # =================================================
        # YOLO DIAGNOSIS
        # =================================================

        detections = detect_cocoa_disease(
            image_path
        )

        # =================================================
        # RISK CALCULATION
        # =================================================

        risk = calculate_risk(
            detections
        )

        # =================================================
        # CREATE REPORT FIRST
        # =================================================

        report_result = db.session.execute(
            text("""
                INSERT INTO dbo.Reports
                (
                    FarmerID,
                    FarmID,
                    ImagePath,
                    Symptoms,
                    Latitude,
                    Longitude,
                    Status
                )

                OUTPUT INSERTED.ReportID

                VALUES
                (
                    :farmer_id,
                    :farm_id,
                    :image_path,
                    :symptoms,
                    :latitude,
                    :longitude,
                    'Analysed'
                )
            """),
            {
                "farmer_id": farmer_id,
                "farm_id": farm_id,
                "image_path": unique_filename,
                "symptoms": symptoms,
                "latitude": latitude,
                "longitude": longitude
            }
        )

        # IMPORTANT:
        # Report ID exists from this point onwards.

        report_id = report_result.scalar()

        # =================================================
        # SAVE YOLO DETECTIONS
        # =================================================

        for detection in detections:

            db.session.execute(
                text("""
                    INSERT INTO dbo.Diagnoses
                    (
                        ReportID,
                        Disease,
                        Confidence,
                        XMin,
                        YMin,
                        XMax,
                        YMax,
                        ModelVersion
                    )
                    VALUES
                    (
                        :report_id,
                        :disease,
                        :confidence,
                        :xmin,
                        :ymin,
                        :xmax,
                        :ymax,
                        :model_version
                    )
                """),
                {
                    "report_id": report_id,
                    "disease":
                        detection["disease"],
                    "confidence":
                        detection["confidence"],
                    "xmin":
                        detection["xmin"],
                    "ymin":
                        detection["ymin"],
                    "xmax":
                        detection["xmax"],
                    "ymax":
                        detection["ymax"],
                    "model_version":
                        "cocoguard-yolo11n-v1"
                }
            )

        # =================================================
        # SAVE RISK ASSESSMENT
        # =================================================

        db.session.execute(
            text("""
                INSERT INTO dbo.RiskAssessments
                (
                    ReportID,
                    RiskScore,
                    RiskLevel,
                    RecommendedAction
                )
                VALUES
                (
                    :report_id,
                    :risk_score,
                    :risk_level,
                    :recommended_action
                )
            """),
            {
                "report_id":
                    report_id,

                "risk_score":
                    risk["risk_score"],

                "risk_level":
                    risk["risk_level"],

                "recommended_action":
                    risk["recommended_action"]
            }
        )

        # =================================================
        # COMMIT EVERYTHING
        # =================================================

        db.session.commit()

        # =================================================
        # RESPONSE
        # =================================================

        return jsonify({
            "success": True,
            "message":
                "Cocoa image analysed successfully",

            "report_id":
                report_id,

            "detections_count":
                len(detections),

            "detections":
                detections,

            "risk_assessment":
                risk

        }), 201

    except Exception as e:

        db.session.rollback()

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# =========================================================
# START APPLICATION
# =========================================================

if __name__ == "__main__":
    app.run(
        debug=True
    )