import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os # We'll use this to correctly build the file paths

# --- DATA LOADING AND COMBINING ---

# The name of the subfolder where your datasets are stored
data_folder = 'datasets'

# List of the file names
file_names = [
    'business_data.csv',
    'education_data.csv',
    'entertainment_data.csv',
    'sports_data.csv',
    'technology_data.csv',
]

# Create a list to hold the individual dataframes
dfs = []

# Loop through the file names, build the full path, and read each CSV
for file in file_names:
    # This creates the correct path, like "datasets/business_data.csv"
    file_path = os.path.join(data_folder, file)

    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        dfs.append(df)
        print(f"📄 Read {file} with {len(df)} articles.")
    else:
        print(f"⚠️ Warning: {file_path} not found. Skipping.")

# Check if any dataframes were loaded before trying to combine them
if not dfs:
    print(f"\n❌ Error: No data files were found in the '{data_folder}' directory.")
else:
    # Combine all the dataframes into one single dataframe
    master_df = pd.concat(dfs, ignore_index=True)

    print("\n-------------------------------------------")
    print("✅ All datasets have been combined!")
    print("-------------------------------------------\n")


    # --- EXPLORATORY DATA ANALYSIS (EDA) ---

    # 1. Get basic information about the dataset
    print("1. Basic Information about the dataset:")
    master_df.info()
    print("\nShape of the combined dataset (Rows, Columns):", master_df.shape)
    print("\n-------------------------------------------\n")


    # 2. Check for any missing values
    print("2. Checking for missing values in each column:")
    print(master_df.isnull().sum())
    print("\n-------------------------------------------\n")


    # 3. Analyze the distribution of articles across categories
    print("3. Number of articles per category:")
    category_counts = master_df['category'].value_counts()
    print(category_counts)
    print("\n-------------------------------------------\n")


    # 4. Visualize the category distribution
    print("4. Generating and showing the category distribution plot...")

    plt.style.use('seaborn-v0_8-whitegrid')
    plt.figure(figsize=(12, 7))

    ax = sns.barplot(x=category_counts.index, y=category_counts.values, palette='viridis')

    plt.title('Distribution of News Articles by Category', fontsize=18, fontweight='bold')
    plt.xlabel('Category', fontsize=14)
    plt.ylabel('Number of Articles', fontsize=14)
    plt.xticks(rotation=45, fontsize=12)
    plt.yticks(fontsize=12)

    for p in ax.patches:
        ax.annotate(f'{int(p.get_height())}',
                    (p.get_x() + p.get_width() / 2., p.get_height()),
                    ha = 'center', va = 'center',
                    xytext = (0, 9),
                    textcoords = 'offset points',
                    fontsize=12,
                    fontweight='bold')

    plt.tight_layout()
    plt.show()