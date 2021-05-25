"""
@Author Ajay Biswas
"""

from http.client import responses
import os
import googleapiclient.discovery
from lib.keys import api_key as DEVELOPER_KEY
import numpy as np
import pandas as pd
import json

def main():

    api_service_name = "youtube"
    api_version = "v3"

    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, developerKey = DEVELOPER_KEY)

    request = youtube.commentThreads().list(
        part="snippet,replies",
        maxResults=100,
        videoId="od23rHF6Wdo"
    )
    response = request.execute()
    
    #print(response)        # dictionary
    #print(response['kind'])
    #print(response['etag'])
    #print(response['nextPageToken'])
    #print(response['pageInfo'])
    #print(response['items'])

    items = response['items']

    # Writing JSON
    with open('items.json', 'w') as outfile:
        json.dump(items, outfile)
    
    df = pd.read_json (r'items.json')
    print(df)

    
    
    # dictionary to csv
    """
        with open('data.csv', 'w',  encoding='utf-8') as f:
            for key in response.keys():
                f.write("%s, %s\n" % (key, response[key]))
    """
if __name__ == "__main__":
    main()