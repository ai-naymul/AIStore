import tweepy

# Replace these values with your own credentials
API_KEY = 'HyX12faK6eC2aISpm8Qxnzddx'
API_KEY_SECRET = 'h8cAXr7pliMUjqoUhmINCEpLuRXTd80TqFj8Zq5jASAIIiP7Ww'
ACCESS_TOKEN = '1902449713837961216-3EoGsTxSokxEky8GCixqR7D4stcZEP'
ACCESS_TOKEN_SECRET = '72Is3aa8gv3BBxq3VAKUTRFnbwstNhMzRckjRHjc2mGGu'
BEARER_TOKEN = 'AAAAAAAAAAAAAAAAAAAAAGMv0AEAAAAArSZSMGvtNW0uOqoYhj0Ij8q8hmE%3D1WhNVGV7OHB3OvSROsZyH03im4nbqepBD4gIJ1Mmra4ENmMfZZ'

# Authenticate to Twitter using OAuth 2.0 Bearer Token
client = tweepy.Client(bearer_token=BEARER_TOKEN, 
                       consumer_key=API_KEY, 
                       consumer_secret=API_KEY_SECRET, 
                       access_token=ACCESS_TOKEN, 
                       access_token_secret=ACCESS_TOKEN_SECRET)

# Post a tweet
tweet = "Hello, world!"
response = client.create_tweet(text=tweet)

print("Tweet posted successfully!", response)