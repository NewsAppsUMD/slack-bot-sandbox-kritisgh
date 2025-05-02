[![Open in Codespaces](https://classroom.github.com/assets/launch-codespace-2972f46106e565e64193e422d61a12cf1da4916b45550586e14ef0a7c637dd04.svg)](https://classroom.github.com/open-in-codespaces?assignment_repo_id=18620074)
# slack-bot-sandbox

A repository for experimenting with the Slack API in Python by students in JOUR328, News Application Development.

# Hitting API endpoint
I have setup my Secrets in Github from WMATA API (https://developer.wmata.com/) and the Slack API. I am able to hit the endpoint for WMATA API. I am accessigng the Incidents API (https://developer.wmata.com/api-details#api=54763641281d83086473f232&operation=54763641281d830c946a3d75). When I run it locally from the file, I am able to post to the slack-bot channel. However, it does not post when I run it from Github Actions. When I ask an LLM it says the Secrets are not able to access the API key so currently I am loading them from a .env file. Please help me with running this from Github Actions.

 I am not storing the data currently. This could be useful in the future to see which buses face more issues and gauge trends. My next step is to not post a list of all the buses that are facing issues but do some further formatting. My next steps are to have all the buses that are delayed just listed out under a heading called Delays, buses on detour under Detour. I will need to see what kind of errors there are. I am planning on adding some / commands. 

I am thinking of adding:
/help : Lists all available bot commands and what they do.
/busalerts : Fetches and displays the latest WMATA bus incident alerts on demand.
/ route : Checks whether a specific bus route has current alerts.

Example: /route 83
Response 1: No current alerts for Bus 83.
or 
Response 2: Expect delays in both directions on Route 83 because of operator availability. Check your bus location by visiting https://buseta.wmata.com/#83 

