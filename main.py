import requests
import time
import json
from bs4 import BeautifulSoup


number_of_products = 0


def getProductInfo(url):
    soup = BeautifulSoup(requests.get(url).text, "html.parser")

    attributes = {}
    name = soup.find("div", {"class": "product-title"}).text.replace("\n", "").replace("\t", "")
    for attr in soup.findAll("tr", {"class": "item-row"}):
        vals = attr.findAll("td")
        attributes[vals[0].text.replace("\n", "").replace("\t", "")] = vals[1].text.replace("\n", "").replace("\t", "")
    info = {
        "name": name,
        "description": soup.find("span", {"class": "description"}).text.replace("\n", "").replace("\t", ""),
        "img": soup.find("img", {"alt": name})['src'],
        "attributes": attributes
    }

    return info


def getAllProducts(led_links, lamp_links):
    products = {}
    base_url = "https://www.leroymerlin.pl"

    for link in led_links:
        product_id = link.split(',')[-2]
        products[product_id] = getProductInfo(base_url + link)
        if len(products) % 10 == 0:
            time.sleep(5)
    for link in lamp_links:
        product_id = link.split(',')[-2]
        products[product_id] = getProductInfo(base_url + link)
        if len(products) % 10 == 0:
            time.sleep(5)

    return products


def getLinks(name):
    global number_of_products
    page = 1
    links = []

    while True:
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
        if len(soup.find_all("a", {"class": "next disabled"})) != 0 or number_of_products >= 20: #zmienić na 500
            break
    return links


if __name__ == "__main__":

    led_links = getLinks('leds')
    lamp_links = getLinks('lamps')

    all_products_info = {"products": getAllProducts(led_links, lamp_links)}

    product_info_json = json.dumps(all_products_info, ensure_ascii=False)

    with open("products.json", "w", encoding='utf8') as file:
        file.write(product_info_json)
