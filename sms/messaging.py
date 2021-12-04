from __future__ import print_function
from telesign.messaging import MessagingClient


customer_id = ""
api_key = ""

phone_number = ""
message_type = "ARN"

messaging = MessagingClient(customer_id, api_key)


def send(msg):
    response = messaging.message(phone_number, msg, message_type)


if __name__=="__main__":
    send("I shouldnt have this power")