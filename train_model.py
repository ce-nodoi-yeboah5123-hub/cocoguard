from ultralytics import YOLO

# Load a small pretrained YOLO model
model = YOLO("yolo11n.pt")

model.train(
    data="cocoguard.yaml",
    epochs=5,
    imgsz=640,
    batch=8,
    workers=2,
    project="runs/cocoguard",
    name="test_run"
)