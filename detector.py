from ultralytics import YOLO
import os


MODEL_PATH = os.path.join(
    os.path.dirname(__file__),
    "trained_models",
    "best.pt"
)

# Load once when Flask starts
model = YOLO(MODEL_PATH)


def detect_cocoa_disease(image_path):
    """
    Run CocoaGuard YOLO model on an image.

    Returns a list of detections.
    """

    results = model.predict(
        source=image_path,
        conf=0.25,
        verbose=False
    )

    detections = []

    for result in results:

        for box in result.boxes:

            class_id = int(box.cls[0])
            confidence = float(box.conf[0])

            xmin, ymin, xmax, ymax = (
                box.xyxy[0].cpu().tolist()
            )

            class_name = model.names[class_id]

            detections.append({
                "class_id": class_id,
                "disease": class_name,
                "confidence": confidence,
                "xmin": xmin,
                "ymin": ymin,
                "xmax": xmax,
                "ymax": ymax
            })

    return detections