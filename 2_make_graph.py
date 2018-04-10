import json
import os
import networkx as nx
import unicodecsv as csv
from tweepy import OAuthHandler, API, TweepError

from twitter_api_config import *

# Instantiate Twitter API. parameter 'wait_on_rate_limit' is required to avoid rate limit error
auth = OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_secret)
api = API(auth, wait_on_rate_limit=True)

# Get user by screen name
user = api.get_user(screen_name)

# nodes = followers + followingers
# friendships = relationship between node
nodes = {}
friendships = {}

# Include current user to nodes
nodes[user.id] = {
    'id' : user.id,
    'name' : user.name,
    'avatar_url' : user.profile_image_url
}

# Read all followers
if os.path.exists('twitter_followers.csv'):
    with open('twitter_followers.csv', 'rbU') as f:
        table = csv.reader(f)
        for id, name, followers_count, avatar_url in table:
            # put each follower in nodes
            nodes[id] = {
                'id': id,
                'name': name,
                'avatar_url': avatar_url
            }

# Load finished links frindship
if os.path.exists('twitter_followers_friendship.csv'):
    with open('twitter_followers_friendship.csv', 'rbU') as f:
        for id_a, id_b, str_fr in csv.reader(f):
            friendships[(id_a, id_b)] = str_fr == 'True'

# Determine friendship between each node
current_iteration = 1
total_iteration = len(nodes) * (len(nodes) - 1)

for id_a, user_a in nodes.items():
    for id_b, user_b in nodes.items():
        # Skip checking friendship for myself
        if id_a == id_b:
            continue

        # Skip if friendship is already processed
        if (id_a, id_b) in list(friendships.keys()):
            # Print on-screen error
            print('{} of {}. Is {} followed by {} ? {}'
                  .format(current_iteration, total_iteration, user_a['name'], user_b['name'],
                          'Yes' if friendships[(id_a, id_b)] else 'No'))
            current_iteration += 1

            print('{} of {}. Is {} followed by {} ? {}'
                  .format(current_iteration, total_iteration, user_b['name'], user_a['name'],
                          'Yes' if friendships[(id_a, id_b)] else 'No'))
            current_iteration += 1

            continue

        # If error tweepy.error.TweepError: Not authorized is happened,
        # It might be that the particular user had protected tweets,
        # So, catch and skip it.
        # See: https://stackoverflow.com/questions/19544401/tweepy-not-authorized-tweepy-error-tweeperror-not-authorized
        try :
            # Check friendship between followinger and follower
            user_a_status, user_b_status = api.show_friendship(source_id=id_a, target_id=id_b)

            # Print on-screen info to see the progress
            print('{} of {}. Is {} followed by {} ? {}'.format(current_iteration, total_iteration, user_a['name'],
                                                               user_b['name'],
                                                               'Yes' if user_a_status.followed_by else 'No'))
            current_iteration += 1

            print('{} of {}. Is {} followed by {} ? {}'.format(current_iteration, total_iteration, user_b['name'],
                                                               user_a['name'],
                                                               'Yes' if user_b_status.followed_by else 'No'))
            current_iteration += 1

            # If follower is followed by followinger, then add to links
            friendships[(user_a['id'], user_b['id'])] = user_a_status.followed_by

            # If followinger is followed by follower, then add to links
            friendships[(user_b['id'], user_a['id'])] = user_b_status.followed_by

            ### Since it will take a long time, it's worth to save data in every iteration,
            ### so everytime you can resume it, without have to start from beginning
            # Save the followers friendship in a .csv file
            with open('twitter_followers_friendship.csv', 'wb') as f:
                writer = csv.writer(f, encoding='utf-8')
                for id_a, id_b in friendships.keys():
                    writer.writerow((id_a, id_b, friendships[(id_a, id_b)]))

        except TweepError as e:
            friendships[(user_a['id'], user_b['id'])] = False
            friendships[(user_b['id'], user_a['id'])] = False

            # Print on-screen error
            print('{} of {}. Is {} followed by {} ? Checking friendship raise error. Message: {}'
                  .format(current_iteration, total_iteration, user_a['name'], user_b['name'], str(e)))
            current_iteration += 1

            print('{} of {}. Is {} followed by {} ? Checking friendship raise error. Message: {}'
                  .format(current_iteration, total_iteration, user_b['name'], user_a['name'], str(e)))
            current_iteration += 1

# Simulate graph in NetworkX
links = []
for (id_a, id_b), followed_by in friendships.items():
    if followed_by:
        links.append((id_a, id_b))

G = nx.DiGraph(links)

# Add name and avatar_url to node attribute
names = {}
avatars = {}
for id, node in nodes.items():
    names[id] = node['name']
    avatars[id] = node['avatar_url']

nx.set_node_attributes(G, names, 'name')
nx.set_node_attributes(G, avatars, 'avatar_url')

# Optional: preview
# nx.draw(G)

# Save the graph in a .json file
with open('twitter_graph.json', 'wb') as f:
    f.write(json.dumps(nx.json_graph.node_link_data(G)).encode('utf-8'))