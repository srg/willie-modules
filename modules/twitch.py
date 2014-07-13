# coding=utf-8
"""
requirements:
- requests
"""

#import willie.module
import requests, json, urllib


format_search = "https://api.twitch.tv/kraken/search/streams?query={0}&offset={1}&limit={2}"


def search(query, offset=0, limit=10):
    query_encoded = urllib.quote(query.encode("utf8"))
    text = requests.get(format_search.format(query_encoded, offset, limit)).text
    return json.loads(text)


if __name__ == "__main__":
    js = search("shovel knight")
    print js["_total"]
    print len(js["streams"])