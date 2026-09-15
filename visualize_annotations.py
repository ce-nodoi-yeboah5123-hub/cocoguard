import pandas as pd
import cv2
import os
import random

dataset_path = r"C:\Users\realr\Downloads\archive"

csv_path = os.path.join(dataset_path, "Train_clean.csv")

df = pd.read_csv(csv_path)

# Pick a random image
image_id = random.choice(df["Image_ID"].unique())

image_annotations = df[df["Image_ID"] == image_id]

image_path = os.path.join(
    dataset_path,
    "dataset",
    "images",
    "train",
    image_id
)

print("Opening:")
print(image_path)

print("\nAnnotations:")
print(
    image_annotations[
        ["class", "xmin", "ymin", "xmax", "ymax"]
    ]
)

image = cv2.imread(image_path)

if image is None:
    raise FileNotFoundError(
        f"Could not load image: {image_path}"
    )

for _, row in image_annotations.iterrows():

    xmin = int(row["xmin"])
    ymin = int(row["ymin"])
    xmax = int(row["xmax"])
    ymax = int(row["ymax"])

    label = row["class"]

    cv2.rectangle(
        image,
        (xmin, ymin),
        (xmax, ymax),
        (0, 255, 0),
        2
    )

    cv2.putText(
        image,
        label,
        (xmin, max(ymin - 10, 20)),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 255, 0),
        2
    )

# Resize just for easier viewing
height, width = image.shape[:2]

max_width = 900

if width > max_width:
    scale = max_width / width

    image = cv2.resize(
        image,
        None,
        fx=scale,
        fy=scale
    )

cv2.imshow("CocoaGuard Annotation Check", image)

print("\nPress any key on the image window to close.")

cv2.waitKey(0)
cv2.destroyAllWindows()