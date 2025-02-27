import json
import time
import cv2
import pandas as pd
import random
import requests
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

douyin_user_url = "https://www.douyin.com/user/MS4wLjABAAAALkD0tV6Gzec7ZIDlNOmYN7QzI0cbM99GTW85f9tRsb2XO8daOKZZMxE8xE4mROTM?from_tab_name=main"

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

def get_slider_distance(iframe):
    """Downloads CAPTCHA images, rescales them, and detects the puzzle slot using SSIM for improved accuracy."""
    bg_image_url = iframe.locator("#captcha_verify_image").get_attribute("src")
    piece_image_url = iframe.locator(".captcha-verify-image-slide").get_attribute("src")
    
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

def solve_captcha(page):
    """Handles and solves the CAPTCHA inside an iframe."""
    try:
        print("[INFO] Checking for CAPTCHA iframe...")
        
        # Wait for iframe to load
        iframe = page.wait_for_selector("iframe[src*='verifycenter']", timeout=15000)
        if not iframe:
            print("❌ CAPTCHA iframe not found!")
            return
        
        print("[INFO] CAPTCHA iframe detected. Switching context...")
        
        # Switch to the iframe
        captcha_frame = iframe.content_frame()
        if not captcha_frame:
            print("❌ Failed to retrieve iframe content!")
            return
        
        # Wait for slider button inside iframe
        slider = captcha_frame.locator(".captcha-slider-btn")
        captcha_frame.wait_for_selector(".captcha-slider-btn", state="visible", timeout=10000)
        
        if not slider.is_visible():
            print("❌ Slider button not found!")
            return
        
        print("✅ Slider button detected!")
        
        # Detect the correct distance to move the slider
        distance = get_slider_distance(captcha_frame)

        print(f"✅ Detected distance is {distance}")
        
        if distance is None:
            print("❌ Failed to detect the target slot. Exiting...")
            return
        
        print(f"[INFO] Calculated slider movement distance: {distance} pixels")
        
        # Perform slider dragging inside the iframe
        print("[INFO] Moving slider...")
        box = slider.bounding_box()
        if not box:
            print("❌ Could not retrieve slider position!")
            return
        
        start_x, start_y = box["x"] + box["width"] / 2, box["y"] + box["height"] / 2
        target_x = start_x + distance
        
        print(f"[DEBUG] Moving slider from ({start_x}, {start_y}) to ({target_x}, {start_y})")
        
        page.mouse.move(start_x, start_y)
        page.mouse.down()
        
        # Move the slider in small steps to simulate human behavior
        for step in range(10):
            step_x = start_x + ((target_x - start_x) * (step + 1) / 10)
            page.mouse.move(step_x, start_y)
            print(f"[DEBUG] Slider moved to: ({step_x}, {start_y})")
            time.sleep(random.uniform(0.05, 0.15))
        
        page.mouse.move(target_x, start_y)
        page.mouse.up()
        
        print("✅ CAPTCHA Solved!")
    
    except Exception as e:
        print(f"❌ CAPTCHA solving failed: {e}")

def get_clean_html(page):
    try:
        print("[INFO] Waiting for page to fully render...")
        
        # Wait for the specific div element with class 'C1cxu0Vq' to appear
        page.wait_for_selector("div.C1cxu0Vq", timeout=60000)
        page.wait_for_selector("ul.q438d7I8", timeout=60000)
        
        rendered_html = page.content()
        
        # Use BeautifulSoup to remove script and style tags
        soup = BeautifulSoup(rendered_html, "html.parser")
        for script in soup(["script", "style"]):
            script.decompose()
        
        clean_html = soup.prettify()
        
        # Save cleaned page content to a file
        with open("douyin_cleaned.html", "w", encoding="utf-8") as file:
            file.write(clean_html)
        print("✅ Cleaned page content saved to douyin_cleaned.html")
    except Exception as e:
        print(f"❌ Error fetching Douyin cleaned page data: {e}")

def scrape_douyin_profile():
    """Scrapes Douyin profile details."""
    print("[INFO] Starting profile scrape...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=500, args=["--disable-blink-features=AutomationControlled"])
        page = browser.new_page()
        page.set_default_timeout(10000)
        page.set_default_navigation_timeout(30000)
        print(f"[INFO] Navigating to {douyin_user_url}")
        page.goto(douyin_user_url, timeout=60000)
        try:
            if "captcha" in page.content():
                print("⚠️ CAPTCHA Detected! Solving...")
                solve_captcha(page)
            page.wait_for_selector("h1", state="attached", timeout=30000)
            username = page.locator("h1").inner_text()
            print(f"✅ Username: {username}")
            get_clean_html(page)
        except Exception as e:
            print(f"❌ Failed to extract profile: {e}")

        finally:
            browser.close()

# ✅ Run Scraper
print("[INFO] Running profile scraper...")
profile_data = scrape_douyin_profile()
print("[INFO] Scraping completed!")