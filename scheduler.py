import os
import csv
import requests
from slack_sdk import WebClient
from datetime import datetime
from dotenv import load_dotenv
from zoneinfo import ZoneInfo 

# Load environment variables (helpful for local testing)
load_dotenv()

# Environment variables
slack_token = os.getenv("SLACK_API_TOKEN", "your-fallback-slack-token")
wmata_api_key = os.getenv("WMATA_API_KEY", "your-fallback-wmata-key")
slack_channel = os.getenv("SLACK_CHANNEL", "#general")

# Slack client
slack_client = WebClient(token=slack_token)

# Cache for deduplication (optional) and route lookup
alert_cache = {}
bus_alert_lookup = {}  # Populated for /route command


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
        now = datetime.now(ZoneInfo("America/New_York"))

        delays = set()
        detours = set()

        with open("alerts.csv", mode="a", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)

            for incident in incidents:
                routes = incident.get("RoutesAffected", [])
                desc = incident.get("Description", "").strip()

                if not desc:
                    continue
                desc_lower = desc.lower()

                # Normalize routes
                if isinstance(routes, str):
                    route_list = [r.strip() for r in routes.split(",") if r.strip()]
                elif isinstance(routes, list):
                    route_list = [r.strip() for r in routes if isinstance(r, str)]
                else:
                    continue

                if not route_list:
                    continue

                # Save full message for /route
                for route in route_list:
                    msg = f"Bus {route} – {desc}"
                    bus_alert_lookup[route.upper()] = msg

                    # Write to CSV
                    writer.writerow([now.isoformat(), route, desc])

                # Categorize
                if "detour" in desc_lower:
                    detours.update(route_list)
                elif any(word in desc_lower for word in ["delay", "delays", "experiencing"]):
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
