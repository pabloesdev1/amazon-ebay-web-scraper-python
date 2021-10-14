from selenium import webdriver
from bs4 import BeautifulSoup
from time import sleep
from notifypy import Notify
from threading import Thread
from connection import *
from Products import Products

def get_soup(url):
    driver = webdriver.Chrome('driver/chromedriver')
    driver.get(url)
    sleep(1)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    driver.close()
    return soup

def get_amazon_object(soup):
    products = soup.find_all('div', {'class':'s-result-item'})
    for i, product in enumerate(products):
        try:
            name = product.find('span', {'class':'a-size-medium a-color-base a-text-normal'}).text
            price = product.find('span', {'class':'a-price'}).text
            print(f'{i+1}. {name}. Precio: {price}')
        except:
            pass
    selected = int(input("Escoja el producto de Amazon: "))
    amazon_url = products[selected-1].find('a', {'class':'a-link-normal s-no-outline'}).attrs['href']
    amazon_price = products[selected-1].find('span', {'class':'a-price'}).text
    return amazon_url, amazon_price.split('$').pop().replace(',', '')

def get_ebay_object(soup):
    products = soup.find_all('li', {'class':'s-item'})
    for i, product in enumerate(products):
        try:
            name = product.find('h3', {'class':'s-item__title'}).text
            price = product.find('span', {'class':'s-item__price'}).text
            print(f'{i+1}. {name}. Precio: {price}')
        except:
            pass
    selected = int(input("Escoja el producto de eBay: "))
    ebay_url = products[selected-1].find('a', {'class':'s-item__link'}).attrs['href']
    ebay_price = products[selected-1].find('span', {'class':'s-item__price'}).text
    return ebay_url, ebay_price[3:]

def check_price():
    while True:
        products = Products(None, None, None, None, None).get_products()
        for product in products:
            amazon_soup = get_soup("https://www.amazon.com"+product[2])
            ebay_soup = get_soup(product[3])
            new_amazon_price = amazon_soup.find('span', {'class': 'a-size-base a-color-base'}).text
            new_ebay_price = ebay_soup.find('div', {'class':'display-price'}).text
            print(f'Producto {product[1].replace("+", " ")}:')
            print(f'Amazon: Precio anterior: {str(product[4])} Nuevo precio: {new_amazon_price[5:]}')
            print(f'eBay: Precio anterior: {str(product[5])} Nuevo precio: {new_ebay_price[3:]}')
            if float(new_amazon_price[5:]) < float(product[4]):
                send_alert(f'El producto {product[1].replace("+", " ")} bajó de precio en Amazon')
            if float(new_ebay_price[3:]) < float(product[5]):
                send_alert(f'El producto {product[1].replace("+", " ")} bajó de precio en eBay')
            if float(new_amazon_price[5:]) < float(new_ebay_price[3:]):
                send_alert(f'El producto {product[1].replace("+", " ")} tiene un precio menor en Amazon')
            if float(new_ebay_price[3:]) < float(new_amazon_price[5:]):
                send_alert(f'El producto {product[1].replace("+", " ")} tiene un precio menor en eBay')
        sleep(3600)

def send_alert(message):
    notification = Notify()
    notification.title = "Cambio de precios de productos"
    notification.message = message
    notification.send()

def init():
    response = input("Desea registrar un nuevo producto? y/n:")
    if response == "y":
        name = input("Ingrese el nombre del producto a buscar: ").replace(" ", "+")
        amazon_result_url = f'https://www.amazon.com/s?k={name}&__mk_es_US=%C3%85M%C3%85%C5%BD%C3%95%C3%91&crid=W76FKPSY8H8K&sprefix=log%2Caps%2C272&ref=nb_sb_noss_1'
        ebay_result_url = f'https://www.ebay.com/sch/i.html?_from=R40&_trksid=p2380057.m570.l1312&_nkw={name}&_sacat=0'
        amazon_soup = get_soup(amazon_result_url)
        ebay_soup = get_soup(ebay_result_url)
        amazon_url, amazon_price = get_amazon_object(amazon_soup)
        ebay_url, ebay_price = get_ebay_object(ebay_soup)
        products = Products(name, amazon_url, ebay_url, amazon_price, ebay_price)
        print(products.save_products())
    
    thread = Thread(target=check_price)
    thread.start()

if __name__ == "__main__":
    init()