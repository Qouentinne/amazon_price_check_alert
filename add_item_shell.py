# Adding items to be tracked in the database from a terminal

from item_manager import item_info_v1
from database_op import db_add_item

want_add_item = True
breaker = "\nType 'exit' to leave the program, 'continue' to register another product\n"

while want_add_item:
    i = item_info_v1()
    db_add_item(i)
    if input(breaker) == 'exit':
        want_add_item = False