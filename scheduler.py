import os
import csv
import requests
from slack_sdk import WebClient
from datetime import datetime
from dotenv import load_dotenv
from zoneinfo import ZoneInfo

# Load environment variables
load_dotenv()

slack_token = os.getenv("SLACK_API_TOKEN", "your-fallback-slack-token")
wmata_api_key = os.getenv("WMATA_API_KEY", "your-fallback-wmata-key")
slack_channel = os.getenv("SLACK_CHANNEL", "#general")

slack_client = WebClient(token=slack_token)

bus_alert_lookup = {}  # Used for /route slash command

CSV_FILE = "alerts.csv"

def load_logged_incident_ids():
    if not os.path.exists(CSV_FILE):
        return set()
    with open(CSV_FILE, newline='', encoding='utf-8') as f:
        return set(row[0] for row in csv.reader(f))

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
        incidents = data.get("BusIncidents", [])
        now = datetime.now(ZoneInfo("America/New_York"))

        logged_ids = load_logged_incident_ids()
        new_rows = []
        delays = set()
        detours = set()

        for incident in incidents:
            incident_id = incident.get("IncidentID", "").strip()
            desc = incident.get("Description", "").strip()
            routes = incident.get("RoutesAffected", [])

            if not incident_id or not desc:
                continue

            # Normalize routes
            if isinstance(routes, str):
                route_list = [r.strip() for r in routes.split(",") if r.strip()]
            elif isinstance(routes, list):
                route_list = [r.strip() for r in routes if isinstance(r, str)]
            else:
                continue

            if not route_list:
                continue

            # Populate for /route command
            for route in route_list:
                bus_alert_lookup[route.upper()] = f"Bus {route} – {desc}"

            # Classify
            desc_lower = desc.lower()
            if "detour" in desc_lower:
                detours.update(route_list)
            elif any(w in desc_lower for w in ["delay", "delays", "experiencing"]):
                delays.update(route_list)

            # Only add to CSV if incident is new
            if incident_id not in logged_ids:
                for route in route_list:
                    new_rows.append([incident_id, now.isoformat(), route, desc])

        if new_rows:
            with open(CSV_FILE, mode="a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerows(new_rows)
            print(f"📝 Logged {len(new_rows)} new incident(s) to CSV.")

        # Always post Slack alert, even for repeated ones
        if not delays and not detours:
            print("ℹ️ No categorized delays or detours.")
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
        print("✅ Posted alert to Slack.")

    except Exception as e:
        print(f"❌ Error in fetch_wmata_alerts: {e}")

if __name__ == "__main__":
    fetch_wmata_alerts()
