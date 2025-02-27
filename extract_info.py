import os
from bs4 import BeautifulSoup
import json

import requests
from playwright.sync_api import sync_playwright
import requests

def get_real_video_url(video_page_url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # Set to True if you don't want to see the browser
        page = browser.new_page()
        
        # Open the Douyin video page
        page.goto(video_page_url, timeout=60000)
        
        # Wait for the video element to load
        page.wait_for_selector("video", timeout=10000)

        # Extract the real video URL from the <video> tag
        video_url = page.evaluate("document.querySelector('video').src")

        print(video_url, "Video url from fun")

        browser.close()
        return "blob:https://www.douyin.com/3eb6f803-1d6c-40ef-befc-766be4015699"

def download_video(video_url, filename="douyin_video.mp4"):
    response = requests.get(video_url, stream=True)
    if response.status_code == 200:
        with open(filename, "wb") as file:
            for chunk in response.iter_content(chunk_size=1024):
                file.write(chunk)
        print(f"Video downloaded successfully as {filename}")
    else:
        print("Failed to download video.")

# Load the HTML file
file_path = "douyin_cleaned.html"
with open(file_path, "r", encoding="utf-8") as file:
    soup = BeautifulSoup(file, "html.parser")

# Extract profile information
profile_name = soup.find("h1", class_="GMEdHsXq").text.strip()  # Update class accordingly
profile_bio = soup.find("span", class_="arnSiSbK").text.strip()  # Update class accordingly

# print(profile_bio)
follower_count = soup.find_all("div", class_="C1cxu0Vq")[1].text.strip()  # Update class accordingly

profile_data = {
    "profile_name": profile_name if profile_name else "N/A",
    "profile_bio": profile_bio if profile_bio else "N/A",
    "follower_count": follower_count if follower_count else "N/A",
}

# # Extract posts
posts = []
post_elements = soup.find_all("li", class_="wqW3g_Kl")[:50]  # Update class accordingly

# Directory to save videos
video_dir = "douyin_videos"
os.makedirs(video_dir, exist_ok=True)

for post in post_elements:
    post_text = post.find("p", class_="H4IE9Xgd")
    post_url = post.find("a", class_="IdxE71f8")
    post_image = post.find("div", class_="oyfanDG1").findChild("img")
    post_video = post.find("video", class_="post-video-class")
    post_likes = post.find("span", class_="BgCg_ebQ")

    video_page_url = f"https://www.douyin.com{post_url['href']}"
    real_video_url = get_real_video_url(video_page_url)

    print(real_video_url, "Video url")

    if real_video_url:
      print(f"Real Video URL: {real_video_url}")
      download_video(real_video_url)
    else:
        print("Failed to find video URL.")

    posts.append({
        "post_text": post_text.text.strip() if post_text else "N/A",
        "post_url": post_url["href"] if post_url else "N/A",
        "post_image": post_image["src"] if post_image else "N/A",
        "post_video": post_video["src"] if post_video else "N/A",
        "likes": post_likes.text.strip() if post_likes else "N/A",
    })

# Final data structure
final_data = {
    "profile": profile_data,
    "posts": posts
}

# Save to JSON file
output_file = "douyin_extracted_data.json"
with open(output_file, "w", encoding="utf-8") as json_file:
    json.dump(final_data, json_file, ensure_ascii=False, indent=4)

print(f"Extracted data saved to {output_file}")
