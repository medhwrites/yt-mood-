import requests
import os
from dotenv import load_dotenv

load_dotenv()

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

def mood_to_query(mood):
    mood_map = {
        "dark": "dark documentary mystery",
        "happy":"cute cat videos",
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
    return mood  # fallback to raw input

def search_videos(query, m, max_results =10):
    url = "https://www.googleapis.com/youtube/v3/search"
    if m>7:
         params = {
        "part": "snippet",
        "q": query,
        "key": YOUTUBE_API_KEY,
        "maxResults": max_results,
        "type": "video",
        "videoDuration": "long",
        "order": "relevance"
    }
    if 3<m<8:
         params = {
        "part": "snippet",
        "q": query,
        "key": YOUTUBE_API_KEY,
        "maxResults": max_results,
        "type": "video",
        "videoDuration": "medium",
        "order": "relevance"
    }
    if m<4:
         params = {
        "part": "snippet",
        "q": query,
        "key": YOUTUBE_API_KEY,
        "maxResults": max_results,
        "type": "video",
        "videoDuration": "short",
        "order": "relevance"
    }
        
    
    response = requests.get(url, params=params)
    return response.json()
def get_video_details(video_ids):
    url = "https://www.googleapis.com/youtube/v3/videos"
    params = {
        "part": "contentDetails,statistics",
        "id": ",".join(video_ids),
        "key": YOUTUBE_API_KEY,
    }
    response = requests.get(url, params=params)
    return response.json()

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

def print_results(data):
    items = data.get("items", [])
    video_ids = [item["id"]["videoId"] for item in items]
    details = get_video_details(video_ids)
    
    details_map = {}
    for item in details.get("items", []):
        vid_id = item["id"]
        duration = item["contentDetails"]["duration"]
        views = item["statistics"].get("viewCount", "N/A")
        details_map[vid_id] = {"duration": duration, "views": views}

    for i, item in enumerate(items, 1):
        title = item["snippet"]["title"]
        channel = item["snippet"]["channelTitle"]
        video_id = item["id"]["videoId"]
        url = f"https://youtube.com/watch?v={video_id}"
        info = details_map.get(video_id, {})
        views = int(info.get("views", 0))
        duration = parse_duration(info.get("duration", "PT0M0S"))
        print(f"{i}. {title}")
        print(f"   {channel}")
        print(f"   Duration: {duration} | Views: {views:,}")
        print(f"   {url}\n")

m=int(input("On a scale of 1 to 10, how much time do you have? "))
mood = input("How are you feeling? ")
query = mood_to_query(mood)
print(f"\nSearching for: {query}\n")
results = search_videos(query,m)
print_results(results)