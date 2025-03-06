import json
import os
import cv2
import pandas as pd
import random
import requests
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import asyncio
from playwright.async_api import async_playwright

douyin_user_urls = [
    "https://www.douyin.com/user/MS4wLjABAAAAHjSVIy-JGVnwh7PrKuFHouXU1O5i5XJkidAbbRVdSioZItx-w5TAxEm9S_NF4kdh?from_tab_name=main",
    "https://www.douyin.com/user/MS4wLjABAAAA64vQ3DNFO4alSxAa8u3NqThgSC4fQ9Rh-csIhrDuCJs",
    "https://www.douyin.com/user/MS4wLjABAAAAgl2aY8rp7cov7E8B36n9i-tLQ6NA6vGNnyrqZlvjJPs",
    "https://www.douyin.com/user/MS4wLjABAAAAxiyBtucx36aFQJgLLvZz42LdEZPAABh-H_JwBa1_HZsDcPyRvcuJDNRd2XH5I458",
    "https://www.douyin.com/user/MS4wLjABAAAA8vUtKe2o8p5acbn6adU0rNbhBn5a-P-t4DXCx6PrP7c"
]


from skimage.metrics import structural_similarity as ssim

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Referer": "https://www.douyin.com/",
    "Accept-Language": "en-US,en;q=0.9",
}

def download_captcha_image(image_url, save_path, target_size):
    """Downloads the CAPTCHA image and resizes it to match the rendered size in the browser."""
    response = requests.get(image_url, stream=True)
    if response.status_code == 200:
        with open(save_path, 'wb') as file:
            for chunk in response.iter_content(1024):
                file.write(chunk)
        print(f"✅ CAPTCHA image saved as {save_path}")
    else:
        print(f"❌ Failed to download CAPTCHA image! HTTP Status: {response.status_code}")
        return
    
    # Resize the image to match the HTML-rendered size
    img = cv2.imread(save_path)
    img_resized = cv2.resize(img, target_size)
    cv2.imwrite(save_path, img_resized)
    print(f"✅ Resized CAPTCHA image to match rendered size: {target_size}")

async def get_slider_distance(iframe):
    """Downloads CAPTCHA images, rescales them, and detects the puzzle slot using SSIM for improved accuracy."""
    
    # ✅ Fix: Await get_attribute() to get the actual URL
    bg_image_url = await iframe.locator("#captcha_verify_image").get_attribute("src")
    piece_image_url = await iframe.locator(".captcha-verify-image-slide").get_attribute("src")
    
    if not bg_image_url or not piece_image_url:
        print("❌ CAPTCHA images not found!")
        return None

    bg_image_path = "captcha_bg.png"
    piece_image_path = "captcha_piece.png"
    
    # Download and resize images to match rendered size
    download_captcha_image(bg_image_url, bg_image_path, (340, 212))
    download_captcha_image(piece_image_url, piece_image_path, (68, 68))
    
    bg = cv2.imread(bg_image_path, cv2.IMREAD_GRAYSCALE)
    piece = cv2.imread(piece_image_path, cv2.IMREAD_GRAYSCALE)
    
    # Apply Canny edge detection
    bg_edges = cv2.Canny(bg, 50, 150)
    piece_edges = cv2.Canny(piece, 50, 150)
    
    # Use SSIM to compare the structural similarity
    best_match = None
    best_score = -1
    piece_h, piece_w = piece_edges.shape
    
    for x in range(bg_edges.shape[1] - piece_w):
        for y in range(bg_edges.shape[0] - piece_h):
            bg_crop = bg_edges[y:y + piece_h, x:x + piece_w]
            score = ssim(bg_crop, piece_edges)
            if score > best_score:
                best_score = score
                best_match = (x, y)
    
    if best_match is None:
        print("❌ Failed to detect puzzle slot!")
        return None
    
    target_x, target_y = best_match
    print(f"✅ Detected puzzle slot at ({target_x}, {target_y})")
    
    # Draw a rectangle on the detected puzzle area
    marked_bg = cv2.cvtColor(bg, cv2.COLOR_GRAY2BGR)
    cv2.rectangle(marked_bg, (target_x, target_y), (target_x + piece_w, target_y + piece_h), (0, 255, 0), 2)
    
    marked_image_path = "captcha_marked.png"
    cv2.imwrite(marked_image_path, marked_bg)
    print(f"✅ Marked image saved as {marked_image_path}")

    print(f"✅ Detected piece width is {piece_w}")
    
    return target_x

async def solve_captcha(page):
    """Handles and solves the CAPTCHA inside an iframe."""
    try:
        print("[INFO] Checking for CAPTCHA iframe...")
        
        # Wait for iframe to load
        iframe = await page.wait_for_selector("iframe[src*='verifycenter']", timeout=0)
        if not iframe:
            print("❌ CAPTCHA iframe not found!")
            return
        
        print("[INFO] CAPTCHA iframe detected. Switching context...")
        
        # ✅ Fix: Await content_frame() to get the correct iframe content
        captcha_frame = await iframe.content_frame()
        if not captcha_frame:
            print("❌ Failed to retrieve iframe content!")
            return
        
        # Wait for slider button inside iframe
        slider = await captcha_frame.wait_for_selector(".captcha-slider-btn", state="visible", timeout=10000)
        if not slider:
            print("❌ Slider button not found!")
            return
        
        print("✅ Slider button detected!")
        
        # Detect the correct distance to move the slider
        distance = await get_slider_distance(captcha_frame)

        print(f"✅ Detected distance is {distance}")
        
        if distance is None:
            print("❌ Failed to detect the target slot. Exiting...")
            return
        
        print(f"[INFO] Calculated slider movement distance: {distance} pixels")
        
        # Perform slider dragging inside the iframe
        print("[INFO] Moving slider...")
        box = await slider.bounding_box()
        if not box:
            print("❌ Could not retrieve slider position!")
            return
        
        start_x, start_y = box["x"] + box["width"] / 2, box["y"] + box["height"] / 2
        target_x = start_x + distance
        
        print(f"[DEBUG] Moving slider from ({start_x}, {start_y}) to ({target_x}, {start_y})")
        
        await page.mouse.move(start_x, start_y)
        await page.mouse.down()
        
        # Move the slider in small steps to simulate human behavior
        for step in range(10):
            step_x = start_x + ((target_x - start_x) * (step + 1) / 10)
            await page.mouse.move(step_x, start_y)
            print(f"[DEBUG] Slider moved to: ({step_x}, {start_y})")
            await asyncio.sleep(random.uniform(0.05, 0.15))
        
        await page.mouse.move(target_x, start_y)
        await page.mouse.up()
        
        print("✅ CAPTCHA Solved!")
    
    except Exception as e:
        print(f"❌ CAPTCHA solving failed: {e}")

async def get_real_video_url(video_page_url):
    """Fetches the real video URL from a Douyin video page."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(video_page_url, timeout=60000)
        
        await page.wait_for_selector("video", timeout=10000)
        video_url = await page.evaluate("document.querySelector('video').src")
        
        await browser.close()
        return video_url if video_url else "N/A"

async def extract_profile_data(page, username):
    """Extracts profile and post data from the cleaned HTML and stores all profiles in a single JSON file."""
    
    print(f"[INFO] Extracting profile data for {username}...")

    await page.wait_for_selector("div.C1cxu0Vq", timeout=6000000)
    await page.wait_for_selector("ul.q438d7I8", timeout=6000000)

    rendered_html = await page.content()
    soup = BeautifulSoup(rendered_html, "html.parser")

    profile_data = {
        "profile_name": soup.find("h1", class_="GMEdHsXq").text.strip() if soup.find("h1", class_="GMEdHsXq") else "N/A",
        "profile_bio": soup.find("span", class_="arnSiSbK").text.strip() if soup.find("span", class_="arnSiSbK") else "N/A",
        "follower_count": soup.find_all("div", class_="C1cxu0Vq")[1].text.strip() if len(soup.find_all("div", class_="C1cxu0Vq")) > 1 else "N/A",
    }

    posts = []
    post_elements = soup.find_all("li", class_="wqW3g_Kl")[:50]  # Limit to first 50 posts

    for post in post_elements:
        post_data = {
            "post_text": post.find("p", class_="H4IE9Xgd").text.strip() if post.find("p", class_="H4IE9Xgd") else "N/A",
            "post_url": post.find("a", class_="IdxE71f8")["href"] if post.find("a", class_="IdxE71f8") else "N/A",
            "post_image": post.find("div", class_="oyfanDG1").find("img")["src"] if post.find("div", class_="oyfanDG1") and post.find("div", class_="oyfanDG1").find("img") else "N/A",
            "likes": post.find("span", class_="BgCg_ebQ").text.strip() if post.find("span", class_="BgCg_ebQ") else "N/A",
        }
        posts.append(post_data)

    final_data = {
        "profile": profile_data,
        "posts": posts
    }

    # ✅ Read existing JSON file if available
    output_file = "douyin_profiles.json"
    if os.path.exists(output_file):
        with open(output_file, "r", encoding="utf-8") as json_file:
            try:
                all_profiles = json.load(json_file)
            except json.JSONDecodeError:
                all_profiles = {}  # Reset if file is corrupted
    else:
        all_profiles = {}

    # ✅ Add new profile data under the username key
    all_profiles[username] = final_data

    # ✅ Save back to file
    with open(output_file, "w", encoding="utf-8") as json_file:
        json.dump(all_profiles, json_file, ensure_ascii=False, indent=4)

    print(f"✅ Profile for {username} added to {output_file}")

# def download_video(video_url, filename):
#     """Downloads a video from a URL."""
#     try:
#         response = requests.get(video_url, stream=True)
#         if response.status_code == 200:
#             with open(filename, "wb") as file:
#                 for chunk in response.iter_content(chunk_size=1024):
#                     file.write(chunk)
#             print(f"✅ Video downloaded successfully as {filename}")
#         else:
#             print(f"❌ Failed to download video. HTTP Status: {response.status_code}")
#     except Exception as e:
#         print(f"❌ Video download failed: {e}")
    
async def scrape_douyin_profile(douyin_url):
    """Scrapes a single Douyin profile."""
    print(f"[INFO] Scraping profile: {douyin_url}")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=["--disable-blink-features=AutomationControlled"])
        page = await browser.new_page()
        await page.goto(douyin_url, timeout=60000)
        
        try:
            if "captcha" in await page.content():
                print("⚠️ CAPTCHA Detected! Solving...")
                await solve_captcha(page)
            
            await page.wait_for_selector("h1", state="attached", timeout=60000000)
            username = await page.locator("h1").inner_text()
            print(f"✅ Username: {username}")
            await extract_profile_data(page, username)
        except Exception as e:
            print(f"❌ Failed to extract profile: {e}")
        finally:
            await browser.close()

# ✅ Run Scraper
print("[INFO] Running profile scraper...")
async def main():
    """Runs multiple profile scrapers in parallel."""
    tasks = [scrape_douyin_profile(url) for url in douyin_user_urls]
    await asyncio.gather(*tasks)  # Run all tasks concurrently

if __name__ == "__main__":
    asyncio.run(main())
print("[INFO] Scraping completed!")