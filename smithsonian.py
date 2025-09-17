#!/usr/bin/env python3
# Written by Christopher Gioconda with ChatGPT assistance 09/27/2025
from flask import Flask, render_template_string
import requests
import random
import time

API_KEY = "PUT_YOUR_API_KEY_HERE"
BASE_URL = "https://api.si.edu/openaccess/api/v1.0"

app = Flask(__name__)

def get_random_highres_image():
    while True:  # Keep trying until we find an image
        try:
            search_url = f"{BASE_URL}/search"
            params = {
                "api_key": API_KEY,
                "q": "online_media_type:Images AND paintings", # Change keywords here for filters
                "rows": 1,
                "start": random.randint(0, 10000)
            }

            response = requests.get(search_url, params=params)
            response.raise_for_status()
            data = response.json()

            items = data.get("response", {}).get("rows", [])
            if not items:
                continue  # Try again

            item = random.choice(items)

            # Extract metadata
            title = item.get("title", "Untitled")
            description = (
                item.get("content", {})
                    .get("freetext", {})
                    .get("notes", [{}])[0]
                    .get("content", "No description available.")
            )

            media = item.get("content", {}).get("descriptiveNonRepeating", {}).get("online_media", {})
            resources = media.get("media", []) if media else []
            if not resources:
                continue  # Try again

            # Pick a random media entry
            image = random.choice(resources)

            # Prefer hi-res resource if available
            url = None
            for res in image.get("resources", []):
                if "hi-res" in res.get("label", "").lower():
                    url = res.get("url")
                    break

            # Fallback to main content
            if not url:
                url = image.get("content")

            if url:
                return {"title": title, "description": description, "url": url}

        except requests.exceptions.RequestException as e:
            print("Error fetching image, retrying...", e)
            time.sleep(1)

# HTML template with 60-second refresh
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>{{ image.title }}</title>
    <meta http-equiv="refresh" content="60">
    <style>
        body { background:black}
        img { max-width: 100%; max-height: 950px; margin-top: 0px}
        div { max-width: 100%; max-height: 950px; margin-top: 0px;   display: flex;
  justify-content: center}
        p { max-width: 100%; margin-top: 70% auto; color:white; font-family: "Times New Roman", Times, serif; text-align: center; padding: 0px; font-weight:bold; font-size:36px}
    </style>
</head>
<body>
    {% if image %}
<div>
        <img src='{{ image.url }}' alt='{{ image.title }}'>
</div>
        <p>{{ image.title }}</p>
    {% else %}
        <p>No image found.</p>
    {% endif %}
</body>
</html>
"""

@app.route("/")
def home():
    image = get_random_highres_image()
    return render_template_string(HTML_TEMPLATE, image=image)

if __name__ == "__main__":
    app.run(debug=True)
