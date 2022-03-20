# Plan

## I/O
- Input: List of celebrity accounts in tech/ml on Twitter
- Output: List of growing accounts in tech/ml on Twitter

## Definitions
- Celebrity account
    - At least 1000 tweets
    - At least 1000 followers
    - At least a follower / following ratio of 3
- Active growing account
    - Less than 600 followers
    - Less than 600 following 
    - At least 100 tweets
    - At least 1 tweets in the past 7 days

## Tasks
1. Given a list of celebrity accounts find their recent 10 posts with at least 10 replies.
2. Gather the accounts that have replied on those tweets and filter the growing accounts.
3. Return the URLs to the Twitter page of growing accounts.

## Tools
- tweepy

## Future Work
1. Find celebrity accounts automatically