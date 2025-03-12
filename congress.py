import os
import json
from datetime import datetime
import requests
from slack import WebClient
from slack.errors import SlackApiError


slack_token = os.environ.get('SLACK_API_TOKEN')
client = WebClient(token=slack_token)

congress_api_key = "bgr9SsFsuHo8DjjEciTcoQPNwUIgIZeZPFxUMwHw"

url = f"https://api.congress.gov/v3/committee-report/119/hrpt?api_key={congress_api_key}&format=json"

r = requests.get(url)

results = r.json()

first_result = results['reports'][0]

display_url = f"https://www.congress.gov/congressional-report/{first_result['congress']}th-congress/house-report/{first_result['number']}"

display_date = datetime.strptime(first_result['updateDate'], '%Y-%m-%dT%H:%M:%SZ')
formatted_date = display_date.strftime('%B %-d, %Y at %-I:%M%p')
sentence = f"On {formatted_date}, the House published {first_result['citation']}, which is available at {display_url}"

msg = sentence
try:
    response = client.chat_postMessage(
        channel="slack-bots",
        text=msg,
        unfurl_links=True, 
        unfurl_media=True
    )
    print("success!")
except SlackApiError as e:
    assert e.response["ok"] is False
    assert e.response["error"]
    print(f"Got an error: {e.response['error']}")