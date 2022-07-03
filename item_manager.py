# TODO 1:
#   Avoir un format d'objet qui pourra être utilisé en argument de scraping : url / prix déclencheur / nom de l'objet
#       Créer un format parent pour format d'objet v1 (ajout item v/ shell) et v2 (ajout item v/ GUI)
#   Boucle qui permet d'ajouter des objets à surveiller (url + prix déclencheur)
#       Bonus : chercher les infos prix sur camelcamelcamel
#   Formaliser un json pour enregistrer les infos => directement BDD Google Sheets ?

# TODO 2:
#   Automatiser le lancement du script
#   Prévoir un système de synchronisation (Google Sheet?) pour la BDD objets
#   Concevoir système d'édition (prix déclencheur) + suppression des objets en BDD
#   GUI pour édition ?
#       Fonction de vérification d'envoi d'email
#   Passer du HTML dans l'email d'alerte
#       => lien
#       => autres : mise en forme, image, etc.

import lxml
import requests
from bs4 import BeautifulSoup
import re
import ast
from database_op import db_get_all_dict


def float_price(raw_price):
    raw_price = raw_price.replace(",", ".")
    clean_p = re.sub(r"[' '€]", "", raw_price)
    return float(clean_p)

def str_price(price) -> str:
    if price == 0:
        return "Price not found"
    else:
        if int(price) == price:
            return str(int(price)) + "€"
        else:
            price = str(price).replace(".", ",")
            return price + "€"

def itemizer(dict):
    """
    Return an item format from database request dict format
    """
    return item_info_master(dict)

def generate_all_item_info_master():
    """Returns all the entries in the database in the form of a list of item_info_master objects"""
    items_list = db_get_all_dict()
    item_info_master_list = [item_info_master(name=d['name'],
                               url=d['url'],
                               price_trigger=d['priceTrigger'],
                               img_url=d['imgUrl'],
                               email_adress=d['emailAddress'],
                               id=d["id"]
                               ) for d in items_list]
    return item_info_master_list

class item_info_master:
    def __init__(self, **kw):
        self.name = kw.get("name")
        self.url = kw.get("url")
        self.email_address = kw.get("email_adress")
        self.img_url = kw.get("img_url")
        self.id = kw.get("id")
        self.amazon_price = "-"
        price_trigger = kw.get("price_trigger")
        if type(price_trigger) in (int, float):
            self.price_trigger = float(price_trigger)
        elif type(price_trigger) == str:
            self.price_trigger = float_price(price_trigger)


    def scrape(self):
        self.headers = {
            "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Accept-Encoding":"gzip, deflate, br",
            "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36",
            "Accept-Language":"fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
        }

        response = requests.get(url=self.url, headers=self.headers)
        data = response.text
        soup = BeautifulSoup(data, "lxml")
        self.scraped_soup = soup

    def parse(self, *args, print_results=False ):
        """"Arguments : price, img_url
        Parse item scraped shop webpage (scrape automatically if required)"""
        #----------- Check if scraping is required -----------#
        if not hasattr(self, "scraped_soup"):
            self.scrape()
        # ----------- Price parsing if price is an argument -----------#
        if "price" in args:
            #Price does not always exist and can fall under various markups / tags
            #Method to retrieve them is to
            #   look for the td that contain the string "Prix :"
            #   get next td => contains the price
            #/!\ Method based on string => only works w/ specific language
            try:
                string_td = self.scraped_soup.find_all("td", string="Prix :")[-1]
                price_td = string_td.find_next_sibling("td")
                raw_price = str(price_td.find(string=re.compile("[€]$")))
                self.amazon_price = float_price(raw_price)
            except:
                self.amazon_price = 0.0
            if print_results:
                print(self.amazon_price)
        # ----------- Image url parsing if img_url is an argument -----------#
        if "img_url" in args:
            #The aim is to get the thumbnail "Other people also bought" url.
            #Main picture requires javascript scraping
            try:
                div = self.scraped_soup.find(class_="a-section thumbnail-1")        #thumbnail is in this div with a unique class
                str_list_url = div.img.attrs["data-a-dynamic-image"]                #String type. A 'dictionary' w/ all thumbnails url w/ various sizes
                img_url_dict = ast.literal_eval(str_list_url)                       #Dictionary type conversion from string
                img_url_list = [index for (index,value) in img_url_dict.items()]    #List comprehension of dictionary
                self.img_url = img_url_list[-1]                                     #Get the last one in the list (better resolution)
            except:
                self.img_url = "https://www.google.com/images/errors/robot.png"
            if print_results:
                print(self.img_url)




class item_info_v1(item_info_master):
    def __init__(self):
        super().__init__()
        self.name = input("\nWhat is the name of the item to be tracked?\n")
        self.url = input('Fill in the Amazon url of the product you want to track\n')
        self.price_trigger = float_price(input('Under which price (€) do you want to receive an alert?\n'))
        self.email_address = 'quent1_jarry@hotmail.com'
        self.parse("img_url") #provides self.img_url