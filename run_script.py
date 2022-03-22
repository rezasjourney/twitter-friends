from constants import CELEBS
from secrets import BEARER_TOKEN, API_KEY, API_SECRET

import os
import tweepy
import pandas as pd

def username_to_id(client, username):
    user = client.get_user(username=username)
    return user.data.id

auth = tweepy.OAuth2BearerHandler(BEARER_TOKEN)
api = tweepy.API(auth)

username = CELEBS[0]
max_potential_accounts = 200
min_tweets = 1000
max_followers = 600
max_following = 600
client = tweepy.Client(bearer_token=BEARER_TOKEN, consumer_key=API_KEY, consumer_secret=API_SECRET)

tweets_filename = f'output/{username}_100_tweets.csv'
retweeted_users_filename = f'output/{username}_retweeted_users.csv'

if not os.path.exists(tweets_filename):
    # Find the recent tweets of the celeb account
    id = username_to_id(client, username)
    tweets = client.get_liked_tweets(id)

    tweets_df = pd.json_normalize([item.data for item in tweets.data])
    tweets_df.to_csv(tweets_filename)
else:
    tweets_df = pd.read_csv(tweets_filename, index_col=0)

if not os.path.exists(retweeted_users_filename):
    # Find users who have quote retweeted the celeb account
    retweeted_users = {
        'id': [],
        'name': [],
        'username': [],
        'followers_count': [], 
        'following_count': [], 
        'tweet_count': [], 
        'listed_count': [],
    }
    for tweet_id in tweets_df.id:
        try:
            quote = client.get_quote_tweets(tweet_id, expansions=['author_id'], user_fields=['public_metrics'])
        except tweepy.errors.TooManyRequests:
            break
        
        if quote.includes:
            for user in quote.includes['users']:
                retweeted_users['id'].append(user.id)
                retweeted_users['name'].append(user.name)
                retweeted_users['username'].append(user.username)
                retweeted_users['followers_count'].append(user.public_metrics['followers_count'])
                retweeted_users['following_count'].append(user.public_metrics['following_count'])
                retweeted_users['tweet_count'].append(user.public_metrics['tweet_count'])
                retweeted_users['listed_count'].append(user.public_metrics['listed_count'])

        if len(retweeted_users['id']) > max_potential_accounts:
            break

    retweeted_users_df = pd.DataFrame(retweeted_users)
    retweeted_users_df.to_csv(retweeted_users_filename)
else:
    retweeted_users_df = pd.read_csv(retweeted_users_filename, index_col=0)

potential_accounts_df = retweeted_users_df.copy()
potential_accounts_rows = (
    (retweeted_users_df['tweet_count'] >= min_tweets) & 
    (retweeted_users_df['following_count'] <= max_following) & 
    (retweeted_users_df['followers_count'] <= max_followers)
)
potential_accounts_df = retweeted_users_df[potential_accounts_rows]
potential_accounts_df['url'] = 'https://twitter.com/' + potential_accounts_df['username']

print()
print(21 * '=')
print(f"\n {len(potential_accounts_df)} Potential Friends\n")
print(21 * '=')
print()
for url in potential_accounts_df.url:
    print(url)
