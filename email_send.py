import smtplib
import os

def send_email(item):
    my_email = "testqj1234@gmail.com"
    msg = f"Subject: {item.name} : son prix passe sous {(item.price_trigger)} sur Amazon\n\nC'est le moment d'acheter : {item.name} est à {item.amazon_price}€\n{item.url}"
    with smtplib.SMTP("smtp.gmail.com", port="587") as connection:
        connection.starttls()
        connection.login(user=my_email, password=os.getenv("TESTQJ_PWD"))
        connection.sendmail(from_addr=my_email, to_addrs=item.email_address, msg=msg.encode("utf8"))