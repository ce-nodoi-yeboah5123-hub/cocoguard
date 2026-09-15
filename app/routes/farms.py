from flask import Blueprint, jsonify, request
from sqlalchemy import text

from app import db


farms_bp = Blueprint(
    "farms",
    __name__
)


@farms_bp.route(
    "/api/farms",
    methods=["POST"]
)
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
        farm_size = data.get(
            "farm_size_hectares"
        )

        if not farmer_id or not farm_name:

            return jsonify({
                "success": False,
                "message":
                    "Farmer ID and farm name are required"
            }), 400

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