import requests
from bs4 import BeautifulSoup
import csv
import time

def scrape_jumia_products(url, max_pages=50):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    }
    product_data = []

    for page in range(1, max_pages + 1):
        print(f"Scraping page {page}...")
        response = requests.get(f"{url}?page={page}", headers=headers)

        if response.status_code != 200:
            print(f"Failed to fetch page {page}")
            continue

        soup = BeautifulSoup(response.content, "html.parser")
        products = soup.find_all("article", class_="prd _fb col c-prd")

        for product in products:
            try:
                name = product.find("h3", class_="name").text.strip()
                image_tag = product.find("img")
                anchor = product.find("a")
                image_url = image_tag.get("data-src") or image_tag.get("src")
                sku = anchor.get("data-ga4-item_id")
                price = product.find("div", class_="prc").text.strip() if product.find("div", class_="prc") else "N/A"
                original_price = product.find("div", class_="old").text.strip() if product.find("div", class_="old") else "N/A"
                discount = product.find("div", class_="bdg _dsct").text.strip() if product.find("div", class_="bdg _dsct") else "N/A"
                stars = product.find("div", class_="stars _s").get("style") if product.find("div", class_="stars _s") else "N/A"
                ratings = product.find("div", class_="rev").text.strip() if product.find("div", class_="rev") else "N/A"
                review_url = f"https://www.jumia.com.ng/catalog/productratingsreviews/sku/{sku}/" if sku else None
                review_comments = fetch_review_comments(review_url) if review_url else []

                product_data.append({
                    "SKU": sku,
                    "Product Name": name,
                    "Image URL": image_url,
                    "Price": price,
                    "Original Price": original_price,
                    "Discount": discount,
                    "Stars": stars,
                    "Ratings": ratings,
                    "Review Comments": " | ".join(review_comments)
                })
            except AttributeError:
                continue

    return product_data


def extract_review_details(html):
    soup = BeautifulSoup(html, "html.parser")
    rating = soup.select_one("div.stars").get_text(strip=True) if soup.select_one("div.stars") else ""
    title = soup.select_one("h3").get_text(strip=True) if soup.select_one("h3") else ""
    review_text = soup.select_one("p").get_text(strip=True) if soup.select_one("p") else ""
    date = soup.select_one("div.-pvs > span").get_text(strip=True) if soup.select_one("div.-pvs > span") else ""
    reviewer = soup.select_one("div.-pvs > span + span").get_text(strip=True) if soup.select_one("div.-pvs > span + span") else ""
    verified_purchase = "Verified Purchase" if soup.select_one("svg[viewBox='0 0 24 24']") else ""

    return f"Rating: {rating} | Title: {title} | Review: {review_text} | Date: {date} | Reviewer: {reviewer} | {verified_purchase}"


def fetch_review_comments(review_url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    }
    comments = []
    retries = 3  # Retry attempts

    while review_url:
        print(f"Fetching reviews from: {review_url}")
        for attempt in range(retries):
            try:
                response = requests.get(review_url, headers=headers, timeout=10)
                if response.status_code != 200:
                    print(f"Failed to fetch reviews. Status code: {response.status_code}")
                    break

                soup = BeautifulSoup(response.content, "html.parser")
                reviews = soup.find_all("article")
                for review in reviews:
                    review_html = str(review)
                    comments.append(extract_review_details(review_html))

                next_page = soup.select_one("a.pg._act._n")
                review_url = "https://www.jumia.com.ng" + next_page['href'] if next_page else None
                break  # Exit retry loop on success
            except requests.exceptions.ConnectTimeout:
                print(f"Timeout on attempt {attempt + 1}. Retrying...")
                time.sleep(2)
            except requests.exceptions.RequestException as e:
                print(f"Error: {e}")
                break
        else:
            print("Max retries reached. Skipping...")
            break

        time.sleep(2)

    return comments


def save_to_csv(data, filename="jumia_products_detailed.csv"):
    keys = data[0].keys()
    with open(filename, "w", newline="", encoding="utf-8") as output_file:
        dict_writer = csv.DictWriter(output_file, fieldnames=keys)
        dict_writer.writeheader()
        dict_writer.writerows(data)


category_url = "https://www.jumia.com.ng/tools-home-improvement"
data = scrape_jumia_products(category_url, max_pages=50)
if data:
    save_to_csv(data)
    print("Data saved to jumia_products_detailed.csv")
else:
    print("No data found.")
