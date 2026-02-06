import json
import time
import math
import base64
import requests
import re


# Spotify API credentials
client_id = '3643649e81ab4729b00c37b2e3c0e223'
client_secret = '702e1935f8aa488cbb7643f2e419a13a'
artist_name = "ranbir kapoor"

# Rate‐limit safety: Spotify allows many requests, but we’ll sleep a bit
REQUESTS_PER_SECOND = 10
MIN_DELAY = 1.0 / REQUESTS_PER_SECOND

def get_access_token():
    """Authenticate and obtain Spotify access token."""
    auth = f"{client_id}:{client_secret}"
    b64 = base64.b64encode(auth.encode()).decode()
    print("🔑 Requesting Spotify access token…")
    resp = requests.post(
        "https://accounts.spotify.com/api/token",
        headers={"Authorization": f"Basic {b64}"},
        data={"grant_type": "client_credentials"},
    )
    resp.raise_for_status()
    token = resp.json()['access_token']
    print("✅ Access token obtained")
    return token

def chunked(iterable, size):
    """Yield successive size-sized chunks from iterable."""
    for i in range(0, len(iterable), size):
        yield iterable[i:i+size]

def is_remix_or_version(track_name: str) -> bool:
    """Check if a track is a remix, version, or alternate version"""
    track_lower = track_name.lower()
    remix_keywords = [
        'remix', 'rmx', 'mix', 'version', 'ver', 'edit', 'remaster', 
        'remastered', 'acoustic', 'live', 'demo', 'instrumental', 
        'radio edit', 'extended', 'club', 'dance', 'dub', 'vip',
        'bootleg', 'mashup', 'cover', 'karaoke', 'clean', 'explicit',"lofi","lo-fi"
    ]
    
    # Check for remix keywords
    for keyword in remix_keywords:
        if keyword in track_lower:
            return True
    
    # Check for patterns like "(Artist Remix)" or "[Something Mix]"
    if re.search(r'\([^)]*(?:remix|mix|version|edit)\)', track_lower):
        return True
    if re.search(r'\[[^\]]*(?:remix|mix|version|edit)\]', track_lower):
        return True
    
    # Check for "feat." or "featuring" which might indicate versions
    if 'feat.' in track_lower or 'featuring' in track_lower:
        return True
    
    return False

def fetch_popularity(tracks_json_path, output_top100_path):
    """Load tracks.json, fetch popularity, select and write Top-100."""
    print("⏳ Starting Top-100 popularity fetch…")
    with open(tracks_json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    tracks = data['tracks']
    total_tracks = len(tracks)
    print(f"🔎 Loaded {total_tracks} unique tracks from {tracks_json_path}")

    # Map IDs to metadata
    id_to_meta = {}
    for t in tracks:
        if not is_remix_or_version(t["name"]):
            url = t['spotify_url']
            tid = url.rstrip('/').split('/')[-1]
            id_to_meta[tid] = {'name': t['name'], 'url': url}

    token = get_access_token()
    headers = {"Authorization": f"Bearer {token}"}

    all_info = []
    batches = list(chunked(list(id_to_meta.keys()), 50))
    num_batches = len(batches)
    print(f"📦 Fetching popularity for {total_tracks} tracks in {num_batches} batches…")

    for idx, batch in enumerate(batches, start=1):
        print(f"  • Batch {idx}/{num_batches}: querying {len(batch)} IDs…")
        time.sleep(MIN_DELAY)
        resp = requests.get(
            "https://api.spotify.com/v1/tracks",
            headers=headers,
            params={'ids': ','.join(batch)},
        )
        resp.raise_for_status()
        items = resp.json().get('tracks', [])
        retrieved = sum(1 for item in items if item)
        print(f"    ↪ Retrieved data for {retrieved} tracks")
        for item in items:
            if not item: 
                continue
            tid = item['id']
            all_info.append({
                'name': id_to_meta[tid]['name'],
                'url': id_to_meta[tid]['url'],
                'popularity': item.get('popularity', 0),
            })

    print(f"🏁 Retrieved popularity for {len(all_info)} tracks")
    print("⭐ Sorting and selecting Top 100 by popularity…")
    top100 = sorted(all_info, key=lambda x: x['popularity'], reverse=True)[:100]

    print(f"🎉 Writing Top 100 list to {output_top100_path}")
    with open(output_top100_path, 'w', encoding='utf-8') as f:
        json.dump({'top100': top100}, f, indent=2, ensure_ascii=False)

    print("✅ Done.")

if __name__ == '__main__':
    # Adjust filenames as needed
    
    input_filename = f"{artist_name}_ALL_TRACKS_NO_REMIXES.json"
    output_filename = f'{artist_name} TOP100_BY_POPULARITY.json'
    fetch_popularity(
        input_filename,
        output_filename
    )

    with open(output_filename,"r", encoding="utf-8") as top100_file:
        top100 = json.load(top100_file)
        top100 = top100["top100"]

    with open(f"{artist_name}_spotdl_input.txt","w") as outfile:
        for x in range(100):
            outfile.write(f"{top100[x]["url"]} ")
            if x == 50:
                outfile.write("\n")