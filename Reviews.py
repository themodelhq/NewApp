import requests
from bs4 import BeautifulSoup
import csv
import time

# URL of the Jumia page to scrape
BASE_URL = "https://www.jumia.com.ng/tools-home-improvement"

# Headers to mimic a browser visit
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}

# Maximum number of pages to scrape
MAX_PAGES = 10

def get_html(url):
    """Fetch HTML content from a URL."""
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return response.text
    else:
        print(f"Failed to retrieve {url}: {response.status_code}")
        return None

def parse_review_comments(product_url):
    """Extract all review comments from the product page, including paginated reviews."""
    comments = []
    while product_url:
        html = get_html(product_url)
        if not html:
            break

        soup = BeautifulSoup(html, "html.parser")

        # Extract comments on the current page
        for comment in soup.select("div.-pbm._erv div.rev__cnt-txt"):
            comments.append(comment.text.strip())

        # Check for a "next" button to navigate to the next page of reviews
        next_page = soup.select_one("a.pg._act._n")
        product_url = "https://www.jumia.com.ng" + next_page['href'] if next_page else None

        # Pause to avoid overloading the server
        time.sleep(2)

    return comments

def parse_products(html):
    """Extract product information from a page."""
    soup = BeautifulSoup(html, "html.parser")
    products = []
    
    # Find all product blocks
    for product in soup.select("article.prd._fb.col.c-prd"):
        name = product.select_one("h3.name").text.strip() if product.select_one("h3.name") else "N/A"
        price = product.select_one("div.prc").text.strip() if product.select_one("div.prc") else "N/A"
        rating = product.select_one("div.rev div.stars._s").get("data-stars") if product.select_one("div.rev div.stars._s") else "N/A"
        reviews = product.select_one("div.rev span").text.strip() if product.select_one("div.rev span") else "0 reviews"
        product_url = product.select_one("a.core")['href'] if product.select_one("a.core") else None
        sku = product.get("data-sku", "N/A")

        if product_url:
            product_url = "https://www.jumia.com.ng" + product_url
            review_comments = parse_review_comments(product_url)
        else:
            review_comments = []

        products.append({
            "name": name,
            "price": price,
            "rating": rating,
            "reviews": reviews,
            "review_comments": review_comments,
            "sku": sku,
        })
    
    return products

def parse_all_pages(base_url):
    """Iterate through all paginated product pages and scrape product data."""
    all_products = []
    next_page_url = base_url
    page_count = 0

    while next_page_url and page_count < MAX_PAGES:
        print(f"Scraping page: {next_page_url}")
        html = get_html(next_page_url)
        if not html:
            break

        products = parse_products(html)
        all_products.extend(products)

        # Check for a "next" button to navigate to the next page of products
        soup = BeautifulSoup(html, "html.parser")
        next_page = soup.select_one("a.pg._act._n")
        next_page_url = "https://www.jumia.com.ng" + next_page['href'] if next_page else None

        # Increment page count
        page_count += 1

        # Pause to avoid overloading the server
        time.sleep(2)

    return all_products

def save_to_csv(data, filename="jumia_reviews.csv"):
    """Save extracted data to a CSV file."""
    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["name", "price", "rating", "reviews", "review_comments", "sku"])
        writer.writeheader()
        for product in data:
            # Flatten review comments into a single string
            product["review_comments"] = " | ".join(product["review_comments"])
            writer.writerow(product)

    print(f"Data saved to {filename}")

def main():
    """Main function to orchestrate scraping."""
    print("Starting scraper...")

    all_products = parse_all_pages(BASE_URL)
    if all_products:
        save_to_csv(all_products)
    else:
        print("No products found.")

if __name__ == "__main__":
    main()
