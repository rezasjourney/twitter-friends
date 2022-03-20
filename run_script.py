from constants import CELEBS
from secrets import BEARER_TOKEN, API_KEY, API_SECRET

import os
import tweepy
import pandas as pd

def username_to_id(client, username):
    user = client.get_user(username=username)
    return user.data.id

def get_public_metrics(client, user_id):
    user = client.get_user(id=user_id, user_fields=['public_metrics'])
    public_metrics = user.data.public_metrics
    public_metrics['username'] = user.data.username
    return user.data.public_metrics

auth = tweepy.OAuth2BearerHandler(BEARER_TOKEN)
api = tweepy.API(auth)

username = CELEBS[0]
max_potential_accounts = 50
min_tweets = 1000
max_followers = 600
max_following = 600
client = tweepy.Client(bearer_token=BEARER_TOKEN, consumer_key=API_KEY, consumer_secret=API_SECRET)

tweets_filename = f'output/{username}_100_tweets.csv'
quote_tweets_filename = f'output/{username}_quote_tweets.csv'
quote_tweets_counts_filename = f'output/{username}_quote_tweets_with_counts.csv'

if not os.path.exists(tweets_filename):
    # Find the recent tweets of the celeb account
    id = username_to_id(client, username)
    tweets = client.get_liked_tweets(id)

    tweets_df = pd.json_normalize([item.data for item in tweets.data])
    tweets_df.to_csv(tweets_filename)
else:
    tweets_df = pd.read_csv(tweets_filename, index_col=0)

if not os.path.exists(quote_tweets_filename):
    # Find users who have quote retweeted the celeb account
    quote_tweets = []
    for tweet_id in tweets_df.id:
        try:
            quote = client.get_quote_tweets(tweet_id, expansions=['author_id'])
        except tweepy.errors.TooManyRequests:
            break
        
        if quote.data:
            quote_tweets += [item.data for item in quote.data]

        if len(quote_tweets) > max_potential_accounts:
            break

    quote_tweets_df = pd.json_normalize(quote_tweets)
    quote_tweets_df.to_csv(quote_tweets_filename)
else:
    quote_tweets_df = pd.read_csv(quote_tweets_filename, index_col=0)

if not os.path.exists(quote_tweets_counts_filename):
    # Get number of followers and following of users who quote retweeted
    quote_tweets_counts_df = quote_tweets_df.copy()
    
    followers_count = []
    following_count = []
    tweet_count = []
    username = []
    for user_id in quote_tweets_counts_df.author_id:
        try:
            public_metrics = get_public_metrics(client, user_id)
            followers_count.append(public_metrics['followers_count'])
            following_count.append(public_metrics['following_count'])
            tweet_count.append(public_metrics['tweet_count'])
            username.append(public_metrics['username'])
        except tweepy.errors.TooManyRequests:
            followers_count.append(-1)
            following_count.append(-1)
            tweet_count.append(-1)
            username.append('')

    quote_tweets_counts_df['followers_count'] = followers_count
    quote_tweets_counts_df['following_count'] = following_count
    quote_tweets_counts_df['tweet_count'] = tweet_count
    quote_tweets_counts_df['username'] = username

    quote_tweets_counts_df.to_csv(quote_tweets_counts_filename)
else:
    quote_tweets_counts_df = pd.read_csv(quote_tweets_counts_filename, index_col=0)

potential_accounts_rows = (
    (quote_tweets_counts_df['tweet_count'] >= min_tweets) & 
    (quote_tweets_counts_df['following_count'] <= max_following) & 
    (quote_tweets_counts_df['followers_count'] <= max_followers)
)
potential_accounts_df = quote_tweets_counts_df[potential_accounts_rows]
potential_accounts_df['url'] = 'https://twitter.com/' + potential_accounts_df['username']

print()
print(21 * '=')
print(f"\n {len(potential_accounts_df)} Potential Friends\n")
print(21 * '=')
print()
for url in potential_accounts_df.url:
    print(url)
