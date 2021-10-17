import os
from twilio.rest import Client


# Find your Account SID and Auth Token at twilio.com/console
# and set the environment variables. See http://twil.io/secure
account_sid = 'AC0a38e4d918e7c1e3e64ba772018512d9'
auth_token = 'aab6a1ee1d105739257b1ca079c0385e'
client = Client(account_sid, auth_token)

message = client.messages \
                .create(
                     body="Join Earth's mightiest heroes. Like Kevin Bacon.",
                     from_='+16627802933',
                     to='+6592375375'
                 )

print(message.sid)
