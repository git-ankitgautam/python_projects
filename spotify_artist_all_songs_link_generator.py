import requests
import base64
import time
import random
import json
import re
from typing import List, Tuple, Optional
from datetime import datetime, timedelta
import threading
from collections import deque

# Replace these with your actual Spotify API credentials
client_id = '3643649e81ab4729b00c37b2e3c0e223'
client_secret = '702e1935f8aa488cbb7643f2e419a13a'

# Ultra-conservative rate limiting configuration
MAX_REQUESTS_PER_30_SECONDS = 15  # Very conservative limit (well under any documented limit)
REQUEST_QUEUE_SIZE = MAX_REQUESTS_PER_30_SECONDS
MINIMUM_DELAY_BETWEEN_REQUESTS = 2.5  # 2.5 seconds between requests
RETRY_ATTEMPTS = 10
BASE_BACKOFF_DELAY = 5  # Starting backoff delay in seconds
MAX_BACKOFF_DELAY = 300  # Maximum backoff delay

# Request tracking for rate limiting
request_times = deque(maxlen=REQUEST_QUEUE_SIZE)
request_lock = threading.Lock()

# Global variable for remix filtering
include_remixes = True

def log_with_timestamp(message: str):
    """Log messages with timestamp for tracking"""
    timestamp = datetime.now().strftime("%HH:%MM:%SS")
    print(f"[{timestamp}] {message}")

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

def filter_tracks(tracks: List[Tuple[str, str]]) -> List[Tuple[str, str]]:
    """Filter out remixes and versions if user chose not to include them"""
    if include_remixes:
        return tracks
    
    filtered_tracks = []
    removed_count = 0
    
    for name, url in tracks:
        if is_remix_or_version(name):
            removed_count += 1
            log_with_timestamp(f"  Filtered out: {name}")
        else:
            filtered_tracks.append((name, url))
    
    if removed_count > 0:
        log_with_timestamp(f"📝 Filtered out {removed_count} remixes/versions")
    
    return filtered_tracks

def calculate_delay_needed() -> float:
    """Calculate how long to wait before making next request"""
    with request_lock:
        current_time = time.time()
        
        # Remove requests older than 30 seconds
        while request_times and current_time - request_times[0] > 30:
            request_times.popleft()
        
        # If we're at the limit, wait until the oldest request is 30+ seconds old
        if len(request_times) >= MAX_REQUESTS_PER_30_SECONDS:
            oldest_request = request_times[0]
            wait_time = 30 - (current_time - oldest_request) + 1  # +1 for safety buffer
            return max(wait_time, MINIMUM_DELAY_BETWEEN_REQUESTS)
        
        return MINIMUM_DELAY_BETWEEN_REQUESTS

def record_request():
    """Record that a request was made"""
    with request_lock:
        request_times.append(time.time())

def safe_delay():
    """Implement safe delay before making requests"""
    delay = calculate_delay_needed()
    if delay > MINIMUM_DELAY_BETWEEN_REQUESTS:
        log_with_timestamp(f"Rate limiting: waiting {delay:.1f} seconds before next request")
    time.sleep(delay)

def exponential_backoff_delay(attempt: int, base_delay: float = BASE_BACKOFF_DELAY) -> float:
    """Calculate exponential backoff delay with jitter and cap"""
    delay = base_delay * (2 ** attempt) + random.uniform(0, 2)
    return min(delay, MAX_BACKOFF_DELAY)

def safe_request(url: str, headers: dict, params: dict = {}, timeout: int = 15) -> Optional[requests.Response]:
    """Make a safe request with comprehensive error handling and rate limiting"""
    for attempt in range(RETRY_ATTEMPTS):
        try:
            # Implement our custom rate limiting
            safe_delay()
            
            # Make the request
            response = requests.get(url, headers=headers, params=params, timeout=timeout)
            record_request()
            
            if response.status_code == 200:
                return response
            elif response.status_code == 429:  # Rate limited by Spotify
                retry_after = int(response.headers.get("Retry-After", 60))
                jitter = random.uniform(1, 5)  # Add jitter to avoid thundering herd
                wait_time = retry_after + jitter
                log_with_timestamp(f"Spotify rate limit hit. Waiting {wait_time:.1f} seconds...")
                time.sleep(wait_time)
            elif response.status_code == 401:  # Token expired
                log_with_timestamp("Token expired. Please get a new token.")
                return None
            elif response.status_code in [500, 502, 503, 504]:  # Server errors
                log_with_timestamp(f"Server error {response.status_code}. Retrying...")
            else:
                log_with_timestamp(f"Request failed with status {response.status_code}: {response.text}")
                
        except requests.exceptions.Timeout:
            log_with_timestamp(f"Request timeout on attempt {attempt + 1}")
        except requests.exceptions.ConnectionError:
            log_with_timestamp(f"Connection error on attempt {attempt + 1}")
        except requests.exceptions.RequestException as e:
            log_with_timestamp(f"Request exception on attempt {attempt + 1}: {e}")
            
        # Exponential backoff between retries
        if attempt < RETRY_ATTEMPTS - 1:
            delay = exponential_backoff_delay(attempt)
            log_with_timestamp(f"Retrying in {delay:.1f} seconds...")
            time.sleep(delay)
    
    log_with_timestamp("All retry attempts failed")
    return None

def get_access_token() -> Optional[str]:
    """Get Spotify access token with retry logic"""
    auth_str = f"{client_id}:{client_secret}"
    b64_auth_str = base64.b64encode(auth_str.encode()).decode()

    headers = {
        "Authorization": f"Basic {b64_auth_str}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}
    
    for attempt in range(RETRY_ATTEMPTS):
        try:
            log_with_timestamp("Requesting access token...")
            response = requests.post(
                "https://accounts.spotify.com/api/token", 
                headers=headers, 
                data=data,
                timeout=15
            )
            
            if response.status_code == 200:
                token = response.json().get("access_token")
                log_with_timestamp("Access token obtained successfully")
                return token
            elif response.status_code == 429:
                retry_after = int(response.headers.get("Retry-After", 60))
                log_with_timestamp(f"Token request rate limited. Waiting {retry_after} seconds...")
                time.sleep(retry_after + 1)
            else:
                log_with_timestamp(f"Token request failed with status {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            log_with_timestamp(f"Token request attempt {attempt + 1} failed: {e}")
            
        if attempt < RETRY_ATTEMPTS - 1:
            delay = exponential_backoff_delay(attempt)
            log_with_timestamp(f"Retrying token request in {delay:.1f} seconds...")
            time.sleep(delay)
    
    return None

def search_artist(artist_name: str, token: str) -> Optional[str]:
    """Search for artist and return artist ID"""
    headers = {"Authorization": f"Bearer {token}"}
    params = {"q": artist_name, "type": "artist", "limit": 1}
    
    log_with_timestamp(f"Searching for artist: {artist_name}")
    response = safe_request("https://api.spotify.com/v1/search", headers, params)
    
    if response:
        artists = response.json()["artists"]["items"]
        if not artists:
            log_with_timestamp(f"No artist found for '{artist_name}'")
            return None
        artist_id = artists[0]["id"]
        log_with_timestamp(f"Found artist ID: {artist_id}")
        return artist_id
    
    return None

def get_artist_albums(artist_id: str, token: str) -> List[str]:
    """Get all album IDs for an artist with safe pagination"""
    albums = []
    url = f"https://api.spotify.com/v1/artists/{artist_id}/albums"
    params = {"limit": 50, "include_groups": "album,single"}
    headers = {"Authorization": f"Bearer {token}"}
    page = 1

    log_with_timestamp("Fetching artist albums...")
    
    while url:
        log_with_timestamp(f"Fetching albums page {page}...")
        response = safe_request(url, headers, params)
        
        if response:
            data = response.json()
            page_albums = [album["id"] for album in data["items"]]
            albums.extend(page_albums)
            url = data.get("next")  # Next page URL
            params = {}  # Clear params for subsequent requests
            
            log_with_timestamp(f"Page {page}: Found {len(page_albums)} albums")
            page += 1
            
            # Extra safety delay between paginated requests
            if url:
                time.sleep(1)
        else:
            log_with_timestamp("Failed to fetch albums page, stopping pagination")
            break

    log_with_timestamp(f"Total albums found: {len(albums)}")
    return albums

def get_album_tracks(album_id: str, token: str, album_index: int, total_albums: int) -> List[Tuple[str, str]]:
    """Get all tracks from an album with safe pagination"""
    tracks = []
    url = f"https://api.spotify.com/v1/albums/{album_id}/tracks"
    params = {"limit": 50}
    headers = {"Authorization": f"Bearer {token}"}
    page = 1

    log_with_timestamp(f"Processing album {album_index}/{total_albums}...")
    
    while url:
        response = safe_request(url, headers, params)
        
        if response:
            data = response.json()
            page_tracks = [
                (track["name"], track["external_urls"]["spotify"]) 
                for track in data["items"]
            ]
            tracks.extend(page_tracks)
            url = data.get("next")
            params = {}  # Clear params for subsequent requests
            
            if len(page_tracks) > 0:
                log_with_timestamp(f"  Found {len(page_tracks)} tracks on page {page}")
            page += 1
            
            # Extra safety delay between paginated requests
            if url:
                time.sleep(1)
        else:
            log_with_timestamp(f"  Failed to fetch tracks from album {album_index}")
            break

    return tracks

def save_progress(tracks: List[Tuple[str, str]], artist_name: str, album_index: int):
    """Save progress periodically to avoid losing data"""
    safe_filename = "".join(c for c in artist_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
    progress_filename = f"{safe_filename}_progress_{album_index}.json"
    
    try:
        progress_data = {
            "artist_name": artist_name,
            "processed_albums": album_index,
            "tracks_found": len(tracks),
            "timestamp": datetime.now().isoformat(),
            "include_remixes": include_remixes,
            "tracks": [{"name": name, "url": url} for name, url in tracks]
        }
        
        with open(progress_filename, "w", encoding="utf-8") as f:
            json.dump(progress_data, f, indent=2, ensure_ascii=False)
            
        log_with_timestamp(f"Progress saved to {progress_filename}")
    except IOError as e:
        log_with_timestamp(f"Failed to save progress: {e}")

def write_tracks_to_file(tracks: List[Tuple[str, str]], artist_name: str):
    """Write final tracks to file with comprehensive metadata and improved formatting"""
    safe_filename = "".join(c for c in artist_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
    remix_suffix = "_WITH_REMIXES" if include_remixes else "_NO_REMIXES"
    filename = f"{safe_filename}_ALL_TRACKS{remix_suffix}.txt"
    json_filename = f"{safe_filename}_ALL_TRACKS{remix_suffix}.json"
    csv_filename = f"{safe_filename}_ALL_TRACKS{remix_suffix}.csv"
    
    try:
        # Write text file with improved formatting
        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"🎵 ALL TRACKS FOR: {artist_name.upper()}\n")
            f.write(f"📊 Total tracks found: {len(tracks)}\n")
            f.write(f"🎛️  Remixes included: {'Yes' if include_remixes else 'No'}\n")
            f.write(f"📅 Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 80 + "\n\n")
            
            # Improved format: Song name and URL on same line for easier reading
            for i, (name, url) in enumerate(tracks, 1):
                f.write(f"{i:4d}. {name} | {url}\n")
        
        # Write CSV file for easy importing into spreadsheets
        with open(csv_filename, "w", encoding="utf-8", newline='') as f:
            f.write("Index,Song Name,Spotify URL,Is Remix/Version\n")
            for i, (name, url) in enumerate(tracks, 1):
                # Clean song name for CSV (escape quotes)
                clean_name = name.replace('"', '""')
                is_remix = "Yes" if is_remix_or_version(name) else "No"
                f.write(f'{i},"{clean_name}",{url},{is_remix}\n')
        
        # Write JSON file for programmatic use
        json_data = {
            "artist_name": artist_name,
            "total_tracks": len(tracks),
            "include_remixes": include_remixes,
            "generated_timestamp": datetime.now().isoformat(),
            "tracks": [
                {
                    "index": i, 
                    "name": name, 
                    "spotify_url": url,
                    "is_remix_version": is_remix_or_version(name)
                } 
                for i, (name, url) in enumerate(tracks, 1)
            ]
        }
        
        with open(json_filename, "w", encoding="utf-8") as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)
        
        log_with_timestamp(f"✅ SUCCESS: {len(tracks)} tracks saved to:")
        log_with_timestamp(f"  📄 Text file: {filename}")
        log_with_timestamp(f"  📊 CSV file: {csv_filename}")
        log_with_timestamp(f"  📋 JSON file: {json_filename}")
        
        # Display a sample of the output for verification
        log_with_timestamp("\n🎵 SAMPLE OUTPUT (first 5 tracks):")
        for i, (name, url) in enumerate(tracks[:5], 1):
            remix_indicator = " 🎛️" if is_remix_or_version(name) else ""
            log_with_timestamp(f"   {i:2d}. {name}{remix_indicator} | {url}")
        if len(tracks) > 5:
            log_with_timestamp(f"   ... and {len(tracks) - 5} more tracks")
        
    except IOError as e:
        log_with_timestamp(f"❌ Error writing files: {e}")

def write_top100_tracks(tracks, artist_name):
    safe_filename = "".join(c for c in artist_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
    filename = f"{safe_filename}_TOP100_TRACKS.txt"
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"🎵 TOP 100 TRACKS FOR: {artist_name.upper()}\n")
            f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 60 + "\n\n")
            for i, (name, url) in enumerate(tracks[:100], 1):
                f.write(f"{i:3d}. {name} | {url}\n")
        log_with_timestamp(f"✅ Top 100 tracks saved to {filename}")
    except IOError as e:
        log_with_timestamp(f"❌ Error writing top 100 file: {e}")


def estimate_runtime(num_albums: int) -> str:
    """Estimate total runtime based on current settings"""
    # Conservative estimate: 2-3 requests per album + delays
    estimated_requests = num_albums * 2.5
    estimated_time_seconds = estimated_requests * MINIMUM_DELAY_BETWEEN_REQUESTS
    estimated_time_minutes = estimated_time_seconds / 60
    
    return f"{estimated_time_minutes:.1f} minutes ({estimated_time_seconds/3600:.1f} hours)"

def get_user_preferences():
    """Get user preferences for remix inclusion"""
    global include_remixes
    
    print("\n🎛️  REMIX & VERSION FILTERING OPTIONS:")
    print("   Remixes include: remixes, acoustic versions, live versions, radio edits,")
    print("   extended versions, club mixes, featuring versions, instrumentals, etc.")
    print()
    
    while True:
        choice = input("Include remixes and alternate versions? (y/N): ").strip().lower()
        if choice in ['y', 'yes']:
            include_remixes = True
            log_with_timestamp("🎛️  Will include all remixes and versions")
            break
        elif choice in ['n', 'no', '']:
            include_remixes = False
            log_with_timestamp("🎛️  Will filter out remixes and versions (original tracks only)")
            break
        else:
            print("Please enter 'y' for yes or 'n' for no.")

def main():
    log_with_timestamp("🎵 Starting Ultra-Safe Spotify Track Fetcher")
    log_with_timestamp(f"Rate limiting: Max {MAX_REQUESTS_PER_30_SECONDS} requests per 30 seconds")
    log_with_timestamp(f"Minimum delay: {MINIMUM_DELAY_BETWEEN_REQUESTS} seconds between requests")
    
    artist_name = input("Enter artist name: ").strip()
    if not artist_name:
        log_with_timestamp("❌ Artist name cannot be empty.")
        return
    
    # Get user preferences
    get_user_preferences()
    
    resp = input("Do you want to generate a Top 100 list? (y/N): ").strip().lower()
    generate_top100 = resp in ("y", "yes")
    if generate_top100:
        # prepare an empty list to hold the current Top 100
        top100_tracks: List[Tuple[str,str]] = []

    # Get access token
    log_with_timestamp("🔑 Getting access token...")
    token = get_access_token()
    if not token:
        log_with_timestamp("❌ Failed to get access token. Please check your credentials.")
        return
    
    try:
        # Search for artist
        artist_id = search_artist(artist_name, token)
        if not artist_id:
            log_with_timestamp("❌ Artist not found or search failed.")
            return
        
        # Get albums
        album_ids = get_artist_albums(artist_id, token)
        if not album_ids:
            log_with_timestamp("❌ No albums found for this artist.")
            return
        
        estimated_runtime = estimate_runtime(len(album_ids))
        log_with_timestamp(f"📊 Found {len(album_ids)} albums")
        log_with_timestamp(f"⏱️  Estimated runtime: {estimated_runtime}")
        
        # Confirm before proceeding
        confirm = input(f"\nProceed with fetching tracks from {len(album_ids)} albums? (y/N): ").strip().lower()
        if confirm != 'y':
            log_with_timestamp("Operation cancelled by user.")
            return
        
        # Fetch tracks from all albums
        log_with_timestamp("🎵 Starting track collection...")
        all_tracks = []
        
        for i, album_id in enumerate(album_ids, 1):
            tracks = get_album_tracks(album_id, token, i, len(album_ids))
            all_tracks.extend(tracks)
            
            # Save progress every 10 albums
            if i % 10 == 0 or i == len(album_ids):
                save_progress(all_tracks, artist_name, i)
                log_with_timestamp(f"📈 Progress: {i}/{len(album_ids)} albums processed, {len(all_tracks)} tracks found so far")
        
        # Apply remix filtering if needed
        if not include_remixes:
            log_with_timestamp("🎛️  Applying remix/version filtering...")
            filtered_tracks = filter_tracks(all_tracks)
        else:
            filtered_tracks = all_tracks
        
        # Remove duplicates while preserving order
        log_with_timestamp("🔄 Removing duplicate tracks...")
        seen = set()
        unique_tracks = []
        for name, url in filtered_tracks:
            if url not in seen:
                seen.add(url)
                unique_tracks.append((name, url))
        
        duplicates_removed = len(filtered_tracks) - len(unique_tracks)
        if duplicates_removed > 0:
            log_with_timestamp(f"📝 Removed {duplicates_removed} duplicate tracks")
        
        # --- Place this after duplicate removal and BEFORE writing final output files

        # Handle top100 flag or user prompt
        generate_top100 = False
        resp = input("Generate top 100 tracks list? (y/N): ").strip().lower()
        if resp in ["y", "yes"]:
            generate_top100 = True

        if generate_top100:
            write_top100_tracks(unique_tracks, artist_name)


        # Write final results
        write_tracks_to_file(unique_tracks, artist_name)
        
        # Final summary
        log_with_timestamp("=" * 60)
        log_with_timestamp("🎉 COMPLETION SUMMARY:")
        log_with_timestamp(f"   Artist: {artist_name}")
        log_with_timestamp(f"   Albums processed: {len(album_ids)}")
        log_with_timestamp(f"   Total tracks found: {len(all_tracks)}")
        log_with_timestamp(f"   After remix filtering: {len(filtered_tracks)}")
        log_with_timestamp(f"   Final unique tracks: {len(unique_tracks)}")
        log_with_timestamp(f"   Remixes included: {'Yes' if include_remixes else 'No'}")
        log_with_timestamp(f"   Duplicates removed: {duplicates_removed}")
        log_with_timestamp("=" * 60)
        
    except KeyboardInterrupt:
        log_with_timestamp("\n⏹️  Operation cancelled by user.")
        log_with_timestamp("💾 Progress has been saved in progress files.")
    except Exception as e:
        log_with_timestamp(f"❌ An unexpected error occurred: {e}")
        log_with_timestamp("💾 Check progress files for partial results.")

if __name__ == "__main__":
    main()
