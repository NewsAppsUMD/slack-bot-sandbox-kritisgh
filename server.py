# server.py
import os
import requests
from flask import Flask, request, jsonify
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

wmata_api_key = os.getenv("WMATA_API_KEY")

@app.route("/route", methods=["POST"])
def route_lookup():
    text = request.form.get("text", "").strip().upper()
    if not text:
        return "Please specify a route, e.g., `/route T2`.", 200

    # Fetch WMATA incidents
    headers = {"api_key": wmata_api_key}
    url = "https://api.wmata.com/Incidents.svc/json/BusIncidents"
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        return "⚠️ Could not fetch WMATA data at the moment.", 200

    incidents = response.json().get("BusIncidents", [])
    matched = [i for i in incidents if text in i.get("RoutesAffected", "")]

    if not matched:
        return f"No alerts found for Bus {text}.", 200

    desc = matched[0]["Description"]
    return f"*Bus {text}* – {desc}", 200

if __name__ == "__main__":
    app.run(port=5000)
