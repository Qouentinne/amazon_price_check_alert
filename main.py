from database_op import *
from item_manager import *
from email_send import send_email



def main():
    list_i = generate_all_item_info_master()
    for item in list_i:
        item.scrape()
        print(f"{item.name}\nPrice Trigger = {item.price_trigger}\nCurrent Price = {item.amazon_price}\n\n")
        if item.amazon_price > item.price_trigger or item.amazon_price == 0:
            pass
        else:
            send_email(item)
    print("Amazon price checker complete")

main()




