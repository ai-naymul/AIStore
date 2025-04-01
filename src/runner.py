from scrapers.producthunt_daily import ProductHunt
from post_process import PostProcess
from tweet import TweetClient
from datetime import datetime
import logging
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Get environment variables
PRODUCT_HUNT_URL = os.getenv("PRODUCT_HUNT_URL")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TWITTER_API_KEY = os.getenv("API_KEY")
TWITTER_API_SECRET = os.getenv("API_KEY_SECRET")
TWITTER_ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
TWITTER_ACCESS_SECRET = os.getenv("ACCESS_TOKEN_SECRET")
BEARER_TOKEN = os.getenv("BEARER_TOKEN")
def main():
    try:
        # Get current date and format for URL
        current_date = datetime.now()
        # formatted_date = f"{current_date.year}/{current_date.month}/{current_date.day}"
        formatted_date = "2025/3/31"

        formatted_ph_url = PRODUCT_HUNT_URL + formatted_date
        
        logger.info(f"Starting Product Hunt daily scrape for {formatted_date}")
        
        # Scrape Product Hunt
        product_hunt_tools = ProductHunt.run(url=formatted_ph_url)
        
        if not product_hunt_tools:
            logger.error("No tools found. Exiting.")
            return
        
        logger.info(f"Found {len(product_hunt_tools)} tools")
        
        # Initialize post processor
        post_processor = PostProcess(api_key=GEMINI_API_KEY)
        
        # Select top tools to tweet about (max 10 per day to stay within 500/month limit)
        top_tools = post_processor.select_top_tools(product_hunt_tools, max_tools=10)
        
        # Generate tweets for each tool
        tweets = []
        for tool in top_tools:
            tweet_text = post_processor.generate_tweet(tool)
            if tweet_text:
                tweets.append(tweet_text)
        
        # Initialize Twitter client
        twitter_client = TweetClient(
            api_key=TWITTER_API_KEY,
            api_secret=TWITTER_API_SECRET,
            access_token=TWITTER_ACCESS_TOKEN,
            access_secret=TWITTER_ACCESS_SECRET,
            bearer_token=BEARER_TOKEN
        )
        
        # Post tweets
        successful_tweets = twitter_client.post_multiple_tweets(tweets, delay_seconds=300)
        logger.info(f"Successfully posted {successful_tweets} tweets")
        
    except Exception as e:
        logger.error(f"Error in main workflow: {str(e)}")

if __name__ == "__main__":
    main()
