import json

import networkx as nx
import unicodecsv as csv
from tweepy import OAuthHandler, API

from twitter_api_config import *

# Instantiate Twitter API. parameter 'wait_on_rate_limit' is required to avoid rate limit error
auth = OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_secret)
api = API(auth, wait_on_rate_limit=True)

# Get user by screen name
user = api.get_user(screen_name)

# nodes = followers + followingers
# links = relationship between node
nodes = {}
links = []

# Include current user to nodes
nodes[user.id] = {
    'id' : user.id,
    'name' : user.name,
    'avatar_url' : user.profile_image_url
}

# Read all followers
with open('twitter_followers.csv', 'rbU') as f:
    table = csv.reader(f)
    for id, name, followers_count, avatar_url in table:
        # put each follower in nodes
        nodes[id] = {
            'id': id,
            'name': name,
            'avatar_url': avatar_url
        }

# Determine friendship between each node
current_iteration = 1;
total_iteration = len(nodes) * (len(nodes) - 1)
processed_friendship = []

for id_a, user_a in nodes.items():
    for id_b, user_b in nodes.items():
        # Skip checking friendship for myself
        if id_a == id_b:
            continue

        # Skip if friendship is already processed
        if (id_a, id_b) in processed_friendship:
            continue

        # Check friendship between followinger and follower
        user_a_status, user_b_status = api.show_friendship(source_id=id_a, target_id=id_b)

        # Print on-screen info to see the progress
        print('{} of {}'.format(current_iteration, total_iteration))

        print('Is {} followed by {} ? {}'.format(user_a['name'], user_b['name'],
                                                 'Yes' if user_a_status.followed_by else 'No'))

        print('Is {} followed by {} ? {}'.format(user_b['name'], user_a['name'],
                                                 'Yes' if user_b_status.followed_by else 'No'))

        # If follower is followed by followinger, then add to links
        if user_a_status.followed_by:
            links.append((user_a['id'], user_b['id']))

        # If followinger is followed by follower, then add to links
        if user_b_status.followed_by:
            links.append((user_b['id'], user_a['id']))

        # Add to processed_friendship
        processed_friendship.append((id_a, id_b))
        processed_friendship.append((id_b, id_a))

        current_iteration += 1


# Simulate graph in NetworkX
# G = nx.DiGraph(links)

# Add name and avatar_url to node attribute
names = {}
avatars = {}
for id, node in nodes.items():
    names[id] = node['name']
    avatars[id] = node['avatar_url']

nx.set_node_attributes(G, 'name', names)
nx.set_node_attributes(G, 'avatar_url', avatars)

# Optional: preview
nx.draw(G)

# Save the graph in a .json file
with open('twitter_graph.json', 'wb') as f:
    f.write(json.dumps(nx.json_graph.node_link_data(G)))