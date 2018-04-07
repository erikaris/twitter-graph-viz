import unicodecsv as csv
from tweepy import OAuthHandler, API

from twitter_api_config import *

# Instantiate Twitter API. parameter 'wait_on_rate_limit' is required to avoid rate limit error
auth = OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_secret)
api = API(auth, wait_on_rate_limit=True)

# Get user by screen name
user = api.get_user(screen_name)

# Get all followers ids of current user
followers_ids = user.followers_ids()

# Iterate over followers_ids and get each user info
csv_rows = []
for idx, follower_id in enumerate(followers_ids):
    follower = api.get_user(follower_id)

    # Print on-screen info to see the progress
    print('{} of {}. User info of {}'.format(idx, len(followers_ids), follower.name))

    csv_rows.append([
        follower.id,                # 1st column -> id of follower
        follower.name,              # 2nd column -> fullname of follower
        follower.followers_count,   # 3rd column -> num of follower. it will be used as link weight
        follower.profile_image_url  # 4th column -> URL of avatar. it will be used in d3 node image
    ])

# Save the followers in a .csv file
with open('twitter_followers.csv', 'wb') as f:
    writer = csv.writer(f, encoding='utf-8')
    writer.writerows(csv_rows)