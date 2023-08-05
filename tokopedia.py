from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import pandas as pd
import time
import requests
import os

def get_html(keyword: str):
    option = webdriver.ChromeOptions()
    option.add_argument('--headless')
    option.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36')
    service = Service('../chromedriver-win32/chromedriver.exe')
    driver = webdriver.Chrome(service=service, options=option)
    driver.set_window_size(1300, 800)

    url = f'https://www.tokopedia.com/search?st=&q={keyword}'
    driver.get(url)

    for i in range(1, 7):   # 6 x scroll
        scroll = i * 1000
        js = f'window.scrollTo(0, {str(scroll)})'
        driver.execute_script(js)
        time.sleep(1)

    time.sleep(3)
    driver.save_screenshot('screenshot.png')
    pageSource = driver.page_source
    driver.quit()
    return pageSource

def download_image(image, productName):
    res = requests.get(image)
    if res.status_code == 200:
        image_data = res.content
        image_name = ''.join(filter(str.isalnum, productName))
        image_filename = os.path.join('images', f'{image_name}.jpg')
        with open(image_filename, 'wb') as f:
            f.write(image_data)

def parse_products(html):
    content = BeautifulSoup(html, 'html.parser')
    items = content.findAll('div', 'pcv3__container css-gfx8z3')
    results = []

    for item in items:
        image = item.find('img', 'css-1q90pod')['src']
        name = item.find('div', 'prd_link-product-name css-3um8ox').text
        price = item.find('div', 'prd_link-product-price css-1ksb19c').text
        location = item.find('span', 'prd_link-shop-loc css-1kdc32b flip')
        shop = item.find('span', 'prd_link-shop-name css-1kdc32b flip')
        rating = item.find('span', 'prd_rating-average-text css-t70v7i')
        sold = item.find('span', 'prd_label-integrity css-1duhs3e')
        link = item.find('a', 'pcv3__info-content css-gwkf0u')['href']

        if location: location = location.text
        if shop: shop = shop.text
        if rating: rating = rating.text
        if sold: sold = sold.text

        download_image(image, name)
        results.append({
            'Product Name': name,
            'Price': price,
            'Location': location,
            'Shop Name': shop,
            'Rating': rating,
            'Sold': sold,
            'Image': image,
            'Link': link
        })
    
    return results

def to_csv(data):
    dataframe = pd.DataFrame(data)
    dataframe.to_csv('Data Products.csv', index=False)

def main():
    html = get_html('sepatu')
    results = parse_products(html)
    to_csv(results)

if __name__ == '__main__':
    main()