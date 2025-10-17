import tweepy
from gemini import execute_gemini 


API_KEY = "GDwN9X3kFYoa1yABO823hBLc2"
API_SECRET_KEY = "H6U3knYSjRvO7jjgSuMX5GXAxc1sZVVi0LrSOvyWWqS7O5hyiw"
ACCESS_TOKEN = "944088005056200705-o5ZtBI9NImDWCnZzqBO8h1SOOwH02Zo"
ACCESS_TOKEN_SECRET = "OUVXQJvcJH2QOPQ2PrqvcWEj8zkRhmjaGh8pJukyw5QpI"
BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAAMaM3gEAAAAAomwOn6K0CNjhxYyG6F35by2xRa0%3D78SOwEvWVonokxRdxG7dGohYU7aldP0zsKbCxYGsUybM8SUOnc"

if __name__ == "__main__":
    # Initialize Tweepy client
    twitterClient = tweepy.Client(
        bearer_token=BEARER_TOKEN,
        consumer_key=API_KEY,
        consumer_secret=API_SECRET_KEY,
        access_token=ACCESS_TOKEN,
        access_token_secret=ACCESS_TOKEN_SECRET,
        wait_on_rate_limit=True,
    )

    # Get user info
    user = twitterClient.get_user(username="sundarpichai")
    user_id = user.data.id

    # Get last 5 tweets
    latest_5_tweets = twitterClient.get_users_tweets(id=user_id, max_results=5)

    if latest_5_tweets.data:
        for tweet in latest_5_tweets.data:
            print(tweet.text)

            prompt = f"""
            Summarize the twitter tweet attached and give it a sentiment analysis score.
            TWEET ==> {tweet.text}
            """
            llm_out = execute_gemini(prompt)
            print(llm_out)
    else:
        print("No tweets found.")
