from tkinter import *
from PIL import ImageTk, Image
from database_op import db_get_all_dict
from item_manager import item_info_master, str_price
import requests
import sys

# ------------------- CONSTANTS ------------------- #
#Main Buttons settings
MB_WIDTH = 50
MB_HEIGHT = MB_WIDTH
MB_X_PADDING = 10
MB_Y_PADDING = 10

#Logo Settings
LOGO_WIDTH = 200
LOGO_HEIGHT = LOGO_WIDTH #Change if logo not square

#Product Pictures Settings
PRODUCT_P_HEIGHT = 150
PRODUCT_P_WIDTH = PRODUCT_P_HEIGHT #Change if picture not square
PRODUCT_P_Y_PAD = int(PRODUCT_P_HEIGHT/10)

#Product Frames settings
PRODUCT_FRAME_WIDTH = PRODUCT_P_WIDTH + 40
PRODUCT_FRAME_HEIGHT = int(PRODUCT_FRAME_WIDTH*1.55)
PRODUCT_FRAME_PADX = 10 #keep it int : ROOT_WIDTH uses this setting
PRODUCT_FRAME_PADY = PRODUCT_FRAME_PADX

SMALL_B_HEIGHT = PRODUCT_P_HEIGHT
SMALL_B_WIDTH = SMALL_B_HEIGHT #Change if picture not square

NB_COLUMNS = 3

#Root settings
ROOT_WIDTH = int(NB_COLUMNS*(PRODUCT_FRAME_WIDTH + 2*PRODUCT_FRAME_PADX) +40)
ROOT_HEIGHT = 800
ROOT_GEOMETRY = str(ROOT_WIDTH) + 'x' + str(ROOT_HEIGHT)

FONT_FAMILY = 'Nirmala UI Semilight'
PRODUCT_NAME_FONT = (FONT_FAMILY, 11)
CURRENT_PRICE_FONT_FAMILY = 'Segoe UI Semibold'
CURRENT_PRICE_FONT_SIZE = 24
TARGET_PRICE_FONT = (FONT_FAMILY, 10, "italic")


# ------------------- CLASSES ------------------- #
class WaitingWindow(Toplevel):
    def __init__(self, takefocus=True, **kw):
        super().__init__(**kw)
        w_lbl = Label(text="Retrieving price data", padx=40, pady=40).pack()

class MainButton(Button):
    def __init__(self, img_file="icons/filler.png", parent=None, *args, **kwargs):
        Button.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        with Image.open(img_file) as i:
            i_resized = i.resize((MB_WIDTH, MB_HEIGHT), Image.NEAREST)
            self.img = ImageTk.PhotoImage(i_resized)
            #kwargs["image"] = img
            self.config(image=self.img, bd=5)

class SmallButton(Button):
    def __init__(self, img_file="icons/filler.png", parent=None, *args, **kwargs):
        Button.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        with Image.open(img_file) as i:
            i_resized = i.resize((SMALL_B_WIDTH, SMALL_B_HEIGHT), Image.NEAREST)
            self.img = ImageTk.PhotoImage(i_resized)
            #kwargs["image"] = img
            self.config(image=self.img, bd=5)

class ItemFrame(item_info_master):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.frame = Frame(ds_frame, bg='white', width=PRODUCT_FRAME_WIDTH, height=PRODUCT_FRAME_HEIGHT)
        self.frame.pack_propagate(0)
        self.product_image = download_image(self.img_url)
        self.product_canvas = Canvas(self.frame, width=PRODUCT_P_WIDTH, height=PRODUCT_P_HEIGHT, bg="white",
                                     highlightthicknes=0)
        self.product_canvas.create_image(PRODUCT_P_WIDTH // 2, PRODUCT_P_HEIGHT // 2, image=self.product_image)
        self.product_canvas.pack(anchor='center', pady=PRODUCT_P_Y_PAD)
        self.name_label = Label(self.frame, text=self.name, anchor="w",font=PRODUCT_NAME_FONT, height=1, wraplength=PRODUCT_P_WIDTH, pady=10, bg='white')
        self.name_label.pack()
        self.current_price_label = Label(self.frame, font=(CURRENT_PRICE_FONT_FAMILY, CURRENT_PRICE_FONT_SIZE), text=str(self.amazon_price), anchor="center", bg="white", fg='green')
        self.current_price_label.pack(fill='x')
        self.target_price_label = Label(self.frame, font=TARGET_PRICE_FONT, text=f"Prix cible : {str_price(self.price_trigger)}", justify="left", anchor="w", bg='white', pady=0)
        self.target_price_label.pack(fill='x')

    def check_update_price(self):
        self.ww = WaitingWindow()
        self.parse("price")
        self.current_price_label.configure(text=str_price(self.amazon_price))
        self.current_price_format()
        self.ww.destroy()

    def current_price_format(self):
        if type(self.amazon_price) not in (int, float) or self.amazon_price <= 0:
            lh = self.current_price_label.winfo_reqheight()
            self.current_price_label.configure(fg='#d8b6a4', font=(CURRENT_PRICE_FONT_FAMILY, CURRENT_PRICE_FONT_SIZE // 2), height=2)
        elif self.price_trigger >= self.amazon_price:
            self.current_price_label.configure(fg='green')
        elif self.price_trigger + min(10, 0.1 * self.price_trigger) >= self.amazon_price:
            self.current_price_label.configure(fg='orange')
        else :
            self.current_price_label.configure(fg='red')



# ------------------- FUNCTIONS ------------------- #
def download_image(url):
    with Image.open(requests.get(url, stream=True).raw) as img:
        img_resized = img.resize((PRODUCT_P_WIDTH, PRODUCT_P_HEIGHT), Image.NEAREST)
        product_img = ImageTk.PhotoImage(img_resized)
    return product_img

def db_get_all_frames():
    items_list = db_get_all_dict()
    f_list = [ItemFrame(name=d['name'],
                                url=d['url'],
                                price_trigger=d['priceTrigger'],
                                img_url=d['imgUrl'],
                                email_adress=d['emailAddress'],
                                id=d["id"]
                                ) for d in items_list]
    return f_list

def leave_b_command():
    raise SystemExit

def check_update_price_all_command():
    global frames_list
    for frame in frames_list:
        frame.check_update_price()

# ------------------- GLOBAL VARIABLES ------------------- #


# ------------------- MAIN WINDOW ------------------- #
root = Tk()
root.title("Amazon Price Comparator")
root.geometry(ROOT_GEOMETRY)
#root.configure(background='white')
window_width = root.winfo_width()
window_height = root.winfo_height()

# ------------------- LOGO ------------------- #
# # - Frame - #
# logo_frame = Frame(root)
# logo_frame.pack()
# # - Image & canvas - #
# with Image.open("icons/logo.png") as img:
#     img_resized = img.resize((LOGO_WIDTH, LOGO_HEIGHT), Image.NEAREST)
#     logo_img = ImageTk.PhotoImage(img_resized)
# logo_canvas = Canvas(logo_frame, width=LOGO_WIDTH, height=LOGO_HEIGHT)
# logo_canvas.create_image(LOGO_WIDTH // 2, LOGO_HEIGHT // 2, image=logo_img)
# logo_canvas.pack()


# ------------------- MAIN BUTTONS ------------------- #
mb_frame = Frame(root)
main_buttons_list_setup = [
    {
        "img_file": "icons/plus.png",
        "command": None,
    },
    {
        "img_file": "icons/download.png",
        "command": check_update_price_all_command,
    },
    {
        "img_file": "icons/search.png",
        "command": None,
    },
    {
        "img_file": "icons/logout.png",
        "command": leave_b_command,
    },
]

main_buttons_list = []
x_b = 0
for b in main_buttons_list_setup:
    button = MainButton(parent=mb_frame, img_file=b["img_file"], command=b["command"])
    main_buttons_list.append(button)
    button.grid(row=0, column=x_b, padx=(0, MB_X_PADDING*2), pady=MB_Y_PADDING)
    x_b += 1
main_buttons_list[-1].grid(row=0, column=x_b, padx=0, pady=MB_Y_PADDING)
mb_frame.pack(pady=(5, 20))

# ------------------- HEADER ------------------- #

# ------------------- GRID ------------------- #
# - Scrollable container - #
def on_frame_configure():
    ds_frame_canvas.configure(scrollregion=ds_frame_canvas.bbox("all"))

ds_frame_canvas = Canvas(root, borderwidth=0, width=ROOT_WIDTH)
ds_frame_canvas_scrollbar = Scrollbar(root, orient='vertical', command=ds_frame_canvas.yview)
ds_frame_canvas.configure(yscrollcommand=ds_frame_canvas_scrollbar.set)

ds_frame_canvas_scrollbar.pack(side="right", fill="y")
ds_frame_canvas.pack(side="left", fill="y", expand=True)


# - Frame Datastructure - #
ds_frame = Frame(ds_frame_canvas)
ds_frame_canvas.create_window((4,4), window=ds_frame, anchor='nw', tags="ds_frame")
ds_frame.bind("<Configure>", lambda event, ds_frame_canvas=ds_frame_canvas: on_frame_configure())

frames_list = db_get_all_frames()
(i, j) = (0, 0)
for f in frames_list:
    f.frame.configure(width=PRODUCT_FRAME_WIDTH)
    f.frame.grid(row=j, column=i, padx=PRODUCT_FRAME_PADX, pady=PRODUCT_FRAME_PADY)
    if i < NB_COLUMNS-1:
        i += 1
    else:
        j += 1
        i = 0















frames_list[0].check_update_price()
frames_list[1].check_update_price()

# ------------------- UI MAINLOOP ------------------- #
root.mainloop()