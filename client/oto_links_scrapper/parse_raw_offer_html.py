from bs4 import BeautifulSoup
import re

from shared.objects.webpage import Webpage

def get_offer_details(webpage:Webpage, page_raw:str):
    soup = BeautifulSoup(page_raw, 'html.parser')
    webpage.offer_title = soup.find('h3', {'class':['offer-title', 'big-text'] }).get_text().strip()
    date_id_box = soup.find('div', {'class':['ooa-xwja0b', 'e14erkch0']})
    date_id_box = date_id_box.find_all(('p', {'class':['e14erkch4', 'ooa-1afacld', 'er34gjf0']}))
    webpage.added_date = date_id_box[0].get_text().strip()
    webpage.offer_id = date_id_box[1].get_text().strip()
    webpage.price = soup.find('h3', {'class':'offer-price__number'}).get_text().strip()
    webpage.currency = soup.find('p', {'class':'offer-price__currency'}).get_text().strip()
    try:
        webpage.description = soup.find('div', {'class':['ooa-1xkwsck', 'e1336z0n2']}).get_text().strip()
    except AttributeError as ae:
        webpage.description = None
    coords_1 = soup.find('div', {'class', 'gm-style'})
    coords_1 = coords_1.find_all('a', attrs={'href': re.compile("^https://")})
    coords_1 = [link.get('href') for link in coords_1][0]
    webpage.coordinates = coords_1.split('ll=')[1].split('&')[0]