import pandas as pd
import os

dataset_path = r"C:\Users\realr\Downloads\archive"

train_path = os.path.join(dataset_path, "Train.csv")

df = pd.read_csv(train_path)

# --------------------------------------------------
# CocoaGuard class mapping
# --------------------------------------------------

class_mapping = {
    "anthracnose": 0,
    "cssvd": 1,
    "healthy": 2
}

# Preserve original class_id for comparison
df["original_class_id"] = df["class_id"]

# Generate correct class ID from class name
df["class_id"] = df["class"].map(class_mapping)

print("=" * 60)
print("COCOAGUARD CLEAN ANNOTATIONS")
print("=" * 60)

print("\nClass mapping:")
for name, class_id in class_mapping.items():
    print(f"{class_id}: {name}")

print("\nClean distribution:")
print(df.groupby(["class", "class_id"]).size())

# Count rows where supplied class ID disagreed with ours
differences = df[
    df["original_class_id"] != df["class_id"]
]

print("\nRows with inconsistent original IDs:")
print(len(differences))

# Save cleaned metadata
output_path = os.path.join(dataset_path, "Train_clean.csv")

df.to_csv(output_path, index=False)

print("\nSaved clean annotations to:")
print(output_path)