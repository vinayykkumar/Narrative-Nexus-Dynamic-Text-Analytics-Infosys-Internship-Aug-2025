import pandas as pd
import os
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
# NEW: Import the WordNetLemmatizer
from nltk.stem import WordNetLemmatizer

# ==============================================================================
# == NLTK SETUP (with Lemmatizer) ==
# ==============================================================================

try:
    # Define the local directory for NLTK data
    local_nltk_dir = os.path.join(os.getcwd(), 'nltk_data')

    # Add the local directory to NLTK's search path
    if local_nltk_dir not in nltk.data.path:
        nltk.data.path.append(local_nltk_dir)

    # Check and download necessary NLTK data packages
    packages = ['punkt', 'stopwords', 'wordnet'] # NEW: Added 'wordnet' for lemmatization
    for package in packages:
        try:
            nltk.data.find(f'corpora/{package}' if package != 'punkt' else f'tokenizers/{package}')
            print(f"✅ NLTK data '{package}' already found. Skipping download.")
        except LookupError:
            print(f"Downloading NLTK data '{package}' to local project folder...")
            nltk.download(package, download_dir=local_nltk_dir)
            print(f"✅ NLTK data '{package}' downloaded successfully.")

    # Load stopwords after ensuring they are available
    stop_words = set(stopwords.words('english'))
    print("\nNLTK setup is complete and verified.")

except Exception as e:
    print(f"\n❌ An error occurred during NLTK setup: {e}")
    exit()

print("-------------------------------------------\n")


# ==============================================================================
# == DATA LOADING AND PREPROCESSING ==
# ==============================================================================

# --- DATA LOADING ---
data_folder = 'datasets'
file_names = [
    'business_data.csv', 'education_data.csv', 'entertainment_data.csv',
    'sports_data.csv', 'technology_data.csv'
]
dfs = []
for file in file_names:
    file_path = os.path.join(data_folder, file)
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        dfs.append(df)
        print(f"📄 Read {file}")

master_df = pd.concat(dfs, ignore_index=True)
print("\n✅ All datasets have been combined!")
master_df.dropna(subset=['content'], inplace=True)
print("Shape after dropping missing content:", master_df.shape)
print("\n-------------------------------------------")

# --- TEXT PREPROCESSING ---
print("🚀 Starting text preprocessing with LEMMATIZATION...")

# Initialize the lemmatizer
lemmatizer = WordNetLemmatizer()

def clean_text(text):
    """
    Function to clean raw text with lemmatization.
    """
    if not isinstance(text, str):
        return ""
    # 1. Lowercasing
    text = text.lower()
    # 2. Removing Punctuation
    text = re.sub(r'[^\w\s]', '', text)
    # 3. Tokenizing
    words = text.split()
    # 4. Removing Stop Words and Lemmatizing
    # NEW: Lemmatize each word after removing stop words
    lemmatized_words = [lemmatizer.lemmatize(word) for word in words if word not in stop_words]
    # 5. Rejoining words
    return " ".join(lemmatized_words)

# Apply the updated cleaning function
master_df['cleaned_content'] = master_df['content'].apply(clean_text)
print("✅ Text cleaning and lemmatization complete!")
print("\n-------------------------------------------")

# --- DISPLAY SAMPLE & SAVE ---
print("Here's a sample of the original vs. cleaned & lemmatized content:")
pd.set_option('display.max_colwidth', 200)
print(master_df[['content', 'cleaned_content']].head())

output_file = 'cleaned_articles.csv'
master_df.to_csv(output_file, index=False)
print(f"\n🎉 Success! The updated cleaned data has been saved to '{output_file}'.")