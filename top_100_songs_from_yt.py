from googleapiclient.discovery import build
import re
from collections import defaultdict
from config import youtube_api_key

API_KEY = youtube_api_key
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

youtube = build(
    YOUTUBE_API_SERVICE_NAME,
    YOUTUBE_API_VERSION,
    developerKey=API_KEY
)

EXCLUDE_KEYWORDS = re.compile(
    r"(live|cover|remix|reaction|karaoke|instrumental|collection| medley|tribute|parody|dance practice|lyric video|fan made|top)",
    re.IGNORECASE
)

def search_videos(artist, max_pages=5):
    videos = []
    request = youtube.search().list(
        q=artist,
        part="id,snippet",
        type="video",
        maxResults=50
    )

    for _ in range(max_pages):
        response = request.execute()

        for item in response["items"]:
            title = item["snippet"]["title"]
            channel = item["snippet"]["channelTitle"]

            if EXCLUDE_KEYWORDS.search(title):
                continue

            video_id = item.get("id", {}).get("videoId")

            if not video_id:
                continue

            videos.append({
                "video_id": video_id,
                "title": title,
                "channel": channel
            })

        request = youtube.search().list_next(request, response)
        if not request:
            break

    return videos


def get_video_stats(video_ids):
    stats = {}

    for i in range(0, len(video_ids), 50):
        response = youtube.videos().list(
            part="statistics",
            id=",".join(video_ids[i:i+50])
        ).execute()

        for item in response["items"]:
            stats[item["id"]] = int(
                item["statistics"].get("viewCount", 0)
            )

    return stats


def normalize_title(title, artist):
    title = title.lower()
    title = title.replace(artist.lower(), "")
    title = re.sub(r"\(.*?\)|\[.*?\]", "", title)
    title = re.sub(r"official.*", "", title)
    return title.strip()


def get_top_tracks(artist, limit=100):
    videos = search_videos(artist)
    video_ids = [v["video_id"] for v in videos]

    stats = get_video_stats(video_ids)

    track_views = defaultdict(int)

    for v in videos:
        if v["video_id"] not in stats:
            continue

        normalized = normalize_title(v["title"], artist)
        track_views[normalized] += stats[v["video_id"]]

    ranked = sorted(
        track_views.items(),
        key=lambda x: x[1],
        reverse=True
    )

    return ranked[:limit]


if __name__ == "__main__":
    artist_name = "Kishor kumar"
    top_tracks = get_top_tracks(artist_name)

    for i, (track, views) in enumerate(top_tracks, 1):
        print(f"{i:03d}. {track} — {views:,} views")
