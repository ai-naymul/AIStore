import tweepy
import os
from dotenv import load_dotenv
import logging
load_dotenv()

# Load enviroment variables
API_KEY = os.getenv("API_KEY")
BEARER_TOKEN = os.getenv("BEARER_TOKEN")
API_KEY_SECRET = os.getenv("API_KEY_SECRET")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.getenv("ACCESS_TOKEN_SECRET")

class TweetClient():
    def __init__(self):
        self.client = tweepy.Client(bearer_token=BEARER_TOKEN, consumer_key=API_KEY, consumer_secret=API_KEY_SECRET, access_token=ACCESS_TOKEN, access_token_secret=ACCESS_TOKEN_SECRET)
    
    def tweet(self, post: str):
        try:
            response = self.client.create_tweet(text=post)
            if response:
                logging.info(f"Posted the tweet with the following post: {post}")
                return response
        except Exception as e:
            logging.error(f"Error posting tweet with error: {str(e)}")