import os
import requests
from slack_sdk import WebClient
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load variables from a .env file if available (for local testing)
load_dotenv()

# Get from environment or fallback
slack_token = os.getenv("SLACK_API_TOKEN", "your-fallback-slack-token")
wmata_api_key = os.getenv("WMATA_API_KEY", "your-fallback-wmata-key")
slack_channel = os.getenv("SLACK_CHANNEL", "#general")


slack_client = WebClient(token=slack_token)

# cache of posted alerts to prevent duplicates
alert_cache = {}  # {"BusNum|Description": datetime_of_last_post}


import os
import requests
from slack_sdk import WebClient
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get environment variables or fallback values
slack_token = os.getenv("SLACK_API_TOKEN", "your-fallback-slack-token")
wmata_api_key = os.getenv("WMATA_API_KEY", "your-fallback-wmata-key")
slack_channel = os.getenv("SLACK_CHANNEL", "#general")

# Slack client setup
slack_client = WebClient(token=slack_token)

# Optional: cache for alert deduplication
alert_cache = {}

def fetch_wmata_alerts():
    try:
        # Debug: confirm env vars
        print(f"SLACK_API_TOKEN present: {bool(slack_token)}")
        print(f"WMATA_API_KEY present: {bool(wmata_api_key)}")
        print(f"SLACK_CHANNEL is: {slack_channel}")

        url = "https://api.wmata.com/Incidents.svc/json/BusIncidents"
        headers = {"api_key": wmata_api_key}
        response = requests.get(url, headers=headers)

        print(f"HTTP Status Code: {response.status_code}")
        if response.status_code != 200:
            print(f"❌ Failed to fetch data: {response.text}")
            return

        data = response.json()
        print(f"Raw Response: {data}")

        incidents = data.get("BusIncidents", [])
        now = datetime.now()
        messages = []

        for incident in incidents:
            routes = incident.get("RoutesAffected", [])
            bus_num = ", ".join(routes) if isinstance(routes, list) else routes
            desc = incident.get("Description", "").strip()

            if not bus_num or not desc:
                continue

            cache_key = f"{bus_num}|{desc}"
            if cache_key not in alert_cache:
                messages.append(f"• *Bus {bus_num}* – {desc}")
                alert_cache[cache_key] = now  # cache this message

        if messages:
            alert_text = (
                f"🚨 *WMATA Bus Service Alerts* ({now.strftime('%b %d, %Y – %I:%M %p')})\n\n"
                + "\n".join(messages)
            )
            slack_client.chat_postMessage(channel=slack_channel, text=alert_text)
            print(f"✅ Posted {len(messages)} alert(s) to Slack.")
        else:
            print("ℹ️ No new WMATA alerts to post.")

    except Exception as e:
        print(f"❌ Error in fetch_wmata_alerts: {e}")

# Run the function (uncomment for local test)
fetch_wmata_alerts()
