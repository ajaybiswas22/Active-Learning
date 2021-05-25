"""
@Author Ajay Biswas
"""
from googleapiclient.discovery import build
from lib.keys import api_key

youtube_service = build('youtube', 'v3', developerKey=api_key)

# list channel
request = youtube_service.channels().list(
    part='statistics',
    id = 'UC8i1UesFfrtbju64uaZB1DA' # Ajay B.
)

response = request.execute()

print(response)

youtube_service.close()
