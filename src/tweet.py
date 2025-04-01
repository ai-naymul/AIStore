import tweepy
import logging
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TweetClient:
    def __init__(self, api_key, api_secret, access_token, access_secret, bearer_token):
        self.auth = tweepy.OAuth1UserHandler(
            api_key, api_secret, access_token, access_secret
        )
        self.api = tweepy.API(self.auth)
        self.client = tweepy.Client(
            bearer_token=bearer_token,
            consumer_key=api_key,
            consumer_secret=api_secret,
            access_token=access_token,
            access_token_secret=access_secret
        )
        
    def post_tweet(self, text):
        """Post a tweet with the given text"""
        try:
            response = self.client.create_tweet(text=text)
            logger.info(f"Posted tweet successfully: {text[:50]}...")
            return response
        except Exception as e:
            logger.error(f"Error posting tweet: {str(e)}")
            return None
    
    def post_multiple_tweets(self, tweets, delay_seconds=300):
        """Post multiple tweets with a delay between each"""
        successful_tweets = 0
        
        for tweet in tweets:
            if not tweet:
                continue
                
            result = self.post_tweet(tweet)
            if result:
                successful_tweets += 1
                
            # Wait between tweets to avoid rate limits
            if successful_tweets < len(tweets):
                logger.info(f"Waiting {delay_seconds} seconds before next tweet...")
                time.sleep(delay_seconds)
        
        return successful_tweets
