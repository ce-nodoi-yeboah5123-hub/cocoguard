from ultralytics import YOLO

# Load our trained CocoaGuard model
model = YOLO(
    r"runs\detect\runs\cocoguard\test_run\weights\best.pt"
)

# Folder containing images the model did NOT train on
test_images = (
    r"C:\Users\realr\Downloads\archive"
    r"\cocoguard_yolo\images\test"
)

# Run predictions
results = model.predict(
    source=test_images,
    conf=0.25,
    save=True
)

print("CocoaGuard predictions complete!")