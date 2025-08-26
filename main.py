import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# ==========================
# Helper Functions
# ==========================

def load_dataset(path: str, sep: str = ",") -> pd.DataFrame:
    """Load a dataset safely, raising a clear error if file is missing."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"File not found: {path}")
    return pd.read_csv(path, sep=sep)

def plot_count(df: pd.DataFrame, column: str, palette: str, title: str):
    """Plot a countplot for a specific column if it exists."""
    if column in df.columns:
        plt.figure(figsize=(8, 5))
        sns.countplot(x=column, data=df, palette=palette)
        plt.title(title)
        plt.xlabel(column.capitalize())
        plt.ylabel("Count")
        plt.show()
    else:
        print(f"[WARN] Column '{column}' not found. Skipping plot.")

def plot_hist(df: pd.DataFrame, column: str, title: str, color: str):
    """Plot histogram if the column exists and is numeric."""
    if column in df.columns:
        plt.figure(figsize=(8, 5))
        sns.histplot(df[column], bins=30, kde=True, color=color)
        plt.title(title)
        plt.xlabel(column)
        plt.ylabel("Frequency")
        plt.show()
    else:
        print(f"[WARN] Column '{column}' not found. Skipping histogram.")

# ==========================
# 1. Load both datasets
# ==========================

feedback_df = load_dataset("merged_student_feedback.csv")
opportunity_df = load_dataset("opportunity.tsv", sep="\t")
# i havent included this file in the github library because of the size limit, so here is the link for it, https://data.mendeley.com/datasets/b2yhc95rnx/1

print("[OK] Merged Student Feedback Dataset Loaded")
print("Shape:", feedback_df.shape)
print(feedback_df.head(), "\n")

print("[OK] Opportunity Dataset Loaded")
print("Shape:", opportunity_df.shape)
print(opportunity_df.head(), "\n")

# ==========================
# 2. Check Missing Values
# ==========================
print("Missing values in Feedback Dataset:", feedback_df.isnull().sum().sum())
print("Missing values in Opportunity Dataset:", opportunity_df.isnull().sum().sum(), "\n")

# ==========================
# 3. Clean Data (drop duplicates if any)
# ==========================
feedback_clean = feedback_df.drop_duplicates()
opportunity_clean = opportunity_df.drop_duplicates()

# ==========================
# 4. Exploratory Data Analysis (EDA)
# ==========================

# ---- Feedback Dataset EDA ----
print("\n[INFO] Feedback Dataset Summary:")
print(feedback_clean.describe(include="all"))

# Countplots
plot_count(feedback_clean, "attendance", "Blues", "Distribution of Student Attendance")
plot_count(feedback_clean, "difficulty", "Oranges", "Distribution of Course Difficulty")

# Correlation heatmap (only numeric columns)
plt.figure(figsize=(12, 6))
corr_matrix = feedback_clean.corr(numeric_only=True)
sns.heatmap(corr_matrix, annot=False, cmap="coolwarm")
plt.title("Correlation Heatmap - Feedback Dataset")
plt.show()

# ---- Opportunity Dataset EDA ----
print("\n[INFO] Opportunity Dataset Summary:")
print(opportunity_clean.describe(include="all"))

# Countplot for isSame label
plot_count(opportunity_clean, "isSame", "Greens", "Distribution of Opportunity Labels (True/Fake)")

# Optional histogram
plot_hist(opportunity_clean, "Unnamed: 0", "Distribution of Index Column in Opportunity Dataset", "purple")

print("\n[DONE] Analysis Completed")
