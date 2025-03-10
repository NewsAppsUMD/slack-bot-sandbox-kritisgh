import requests
import json
from slack import WebClient
from slack.errors import SlackApiError
import os

# congress_key = os.environ.get('CONGRESS_API_KEY')
congress_api_key = "bgr9SsFsuHo8DjjEciTcoQPNwUIgIZeZPFxUMwHw"
url = f"https://api.congress.gov/v3/committee-report/119/hrpt?api_key={congress_api_key}&format=json"
print(url)
r = requests.get(url)
results = r.json()
print(results)