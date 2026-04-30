from flask import Flask, render_template, request
import requests
import os
from dotenv import load_dotenv

load_dotenv()

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

app = Flask(__name__)

def mood_to_query(mood):
    mood_map = {
        "dark": "dark documentary mystery",
        "happy": "cute cat videos",
        "funny": "stand up comedy",
        "chill": "lofi music ambient",
        "motivated": "motivational speech hustle",
        "sad": "emotional storytelling film",
        "bored": "interesting facts mind blowing",
        "learning": "educational explained",
    }
    mood = mood.lower()
    for key in mood_map:
        if key in mood:
            return mood_map[key]
    return mood

def parse_duration(duration):
    duration = duration.replace("PT", "")
    if "M" in duration and "S" in duration:
        parts = duration.split("M")
        minutes = parts[0]
        seconds = parts[1].replace("S", "")
    elif "M" in duration:
        minutes = duration.replace("M", "")
        seconds = "00"
    else:
        minutes = "0"
        seconds = duration.replace("S", "")
    return f"{minutes}:{seconds}"

def search_videos(query, m, max_results=10):
    if m > 7:
        duration = "long"
    elif 3 < m < 8:
        duration = "medium"
    else:
        duration = "short"

    params = {
        "part": "snippet",
        "q": query,
        "key": YOUTUBE_API_KEY,
        "maxResults": max_results,
        "type": "video",
        "videoDuration": duration,
        "order": "relevance"
    }
    response = requests.get("https://www.googleapis.com/youtube/v3/search", params=params)
    data = response.json()

    items = data.get("items", [])
    video_ids = [item["id"]["videoId"] for item in items]

    details_resp = requests.get("https://www.googleapis.com/youtube/v3/videos", params={
        "part": "contentDetails,statistics",
        "id": ",".join(video_ids),
        "key": YOUTUBE_API_KEY,
    })
    details = {item["id"]: item for item in details_resp.json().get("items", [])}

    results = []
    for item in items:
        vid_id = item["id"]["videoId"]
        detail = details.get(vid_id, {})
        results.append({
            "title": item["snippet"]["title"],
            "channel": item["snippet"]["channelTitle"],
            "url": f"https://youtube.com/watch?v={vid_id}",
            "duration": parse_duration(detail.get("contentDetails", {}).get("duration", "PT0M0S")),
            "views": int(detail.get("statistics", {}).get("viewCount", 0))
        })
    return results

@app.route("/", methods=["GET", "POST"])
def index():
    videos = []
    if request.method == "POST":
        mood = request.form.get("mood")
        m = int(request.form.get("time"))
        query = mood_to_query(mood)
        videos = search_videos(query, m)
    return render_template("index.html", videos=videos)

if __name__ == "__main__":
    app.run(debug=True)