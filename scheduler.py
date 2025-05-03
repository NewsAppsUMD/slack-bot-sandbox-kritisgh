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

        delays = set()
        detours = set()

        for incident in incidents:
            routes = incident.get("RoutesAffected", [])
            desc = incident.get("Description", "").strip().lower()

            # Handle both string and list cases
            if isinstance(routes, str):
                route_list = [r.strip() for r in routes.split(",") if r.strip()]
            elif isinstance(routes, list):
                route_list = [r.strip() for r in routes if isinstance(r, str)]
            else:
                continue

            if not route_list or not desc:
                continue

            # Categorize
            if "detour" in desc:
                detours.update(route_list)
            elif any(word in desc for word in ["delay", "delays", "experiencing"]):
                delays.update(route_list)

        if not delays and not detours:
            print("ℹ️ No new categorized alerts to post.")
            return

        def make_links(route_set):
            return ", ".join([f"<https://buseta.wmata.com/#{r}|{r}>" for r in sorted(route_set)])

        alert_sections = []
        if delays:
            alert_sections.append(f"*Delays*\n{make_links(delays)}")
        if detours:
            alert_sections.append(f"*Detours*\n{make_links(detours)}")

        alert_text = (
            f"🚨 *WMATA Bus Service Alerts* ({now.strftime('%b %d, %Y – %I:%M %p')})\n\n"
            + "\n\n".join(alert_sections)
        )

        slack_client.chat_postMessage(channel=slack_channel, text=alert_text)
        print(f"✅ Posted alert to Slack.")
    except Exception as e:
        print(f"❌ Error in fetch_wmata_alerts: {e}")

if __name__ == "__main__":
    fetch_wmata_alerts()
