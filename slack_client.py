# slack_client.py
import os
from slack_sdk import WebClient
from slack_sdk.webhook import WebhookClient
from slack_sdk.errors import SlackApiError
import requests
from datetime import datetime

slack_token = os.environ.get("SLACK_BOT_TOKEN")
wmata_api_key = os.environ.get("WMATA_API_KEY")
slack_client = WebClient(token=slack_token)


def handle_bus_command(request):
    text = request.form.get("text", "").strip()
    response_url = request.form.get("response_url")

    if not text:
        return {"response_type": "ephemeral", "text": "Please specify a bus route, e.g., `/bus 70`"}

    is_public = text.endswith(" public")
    query = text.replace(" public", "").strip()

    headers = {"api_key": wmata_api_key}
    resp = requests.get("https://api.wmata.com/Incidents.svc/json/BusIncidents", headers=headers)
    incidents = resp.json().get("BusIncidents", [])

    matches = []
    for incident in incidents:
        route = incident.get("RoutesAffected", "")
        if query.lower() in route.lower():
            matches.append(f"• *Bus {route}* – {incident.get('Description', '').strip()}")

    if matches:
        result_text = "\n".join(matches)
    else:
        result_text = f"✅ No current alerts for buses matching \"{query}\"."

    payload = {
        "response_type": "in_channel" if is_public else "ephemeral",
        "text": result_text
    }
    webhook = WebhookClient(response_url)
    webhook.send(**payload)

    return "", 200


def handle_alerts_command(request):
    headers = {"api_key": wmata_api_key}
    resp = requests.get("https://api.wmata.com/Incidents.svc/json/BusIncidents", headers=headers)
    incidents = resp.json().get("BusIncidents", [])

    if not incidents:
        return {"response_type": "ephemeral", "text": "✅ There are no current WMATA bus alerts."}

    result_text = "\n".join([f"• *Bus {inc['RoutesAffected']}* – {inc['Description']}" for inc in incidents])
    now = datetime.now().strftime('%b %d, %Y – %I:%M %p')
    return {"response_type": "ephemeral", "text": f"🚨 *Current WMATA Bus Alerts* ({now})\n\n{result_text}"}


def handle_help_command():
    help_text = (
        "🤖 *WMATA Bus Alert Bot Help*\n\n"
        "• `/bus <route>` – Check status of a specific bus (e.g., `/bus 70`)\n"
        "• `/bus <route> public` – Post result in the channel\n"
        "• `/alerts` – Show all current WMATA bus alerts\n"
        "• `/help` – Show this help message\n\n"
        "The bot also posts alerts automatically as they occur."
    )
    return {"response_type": "ephemeral", "text": help_text}
