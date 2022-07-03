# Where all the requests to the database happen

import requests
URL = "https://api.sheety.co/2567eed278a0ace4c26769a1a2149216/amazonItemsDatabase/items"

def db_get_all_dict():
    payload = requests.get(url=URL)
    payload.raise_for_status()
    d = payload.json()
    list_d = items_add_id(d["items"])
    return list_d

def items_add_id(items_list):
    i = 2
    for k in items_list:
        k["id"] = i
        i += 1
    return items_list


def db_add_item(item):
    # Beware of init : datasheet should be set with proper columns to work
    dict = {
        "name": item.name,
        "url": item.url,
        "priceTrigger": item.price_trigger,
        "imgUrl": item.img_url,
        "emailAddress": item.email_address,
    }

    payload = {"item": dict}

    add = requests.post(url=URL, json=payload)
    add.raise_for_status()

def db_del_item(item):
    url_suppr = URL+"/"+str(item.id)
    suppr = requests.delete(url=url_suppr)
    suppr.raise_for_status()


