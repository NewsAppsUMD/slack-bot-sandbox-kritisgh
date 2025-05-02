import os
import requests
from slack_sdk import WebClient
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from a .env file (useful for local testing)
load_dotenv()

# Get environment variables or fallback values
slack_token = os.getenv("SLACK_API_TOKEN", "your-fallback-slack-token")
wmata_api_key = os.getenv("WMATA_API_KEY", "your-fallback-wmata-key")
slack_channel = os.getenv("SLACK_CHANNEL", "#general")

# Initialize Slack client
slack_client = WebClient(token=slack_token)

# Optional: cache for deduplication
alert_cache = {}

def fetch_wmata_alerts():
    try:
        # Debug: confirm environment variables
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
        incidents = data.get("BusIncidents", [])
        print(f"Raw Response: {data}")

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
                alert_cache[cache_key] = now

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

if __name__ == "__main__":
    fetch_wmata_alerts()
