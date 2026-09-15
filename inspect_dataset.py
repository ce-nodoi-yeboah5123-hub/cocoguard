import pandas as pd
import os

# CHANGE THIS to where you extracted the Kaggle dataset
dataset_path = r"C:\Users\realr\Downloads\archive"

train_path = os.path.join(dataset_path, "Train.csv")
test_path = os.path.join(dataset_path, "Test.csv")

print("=" * 60)
print("COCOAGUARD DATASET INSPECTION")
print("=" * 60)

# Check that the files exist
print("\nTrain.csv exists:", os.path.exists(train_path))
print("Test.csv exists:", os.path.exists(test_path))

# Load CSV files
train = pd.read_csv(train_path)
test = pd.read_csv(test_path)

print("\nTRAIN DATA")
print("Shape:", train.shape)

print("\nColumns:")
print(train.columns.tolist())

print("\nFirst 10 rows:")
print(train.head(10).to_string())

print("\n" + "=" * 60)

print("TEST DATA")
print("Shape:", test.shape)

print("\nColumns:")
print(test.columns.tolist())

print("\nFirst 10 rows:")
print(test.head(10).to_string())

print("\n" + "=" * 60)
print("CLASS DISTRIBUTION")
print("=" * 60)

print(train["class"].value_counts())

print("\nClass IDs:")
print(
    train[["class", "class_id"]]
    .drop_duplicates()
    .sort_values("class_id")
)

print("\nNumber of unique training images:")
print(train["Image_ID"].nunique())

print("\nNumber of annotations:")
print(len(train))

print("\nAverage annotations per image:")
print(len(train) / train["Image_ID"].nunique())

print("\n" + "=" * 60)
print("CLASS / CLASS_ID COMBINATIONS")
print("=" * 60)

print(
    train.groupby(["class", "class_id"])
    .size()
    .reset_index(name="count")
    .to_string(index=False)
)