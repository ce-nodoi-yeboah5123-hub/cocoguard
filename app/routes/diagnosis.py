import os
import uuid

from flask import (
    Blueprint,
    jsonify,
    request,
    current_app
)

from sqlalchemy import text
from werkzeug.utils import secure_filename

from app import db
from app.services.detector import detect_cocoa_disease
from app.services.risk_engine import calculate_risk


diagnosis_bp = Blueprint(
    "diagnosis",
    __name__
)


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


@diagnosis_bp.route(
    "/api/diagnose",
    methods=["POST"]
)
def diagnose():

    try:

        # --------------------------------------------------
        # Read form data
        # --------------------------------------------------

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


        # --------------------------------------------------
        # Validate farmer
        # --------------------------------------------------

        if not farmer_id:

            return jsonify({
                "success": False,
                "message": "Farmer ID is required"
            }), 400


        # --------------------------------------------------
        # Validate image
        # --------------------------------------------------

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


        # --------------------------------------------------
        # Check farmer exists
        # --------------------------------------------------

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


        # --------------------------------------------------
        # Verify farm belongs to farmer
        # --------------------------------------------------

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


        # --------------------------------------------------
        # Save image
        # --------------------------------------------------

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
            current_app.config[
                "UPLOAD_FOLDER"
            ],
            unique_filename
        )

        image.save(
            image_path
        )


        # --------------------------------------------------
        # Run YOLO
        # --------------------------------------------------

        detections = detect_cocoa_disease(
            image_path
        )


        # --------------------------------------------------
        # Calculate risk
        # --------------------------------------------------

        risk = calculate_risk(
            detections
        )


        # --------------------------------------------------
        # Create report
        # --------------------------------------------------

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


        report_id = report_result.scalar()


        # --------------------------------------------------
        # Save detections
        # --------------------------------------------------

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
                    "report_id":
                        report_id,

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


        # --------------------------------------------------
        # Save risk assessment
        # --------------------------------------------------

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


        # --------------------------------------------------
        # Commit
        # --------------------------------------------------

        db.session.commit()


        # --------------------------------------------------
        # Return result
        # --------------------------------------------------

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