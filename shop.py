import requests
from bs4 import BeautifulSoup
from requests.exceptions import ConnectionError
from telegram import Logger
from dotenv import load_dotenv
import os

load_dotenv()


logger = Logger(
    token=os.getenv("APIKey"), chat_id=os.getenv('chatID1'))

TRENDYOL = "www.trendyol.com"
ZARA = "www.zara.com"
class Shop:
    _headers = {
        'User-agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:108.0) Gecko/20100101 Firefox/108.0'}
    stock_list = []
    discount_list = []

    def __init__(self, url, price_check=False):
        self.URL = url
        self.price_check = price_check
        self.html_page = self.get_html()
        self.name = self.get_name()
        self.price = self.get_price()
        self.stock_or_discount()
        self.stock_control()

    def get_html(self):
        try:
            response = requests.get(self.URL, headers=Shop._headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            return soup
        except ConnectionError:
            logger.warning(message=f"{self.name} gelen response istenilen türde değil lütfen siteyi kontrol et.{self.URL}\nfunc: get_html")

    def stock_or_discount(self):
        """
        Oluşturulan objenin discount_list mi stock_list e mi gideceğine
        karar veren fonksiyon.
        """
        if self.price_check:
            Shop.discount_list.append(self)
        else:
            Shop.stock_list.append(self)

    def stock_control(self):
        """
        Gelen linkin mağazasını kontrol edip ona göre CSS selector ile 
        stock kontrolu yapıyor ve main.py da yakalanmak üzere objenin boolean değerini
        döndürüyor.
        """
        try:
            if TRENDYOL in self.URL:
                button = self.html_page.find(class_="sold-out")
                if button:
                    self.is_stock = False
                else:
                    self.is_stock = True

            elif ZARA in self.URL:
                buttons = self.html_page.find(class_="zds-button")
                no_stock_list = ["TÜKENDİ", "BENZER ÜRÜNLER", "COMİNG SOON"]
                if buttons.text in no_stock_list:
                    self.is_stock = False
                else:
                    self.is_stock = True
        except AttributeError:
            logger.warning(message=f"{self.name} Ürünle ile ilgili sıkıntı var yetiş {self.URL}\nfunc: stock_control")

    def get_name(self):
        try:
            if TRENDYOL in self.URL:
                name = self.html_page.find(class_="pr-new-br")
                name = name.span.text.strip()
                return name
            elif ZARA in self.URL:
                header = self.html_page.find(
                    class_="product-detail-info__header-name").text
                return header
        except AttributeError:
            logger.warning(message=f"{self.name} Ürün silinmiş olabilir {self.URL}\nfunc: get_name")

    def get_price(self):
        try:
            if TRENDYOL in self.URL:
                price = self.html_page.find(class_="prc-dsc")
                price = price.text.split(" ")[0].replace(",", ".")
                return price
            elif ZARA in self.URL:
                current_price_text = self.html_page.find(
                    class_="price-current__amount").text
                current_price = current_price_text.split(' ')[0]
                current_price = current_price.replace(",", ".")
                return current_price
        except AttributeError:
            logger.warning(message=f"{self.name} Ürünün fiyatıyla alakalı bir problem var. {self.URL}\nfunc: get_price")
        
