# scheduler.py
import os
import requests
from slack_sdk import WebClient
from datetime import datetime, timedelta

slack_token = os.environ.get("SLACK_API_TOKEN")
wmata_api_key = os.environ.get("WMATA_API_KEY")
slack_channel = os.environ.get("SLACK_CHANNEL", "#general")
slack_client = WebClient(token=slack_token)

# cache of posted alerts to prevent duplicates
alert_cache = {}  # {"BusNum|Description": datetime_of_last_post}


def fetch_wmata_alerts():
    try:
        # 🔍 DEBUG: Check if secrets were loaded
        print(f"SLACK_API_TOKEN present: {bool(slack_token)}")
        print(f"WMATA_API_KEY present: {bool(wmata_api_key)}")
        print(f"SLACK_CHANNEL is: {slack_channel}")

        headers = {"api_key": wmata_api_key}
        response = requests.get("https://api.wmata.com/Incidents.svc/json/BusIncidents", headers=headers)
        incidents = response.json().get("BusIncidents", [])

        now = datetime.now()
        messages = []

        for incident in incidents:
            routes = incident.get("RoutesAffected", [])
            bus_num = ", ".join(routes) if isinstance(routes, list) else routes
            desc = incident.get("Description", "").strip()

            if not bus_num or not desc:
                continue

            cache_key = f"{bus_num}|{desc}"
            last_posted = alert_cache.get(cache_key)
            if True:
                messages.append(f"• *Bus {bus_num}* – {desc}")

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
