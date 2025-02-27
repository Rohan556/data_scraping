from playwright.sync_api import sync_playwright
import requests

def get_real_video_url(video_page_url):
    print("[INFO] Starting Playwright session...")
    with sync_playwright() as p:
        print("[INFO] Launching browser...")
        browser = p.chromium.launch(headless=False)  # Change to True for headless mode
        page = browser.new_page()
        
        # Store the real video URL
        video_url = None

        # Intercept network requests
        def intercept_response(response):
            nonlocal video_url
            print(f"[DEBUG] Captured network request: {response.url}")
            if "video" in response.url and (response.url.endswith(".mp4") or "mime_type=video_mp4" in response.url):
                print(f"[INFO] Found video URL: {response.url}")
                video_url = response.url
        
        # Listen for network responses
        page.on("response", intercept_response)
        
        print(f"[INFO] Navigating to {video_page_url}...")
        page.goto(video_page_url, timeout=60000)

        print("[INFO] Waiting for video element to appear...")
        try:
            page.wait_for_selector("video", timeout=15000)
        except Exception as e:
            print(f"[WARNING] Video element not found: {e}")

        print("[INFO] Waiting for network requests to be captured...")
        page.wait_for_timeout(5000)

        browser.close()
        if video_url:
            print(f"[SUCCESS] Extracted video URL: {video_url}")
        else:
            print("[ERROR] Failed to extract video URL.")
        return video_url

def download_video(video_url, filename="douyin_video.mp4"):
    print(f"[INFO] Downloading video from {video_url}...")
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
        "Referer": "https://www.douyin.com/",
        "Range": "bytes=0-"
    }
    response = requests.get(video_url, headers=headers, stream=True)
    if response.status_code in [200, 206]:
        print("[INFO] Saving video to file...")
        with open(filename, "wb") as file:
            for chunk in response.iter_content(chunk_size=1024):
                file.write(chunk)
        print(f"[SUCCESS] Video downloaded successfully as {filename}")
    else:
        print(f"[ERROR] Failed to download video. Status Code: {response.status_code}")

# Replace with an actual Douyin video page URL
video_page_url = "https://www.douyin.com/video/7448976324254928139"

# Extract real video URL
print("[INFO] Extracting real video URL...")
real_video_url = get_real_video_url(video_page_url)

if real_video_url:
    print(f"[INFO] Real Video URL: {real_video_url}")
    download_video(real_video_url)
else:
    print("[ERROR] Failed to find video URL.")
