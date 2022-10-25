import requests
import time
import json
import csv
from bs4 import BeautifulSoup


number_of_products = 0


def getProductInfo(url, category):
    soup = BeautifulSoup(requests.get(url).text, "html.parser")

    attributes = {}
    name = soup.find("div", {"class": "product-title"}).text.replace("\n", "").replace("\t", "")

    for attr in soup.findAll("tr", {"class": "item-row"}):
        vals = attr.findAll("td")
        attributes[vals[0].text.replace("\n", "").replace("\t", "")] = vals[1].text.replace("\n", "").replace("\t", "")

    images = {1: soup.find("img", {"alt": name})["src"]}
    preview_images = soup.findAll("a", {"class": "thumb-image js-init-gallery"})
    img_id = 2

    for preview_image in preview_images:
        images[img_id] = preview_image["data-src-large"]
        img_id += 1

    description = soup.find("span", {"class": "description"}).text.replace("\n", "").replace("\t", "")

    ID = url.split(',')[-2]

    info = {
        "id": ID,
        "name": name,
        "category": category,
        "description": description,
        "attributes": attributes,
        "img": images
    }
    return info


def getAllProducts(led_links, lamp_links):
    products = {}
    base_url = "https://www.leroymerlin.pl"
    for link in led_links:
        products[link.split(',')[-2]] = getProductInfo(base_url + link, "leds")
        if len(products) % 10 == 0:
            time.sleep(5)
    for link in lamp_links:
        products[link.split(',')[-2]] = getProductInfo(base_url + link, "lamps")
        if len(products) % 10 == 0:
            time.sleep(1)

    return products


def getLinks(name):
    global number_of_products
    page = 1
    links = []

    while number_of_products <= 20:  # zmienić na 500
        urls = {
            "leds": f"https://www.leroymerlin.pl/oswietlenie/tasmy-led-profile-zasilacze,a1185,strona-{page}.html",
            "lamps": f"https://www.leroymerlin.pl/oswietlenie/oswietlenie-scienne-i-sufitowe/zyrandole-lampy-wiszace-i-sufitowe,a956,strona-{page}.html"
        }
        soup = BeautifulSoup(requests.get(urls[name]).text, "html.parser")
        links_on_page = [div.find('a')['href'] for div in soup.find_all("div", {"class": "product"})]
        number_of_products += len(links_on_page)
        for link in links_on_page:
            links.append(link)
        page += 1
        if len(soup.find_all("a", {"class": "next disabled"})) != 0:
            break
    return links


if __name__ == "__main__":
    csv_columns = ['ID', 'Name', 'Categories', 'Price', 'Short desc.', 'Long desc', 'Images URL']

    led_links = getLinks('leds')
    lamp_links = getLinks('lamps')

    all_products_info = {"products": getAllProducts(led_links, lamp_links)}

    # all_products_json = json.dumps(all_products_info, ensure_ascii=False)

    # with open("products.json", "w", encoding="utf8") as file:
    #     file.write(all_products_json)

    with open("products.csv", "w", encoding="utf8") as file:
        writer = csv.DictWriter(file, fieldnames=csv_columns, delimiter=';')
        writer.writeheader()
        for data in all_products_info["products"]:
            writer.writerow({
                "ID": all_products_info["products"][data]["id"],
                "Name": all_products_info["products"][data]["name"],
                "Categories": all_products_info["products"][data]["category"],
                "Price": all_products_info["products"][data]["attributes"]["Cena"].split("/")[0].replace(" ", ""),
                "Short desc.": all_products_info["products"][data]["description"],
                "Long desc": str(all_products_info["products"][data]["attributes"]).replace("{", "").replace("}", ""),
                "Images URL": all_products_info["products"][data]["img"]
            })
