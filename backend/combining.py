import pandas as pd

amazon = pd.read_csv('reviews_ratings.csv')
amazon = amazon[['translated']].rename(columns={'translated': 'text'})

bbc = pd.read_csv('bbc_news.csv')
bbc = bbc[['text']]

tweets = pd.read_csv('twitter_tweets.csv')
tweets = tweets[['text']]

articles = pd.read_csv('articles.csv')
articles = articles[['Description']].rename(columns={'Description': 'text'})

combined = pd.concat([amazon, bbc, tweets, articles], ignore_index=True)

combined.to_csv('combined_data.csv', index=False)