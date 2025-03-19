import datetime
from itertools import islice
import json
import os
import cv2
import random
import requests
from bs4 import BeautifulSoup
import asyncio
from playwright.async_api import async_playwright
import requests

douyin_user_urls = [
    "https://www.douyin.com/user/MS4wLjABAAAAkZr9MZoq3qY9T5Cbevdn1OLas2Eo8NgkIW0_otxlUr9Pl7aJz_znpmboZMN7w60f",
    "https://www.douyin.com/user/MS4wLjABAAAA-4cQjvDKEpS661dhHTYBrZ0c-Ou4unYEoBuu-a-KIkk",
    "https://www.douyin.com/user/MS4wLjABAAAAzbL4-sPU0XkZGtlWPNr9mZWlYORbPVpLPN-OCskTHhGgHCDX1A9V9InVT1FSI2PX",
    "https://www.douyin.com/user/MS4wLjABAAAAx0NhX3zP9GBuvdAsQ7QxRi2h1GfQMRFLsmVW0lK8yBf5hkPzv33L3WATcMr3EBlg",
    "https://www.douyin.com/user/MS4wLjABAAAAR5GJYvUMKEI-mWcD8B3Ug4XMSR420gBCXIWENaiXQl_Ga-21tdLTQDDPY_l_hYYX",
    "https://www.douyin.com/user/MS4wLjABAAAA2PYKejbsMi_x5bJqgfl_vk_j3nrlZXe0Z4PoD4tHXVY",
    "https://www.douyin.com/user/MS4wLjABAAAAhS_5gW1swV7P8_eYjX1Z3J5qq2CoGPMoyrnAX_U0DPs",
    "https://www.douyin.com/user/MS4wLjABAAAAFB49tTeczFVYPJiQTnNmLFr7EqyWX2sOSROdnMfAnvbZyRmDanx2sYq3gj-55-_4",
    "https://www.douyin.com/user/MS4wLjABAAAA_qIGDyP7J-2meah2B6voHW7z0mEBx_8RYB_tx5RbGXjPzyytYxWE8WWZq9Eb8Ya5",
    "https://www.douyin.com/user/MS4wLjABAAAAJd-rprT-LvzB-EVYvO0FSnZYlFV2xSvX1vx_x5iZKpsgUUH2fRdyhlofD45ImuhU",
    "https://www.douyin.com/user/MS4wLjABAAAA9Uh6G5zVTaM02js5TRqulYyqQH6KmX5LDKjt0ScCyvc",
    "https://www.douyin.com/user/MS4wLjABAAAAdyAwlemhWajPiP1Dh4sjWiSKPHYXThfVoRSc9l0pCDEFSc2-cn3pZxGLWkEo-yhh",
    "https://www.douyin.com/user/MS4wLjABAAAAp9O4zsJU93H2wj7hifQwAHYjG3gkUqi6cVZH9a3LfpiC7ob2H-JeEWyUtksA-d8k",
    "https://www.douyin.com/user/MS4wLjABAAAAx_NntYOnXyhBe6fBbwSFEkuXxyJrj-hbeCW1iBXG_Jo",
    "https://www.douyin.com/user/MS4wLjABAAAAJeHIV2tXeuo74Ct21XYpZmttfUIovSZZ03VsgHIJeto",
    "https://www.douyin.com/user/MS4wLjABAAAAviysHpXAsNQFROVSxgKDkEewSofA3TaJkjV3_9x-99spKSWHzhp_6ka8JLgO-7x3",
    "https://www.douyin.com/user/MS4wLjABAAAAof16izLLS8h5Ea6jG4b3j-0jwMf-3L-8YV9LRM1b4Ao",
    "https://www.douyin.com/user/MS4wLjABAAAARUooi_RFNDwVxgQNezxIPxGQznj2CwyIGIZvuYwUyB7v_9Njxpdrh84etf4FXe_5",
    "https://www.douyin.com/user/MS4wLjABAAAA3clMCXOg3MJ2ZnhProTi_BbChtbBw6Ljhs0QsrqgcgM",
    "https://www.douyin.com/user/MS4wLjABAAAAz-yZMW-zPDeLl_mbXhVFpnM81oR5d4LijbEuaGO54RA",
    "https://www.douyin.com/user/MS4wLjABAAAA-G06poNGt42dlTr0awsh_5KRi8D50DjHEfR2AeJDlSc7skQodBzD6EBXOo6iA5aF",
    "https://www.douyin.com/user/MS4wLjABAAAA8RJbSiXhaAmGqbN79c2KHQ50B65e-trOV84k0r-sKFCBGJB7-ZunP2Y8AqjtP1lK",
    "https://www.douyin.com/user/MS4wLjABAAAA_h_1WcTvNvRE4WrbM4ihSHcQhpNyTsRnibkIZR4kqd4",
    "https://www.douyin.com/user/MS4wLjABAAAA-N-ownfwaFP7t04LqjTXDbNuW4Enp78j7oLa--2cMPfUXTHu9zDLAGeA9n1RNZAg",
    "https://www.douyin.com/user/MS4wLjABAAAAM7GnvZcWeYeBFaV9flixcEJxCyTxk8_ZhdYnhjRBFjOlhUdtT6GEmP0-_YNaKQX_",
    "https://www.douyin.com/user/MS4wLjABAAAA8jjMOMUhfFET_giqWoq9o96zZo05SzOOo0CfMi3wV-w",
    "https://www.douyin.com/user/MS4wLjABAAAA1OjJEe_A7fPznSHjpf71i2cOOCfxaB-P6M-haWR01-Y-tgK0eppqNEU5hrDfjMYu",
    "https://www.douyin.com/user/MS4wLjABAAAAfmSiEnsfV8gVNfA-IID3ISDU3QxEBszF8hutpvbbvREjOC38R8gQY3BVNX_uRQv0",
    "https://www.douyin.com/user/MS4wLjABAAAAsZzAc44_I3I1zU7cM-3gRKvTz2oO7uH12hyLCB-2P0s",
    "https://www.douyin.com/user/MS4wLjABAAAAntUEvxNRbGcLLWYxaKQmFLAXQMuD4cXSNESrvDZlq9k",
    "https://www.douyin.com/user/MS4wLjABAAAAZd6FoXlXnqvii4ruQH35IYMp-wbNwbnC4M9WEb34RqkXEseNkb_jji3o_-0Nn9-z",
    "https://www.douyin.com/user/MS4wLjABAAAAV62_JpWKYfTTtZbhAprrMoOg0nDWx4J2zEK62-PlByg",
    "https://www.douyin.com/user/MS4wLjABAAAANpUcgaH0AGGeQqOoeKIc7YkYxqVOmiIyxl3iTQpdx9k",
    "https://www.douyin.com/user/MS4wLjABAAAArhtaed7dwsXPNDczwqS9MZVNoKzvj0CnsaxVO1SLS7Y"
]

douyin_user_urls = [url + "?from_tab_name=main" for url in douyin_user_urls]


from skimage.metrics import structural_similarity as ssim

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Referer": "https://www.douyin.com/",
    "Accept-Language": "en-US,en;q=0.9",
}

profile_folder_name = "douyin_profiles"

async def intercept_request(response):
    """Intercepts network responses and saves JSON API response to a file only after both profile & posts data are received."""
    url = response.url

    # ✅ Debugging: Log the intercepted URL
    # print(f"[DEBUG] Intercepted Response: {url}")

    # ✅ Check if the response is from the profile API
    if "aweme/v1/web/user/profile/other" in url:
        print(f"✅ Intercepted Profile API Response: {url}")

        try:
            response_body = await response.json()  # Convert response to JSON

            profile_details = {
                "profile_info": {
                    "username": response_body["user"].get("nickname", "Unknown"),
                    "profile_bio": response_body["user"].get("signature", "N/A"),
                    "follower_count": response_body["user"].get("follower_count", 0)
                }
            }

            username = profile_details["profile_info"]["username"].replace("/", "_").replace("\\", "_")
            file_path = os.path.join(profile_folder_name, f"{username}.json")

            # ✅ Read existing file if it exists
            if os.path.exists(file_path):
                try:
                    with open(file_path, "r", encoding="utf-8") as file:
                        existing_data = json.load(file)
                except json.JSONDecodeError:
                    print(f"⚠️ Warning: Corrupted JSON in {file_path}. Resetting data.")
                    existing_data = {}
            else:
                existing_data = {}

            # ✅ Overwrite "profile_info" (since it's always one profile, not a list)
            existing_data["profile_info"] = profile_details["profile_info"]

            # ✅ Save back to file
            with open(file_path, "w", encoding="utf-8") as file:
                json.dump(existing_data, file, ensure_ascii=False, indent=4)

            print(f"✅ Profile details successfully updated in {file_path}")

        except Exception as e:
            print(f"❌ Failed to process Profile API response: {e}")

    # ✅ Check if the response is from the posts API
    if "/aweme/v1/web/aweme/post/" in url:
        print(f"✅ Intercepted Posts API Response: {url}")

        try:
            response_body = await response.json()  # Extract JSON response
            extracted_data = []

            profile_details = {}

            # Extract posts safely
            for post in response_body.get("aweme_list", []):  # Ensure 'aweme_list' exists
                post_data = {
                    "like_count": post.get("statistics", {}).get("digg_count", 0),
                    "share_count": post.get("statistics", {}).get("share_count", 0),
                    "post_text": post.get("desc", ""),
                    "post_video_url": post.get("video", {}).get("play_addr", {}).get("url_list", [""])[0],
                    "post_image_url": post.get("video", {}).get("cover", {}).get("url_list", [""])[0],
                    "date_posted": datetime.datetime.fromtimestamp(
                        post.get("create_time", 0)
                    ).strftime('%Y-%m-%d %H:%M:%S'),
                    "post_url": post.get("share_info", {}).get("share_url", ""),
                    "nickname": post.get("author", {}).get("nickname", "Unknown")
                }
                extracted_data.append(post_data)

            profile_details["posts"] = extracted_data

            if "posts" in profile_details and len(profile_details["posts"]) > 0:
                # Check if the profile nickname matches the existing post data
                username = profile_details["posts"][0].get("nickname", "")
                print("141", username, profile_details["posts"][0])
                file_path = os.path.join(profile_folder_name, f"{username}.json")

                # ✅ Read the existing file if it exists
                if os.path.exists(file_path):
                    try:
                        with open(file_path, "r", encoding="utf-8") as file:
                            existing_data = json.load(file)
                    except json.JSONDecodeError:
                        print(f"⚠️ Warning: Corrupted JSON in {file_path}. Resetting data.")
                        existing_data = {}
                else:
                    existing_data = {}

                # ✅ Ensure "posts" is a list in the existing data
                if "posts" in existing_data and isinstance(existing_data["posts"], list):
                    existing_data["posts"].extend(profile_details["posts"])
                else:
                    existing_data["posts"] = profile_details["posts"]

                # ✅ Save back to the file
                with open(file_path, "w", encoding="utf-8") as file:
                    json.dump(existing_data, file, ensure_ascii=False, indent=4)

                print(f"✅ Posts successfully updated in {file_path}")
            else:
                profile_details["posts"] = extracted_data


            print(f"✅ {len(extracted_data)} posts extracted.")

        except Exception as e:
            print(f"❌ Failed to process Posts API response: {e}")

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
        iframe = await page.wait_for_selector("iframe[src*='verifycenter']", timeout=15000)
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
        slider = await captcha_frame.wait_for_selector(".captcha-slider-btn", state="visible", timeout=600000)
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
            await asyncio.sleep(random.uniform(0.05, 0.15))

        await page.mouse.move(target_x, start_y)
        await page.mouse.up()

        print("✅ CAPTCHA Solved!")

    except Exception as e:
        print(f"❌ CAPTCHA solving failed: {e}")

async def get_real_video_url(video_page_url):
    """Fetches the real video URL from a Douyin video page."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        await page.goto(video_page_url, timeout=60000)
        
        await page.wait_for_selector("video", timeout=10000)
        video_url = await page.evaluate("document.querySelector('video').src")
        
        await browser.close()
        return video_url if video_url else "N/A"

async def save_html(page, username):
    """Saves the HTML content of the page for debugging and later use."""
    rendered_html = await page.content()

    # Define filename
    filename = f"{username}_profile.html"

    # Save HTML file
    with open(filename, "w", encoding="utf-8") as file:
        file.write(rendered_html)

    print(f"✅ HTML saved as {filename}")

async def extract_profile_data(page, username):
    """Extracts profile and post data from the cleaned HTML and stores all profiles in a single JSON file."""

    print(f"[INFO] Extracting profile data for {username}...")

    await page.wait_for_selector("div.sCnO6dhe", timeout=6000000)
    await page.wait_for_selector("ul.e6wsjNLL", timeout=6000000)
    await page.wait_for_selector("li.niBfRBgX", timeout=6000000)
    await page.wait_for_selector("div.LPv6KBIL", timeout=6000000)
    await asyncio.sleep(5)
    await save_html(page, username)

    rendered_html = await page.content()
    soup = BeautifulSoup(rendered_html, "html.parser")

    try:
        profile_name = soup.find("span", class_="j5WZzJdp").text.strip()
        profile_bio = soup.find("span", class_="arnSiSbK").text.strip()
        follower_count = soup.find_all("div", class_="sCnO6dhe")[1].text.strip()
    except Exception as e:
        print(f"❌ Error extracting profile data: {e}")
        return

    profile_data = {
        "profile_name": profile_name,
        "profile_bio": profile_bio,
        "follower_count": follower_count
    }

    posts = []
    post_elements = soup.find_all("li", class_="niBfRBgX")[:50]  # Limit to first 50 posts

    for post in post_elements:
        post_data = {
            "post_text": post.find("p", class_="Ja95nb2Z").text.strip() if post.find("p", class_="H4IE9Xgd") else "N/A",
            "post_url": post.find("a", class_="IdxE71f8")["href"] if post.find("a", class_="IdxE71f8") else "N/A",
            "post_image": post.find("div", class_="VCzQd6LR").find("img")["src"] if post.find("div",
                                                                                              class_="VCzQd6LR") and post.find(
                "div", class_="oyfanDG1").find("img") else "N/A",
            "likes": post.find("span", class_="b3Dh2ia8").text.strip() if post.find("span",
                                                                                    class_="b3Dh2ia8") else "N/A",
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

# Function to scrape a single profile
async def scrape_douyin_profile(page, douyin_url):
    print(f"[INFO] Scraping profile: {douyin_url}")

    # Enable request interception
    page.on("response", intercept_request)

    try:
        await page.goto(douyin_url, timeout=90000)

        # Check and close login popup if present
        try:
            close_button = await page.query_selector(".douyin-login__close.dy-account-close")
            if close_button:
                await close_button.click()
                print("✅ Closed login popup")
        except Exception:
            pass  # Ignore if not found

        # Check for CAPTCHA and solve if needed
        if "captcha" in await page.content():
            await solve_captcha(page)
            await asyncio.sleep(5)

        await page.wait_for_selector("h1", state="attached", timeout=20000)
        username = await page.locator("h1").inner_text()
        print(f"✅ Username: {username}")

        await extract_profile_data(page, username)
        await page.close()
    except Exception as e:
        print(f"❌ Failed to extract profile: {e}")

# ✅ Run Scraper
print("[INFO] Running profile scraper...")


async def process_batch(browser, batch):
    """Processes a batch of profiles in new tabs within the same browser window."""
    print(f"\n[INFO] Processing batch of {len(batch)} profiles...\n")

    pages = []
    for url in batch:
        page = await browser.new_page()  # Open a new tab
        pages.append(scrape_douyin_profile(page, url))

    await asyncio.gather(*pages)  # Run all profile scrapers in parallel

    # Optional: Add delay between batches
    await asyncio.sleep(random.uniform(5, 10))


def chunked_iterable(iterable, size):
    it = iter(iterable)
    return iter(lambda: tuple(islice(it, size)), ())

async def retry_goto(page, url, max_retries=3, timeout=120000):
    """Retries page.goto up to max_retries times if it fails."""
    for attempt in range(max_retries):
        try:
            print(f"[INFO] Navigating to {url} (Attempt {attempt + 1}/{max_retries})")
            await page.goto(url, timeout=timeout)
            return True
        except Exception as e:
            print(f"⚠️ Page load failed: {e}. Retrying...")
            await asyncio.sleep(random.uniform(3, 7))  # Small delay before retry
    print("❌ Page failed to load after retries. Skipping.")
    return False


async def main():
    chunk_size = 5
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        for chunk in (douyin_user_urls[i:i + chunk_size] for i in range(0, len(douyin_user_urls), chunk_size)):
            # Open first tab and scrape the first profile
            first_page = await context.new_page()
            await scrape_douyin_profile(first_page, chunk[0])

            # Open remaining profiles in new tabs after the first one is done
            pages = [await context.new_page() for _ in chunk[1:]]
            tasks = [scrape_douyin_profile(page, url) for page, url in zip(pages, chunk[1:])]
            await asyncio.gather(*tasks)

            await asyncio.sleep(random.uniform(5, 10))
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())