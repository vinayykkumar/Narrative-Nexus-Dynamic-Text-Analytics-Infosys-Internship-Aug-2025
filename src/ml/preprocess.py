import pandas as pd
from .utils import preprocess_text


def load_csv(path: str, text_col: str = 'text') -> pd.DataFrame:
    """Load dataset and preprocess text"""
    df = pd.read_csv(path)
    df = df.dropna(subset=[text_col])
    df['raw_text'] = df[text_col].astype(str)
    df['clean_text'] = df['raw_text'].apply(preprocess_text)
    return df

if __name__ == '__main__':
    df = load_csv('data/bbc-text.csv', text_col='text')
    print(df[['raw_text','clean_text']].head())
    df = load_csv('data/cnn_dailymail.csv', text_col='text')
    print(df[['raw_text','clean_text']].head())
    df = load_csv('data/imdb-dataset.csv', text_col='text')
    print(df[['raw_text','clean_text']].head())
