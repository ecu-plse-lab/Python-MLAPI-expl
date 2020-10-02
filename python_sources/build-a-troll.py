#!/bin/python
import json
import os
import re
from math import isnan

import markovify
import numpy as np
import pandas as pd


def clean(string):
    tw = string
    tw = re.sub("(https?://.*)|(www\..*)|(t\.co.*)|(amzn\.to.*)( |$)|", "", tw)  # remove links + newlines
    tw = re.sub("\n", " ", tw)
    return tw


def get_corpus():
    # russian trolls, with an ID set for constant time user access
    users = pd.read_csv("../input/users.csv")
    users.set_index(keys="id", inplace=True, drop=False)
    tweets = pd.read_csv("../input/tweets.csv")

    # sort users by their ratio of favorites per follower
    users["favorites_per_follower"] = users.apply(lambda r: r.favourites_count / (r.followers_count + 1), axis=1)
    users.sort_values(by=["favorites_per_follower"], ascending=False, inplace=True)

    # create a column of empty lists to collect tweets in, then make a list of dictionaries from users
    users["tweets"] = np.empty((len(users), 0)).tolist()
    curated_tweets = pd.Series(users.tweets.values, index=users.id).to_dict()

    for index, tweet in tweets.iterrows():
        if isnan(tweet.user_id) or "RT" in str(tweet.text):  # ignore unidentified tweets and re-tweets
            continue
        # curate list of tweets and their # of favorites
        curated_tweets[tweet.user_id].append([str(tweet.text), tweet.favorite_count if not "nan" else 0])
    # sort the list by # of favorites then combine its contents into a corpus, taking care to clean the text
    corpus = " ".join(" ".join(clean(z[0]) for z in sorted(x, key=lambda y: y[1])) for x in curated_tweets.values())
    return corpus


if __name__ == "__main__":
    corpus = get_corpus()
    markov_model = markovify.Text(corpus)
    for i in range(10):
        print("The Russians say:", markov_model.make_short_sentence(140))  # characters max
    exit(0)