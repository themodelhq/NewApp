import requests
from bs4 import BeautifulSoup
import json

def extract_attributes_and_classes(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    }

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(f"Failed to fetch the page: {url}")
        return

    soup = BeautifulSoup(response.content, "html.parser")

    elements_data = []

    # Iterate over all elements in the page
    for element in soup.find_all():
        element_info = {
            "tag": element.name,
            "attributes": element.attrs,
            "classes": element.get("class", [])
        }
        elements_data.append(element_info)

    return elements_data

# URL of the product page
product_page_url = "https://www.jumia.com.ng/poco-c61-6.71-3gb-ram-64gb-rom-android-14-black-380046441.html"

# Extract attributes and classes
attributes_and_classes = extract_attributes_and_classes(product_page_url)

# Save the data to a JSON file
if attributes_and_classes:
    with open("product_page_attributes.json", "w", encoding="utf-8") as file:
        json.dump(attributes_and_classes, file, indent=4, ensure_ascii=False)
    print("Attributes and classes saved to product_page_attributes.json")
else:
    print("No data found.")
