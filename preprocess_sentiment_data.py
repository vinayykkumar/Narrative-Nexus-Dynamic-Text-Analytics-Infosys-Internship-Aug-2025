import pandas as pd
import os
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

# ==============================================================================
# == NLTK SETUP ==
# ==============================================================================
# This block correctly handles the NLTK data setup.

try:
    # Define the local directory for NLTK data
    local_nltk_dir = os.path.join(os.getcwd(), 'nltk_data')

    # Add the local directory to NLTK's search path
    if local_nltk_dir not in nltk.data.path:
        nltk.data.path.append(local_nltk_dir)

    # Check and download necessary NLTK data packages
    packages = ['punkt', 'stopwords', 'wordnet']
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
# == DATA LOADING AND PREPROCESSING FOR SENTIMENT ANALYSIS ==
# ==============================================================================

# --- 1. LOAD THE IMDB DATA ---
data_file = os.path.join('datasets', 'IMDB Dataset.csv')

try:
    df = pd.read_csv(data_file)
    print("✅ IMDB Movie Reviews dataset loaded successfully.")
except FileNotFoundError:
    print(f"❌ Error: '{data_file}' not found.")
    print("Please make sure you have downloaded the dataset and placed it in the 'datasets' folder.")
    exit()

df.dropna(subset=['review'], inplace=True)
print("Shape of dataset:", df.shape)
print("\n-------------------------------------------")


# --- 2. TEXT PREPROCESSING ---
print("🚀 Starting text preprocessing with lemmatization for sentiment data...")

lemmatizer = WordNetLemmatizer()

def clean_text(text):
    """
    Function to clean raw text with lemmatization.
    """
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r'<br\s*/?>', ' ', text) # Remove HTML line breaks
    text = re.sub(r'[^\w\s]', '', text) # Remove punctuation
    words = text.split()
    lemmatized_words = [lemmatizer.lemmatize(word) for word in words if word not in stop_words]
    return " ".join(lemmatized_words)

# Apply the cleaning function to the 'review' column
df['cleaned_review'] = df['review'].apply(clean_text)
print("✅ Text cleaning and lemmatization complete!")
print("\n-------------------------------------------")


# --- 3. DISPLAY SAMPLE & SAVE ---
print("Here's a sample of the original vs. cleaned review:")
pd.set_option('display.max_colwidth', 200)
# Note: We are displaying the 'review' and 'cleaned_review' columns
print(df[['review', 'cleaned_review']].head())

# Define the new output file name
output_file = 'cleaned_sentiment_data.csv'
df.to_csv(output_file, index=False)
print(f"\n🎉 Success! The cleaned sentiment data has been saved to '{output_file}'.")