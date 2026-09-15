import os
import shutil
import random
import cv2
import pandas as pd

# --------------------------------------------------
# PATHS
# --------------------------------------------------

dataset_root = r"C:\Users\realr\Downloads\archive"

csv_path = os.path.join(dataset_root, "Train_clean.csv")

source_images = os.path.join(
    dataset_root,
    "dataset",
    "images",
    "train"
)

# YOLO dataset will be created here
output_root = os.path.join(
    dataset_root,
    "cocoguard_yolo"
)

# --------------------------------------------------
# SETTINGS
# --------------------------------------------------

random.seed(42)

train_ratio = 0.80
val_ratio = 0.10
test_ratio = 0.10

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

df = pd.read_csv(csv_path)

print("=" * 60)
print("COCOAGUARD YOLO DATASET PREPARATION")
print("=" * 60)

print("\nAnnotations:", len(df))
print("Unique images:", df["Image_ID"].nunique())

# --------------------------------------------------
# CREATE IMAGE SPLITS
# --------------------------------------------------

image_ids = df["Image_ID"].unique().tolist()

random.shuffle(image_ids)

total = len(image_ids)

train_end = int(total * train_ratio)
val_end = train_end + int(total * val_ratio)

train_images = image_ids[:train_end]
val_images = image_ids[train_end:val_end]
test_images = image_ids[val_end:]

splits = {
    "train": train_images,
    "val": val_images,
    "test": test_images
}

print("\nSplit sizes:")
for split, images in splits.items():
    print(f"{split}: {len(images)} images")

# --------------------------------------------------
# CREATE FOLDERS
# --------------------------------------------------

for split in splits:

    os.makedirs(
        os.path.join(output_root, "images", split),
        exist_ok=True
    )

    os.makedirs(
        os.path.join(output_root, "labels", split),
        exist_ok=True
    )

# --------------------------------------------------
# CONVERT BOUNDING BOXES
# --------------------------------------------------

def convert_to_yolo(xmin, ymin, xmax, ymax, width, height):

    x_center = ((xmin + xmax) / 2) / width
    y_center = ((ymin + ymax) / 2) / height

    box_width = (xmax - xmin) / width
    box_height = (ymax - ymin) / height

    return x_center, y_center, box_width, box_height


# --------------------------------------------------
# PROCESS EACH SPLIT
# --------------------------------------------------

for split_name, split_images in splits.items():

    print(f"\nProcessing {split_name}...")

    for index, image_id in enumerate(split_images):

        source_image_path = os.path.join(
            source_images,
            image_id
        )

        if not os.path.exists(source_image_path):
            print("Missing image:", source_image_path)
            continue

        image = cv2.imread(source_image_path)

        if image is None:
            print("Could not read:", source_image_path)
            continue

        height, width = image.shape[:2]

        # All boxes for this image
        annotations = df[df["Image_ID"] == image_id]

        yolo_lines = []

        for _, row in annotations.iterrows():

            class_id = int(row["class_id"])

            xmin = float(row["xmin"])
            ymin = float(row["ymin"])
            xmax = float(row["xmax"])
            ymax = float(row["ymax"])

            # Keep boxes within image boundaries
            xmin = max(0, min(xmin, width))
            xmax = max(0, min(xmax, width))
            ymin = max(0, min(ymin, height))
            ymax = max(0, min(ymax, height))

            if xmax <= xmin or ymax <= ymin:
                continue

            x_center, y_center, box_width, box_height = convert_to_yolo(
                xmin,
                ymin,
                xmax,
                ymax,
                width,
                height
            )

            line = (
                f"{class_id} "
                f"{x_center:.6f} "
                f"{y_center:.6f} "
                f"{box_width:.6f} "
                f"{box_height:.6f}"
            )

            yolo_lines.append(line)

        # --------------------------------------------------
        # COPY IMAGE
        # --------------------------------------------------

        destination_image = os.path.join(
            output_root,
            "images",
            split_name,
            image_id
        )

        shutil.copy2(
            source_image_path,
            destination_image
        )

        # --------------------------------------------------
        # WRITE YOLO LABEL FILE
        # --------------------------------------------------

        label_name = os.path.splitext(image_id)[0] + ".txt"

        label_path = os.path.join(
            output_root,
            "labels",
            split_name,
            label_name
        )

        with open(label_path, "w") as f:
            f.write("\n".join(yolo_lines))

        if (index + 1) % 500 == 0:
            print(f"Processed {index + 1}/{len(split_images)}")

print("\n" + "=" * 60)
print("DATASET PREPARATION COMPLETE")
print("=" * 60)

print("\nYOLO dataset created at:")
print(output_root)