def calculate_risk(detections):
    """
    Calculate CocoaGuard risk from YOLO detections.

    This is the MVP rule-based risk engine.
    """

    if not detections:
        return {
            "risk_score": 0,
            "risk_level": "Low",
            "recommended_action":
                "No disease was detected. Continue routine monitoring."
        }

    # Find highest-confidence detection for each disease
    cssvd_confidence = 0
    anthracnose_confidence = 0
    healthy_confidence = 0

    for detection in detections:

        disease = detection["disease"].lower()
        confidence = detection["confidence"]

        if disease == "cssvd":
            cssvd_confidence = max(
                cssvd_confidence,
                confidence
            )

        elif disease == "anthracnose":
            anthracnose_confidence = max(
                anthracnose_confidence,
                confidence
            )

        elif disease == "healthy":
            healthy_confidence = max(
                healthy_confidence,
                confidence
            )

    # CSSVD takes highest priority
    if cssvd_confidence > 0:

        score = 70 + (cssvd_confidence * 30)

        return {
            "risk_score": round(min(score, 100), 2),
            "risk_level": "High"
                if score < 90 else "Critical",
            "recommended_action":
                "Possible CSSVD detected. Isolate the affected area "
                "and request inspection by an agricultural extension officer."
        }

    # Anthracnose
    if anthracnose_confidence > 0:

        score = 45 + (anthracnose_confidence * 35)

        return {
            "risk_score": round(min(score, 100), 2),
            "risk_level": "Medium"
                if score < 65 else "High",
            "recommended_action":
                "Possible anthracnose detected. Inspect affected plants, "
                "remove severely infected material where appropriate, "
                "and seek agricultural guidance."
        }

    # Only healthy detections
    if healthy_confidence > 0:

        score = max(
            0,
            20 - (healthy_confidence * 20)
        )

        return {
            "risk_score": round(score, 2),
            "risk_level": "Low",
            "recommended_action":
                "The cocoa appears healthy. Continue routine monitoring."
        }

    return {
        "risk_score": 0,
        "risk_level": "Low",
        "recommended_action":
            "Continue monitoring the cocoa plants."
    }