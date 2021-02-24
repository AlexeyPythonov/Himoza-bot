import requests
from bs4 import BeautifulSoup as BS

class Parse():
    def __init__(self, url):
        self.url = url
        self.values = []
        source = requests.get(self.url)
        self.html = BS(source.text, 'lxml')

    def get_content(self):
        div = self.html.find('div', {'data-marker': 'catalog-serp'})
        
        for div_it in div.find_all('div', {'data-marker': 'item'}):
            div_it_cont = div_it.find('div', {'class': 'iva-item-content-m2FiN'})           

            for img in div_it_cont.find_all('img', {'class': 'photo-slider-image-3kAVC'}):              
                div_it_img = img.get('src')           
            div_it_title = div_it_cont.find('div', {'class': 'iva-item-titleStep-2bjuh'})
            div_it_price = div_it_cont.find('div', {'class': 'iva-item-priceStep-2qRpg'})
            div_it_price = div_it_price.text
            div_it_price = div_it_price.replace('\xa0', '')
            div_it_date = div_it_cont.find('div', {'class': 'iva-item-dateStep-pZ3hT'})

            if div_it_img not in self.values:
                self.values.append(div_it_img)
                self.values.append(div_it_title.text)
                self.values.append(div_it_price)
                self.values.append(div_it_date.text)

        self.values = self.values[:16]

        return self.values
