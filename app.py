from flask import Flask, request, jsonify
from scheduler import fetch_wmata_alerts
from slack_client import handle_bus_command, handle_alerts_command, handle_help_command
from apscheduler.schedulers.background import BackgroundScheduler
import os

app = Flask(__name__)

# Start scheduler for auto-alerts
scheduler = BackgroundScheduler()
scheduler.add_job(fetch_wmata_alerts, 'interval', seconds=60)
scheduler.start()

@app.route("/slash/bus", methods=["POST"])
def slash_bus():
    return handle_bus_command(request)

@app.route("/slash/alerts", methods=["POST"])
def slash_alerts():
    return handle_alerts_command(request)

# @app.route("/slash/help", methods=["POST"])
# def slash_help():
#     return handle_help_command()



@app.route("/slash/help", methods=["POST"])
def help_command():
    help_text = (
        "*WMATA Slack Bot Help*\n\n"
        "• `/route [bus number]` – Get a detailed alert for a specific route (e.g., `/route T2`)\n"
        "• `/help` – Show this help message\n"
        "\n"
        "Alerts are pulled live from WMATA's Bus Incidents API. Routes with active delays or detours will show alerts here."
    )

    return jsonify({
        "response_type": "ephemeral",
        "text": help_text
    })


if __name__ == "__main__":
    app.run(debug=True, port=5000)
